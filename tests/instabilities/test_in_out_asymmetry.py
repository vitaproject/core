#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 19 09:31:08 2020

@author: jmbols
"""

import numpy as np
import matplotlib.pyplot as plt
from vita.modules.sol_heat_flux.instabilities.in_out_asymmetry import DivertorPowerSharing

def test_in_out_asymmetry():
    '''
    Function for testing the DivertorPowerSharing class

    Returns
    -------
    None.

    '''
    # The total power to all divertors.
    p_tot = 1

    # Separatrix distance
    d_rseps = np.linspace(-0.004, 0.004, 1000)

    # e-folding length LFS
    lambda_o = 0.0025

    f_x = 3

    # e-folding length HFS. Assumed to be of the LFS times the
    # inboard-outboard flux expansion
    lambda_i = lambda_o/f_x

    # Width of the gaussian for the in-out power asymmetry. Assumed to be
    # twice the inboard width
    lambda_io = 2*lambda_i

    # The power ratio to the inboard divertor for a perfect double null.
    # Set to 10% based on C-mod paper
    p_i0 = 0.1

    # The in-out power asymmetry. Set to correlate with the difference in connection
    # lengths. L_par to inner divertor is roughly 2-times that to the outer divertor,
    # based on eq_010_export.mat.
    # This means inner divertor gets 1/3 and outer gets 2/3 of the power.
    l_par_out_in = 1./2.
    p_iinf = 1.-1./(1 + l_par_out_in)

    p_i = []
    p_o = []
    p_il = []
    p_iu = []
    p_ol = []
    p_ou = []
    for d_rsep in d_rseps:
        power_dist = DivertorPowerSharing(d_rsep=d_rsep, p_tot=p_tot,
                                          lambda_q_lfs=lambda_o, lambda_q_hfs=lambda_i,
                                          lambda_io=lambda_io, p_io_0drsep=p_i0,
                                          p_io_infdrsep=p_iinf)
    p_i.append(power_dist.p_i)
    p_o.append(power_dist.p_o)
    p_il.append(power_dist.p_il)
    p_ol.append(power_dist.p_ol)
    p_iu.append(power_dist.p_iu)
    p_ou.append(power_dist.p_ou)

    p_i = np.array(p_i)
    p_o = np.array(p_o)
    p_il = np.array(p_il)
    p_ol = np.array(p_ol)
    p_iu = np.array(p_iu)
    p_ou = np.array(p_ou)

    plt.figure()
    plt.plot(d_rseps, p_i, 'r')
    plt.plot(d_rseps, p_o, 'b')

    plt.figure()
    plt.plot(d_rseps, p_il/p_i, 'r')
    plt.plot(d_rseps, p_iu/p_i, 'b')

    plt.figure()
    plt.plot(d_rseps, p_ol/p_o, 'g')
    plt.plot(d_rseps, p_ou/p_o, 'k')

if __name__ == '__main__':
    test_in_out_asymmetry()
