#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 18:28:22 2019

@author: Daniel.Ibanez
"""

import os

def is_valid_file(parser, arg):
  if not os.path.exists(arg):
    parser.error("The file %s does not exist!" % arg)
  else:
    return open(arg, 'r')  # return an open file handle


if __name__ == "__main__":
  import json
  import argparse
  from vita.controller.midplane_power import *

  parser = argparse.ArgumentParser(description='Run VITA controller processes in batch mode.\
                                   Input is read from a JSON file (required).')
  parser.add_argument("file",
                      help="input file with JSON data for running simulations", 
                      metavar="InputFile",
                      type=lambda x: is_valid_file(parser, x))
  args = parser.parse_args()

  print(args.file.name)

  with open(args.file.name, 'r') as fh:
      vita_input = json.load(fh)

  print()
  print(vita_input['run_id'])
  print(vita_input['run_date'])
  print(vita_input['user'])
  print()
  print('Plasma Settings:')
  print('- Isotopes -> {}'.format(vita_input['plasma-settings']['isotopes']))
  print('- NBI Power -> {}'.format(vita_input['plasma-settings']['heating']['NBI-power']))
  print('- Ohmic-power -> {}'.format(vita_input['plasma-settings']['heating']['Ohmic-power']))
  print('- rf-power -> {}'.format(vita_input['plasma-settings']['heating']['rf-power']))
  print(vita_input['analysis'])
  print()

  if vita_input['analysis'][0]['mode'] == "midplane_power":
    run_midplane_power(vita_input['analysis'][0]['type'], vita_input['plasma-settings'])

