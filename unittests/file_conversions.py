# -*- encoding: utf-8 -*-

from collections import OrderedDict
from io import BytesIO
import os.path
import re
from shutil import copyfileobj
from zipfile import ZipFile

import h5py
import numpy as np
import xlrd

SAMPLING_FREQUENCY = 25.0


def convert_text_file_to_h5(input_file, output_file):
    '''Convert a text file into a HDF5 file

    The parameter "input_file" should be a file-like object. The HDF5 file will
    be saved into "output_file" (which can either be a file name or a file-like
    object).
    '''

    rawdata = np.loadtxt(input_file, skiprows=1)
    if rawdata.shape[1] != 13:
        raise ValueError('the input file has {0} columns instead of 13'
                         .format(data.shape[1]))

    data_type = np.dtype([
        ('time_s', np.float32),
        ('pctime', np.float32),
        ('phb', np.int8),
        ('record', np.int8),
        ('dem_Q1_ADU', np.float32),
        ('dem_U1_ADU', np.float32),
        ('dem_U2_ADU', np.float32),
        ('dem_Q2_ADU', np.float32),
        ('pwr_Q1_ADU', np.float32),
        ('pwr_U1_ADU', np.float32),
        ('pwr_U2_ADU', np.float32),
        ('pwr_Q2_ADU', np.float32),
        ('rfpower_dB', np.float32),
        ('freq_Hz', np.float32)
    ])

    with h5py.File(output_file, 'w') as h5_file:
        data = h5_file.create_dataset(
            'time_series', (rawdata.shape[0],),
            dtype=data_type, compression='gzip', shuffle=True)

        data['time_s'] = np.arange(rawdata.shape[0]) / SAMPLING_FREQUENCY
        data['pctime'] = rawdata[:, 0]
        data['phb'] = rawdata[:, 1]
        data['record'] = rawdata[:, 2]
        data['dem_Q1_ADU'] = rawdata[:, 3]
        data['dem_U1_ADU'] = rawdata[:, 4]
        data['dem_U2_ADU'] = rawdata[:, 5]
        data['dem_Q2_ADU'] = rawdata[:, 6]
        data['pwr_Q1_ADU'] = rawdata[:, 7]
        data['pwr_U1_ADU'] = rawdata[:, 8]
        data['pwr_U2_ADU'] = rawdata[:, 9]
        data['pwr_Q2_ADU'] = rawdata[:, 10]
        data['rfpower_dB'] = rawdata[:, 11]
        data['freq_Hz'] = rawdata[:, 12]


def read_worksheet_table(wks):
    '''Read a table of numbers from an Excel file saved by Keithley.

    This function reads the first worksheet in the Excel file passed as
    argument and returns a dictionary associating NumPy arrays with their
    names.
    '''

    sheet = wks.sheet_by_index(0)
    result = OrderedDict()
    nrows = sheet.nrows
    for cur_col in range(sheet.ncols):
        name = sheet.cell(0, cur_col).value
        if len(name) >= len('START') and name[:5] == 'START':
            # This column and the following are not useful
            break
        result[name] = np.array([sheet.cell(i, cur_col).value
                                 for i in range(1, nrows)])

    return result


def read_worksheet_settings(wks):
    sheet = wks.sheet_by_name('Settings')
    result = OrderedDict()
    for cur_row in range(sheet.nrows):
        key = str(sheet.cell(cur_row, 0).value)
        if key == '':
            continue

        if key == 'Formulas':
            break

        values = []
        for cur_col in range(1, sheet.ncols):
            cur_value = sheet.cell(cur_row, cur_col).value
            if str(cur_value) == '':
                break

            values.append(cur_value)

        if len(values) == 1:
            values = values[0]

        result[key] = values

    return result


def hygenize_name(name):
    'Return a name which is suitable for HDF5 column/keyword names'

    # Remove unwanted character and clip to the first 8 characters
    return ''.join([ch for ch in name.upper() if not ch in (' ', '+', '-', '(', ')')])[:8]


def unit_from_name(name):
    'Return a reasonable measure unit for a column in the Excel file'

    if 'DrainI' in name:
        return 'A'
    elif 'GateI' in name:
        return 'A'
    elif 'AnodeI' in name:
        return 'A'
    elif 'BaseI' in name:
        return 'A'
    elif 'EmitterI' in name:
        return 'A'
    elif 'DrainV' in name:
        return 'V'
    elif 'GateV' in name:
        return 'V'
    elif 'AnodeV' in name:
        return 'V'
    elif 'BaseV' in name:
        return 'V'
    elif 'EmitterV' in name:
        return 'V'
    else:
        raise ValueError('column "{0}" was not recognized'.format(name))


