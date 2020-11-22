#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 19 11:15:47 2020

@author: jmbols
"""

import numpy as np
from vita.modules.sol_heat_flux.instabilities.elm_evaluation import ELM

if __name__ == "__main__":
    T_EPED = 1000.
    T_IPED = 1000.
    N_PED = 1e20
    CHARGE_NUMBER = 1.

    MAJOR_R = 1.4
    MINOR_R = 1.4/1.9
    V_PLASMA = 2.*np.pi*MAJOR_R*np.pi*MINOR_R**2
    Q_95 = 5

    PEDESTAL_PARAMS = {}
    PEDESTAL_PARAMS["t_e"] = T_EPED
    PEDESTAL_PARAMS["t_i"] = T_IPED
    PEDESTAL_PARAMS["n"] = N_PED
    PEDESTAL_PARAMS["Z"] = CHARGE_NUMBER

    MACHINE_PARAMS = {}
    MACHINE_PARAMS["V"] = V_PLASMA
    MACHINE_PARAMS["R_0"] = MAJOR_R
    MACHINE_PARAMS["a"] = MINOR_R
    MACHINE_PARAMS["q_95"] = Q_95

    ELM = ELM(MACHINE_PARAMS, PEDESTAL_PARAMS)
    print(ELM.elm_energy)