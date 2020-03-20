#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 18:28:22 2019

@author: Daniel.Ibanez
"""
from vita.modules.sol_heat_flux.eich import Eich
import numpy as np

footprint = Eich(lambda_q=2.5e-3, S=0.5e-3, r0_lfs=0.75, r0_hfs=0.2)# lambda_q=2.5, S=0.5

x=np.linspace(-1, 10, 1000)*1e-3
footprint.s_disconnected_dn_max = 1.0e-3
footprint.f_x_in_out = 5.0
footprint.set_coordinates(x*footprint.f_x_in_out)
q_0 = 1e6

footprint.calculate_heat_flux_density("hfs-mp")
footprint.plot_heat_power_density()
print(footprint._s_disconnected_dn_inboard)
print(q_0*footprint.calculate_heat_power()*2*np.pi*footprint.r0_hfs)
