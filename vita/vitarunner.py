#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 18:28:22 2019

@author: Daniel.Ibanez
"""

import os

def is_valid_file(parser, arg):
    '''
    Function for checking it a file exists

    Input:  parser, an argparse.ArgumentParser object for parsing the terminal input
            arg,    a terminal input with the file to load

    return: open(arg, 'r'), an open file handle if file exists, else -1
    '''
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
        return -1

    return open(arg, 'r')

if __name__ == "__main__":
    import json
    import argparse
    from vita.controller.midplane_power import run_midplane_power

    PARSER = argparse.ArgumentParser(description='Run VITA controller processes in batch mode.\
                                         Input is read from a JSON file (required).')
    PARSER.add_argument("file",
                        help="input file with JSON data for running simulations",
                        metavar="InputFile",
                        type=lambda x: is_valid_file(PARSER, x))

    ARGS = PARSER.parse_args()

    print(ARGS.file.name)

    with open(ARGS.file.name, 'r') as fh:
        VITA_INPUT = json.load(fh)

    print()
    print(VITA_INPUT['run_id'])
    print(VITA_INPUT['run_date'])
    print(VITA_INPUT['user'])
    print()
    print('Plasma Settings:')
    print('- Isotopes -> {}'.format(VITA_INPUT['plasma-settings']['isotopes']))
    print('- NBI Power -> {}'.format(VITA_INPUT['plasma-settings']['heating']['NBI-power']))
    print('- Ohmic-power -> {}'.format(VITA_INPUT['plasma-settings']['heating']['Ohmic-power']))
    print('- rf-power -> {}'.format(VITA_INPUT['plasma-settings']['heating']['rf-power']))
    print(VITA_INPUT['analysis'])
    print()

    if VITA_INPUT['analysis'][0]['mode'] == "midplane_power":
        run_midplane_power(VITA_INPUT['analysis'][0]['type'], VITA_INPUT['plasma-settings'])
