#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 10:21:47 2020

@author: jmbols
"""
import pickle

def load_pickle(file_name):
    '''
    Function for loading a .pickle file

    Input: file_name,    a string with the .pickle file to load, e.g. 'fiesta/eq_0002'

    Return: pickle_dict, the dictionary stored in the .pickle file
    '''
    pickle_filename = file_name + '.pickle'
    with open(pickle_filename, 'rb') as handle:
        pickle_dict = pickle.load(handle)
    handle.close()
    return pickle_dict