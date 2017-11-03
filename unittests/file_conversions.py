# -*- encoding: utf-8 -*-

from io import BytesIO
import os.path
import re
from zipfile import ZipFile
from typing import Any, Dict

from astropy.io import fits
import numpy as np
import xlrd

SAMPLING_FREQUENCY = 25.0


def convert_text_file_to_fits(input_file, output_file):
    '''Convert a text file into a FITS file

    The parameter "input_file" should be a file-like object. The FITS file will
    be saved into "output_file" (which can either be a file name or a file-like
    object).
    '''

    data = np.loadtxt(input_file, skiprows=1)
    if data.shape[1] != 13:
        raise ValueError('the input file has {0} columns instead of 13'
                         .format(data.shape[1]))

    table_hdu = fits.BinTableHDU.from_columns([
        fits.Column(name='TIME', format='E', unit='s',
                    array=np.arange(data.shape[0]) / SAMPLING_FREQUENCY),
        fits.Column(name='PCTIME', format='E', unit='', array=data[:, 0]),
        fits.Column(name='PHB', format='B', unit='', array=data[:, 1]),
        fits.Column(name='RECORD', format='B', unit='', array=data[:, 2]),
        fits.Column(name='DEM0', format='E', unit='ADU', array=data[:, 3]),
        fits.Column(name='DEM1', format='E', unit='ADU', array=data[:, 4]),
        fits.Column(name='DEM2', format='E', unit='ADU', array=data[:, 5]),
        fits.Column(name='DEM3', format='E', unit='ADU', array=data[:, 6]),
        fits.Column(name='PWR0', format='E', unit='ADU', array=data[:, 7]),
        fits.Column(name='PWR1', format='E', unit='ADU', array=data[:, 8]),
        fits.Column(name='PWR2', format='E', unit='ADU', array=data[:, 9]),
        fits.Column(name='PWR3', format='E', unit='ADU', array=data[:, 10]),
        fits.Column(name='RFPOWER', format='E', unit='dB', array=data[:, 11]),
        fits.Column(name='FREQ', format='E', unit='GHz', array=data[:, 12]),
    ])

    hdulist = fits.HDUList([fits.PrimaryHDU(), table_hdu])
    hdulist.writeto(output_file, checksum=True)


def read_worksheet_table(wks: xlrd.book.Book) -> Dict[str, Any]:
    '''Read a table of numbers from an Excel file saved by Keithley.

    This function reads the first worksheet in the Excel file passed as
    argument and returns a dictionary associating NumPy arrays with their
    names.
    '''

    sheet = wks.sheet_by_index(0)
    result = {}
    nrows = sheet.nrows
    for cur_col in range(sheet.ncols):
        name = sheet.cell(0, cur_col).value
        if len(name) >= len('START') and name[:5] == 'START':
            # This column and the following are not useful
            break
        result[name] = np.array([sheet.cell(i, cur_col).value
                                 for i in range(1, nrows)])

    return result


def read_worksheet_settings(wks: xlrd.book.Book) -> Dict[str, Any]:
    sheet = wks.sheet_by_name('Settings')
    result = {}
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


def hygenize_name(name: str) -> str:
    'Return a name which is suitable for FITS column/keyword names'

    # Remove unwanted character and clip to the first 8 characters
    return ''.join([ch for ch in name.upper() if not ch in (' ', '+', '-', '(', ')')])[:8]


def unit_from_name(name: str) -> str:
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


def convert_excel_file_to_fits_hdu(input_file) -> fits.BinTableHDU:
    'Convert an Excel file into a FITS HDU'
    with xlrd.open_workbook(file_contents=input_file.read()) as workbook:
        settings = read_worksheet_settings(workbook)
        datatable = read_worksheet_table(workbook)

    column_list = []
    for cur_key in sorted(datatable.keys()):
        cur_values = datatable[cur_key]
        column_list.append(fits.Column(name=hygenize_name(cur_key),
                                       format='E',
                                       unit=unit_from_name(cur_key),
                                       array=cur_values))

    data_hdu = fits.BinTableHDU.from_columns(column_list)
    for key, value in settings.items():
        if type(value) is str:
            data_hdu.header[hygenize_name(key)] = value

    return data_hdu


