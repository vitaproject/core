#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 9 07:35:12 2019

@author: Daniel.Iglesias@tokamakenergy.co.uk
"""
#import scipy.integrate as integrate
#from scipy.interpolate import interp1d
#import matplotlib.pyplot as plt
from vita.modules.fiesta.fiesta_interface import Fiesta


class PsiMapper:

    def __init__(self):
        self.r0_hfs = 0.  # edge radius at outboard equatorial midplane
        self.r0_lfs = 0.  # edge radius at inboard equatorial midplane
        self.__s = []  # limiter profile coordinate array
        self.__q = []  # heat flux density profile
        self.__totalPower = 0.
        self.model_type = None
        self.s_disconnected_dn_max = 0.001
        self._s_disconnected_dn_inboard = 0.001
        self._interp_func = None
 
    def setEquilibrium(self,equil_in):
        self.equil = equil_in
    
    def setLimiterProfile(self,profile_in):
        self.__profile = profile_in
        
    def mapMidPlaneFlux(self, q_mp, r_mp, equil):
        self.__q = q_mp
        self.__s

if __name__ == '__main__':
    from vita.utility import get_resource

    equil = get_resource("ST40", "equilibrium", "eq002")
    FIESTA_EQUIL = Fiesta(equil)
    print(FIESTA_EQUIL.get_midplane_lcfs())