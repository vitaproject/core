#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 10:34:50 2020

@author: jmbols
"""
import numpy as np
import matplotlib.pyplot as plt
from vita.utility import get_resource
from vita.modules.projection.projection2D.field_line.field_line import FieldLine
from vita.modules.projection.projection2D.field_line.field_line_projection import project_field_lines
from vita.modules.equilibrium.fiesta.fiesta_interface import Fiesta
from vita.modules.sol_heat_flux.eich.eich import Eich
from cherab.core.math import Interpolate2DCubic
from vita.modules.projection.projection2D.psi_map_projection import map_psi_omp_to_divertor
from vita.modules.projection.projection2D.project_heat_flux import project_heat_flux

if __name__ == "__main__":
    FILEPATH = get_resource("ST40", "equilibrium", "eq002")

    FIESTA = Fiesta(FILEPATH)
    B_POL = FIESTA.b_theta.T
    B_POL_INTERP = Interpolate2DCubic(FIESTA.r_vec, FIESTA.z_vec, B_POL)

    FIELD_LINE = FieldLine(FILEPATH)
    MID_PLANE_LOC = FIESTA.get_midplane_lcfs()[1]

    FOOTPRINT = Eich(0.0025, 0.0005, r0_lfs=MID_PLANE_LOC+0.001)  # lambda_q=2.5, S=0.5

    X_OMP = np.linspace(0, 10, 100)*1e-3
    FOOTPRINT.set_coordinates(X_OMP)
    FOOTPRINT.s_disconnected_dn_max = 2.1
    FOOTPRINT.fx_in_out = 5.
    FOOTPRINT.calculate_heat_flux_density("lfs")

    Q_PARALLEL = FOOTPRINT._q
    X_AFTER_LCFS = FOOTPRINT.get_global_coordinates()

    DIVERTOR_COORDS = np.array((np.array([0.375, 0.675]), np.array([-0.78, -0.885])))

    HEAT_FLUX_AT_OMP = np.array(Q_PARALLEL)
    MAP_DICT_PSI = map_psi_omp_to_divertor(X_AFTER_LCFS, DIVERTOR_COORDS, FIESTA)
    MAP_DICT = project_field_lines(X_AFTER_LCFS, DIVERTOR_COORDS, FIESTA)
    Q_DIV_PSI = project_heat_flux(X_AFTER_LCFS, HEAT_FLUX_AT_OMP, MAP_DICT_PSI)
    Q_DIV = project_heat_flux(X_AFTER_LCFS, HEAT_FLUX_AT_OMP, MAP_DICT)
    X = [MAP_DICT[i]["R_pos"] for i in X_AFTER_LCFS]
    X_PSI = [MAP_DICT[i]["R_pos"] for i in X_AFTER_LCFS]
    plt.plot(X, Q_DIV)
    plt.plot(X_PSI, Q_DIV_PSI)