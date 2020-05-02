#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 09:04:48 2020

@author: jmbols
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import m_p, m_n, e
from vita.utility import get_resource
from vita.modules.projection.projection2D.particle_path_projection import ParticlePath
from vita.modules.equilibrium.fiesta.fiesta_interface import Fiesta
from vita.modules.utils.getOption import getOption

if __name__ == '__main__':
    FILEPATH = get_resource("ST40-IVC1", "equilibrium", "eq_006_2T_export")
    FIESTA = Fiesta(FILEPATH)
#    DATA = sio.loadmat(FILEPATH)

    PARTICLE_MASS = m_n + m_p

    ZE_M = e / PARTICLE_MASS

    PATH_OBJ = ParticlePath(ZE_M, FIESTA, charge=e)

    # %%
    INITIAL_POS = np.array([0.728, 0, 0])

    B_HERE = np.array([float(PATH_OBJ.interp_b_r(INITIAL_POS[0], INITIAL_POS[2])),
                       float(PATH_OBJ.exact_b_phi(INITIAL_POS[0])),
                       float(PATH_OBJ.interp_b_z(INITIAL_POS[0], INITIAL_POS[2]))])

    B_MAG = np.sqrt(np.sum(B_HERE**2))

    B_DIR = B_HERE / B_MAG

    V_PARA_0 = 5e5

    MAG_MO_0 = 1e-15

    INITIAL_VEC = np.concatenate([INITIAL_POS, np.array([V_PARA_0, MAG_MO_0])])

    OUT = PATH_OBJ.follow_path(INITIAL_VEC)

# %%
    plt.figure()
    plt.plot(OUT['r_tot'], OUT['z_tot'])
    plt.plot(FIESTA.r_limiter.T, FIESTA.z_limiter.T)
    plt.plot(FIESTA.lcfs_polygon[0, :], FIESTA.lcfs_polygon[1, :])
    plt.xlabel('r')
    plt.ylabel('z')
    plt.show()

    plt.figure()
    plt.plot(OUT['time'], OUT['v_para'])
    plt.ylabel('vpara')
    plt.show()

    plt.figure()
    plt.plot(OUT['time'], OUT['v_perp'])
    plt.ylabel('vperp')
    plt.show()

    plt.figure()
    plt.plot(OUT['time'], OUT['moment'])
    plt.ylabel('Magnetic moment')
    plt.show()

    plt.figure()
    plt.plot(OUT['time'], OUT['v_para']**2 + OUT['v_perp']**2)
    plt.ylabel('Kinetic Energy')
    plt.show()

    # plt.figure()
    # plt.plot(OUT['r_lorentz'], OUT['z_lorentz'])
    # plt.show()
        
    imageFile = getOption('imageFile')
    if imageFile :
        plt.savefig(imageFile)
    else :
        plt.show()
