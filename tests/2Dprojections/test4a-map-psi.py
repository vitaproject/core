#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 16:37:33 2020

@author: jmbols
"""
import numpy as np
import matplotlib.pyplot as plt
from vita.modules.fiesta.fiesta_interface import Fiesta
from vita.modules.sol_heat_flux.hesel_data import HESELdata
from vita.modules.projection2D.map_psi import map_psi_omp_to_divertor
from vita.utility import get_resource

def load_x_axis(file_name):
    '''
    Function for loading HESEL data
    '''
    hesel_data = HESELdata(file_name)
    hesel_data._load_file()

    i_after_lcfs = np.where(hesel_data.hesel_params.xaxis >= 0)[0]

    x_after_lcfs = hesel_data.hesel_params.xaxis[i_after_lcfs]

    return x_after_lcfs

def load_fiesta_equilibrium(file_name):
    '''
    Load Fiesta eqiulibrium
    '''
    fiesta = Fiesta(file_name)

    return fiesta

if __name__ == '__main__':
    filename_hesel = '/media/jmbols/Data/jmbols/ST40/Programme 3/Te(i)_grad_scan/ST40.00003.20.h5'
    eq002 = get_resource("ST40", "equilibrium", "eq002")

    x_axis = load_x_axis(filename_hesel)[:800]
    fiesta = load_fiesta_equilibrium(eq002)
    x_axis += fiesta.get_midplane_lcfs()[1]

    divertor_coords_x = np.array([0.375, 0.675])
    divertor_coords_y = np.array([-0.78, -0.885])
    divertor_coords = np.array([divertor_coords_x, divertor_coords_y])
    divertor_map = map_psi_omp_to_divertor(x_axis, fiesta, divertor_coords)
    r_div = divertor_map["R_div"]
    angles = divertor_map["Angles"]
    plt.plot(r_div, angles)