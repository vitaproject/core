#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 18:28:22 2019

@author: Daniel.Ibanez
"""
import os
print (os.getcwd())
import sys
sys.path.append(".\..\Modules") # Adds higher directory to python modules path.

from modelSOLHeatFlux.eich import Eich
import numpy as np

footprint = Eich(2.5,0.5)# lambda_q=2.5, S=0.5

x=np.linspace(-1,10,100)
footprint.setCoordinates(x)

footprint.calculateHeatFluxDensity()
footprint.plotHeatPowerDensity()
print(footprint.calculateHeatPower())
