#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 16:37:33 2020

@author: jmbols
"""
import numpy as np
import matplotlib.pyplot as plt
from vita.modules.equilibrium.fiesta.fiesta_interface import Fiesta
from vita.modules.projection.projection2D.map_psi import map_psi_omp_to_divertor
from vita.utility import get_resource
from vita.modules.sol_heat_flux.eich.eich import Eich

if __name__ == '__main__':
    FILEPATH = get_resource("ST40", "equilibrium", "eq002")

    FIESTA = Fiesta(FILEPATH)

    MID_PLANE_LOC = FIESTA.get_midplane_lcfs()[1]
    # specify and load heatflux profile
    FOOTPRINT = Eich(0.0025, 0.0005, r0_lfs=MID_PLANE_LOC)  # lambda_q=2.5, S=0.5

    X_OMP = np.linspace(0, 10, 100)*1e-3
    FOOTPRINT.set_coordinates(X_OMP)
    FOOTPRINT.s_disconnected_dn_max = 2.1
    FOOTPRINT.fx_in_out = 5.
    FOOTPRINT.calculate_heat_flux_density("lfs")

    Q_PARALLEL = FOOTPRINT._q
    X_AFTER_LCFS = FOOTPRINT.get_global_coordinates()

    DIVERTOR_COORDS_X = np.array([0.375, 0.675])
    DIVERTOR_COORDS_Y = np.array([-0.78, -0.885])
    DIVERTOR_COORDS = np.array([DIVERTOR_COORDS_X, DIVERTOR_COORDS_Y])
    DIVERTOR_MAP = map_psi_omp_to_divertor(X_AFTER_LCFS, FIESTA, DIVERTOR_COORDS)
    R_DIV = DIVERTOR_MAP["R_div"]
    Z_DIV = DIVERTOR_MAP["Z_div"]
    ANGLES = DIVERTOR_MAP["Angles"]
    F_X = DIVERTOR_MAP["Flux_expansion"]
    plt.figure()
    plt.plot(R_DIV, ANGLES)

    plt.figure()
    plt.plot(R_DIV, F_X)

    plt.figure()
    plt.plot(R_DIV, Z_DIV)

    plt.figure()
    plt.plot(R_DIV, Q_PARALLEL*X_AFTER_LCFS/(R_DIV*F_X/np.sin(ANGLES)))