def convert_excel_file_to_h5(input_file, h5_file, dataset_name):
    'Convert an Excel file into a HDF5 dataset'

    # Read data and metadata from the Excel file
    with xlrd.open_workbook(file_contents=input_file.read()) as workbook:
        settings = read_worksheet_settings(workbook)
        datatable = read_worksheet_table(workbook)

    assert len(datatable.keys()) > 0, \
        'unexpected format for Excel file "{0}", no rows of data'.format(
            input_file.name)

    # In a data table produced by Keithley, we have columns named like in the
    # following example:
    #
    #   GateI(1) GateV(1) DrainI(1)  GateI(2) GateV(2) DrainI(2)  ...
    #
    # We refer to the tuple (GateI, GateV, DrainI) as a «block», and we are
    # going to save all these data in a HDF5 3D data block. To do this, we need
    # to understand how many columns are in a block, so we build the variable
    # "basenames", which should ideally be equal to ["GateI", "GateV", "DrainI"]
    # for the example above.

    basename_re = re.compile('^[a-zA-Z]+')
    basenames = []
    samples_per_column = None
    for cur_key in datatable.keys():
        if not samples_per_column:
            samples_per_column = len(datatable[cur_key])
        cur_basename = basename_re.search(cur_key)
        assert cur_basename, 'unable to understand column "{0}"'.format(
            cur_key)
        cur_column_name = cur_basename.group(0)
        if cur_column_name in basenames:
            # We're done, we have got a column which we already got: this
            # signals a new block (e.g., we are getting "DrainI(2)" after we
            # already found "DrainI(1)")
            break

        basenames.append(cur_column_name)

    # If we built "basenames" correctly, the number of columns should be a
    # multiple of "basename"'s length
    assert len(datatable.keys()) % len(basenames) == 0, \
        'unexpected data columns at the end of the Excel file "{0}"'.format(
            input_file.name)

    # We use a custom type for samples in a block, so we can keep the 3-tuple of
    # values together
    data_type = np.dtype([(x, np.float32) for x in basenames])

    num_of_blocks = len(datatable.keys()) // len(basenames)
    dataset = h5_file.create_dataset(
        dataset_name, (samples_per_column, num_of_blocks),
        dtype=data_type, compression='gzip', shuffle=True)

    # It's time to fill the HDF5 dataset
    fixed_column = None
    fixed_min, fixed_max = None, None
    for cur_block_idx in range(num_of_blocks):
        for cur_basename in basenames:
            if num_of_blocks > 1:
                cur_key = '{0}({1})'.format(cur_basename, cur_block_idx + 1)
                values = datatable[cur_key]
            else:
                values = datatable[cur_basename]

            dataset[cur_basename, :, cur_block_idx] = values

            # If the column doesn't change, keep track of it
            if not fixed_column and (np.max(values) - np.min(values) < 1e-10):
                fixed_column = cur_basename

            # Extract some statistics from fixed columns
            if fixed_column == cur_basename:
                if not fixed_min:
                    # Take just the first, they're all the same
                    fixed_min = values[0]
                else:
                    fixed_min = min(fixed_min, values[0])
                if not fixed_max:
                    fixed_max = values[0]
                else:
                    fixed_max = max(fixed_max, values[0])

    if fixed_column:
        dataset.attrs['fixed_value'] = fixed_column
        dataset.attrs['fixed_min'] = fixed_min
        dataset.attrs['fixed_max'] = fixed_max
        dataset.attrs['fixed_delta'] = (fixed_max - fixed_min) / num_of_blocks

    # For completeness, we append any string taken from the Excel file's
    # metadata to the list of attributes for this dataset
    for key, value in settings.items():
        if type(value) is str:
            dataset.attrs[hygenize_name(key)] = value


