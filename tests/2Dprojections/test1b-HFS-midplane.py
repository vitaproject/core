#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 18:28:22 2019

@author: Daniel.Ibanez
"""
from vita.modules.sol_heat_flux.eich import Eich
import numpy as np

footprint = Eich(2.5,0.5)# lambda_q=2.5, S=0.5

x=np.linspace(-1,10,100)
footprint.set_coordinates(x)
footprint.s_disconnected_dn_max = 1.0
footprint.fx_in_out = 5.0


footprint.calculate_heat_flux_density("hfs-mp")
footprint.plot_heat_power_density()
print(footprint._s_disconnected_dn_inboard)
print(footprint.calculate_heat_power())
