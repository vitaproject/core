#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 15:37:52 2019

@author: jmbols
"""
import pickle
import pathlib
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from vita.utility import get_resource
from vita.modules.utils import intersection
from vita.modules.fiesta.field_line import FieldLine
from vita.modules.fiesta.map_field_lines import map_field_lines
from vita.modules.sol_heat_flux.hesel_data import HESELdata

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

def project_heat_flux(heat_flux_profile_omp, surface_position, equilibrium):
    '''
    Function for projecting a heat flux from the OMP to a given surface (without taking diffusion
    into account)

    Input:  heat_flux_profile_omp, a 2-by-n numpy array, where heat_flux_profile_omp[0] is the radial
                                   coordinates of each point at the OMP and heat_flux_profile_omp[1]
                                   is the parallel heat flux at the corresponding radial points
            surface_position,      a 2-by-m numpy array with the surface_position[0] being the radial
                                   coordinates and surface_position[1] being the poloidal positions
            equilibrium,           a string with the equilibrium to load, e.g. eq_0002

    Return: heat_flux_at_intersection, a 3-by-n numpy array, where heat_flux_at_intersection[0]
                                       is the radial coordinates of each point at the target,
                                       heat_flux_at_intersection[1] is the vertical coordinates
                                       of each point at the target, and heat_flux_profile_omp[2]
                                       is the parallel heat flux at the corresponding positions
    '''
    x_after_lcfs = heat_flux_profile_omp[0]
    equlibrium_file = '../fiesta/' + equilibrium

    if pathlib.Path(equlibrium_file + '.pickle').exists():
        field_lines = load_pickle(equlibrium_file)
    else:
        field_lines = map_field_lines(x_after_lcfs, equlibrium_file)

    intersection_x = []
    intersection_y = []
    for i in field_lines:
        func1 = np.array((field_lines[i]['R'], field_lines[i]['Z']))
        (_, _), (x_at_surface, y_at_surface) = intersection(func1,
                                                            (surface_position))
        if np.isnan(x_at_surface):
            break
        intersection_x.append(x_at_surface[0])
        intersection_y.append(y_at_surface[0])

    intersection_x = np.array(intersection_x)
    intersection_y = np.array(intersection_y)

    not_in_div = len(intersection_x)
    x_after_lcfs = x_after_lcfs[:not_in_div]
    f_x = np.zeros(not_in_div)
    dist_div = np.sqrt(np.square(intersection_x[1:]-intersection_x[:-1])
                       + np.square(intersection_y[1:]-intersection_y[:-1]))
    f_x[0:-1] = (dist_div)/(x_after_lcfs[1:]-x_after_lcfs[:-1])
    f_x[-1] = f_x[-2]
    f_x = savgol_filter(f_x, 51, 3)
    q_div = x_after_lcfs/intersection_x * \
          heat_flux_profile_omp[1, :not_in_div]/f_x

    heat_flux_at_intersection = np.array([intersection_x, intersection_y, q_div])

    return heat_flux_at_intersection

if __name__ == '__main__':
    HESEL_FILE_PATH = '/media/jmbols/Data/jmbols/ST40/Programme 3/Te(i)_grad_scan/ST40.00003.20.h5'
    HESELDATA = HESELdata(HESEL_FILE_PATH)
    HESELDATA.evaluate_parallel_heat_fluxes()

    FILEPATH = get_resource("ST40", "equilibrium", "eq002")

    FIELD_LINE = FieldLine(FILEPATH)
    MID_PLANE_LOC = FIELD_LINE.fiesta_equil.get_midplane_lcfs()[1]

    I_AFTER_LCFS = np.where(HESELDATA.hesel_params.xaxis >= 0)[0]
    X_AFTER_LCFS = HESELDATA.hesel_params.xaxis[I_AFTER_LCFS] + MID_PLANE_LOC
    DIVERTOR_COORDS = np.array((np.array([0.375, 0.675]), np.array([-0.78, -0.885])))
    EQUILIBRIUM = 'eq_0002'
    HEAT_FLUX_AT_OMP = np.array((X_AFTER_LCFS, HESELDATA.q_parallel_tot[I_AFTER_LCFS]))
    COORDS = project_heat_flux(HEAT_FLUX_AT_OMP, DIVERTOR_COORDS, EQUILIBRIUM)
    FIG = plt.figure()
    plt.plot(COORDS[0], COORDS[2])