def convert_zip_file_to_h5(input_file, output_file):
    '''Convert the Excel files in a ZIP file into one HDF5 file

    The Excel files must have been saved using the Keithley machine, either the
    old or the new one. All the files are saved in separate HDU in the HDF5
    files.

    The parameter "input_file" must be a file-like object, which will be treated
    as a ZIP archive. The HDF5 file will be named after "output_file".
    '''

    # To check the correspondences between the (two!) notations used in
    # Bicocca and the proper STRIP naming conventions, refer to the note
    # LSPE-STRIP-SP-004 («LSPE-STRIP naming convention»)
    dataset_names = {
        # HEMT tests (Idrain vs Vdrain)
        'Q1/tests/data/Id_vs_Vd': 'HA1/IDVD', 'Id_vs_Vd_H0': 'HA1/IDVD',
        'Q2/tests/data/Id_vs_Vd': 'HA2/IDVD', 'Id_vs_Vd_H2': 'HA2/IDVD',
        'Q3/tests/data/Id_vs_Vd': 'HA3/IDVD', 'Id_vs_Vd_H4': 'HA3/IDVD',
        'Q6/tests/data/Id_vs_Vd': 'HB1/IDVD', 'Id_vs_Vd_H1': 'HB1/IDVD',
        'Q5/tests/data/Id_vs_Vd': 'HB2/IDVD', 'Id_vs_Vd_H3': 'HB2/IDVD',
        'Q4/tests/data/Id_vs_Vd': 'HB3/IDVD', 'Id_vs_Vd_H5': 'HB3/IDVD',

        # HEMT tests (Idrain vs Vgate)
        'Q1/tests/data/Id_vs_Vg': 'HA1/IDVG', 'Id_vs_Vg_H0': 'HA1/IDVG',
        'Q2/tests/data/Id_vs_Vg': 'HA2/IDVG', 'Id_vs_Vg_H2': 'HA2/IDVG',
        'Q3/tests/data/Id_vs_Vg': 'HA3/IDVG', 'Id_vs_Vg_H4': 'HA3/IDVG',
        'Q6/tests/data/Id_vs_Vg': 'HB1/IDVG', 'Id_vs_Vg_H1': 'HB1/IDVG',
        'Q5/tests/data/Id_vs_Vg': 'HB2/IDVG', 'Id_vs_Vg_H3': 'HB2/IDVG',
        'Q4/tests/data/Id_vs_Vg': 'HB3/IDVG', 'Id_vs_Vg_H5': 'HB3/IDVG',

        # Detector tests
        'DET1/tests/data/If_vs_Vf': 'Q1/IFVF', 'If_vs_Vf_Det1': 'Q1/IFVF',
        'DET4/tests/data/If_vs_Vf': 'Q2/IFVF', 'If_vs_Vf_Det4': 'Q2/IFVF',
        'DET2/tests/data/If_vs_Vf': 'U1/IFVF', 'If_vs_Vf_Det2': 'U1/IFVF',
        'DET3/tests/data/If_vs_Vf': 'U2/IFVF', 'If_vs_Vf_Det3': 'U2/IFVF',

        # PHSW tests (forward)
        'V1_PS1/tests/data/If_vs_Vf': 'PSA1/IFVF', 'If_vs_Vfd_V1_PS1': 'PSA1/IFVF',
        'V2_PS1/tests/data/If_vs_Vf': 'PSA2/IFVF', 'If_vs_Vfd_V2_PS1': 'PSA2/IFVF',
        'V1_PS2/tests/data/If_vs_Vf': 'PSB1/IFVF', 'If_vs_Vfd_V1_PS2': 'PSB1/IFVF',
        'V2_PS2/tests/data/If_vs_Vf': 'PSB2/IFVF', 'If_vs_Vfd_V2_PS2': 'PSB2/IFVF',

        # PHSW tests (reverse)
        'V1_PS1/tests/data/Ir_vs_Vr': 'PSA1/IRVR', 'Ir_vs_Vr_V1_PS1': 'PSA1/IRVR',
        'V2_PS1/tests/data/Ir_vs_Vr': 'PSA2/IRVR', 'Ir_vs_Vr_V2_PS1': 'PSA2/IRVR',
        'V1_PS2/tests/data/Ir_vs_Vr': 'PSB1/IRVR', 'Ir_vs_Vr_V1_PS2': 'PSB1/IRVR',
        'V2_PS2/tests/data/Ir_vs_Vr': 'PSB2/IRVR', 'Ir_vs_Vr_V2_PS2': 'PSB2/IRVR',
    }

    with h5py.File(output_file, 'w') as h5_file:
        with ZipFile(input_file) as zip_file:
            for info in zip_file.infolist():
                if not info.filename.endswith('.xls'):
                    # Skip non-Excel files
                    continue

                # Files in tests/data do not contain valid information
                if 'tests' in info.filename and 'data' in info.filename:
                    continue

                dataset_name = None
                for pattern, hduname in dataset_names.items():
                    if pattern in info.filename:
                        dataset_name = hduname
                        break

                if not dataset_name:
                    continue

                with zip_file.open(info) as xls_file:
                    convert_excel_file_to_h5(xls_file, h5_file, dataset_name)


def convert_data_file_to_h5(data_file_name, data_file, output_file):
    '''Convert a data file into a HDF5 file

    The parameter "data_file_name" is used only to infer the type of the file
    from its extension: it does not need to match a real file.
    '''
    basename = os.path.basename(data_file_name)
    _, file_ext = os.path.splitext(basename)

    with BytesIO(data_file.read()) as input_file:
        file_ext = file_ext.lower()
        if file_ext == '.txt':
            convert_text_file_to_h5(input_file, output_file)
        elif file_ext == '.zip':
            convert_zip_file_to_h5(input_file, output_file)
        elif file_ext in ['.h5', '.hdf5']:
            # No conversion is needed
            copyfileobj(data_file, output_file)
        else:
            raise ValueError('extension "{0}" not recognized'.format(file_ext))

    return output_file
