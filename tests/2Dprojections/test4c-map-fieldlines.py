#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 10:42:34 2020

@author: jmbols
"""
import numpy as np
import matplotlib.pyplot as plt
from vita.utility import get_resource
from vita.modules.equilibrium.fiesta import Fiesta
from vita.modules.projection.projection2D.field_line.field_line import FieldLine
from vita.modules.projection.projection2D.field_line.map_field_lines import map_field_lines

if __name__ == "__main__":
    #FILEPATH = '/home/jmbols/Postdoc/ST40/Programme 1/Equilibrium/eq001_limited.mat'
    #FILEPATH = '/media/jmbols/Data/jmbols/ST40/Programme 3/Equilibrium/eq_0002.mat'
    FILEPATH = get_resource("ST40-IVC1", "equilibrium", "eq_006_2T_export")
   #HESEL_FILE_PATH = '/media/jmbols/Data/jmbols/ST40/Programme 1/n_inner_bnd_scan/ST40.00001.03.h5'
    #HESEL_FILE_PATH = '/media/jmbols/Data/jmbols/ST40/Programme 3/Te(i)_grad_scan/ST40.00003.20.h5'

    #FILE = h5py.File(HESEL_FILE_PATH, 'r')
    #HESEL_PARAMS = HESELparams(FILE)
    #FILE.close()
    FIESTA = Fiesta(FILEPATH)

    FIELD_LINE = FieldLine(FIESTA)
    MID_PLANE_LOC = FIESTA.get_midplane_lcfs()[1]

    X_AFTER_LCFS = np.linspace(0, 10, 100)*1e-3 + MID_PLANE_LOC

#    I_AFTER_LCFS = np.where(HESEL_PARAMS.xaxis >= 0)[0]
#    X_AFTER_LCFS = HESEL_PARAMS.xaxis[I_AFTER_LCFS] + MID_PLANE_LOC

    FIELD_LINES = map_field_lines(X_AFTER_LCFS, FIESTA)
#    save_as_pickle(FIELD_LINES, 'eq_0002')

    plt.plot(FIELD_LINE.fiesta_equil.r_limiter, FIELD_LINE.fiesta_equil.z_limiter)
    for I in X_AFTER_LCFS:
        plt.plot(FIELD_LINES[I]['R'], FIELD_LINES[I]['Z'])
        plt.plot(FIELD_LINES[I]['Vessel_Intersect'][0], FIELD_LINES[I]['Vessel_Intersect'][1], '*')