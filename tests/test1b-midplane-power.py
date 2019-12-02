#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 18:28:22 2019

@author: Daniel.Ibanez
"""
import math
import sys
import pathlib
path_modules = pathlib.Path('../vita/modules')
if str(path_modules) not in sys.path:
    sys.path.append(str(path_modules)) # Adds higher directory to python modules path.

from sol_heat_flux.eich import Eich
import numpy as np

footprint = Eich(5*0.002,0.001)# lambda_q=2.5, S=0.1
footprint.R0 = 1.7
footprint.q0 = (1.7/0.55)*0.1*(10+0.2*20)/(0.00245419*2.*footprint.R0*math.pi)
print ("Peak power density is ", footprint.q0, "MW/m2")
print ("Total footprint Power is ", footprint.q0*0.00245419, "MW/m")
print ("Total Power is ", footprint.q0*0.00245419*2.*footprint.R0*math.pi*(.55/1.7), "MW")
x=np.linspace(-0.001,0.020,100)
footprint.setCoordinates(x)

footprint.calculateHeatFluxDensity()

footprint.xlabel='$s\quad [m]$'
footprint.ylabel='$q//(s)\quad [MW/m^2]$'
footprint.plotHeatPowerDensity()
print(footprint.calculateHeatPower())