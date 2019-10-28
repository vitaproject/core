#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 18:28:22 2019

@author: Daniel.Ibanez
"""
import sys
import pathlib
path_modules = pathlib.Path('../vita/modules')
if str(path_modules) not in sys.path:
    sys.path.append(str(path_modules)) # Adds higher directory to python modules path.

from sol_heat_flux.eich import Eich
import numpy as np

footprint = Eich(2.5,0.0005)# lambda_q=2.5, S=0.5

x=np.linspace(-1,10,100)
footprint.setCoordinates(x)

footprint.calculateHeatFluxDensity()
footprint.plotHeatPowerDensity()
print(footprint.calculateHeatPower())
