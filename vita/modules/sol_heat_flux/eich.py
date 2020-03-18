#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#Module that creates a heat load model based on the Eich parameters
Created on Sun Oct 20 18:28:22 2019
@author: Daniel.Iglesias@tokamak.energy.co.uk
"""
import numpy as np
from scipy.special import erfc
from vita.modules.sol_heat_flux.mid_plane_heat_flux import HeatLoad

class Eich(HeatLoad):
    def __init__(self, lambda_q=0, S=0, r0_lfs=0, r0_hfs=0.):
        HeatLoad.__init__(self, r0_lfs, r0_hfs)
        self.lambda_q = lambda_q
        self.S = S
        self.q_0 = 1.
        self.model_type = "Eich"

    def calculate_heat_flux_density(self, where="lfs"):
        self._HeatLoad__q = np.zeros(len(self._HeatLoad__s))
        self._s_disconnected_dn_inboard = self.fx_in_out*self.s_disconnected_dn_max

        if where == "lfs-mp":
            i_cut = np.where(self._HeatLoad__s > 0)[0]
            self._HeatLoad__q[i_cut] = self.q_0 * np.exp(-self._HeatLoad__s[i_cut]\
                                                        /(self.lambda_q))

        elif where == "hfs-mp":
            i_cut = np.where(np.logical_and(self._HeatLoad__s > 0,
                                            self._HeatLoad__s < self._s_disconnected_dn_inboard))[0]
            profile = np.zeros(len(self._HeatLoad__s))
            profile[i_cut] = self.q_0*np.exp(-self._HeatLoad__s[i_cut]\
                                             /(self.lambda_q))/self.fx*self.r0_lfs/self.r0_hfs
            self._HeatLoad__q = profile

        elif where == "hfs":
            a = self.S / (2 * self.lambda_q * self.fx)
            self._HeatLoad__q = self.q_0/2*np.exp(a**2 - self._HeatLoad__s/(self.lambda_q*self.fx))\
                                    *erfc(a - self._HeatLoad__s/self.S)

        elif where == "lfs":
            a = self.S / (2 * self.lambda_q * self.fx)
            self._HeatLoad__q = self.q_0/2*np.exp(a**2 - self._HeatLoad__s/(self.lambda_q*self.fx))\
                                *erfc(a - self._HeatLoad__s/self.S)

        else:
            error_string = "calculate_heat_flux_density for"
            error_string += " the {} is not yet implemented.".format(where)
            NotImplementedError(error_string)
