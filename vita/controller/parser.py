#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 12:28:22 2019

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
