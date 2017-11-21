#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from argparse import ArgumentParser
from unittests.file_conversions import convert_data_file_to_h5
import sys


def main(argv):
    parser = ArgumentParser(description='Convert data files acquired in Bicocca intoto HDF5 files',
                            epilog='Report bugs through the page https://github.com/lspestrip/stdb2/issues')
    parser.add_argument('input_file_path',
                        help='Name of the data file to read')
    parser.add_argument('output_file_path',
                        help='Name of the HDF5 file to create')
    arguments = parser.parse_args(argv[1:])

    with open(arguments.input_file_path, 'rb') as input_file:
        convert_data_file_to_h5(
            arguments.input_file_path, input_file, arguments.output_file_path)

    print('file "{inp}" converted into "{outp}"'
          .format(inp=arguments.input_file_path,
                  outp=arguments.output_file_path))


if __name__ == '__main__':
    main(sys.argv)
