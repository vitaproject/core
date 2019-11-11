#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 11:55:48 2019

@author: jmbols
"""
import pickle
import h5py
import numpy as np
import matplotlib.pyplot as plt
from vita.modules.fiesta.field_line import FieldLine
from vita.modules.utils import intersection
from vita.modules.sol_heat_flux.hesel_parameters import HESELparams

def map_field_lines(x_vec_at_omp, file_path, configuration='diverted'):
    '''
    Function for mapping each field-line to the intersection with the vessel walls

    Input: x_vec_at_omp,  a numpy array with the radial points at the OMP where
                          we want the mapping to start
           file_path,     a string with the path to the FIESTA equilibrium .mat file
           configuration, a string with either 'limited' or 'diverted', where 'diverted'
                          is the defualt configuration

    return: field_line_dict, a python dictionary with the radial position from the OMP in m
                             as the key and the field-line dictionary with the R, phi
                             and Z components along the field line as well as the length, l,
                             from the LCFS to the current point along the field-line
    '''
    field_line = FieldLine(file_path)
    field_line_dict = {}
    for i in x_vec_at_omp:
        p_0 = [i, 0, 0]
        field_lines = field_line.follow_field_in_plane(p_0=p_0, max_length=10.0)

        func1 = np.array([field_lines["R"], field_lines["Z"]])
        func2 = np.array([field_line.fiesta_equil.r_limiter, field_line.fiesta_equil.z_limiter])

        (i_intersect_func1, _),\
        (r_intersect, z_intersect) = intersection(func1, func2)

        if not np.any(np.isnan(r_intersect)):
            i_first_intersect = np.argmin(field_lines["l"][i_intersect_func1])
            i_intersection = i_intersect_func1[i_first_intersect]
            if configuration == 'limited':
                i_min_intersect = np.argmin(field_lines["R"][i_intersection] - r_intersect)
                i_intersection = np.where(field_lines["R"][:] < r_intersect[i_min_intersect])[0][0]
            elif configuration == 'diverted':
                i_min_intersect = np.argmin(field_lines["Z"][i_intersection] - z_intersect)
                i_intersection = np.where(field_lines["Z"][:] < z_intersect[i_min_intersect])[0][0]
            else:
                print("Error: unknown configuration. Please use either 'limited' or 'diverted'")
                break

            field_lines["l"] = field_lines["l"][:i_intersection + 1]
            field_lines["R"] = field_lines["R"][:i_intersection + 1]
            field_lines["Z"] = field_lines["Z"][:i_intersection + 1]

            field_lines["Vessel_Intersect"] = (r_intersect[i_min_intersect],
                                               z_intersect[i_min_intersect])

            field_line_dict[i] = field_lines
        else:
            field_lines["Vessel_Intersect"] = (np.nan, np.nan)
            field_line_dict[i] = field_lines

    return field_line_dict

def save_as_pickle(input_dictionary, save_name):
    '''
    Function for saving a dictionary as a .pickle file

    Input:  input_dictionary, a dictionary to be save to the .pickle file
            save_name,        a string with the name of the .pickle file to save

    Output: save_name.pickle, a .pickle file with the name specified
    '''
    pickle_save_name = save_name + '.pickle'
    with open(pickle_save_name, 'wb') as handle:
        pickle.dump(input_dictionary, handle, protocol=pickle.HIGHEST_PROTOCOL)
    handle.close()

if __name__ == "__main__":
    #FILEPATH = '/home/jmbols/Postdoc/ST40/Programme 1/Equilibrium/eq001_limited.mat'
    FILEPATH = '/media/jmbols/Data/jmbols/ST40/Programme 3/Equilibrium/eq_0002.mat'

   #HESEL_FILE_PATH = '/media/jmbols/Data/jmbols/ST40/Programme 1/n_inner_bnd_scan/ST40.00001.03.h5'
    HESEL_FILE_PATH = '/media/jmbols/Data/jmbols/ST40/Programme 3/Te(i)_grad_scan/ST40.00003.20.h5'

    FILE = h5py.File(HESEL_FILE_PATH, 'r')
    HESEL_PARAMS = HESELparams(FILE)
    FILE.close()

    FIELD_LINE = FieldLine(FILEPATH)
    MID_PLANE_LOC = FIELD_LINE.fiesta_equil.get_midplane_lcfs()[1]

    I_AFTER_LCFS = np.where(HESEL_PARAMS.xaxis >= 0)[0]
    X_AFTER_LCFS = HESEL_PARAMS.xaxis[I_AFTER_LCFS] + MID_PLANE_LOC

    FIELD_LINES = map_field_lines(X_AFTER_LCFS, FILEPATH)
    save_as_pickle(FIELD_LINES, 'eq_0002')

    plt.plot(FIELD_LINE.fiesta_equil.r_limiter, FIELD_LINE.fiesta_equil.z_limiter)
    for I in X_AFTER_LCFS:
        plt.plot(FIELD_LINES[I]['R'], FIELD_LINES[I]['Z'])
        plt.plot(FIELD_LINES[I]['Vessel_Intersect'][0], FIELD_LINES[I]['Vessel_Intersect'][1], '*')
