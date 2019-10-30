#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 12:59:47 2019

@author: jmbols
"""
import numpy as np

def get_physics_constants():
    '''
    Function for populating the physics constant dictionary

    Input: none

    return: physics_constants, a dictionary with a series of physics constants
            in SI units
    '''
    physics_constats = {}
    physics_constats["e"] = 1.60217662e-19
    physics_constats["k_b"] = 1.38064852e-23
    physics_constats["m_p"] = 1.6726219e-27
    physics_constats["epsilon_0"] = 8.8541878128e-12
    physics_constats["mu_0"] = 4.*np.pi*1.e-7

    return physics_constats
