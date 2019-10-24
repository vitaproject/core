#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#Module that creates a heat load model based on the Eich parameters
Created on Sun Oct 20 18:28:22 2019
@author: Daniel.Iglesias@tokamak.energy.co.uk
"""
from modelSOLHeatFlux.midPlaneHeatFlux import HeatLoad
import numpy as np
from scipy import special

class Eich(HeatLoad): 
  def __init__(self, lambda_q=0, S=0):
    HeatLoad.__init__(self)
    self.lambda_q = lambda_q
    self.S = S
    self.__q0 = 1.
    self.model_type = "Eich"
    
  def calculateHeatFluxDensity(self):
      a = self.S / (2 * self.lambda_q * self.fx)
      self._HeatLoad__q = self.__q0/2*np.exp(a**2 - self._HeatLoad__s/(self.lambda_q*self.fx)) * \
               special.erfc( a - self._HeatLoad__s/self.S)


