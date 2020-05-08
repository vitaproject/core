#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 16:24:11 2019

@author: jmbols
"""
import json
import numpy as np
import matplotlib.pyplot as plt
from vita.controller.midplane_power import run_midplane_power
from vita.modules.equilibrium.fiesta.fiesta_interface import Fiesta
from vita.modules.equilibrium.fiesta.map_psi import map_psi

def run_midplane_to_div_power(midplane_model, plasma, equilibrium, divertor_coord):
    '''
    .
    '''
    fiesta = Fiesta(equilibrium)
    mid_plane_power = run_midplane_power(midplane_model, plasma)
    pos_from_strikepoint = mid_plane_power.get_local_coordinates() + fiesta.get_midplane_lcfs()[1]
    
    psi_map = map_psi(fiesta, divertor_coord)
    
    interp_heatload = np.interp(psi_map['R_omp'],\
                                pos_from_strikepoint,\
                                mid_plane_power._HeatLoad__q)

    print(np.sin(psi_map['theta_inc']))
    div_heatload = psi_map['R_omp']/psi_map['R_div']*interp_heatload/(psi_map['f_x']/np.sin(psi_map['theta_inc'][0]))
    plt.plot(psi_map['R_div'], div_heatload)


if __name__ == '__main__':
    EQUIL = '/media/jmbols/Data/jmbols/ST40/Programme 3/Equilibrium/eq_0002.mat'
    DIVERTOR_POS = np.array((np.array([0.375, 0.675]), np.array([-0.68, -0.885])))
    MIDPLANE_MODEL = 'Eich'
    FILE_NAME = '/home/jmbols/Postdoc/Daniel_github/vitaproject/core/tests/json_input/vita_input.json'
    with open(FILE_NAME, 'r') as FILE_HANDLE:
        PLASMA = json.load(FILE_HANDLE)
    PLASMA = PLASMA['plasma-settings']

    plt.close()
    run_midplane_to_div_power(MIDPLANE_MODEL, PLASMA, EQUIL, DIVERTOR_POS)
    