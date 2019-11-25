#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#Module that creates a heat load model based on the Eich parameters
Created on Sun Oct 20 18:28:22 2019
@author: Daniel.Iglesias@tokamak.energy.co.uk
"""
from vita.modules.sol_heat_flux.mid_plane_heat_flux import HeatLoad
import numpy as np
from scipy import special
from scipy.ndimage import convolve1d
import bisect

class Eich(HeatLoad): 
  def __init__(self, lambda_q=0, S=0):
    HeatLoad.__init__(self)
    self.lambda_q = lambda_q
    self.S = S
    self.q0 = 1.
    self.model_type = "Eich"
    
  def calculate_heat_flux_density(self, where="hfs"):
    self._HeatLoad__q = np.zeros( len(self._HeatLoad__s) )
    self._s_disconnected_dn_inboard = self.fx_in_out*self.s_disconnected_dn_max
    if(where=="hfs"):
      a = self.S / (2 * self.lambda_q * self.fx)
      self._HeatLoad__q = self.q0/2*np.exp(a**2 - self._HeatLoad__s/(self.lambda_q*self.fx)) * \
             special.erfc( a - self._HeatLoad__s/self.S)
    if(where=="hfs-mp"):
      i_cut = np.where( self._HeatLoad__s > 0 )[0]
      self._HeatLoad__q[i_cut] = self.q0 * np.exp( - self._HeatLoad__s[i_cut]/(self.lambda_q*self.fx) )
    if(where=="lfs-mp"):
      i_cut = np.where( np.logical_and(self._HeatLoad__s > 0, self._HeatLoad__s < self._s_disconnected_dn_inboard) )[0]
      profile = np.zeros( len(self._HeatLoad__s) )
      profile[i_cut] = self.q0 * np.exp( - self._HeatLoad__s[i_cut]/(self.lambda_q*self.fx) )
      gaussian = self.q0 * np.exp( - (self._HeatLoad__s - 2.25*self._HeatLoad__s[i_cut[-1]])**2 / 0.05 )
      print(self._HeatLoad__q.size, profile.size, gaussian.size)
#      self._HeatLoad__q = convolve1d(profile, gaussian)
      self._HeatLoad__q = profile
#      self._HeatLoad__q = gaussian
    elif(where=="lfs"):
      a = self.S / (2 * self.lambda_q * self.fx)
      self._HeatLoad__q = self.q0/2*np.exp(a**2 - self._HeatLoad__s/(self.lambda_q*self.fx)) * \
             special.erfc( a - self._HeatLoad__s/self.S)
    else: NotImplementedError("calculate_heat_flux_density for the {} is not yet implemented.".format(where))


