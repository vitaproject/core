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
    '''
    Class for evaluating and storing the heat load at the up-stream and down-stream
    positions using an Eich-like single exponential fit.

    Member functions:

        calculate_heat_flux_density: Function for calculating the heat-flux given
        a set of input parameters.
    '''
    def __init__(self, lambda_q=1.5e-3, S=0., r0_lfs=0., r0_hfs=0.):
        '''
        Inputs for the class are

        Parameters
        ----------
        lambda_q : float, optional
            The scrape-off layer power fall-off length. The default is 0.0015 m.
        S : float, optional
            Spreading factor. The default is 0.
        r0_lfs : float, optional
            The position of the low field side LCFS. The default is 0.
        r0_hfs : float, optional
            The position of the high field side LCFS. The default is 0.

        Returns
        -------
        None.

        '''
        HeatLoad.__init__(self, r0_lfs, r0_hfs)
        self.lambda_q = lambda_q
        self.S = S
        self.q_0 = 1.
        self.model_type = "Eich"

    def calculate_heat_flux_density(self, where="lfs-mp"):
        '''
        Function for evaluating the heat flux density using an Eich-like
        exponential at the mid-plane and an Eich function at the divertor.

        The heat flux for the different positions is given by:

            lfs-mp:
                lambda_q = q_0*exp[-s/lambda_q] for s > 0

            hfs-mp:
                lambda_q = q_0*exp[-s/lambda_q]/f_x_in_out*r0_lfs/r0_hfs
                                                for s > 0 and s < d_rsep
                lambda_q = 0                    for s > d_rsep

            lfs:
                lambda_q = q_0/2*exp[S^2/(2*lambda_q*f_x)^2 - s/(lambda_q*f_x)]
                                *erfc(S/(2*lambda_q*f_x) - s/S)
            hfs:
                So far, this has not been implemented properly, so it simply
                gives the same output as hfs-mp

        Parameters
        ----------
        where : string, optional
            A string with the position to evaluate.
            The options are:
                "lfs-mp"
                "hfs-mp"
                "lfs"
                "hfs"
            The default is "lfs-mp".

        Returns
        -------
        None.

        '''
        self._q = np.zeros(len(self._s))
        self._s_disconnected_dn_inboard = self.f_x_in_out*self.s_disconnected_dn_max

        if where == "lfs-mp":
            i_cut = np.where(self._s > 0)[0]
            self._q[i_cut] = self.q_0 * np.exp(-self._s[i_cut]\
                                                        /(self.lambda_q))

        elif where == "hfs-mp":
            i_cut = np.where(np.logical_and(self._s > 0,
                                            self._s < self._s_disconnected_dn_inboard))[0]
            profile = np.zeros(len(self._s))
            profile[i_cut] = self.q_0*np.exp(-self._s[i_cut]\
                                             /(self.lambda_q*self.f_x_in_out))\
                                             /self.f_x_in_out\
                                             *self.r0_lfs/self.r0_hfs
            self._q = profile

        elif where == "hfs":
            i_cut = np.where(np.logical_and(self._s > 0,
                                            self._s < self._s_disconnected_dn_inboard))[0]
            profile = np.zeros(len(self._s))
            profile[i_cut] = self.q_0*np.exp(-self._s[i_cut]\
                                             /(self.lambda_q*self.f_x_in_out))\
                                             /self.f_x_in_out\
                                             *self.r0_lfs/self.r0_hfs
            self._q = profile

        elif where == "lfs":
            a_temp = self.S / (2 * self.lambda_q * self.f_x)
            self._q = self.q_0/2*np.exp(a_temp**2 - self._s\
                                                  /(self.lambda_q*self.f_x))\
                                *erfc(a_temp - self._s/self.S)

        else:
            error_string = "calculate_heat_flux_density for"
            error_string += " the {} is not yet implemented.".format(where)
            NotImplementedError(error_string)
