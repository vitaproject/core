#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 10:21:15 2020

@author: jmbols
"""

import numpy as np
import matplotlib.pyplot as plt
from vita.utility import get_resource
from vita.modules.projection2D.field_line_projection import project_heat_flux
from vita.modules.fiesta.field_line import FieldLine
from vita.modules.fiesta.fiesta_interface import Fiesta
from vita.modules.sol_heat_flux.eich import Eich
from cherab.core.math import Interpolate2DCubic


if __name__ == '__main__':
    #HESEL_FILE_PATH = '/media/jmbols/Data/jmbols/ST40/Programme 3/Te(i)_grad_scan/ST40.00003.20.h5'
    #HESELDATA = HESELdata(HESEL_FILE_PATH)
    #HESELDATA.evaluate_parallel_heat_fluxes()

    FILEPATH = get_resource("ST40", "equilibrium", "eq002")

    FIESTA = Fiesta(FILEPATH)
    B_POL = np.sqrt(FIESTA.b_r**2 + FIESTA.b_theta**2 + FIESTA.b_z**2).T
    B_POL_INTERP = Interpolate2DCubic(FIESTA.r_vec, FIESTA.z_vec, B_POL)

    FIELD_LINE = FieldLine(FILEPATH)
    MID_PLANE_LOC = FIELD_LINE.fiesta_equil.get_midplane_lcfs()[1]

    #I_AFTER_LCFS = np.linspace(-1, 10, 100)*1e-3
    #I_AFTER_LCFS = np.where(HESELDATA.hesel_params.xaxis >= 0)[0]
    # specify and load heatflux profile
    FOOTPRINT = Eich(0.0025, 0.0005, r0_lfs=MID_PLANE_LOC)  # lambda_q=2.5, S=0.5

    X_OMP = np.linspace(0, 10, 100)*1e-3
    FOOTPRINT.set_coordinates(X_OMP)
    FOOTPRINT.s_disconnected_dn_max = 2.1
    FOOTPRINT.fx_in_out = 5.
    FOOTPRINT.calculate_heat_flux_density("lfs")

    Q_PARALLEL = FOOTPRINT._q
    X_AFTER_LCFS = FOOTPRINT.get_global_coordinates()
    EQUILIBRIUM = {}
    plt.figure()
    for i in X_AFTER_LCFS:
        P_0 = [i, 0, 0]
        FIELD_LINE_DICT = FIELD_LINE.follow_field_in_plane(p_0=P_0, max_length=15.0)
        plt.plot(FIELD_LINE_DICT['R'], FIELD_LINE_DICT['Z'])
        EQUILIBRIUM[i] = FIELD_LINE_DICT
    # X_AFTER_LCFS = HESELDATA.hesel_params.xaxis[I_AFTER_LCFS] + MID_PLANE_LOC
    DIVERTOR_COORDS = np.array((np.array([0.375, 0.675]), np.array([-0.78, -0.885])))
    # EQUILIBRIUM = 'eq_0002'
    HEAT_FLUX_AT_OMP = np.array((X_AFTER_LCFS, Q_PARALLEL))
    COORDS = project_heat_flux(HEAT_FLUX_AT_OMP, DIVERTOR_COORDS, EQUILIBRIUM, B_POL_INTERP)
    FIG = plt.figure()
    plt.plot(COORDS[0], COORDS[2])