def convert_zip_file_to_fits(input_file, output_file):
    '''Convert the Excel files in a ZIP file into one single FITS

    The Excel files must have been saved using the Keithley machine, either the
    old or the new one. All the files are saved in separate HDU in the FITS
    files.

    The parameter "input_file" must be a file-like object, which will be treated
    as a ZIP archive. The FITS file will be named after "output_file".
    '''

    # To check the correspondences between the (two!) notations used in
    # Bicocca and the proper STRIP naming conventions, refer to the note
    # LSPE-STRIP-SP-004 («LSPE-STRIP naming convention»)
    hdu_names = {
        # HEMT tests (Idrain vs Vdrain)
        'Q1/tests/data/Id_vs_Vd': 'HA1IDVD', 'Id_vs_Vd_H0': 'HA1IDVD',
        'Q2/tests/data/Id_vs_Vd': 'HA2IDVD', 'Id_vs_Vd_H2': 'HA2IDVD',
        'Q3/tests/data/Id_vs_Vd': 'HA3IDVD', 'Id_vs_Vd_H4': 'HA3IDVD',
        'Q6/tests/data/Id_vs_Vd': 'HB1IDVD', 'Id_vs_Vd_H1': 'HB1IDVD',
        'Q5/tests/data/Id_vs_Vd': 'HB2IDVD', 'Id_vs_Vd_H3': 'HB2IDVD',
        'Q4/tests/data/Id_vs_Vd': 'HB3IDVD', 'Id_vs_Vd_H5': 'HB3IDVD',

        # HEMT tests (Idrain vs Vgate)
        'Q1/tests/data/Id_vs_Vg': 'HA1IDVG', 'Id_vs_Vg_H0': 'HA1IDVG',
        'Q2/tests/data/Id_vs_Vg': 'HA2IDVG', 'Id_vs_Vg_H2': 'HA2IDVG',
        'Q3/tests/data/Id_vs_Vg': 'HA3IDVG', 'Id_vs_Vg_H4': 'HA3IDVG',
        'Q6/tests/data/Id_vs_Vg': 'HB1IDVG', 'Id_vs_Vg_H1': 'HB1IDVG',
        'Q5/tests/data/Id_vs_Vg': 'HB2IDVG', 'Id_vs_Vg_H3': 'HB2IDVG',
        'Q4/tests/data/Id_vs_Vg': 'HB3IDVG', 'Id_vs_Vg_H5': 'HB3IDVG',

        # Detector tests
        'DET1/tests/data/If_vs_Vf': 'Q1IFVF', 'If_vs_Vf_Det1': 'Q1IFVF',
        'DET4/tests/data/If_vs_Vf': 'Q2IFVF', 'If_vs_Vf_Det4': 'Q2IFVF',
        'DET2/tests/data/If_vs_Vf': 'U1IFVF', 'If_vs_Vf_Det2': 'U1IFVF',
        'DET3/tests/data/If_vs_Vf': 'U2IFVF', 'If_vs_Vf_Det3': 'U2IFVF',

        # PHSW tests
        'V1_PS1/tests/data/If_vs_Vf': 'PSA1IFVF', 'If_vs_Vfd_V1_PS1': 'PSA1IFVF',
        'V2_PS1/tests/data/If_vs_Vf': 'PSA2IFVF', 'If_vs_Vfd_V2_PS1': 'PSA2IFVF',
        'V1_PS2/tests/data/If_vs_Vf': 'PSB1IFVF', 'If_vs_Vfd_V1_PS2': 'PSB1IFVF',
        'V2_PS2/tests/data/If_vs_Vf': 'PSB2IFVF', 'If_vs_Vfd_V2_PS2': 'PSB2IFVF',
    }

    with ZipFile(input_file) as zip_file:
        hdu_list = []
        for info in zip_file.infolist():
            if not info.filename.endswith('.xls'):
                # Skip non-Excel files
                continue

            current_hduname = None
            for pattern, hduname in hdu_names.items():
                if pattern in info.filename:
                    current_hduname = hduname
                    break

            if not current_hduname:
                continue

            with zip_file.open(info) as xls_file:
                cur_hdu = convert_excel_file_to_fits_hdu(xls_file)
                cur_hdu.header['EXTNAME'] = current_hduname
                hdu_list.append(cur_hdu)

    # Order the HDUs depending on their name
    hdu_list.sort(key=lambda x: x.header['EXTNAME'])

    fits.HDUList([fits.PrimaryHDU()] +
                 hdu_list).writeto(output_file, checksum=True)


def convert_data_file_to_fits(data_file_name, data_file, output_file):
    '''Convert a data file into a FITS file

    Return the name of the FITS file which has just been created. The parameter
    "data_file_name" is used only to infer the type of the file from its extension.
    '''
    basename = os.path.basename(data_file_name)
    _, file_ext = os.path.splitext(basename)

    with BytesIO(data_file.read()) as input_file:
        file_ext = file_ext.lower()
        if file_ext == '.txt':
            convert_text_file_to_fits(input_file, output_file)
        elif file_ext == '.zip':
            convert_zip_file_to_fits(input_file, output_file)
        else:
            raise ValueError('extension "{0}" not recognized'.format(file_ext))

    return output_file
