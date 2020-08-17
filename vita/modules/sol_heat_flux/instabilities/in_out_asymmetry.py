#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 11:05:27 2020

@author: jmbols
"""

import numpy as np

class DivertorPowerSharing():
    '''
    Class for storing the in-out and up-down power asymmetries calculated based
    on the C-mod paper:
        D. Brunner et al 2018 Nucl. Fusion 58 076010

    Member functions:
        _calculate_in_out_asymmetry()
        _calculate_hfs_up_down_asymmetry()
        _calculate_lfs_up_down_asymmetry()
    '''
    def __init__(self, d_rsep, p_tot=1., lambda_q_lfs=1.5e-3, lambda_q_hfs=0.5e-3,
                 lambda_io=1.0e-3, p_io_0drsep=0.1, p_io_infdrsep=1./3.):
        self.d_rsep = d_rsep
        self.p_tot = p_tot
        self.lambda_q_lfs = lambda_q_lfs
        self.lambda_q_hfs = lambda_q_hfs
        self.lambda_io = lambda_io
        self.p_io_0drsep = p_io_0drsep
        self.p_io_infdrsep = p_io_infdrsep
        self.p_i = self._calculate_in_out_asymmetry()
        self.p_o = self.p_tot - self.p_i
        self.p_il, self.p_iu = self._calculate_hfs_up_down_asymmetry()
        self.p_ol, self.p_ou = self._calculate_lfs_up_down_asymmetry()

    def _calculate_in_out_asymmetry(self):
        '''
        Function for calculating the in-put power asymmetry in a double null
        configuration as a function of d_rsep, the distance between the
        two separatrices at the outer midplane.

        The expression is given by a gaussian fit:
            p_i = p_tot*(p_i_0 + (p_i_0 + p_i_inf)*(1 - 2/(1+exp((-d_r,sep/lambda_io)^2)))),

        where p_tot is the total power into the scrape-off layer, p_i_0 is the
        power that flows to the inboard side if d_rsep = 0, p_i_inf is the power
        that flows to inboard side if it is a perfect single null configuration.
        lambda_io is the width of the gaussian fit and is a fitting parameter.

        Returns
        -------
        p_i : float
            The total power that flows to the HFS divertors

        '''
        p_i = self.p_tot*(self.p_io_0drsep + (self.p_io_0drsep - self.p_io_infdrsep)\
                          *(1 - 2/(1+np.exp(-(self.d_rsep/self.lambda_io)**2))))
        return p_i

    def _calculate_hfs_up_down_asymmetry(self):
        '''
        Function for calculating the up-down power asymmetry in the inboard
        side as a function of d_rsep, the distance between the separatrices
        at the outer midplane.

        The expression is a logistic fit and is given by:
            p_il = p_i/(1+exp(d_rsep/lambda_q_hfs))
            p_io = p_i/(1+exp(-d_rsep/lambda_q_hfs)),

        where p_i is the power that flows to the inboard side, and
        lambda_q_hfs is the fall-off length at the HFS

        Returns
        -------
        p_il : float
            The power that flows to the lower HFS divertor
        p_iu : float
            The power that flows to the upper HFS divertor

        '''
        p_il = self.p_i/(1+np.exp(self.d_rsep/self.lambda_q_hfs))

        p_iu = self.p_i/(1+np.exp(-self.d_rsep/self.lambda_q_hfs))

        return p_il, p_iu

    def _calculate_lfs_up_down_asymmetry(self):
        '''
        Function for calculating the up-down power asymmetry in the outboard
        side as a function of d_rsep, the distance between the separatrices
        at the outer midplane.

        The expression is a logistic fit and is given by:
            p_ol = p_o/(1+exp(-d_rsep/lambda_q_lfs))
            p_ou = p_o/(1+exp(d_rsep/lambda_q_lfs)),

        where p_o is the power that flows to the outboard side, and
        lambda_q_lfs is the fall-off length at the OMP

        Returns
        -------
        p_ol : float
            The power that flows to the lower LFS divertor
        p_ou : float
            The power that flows to the upper LFS divertor

        '''
        p_ol = self.p_o/(1 + np.exp(self.d_rsep/self.lambda_q_lfs))

        p_ou = self.p_o/(1 + np.exp(-self.d_rsep/self.lambda_q_lfs))

        return p_ol, p_ou
