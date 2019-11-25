# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 09:51:09 2019

@author: Daniel.Iglesias@tokamak.energy.co.uk
"""
import scipy.integrate as integrate
import matplotlib.pyplot as plt

class HeatLoad():
  def __init__(self):
    self.fx = 1. # edge radius at outboard equatorial midplane
    self.fx_in_out = 1. # edge radius at outboard equatorial midplane
    self.r0_hfs = 0. # edge radius at outboard equatorial midplane
    self.r0_lfs = 0. # edge radius at inboard equatorial midplane
    self.__s = [] # equatorial midplane coordinate array
    self.__q = [] # heat flux density profile
    self.__totalPower = 0.
    self.model_type = None
    self.s_disconnected_dn_max = 0.001
    self._s_disconnected_dn_inboard = 0.001
    
  def calculate_heat_flux_density(self):
    raise NotImplementedError("The inheriting class must implement this virtual function.")

  def set_coordinates(self,s_in=[]):
    if self.model_type=="Eich":
        self.__s = s_in
    else:
        print("Warning: The HeatFlux model in use does not allow setting coordinates")
        return -1
  
  def set_edge_radius(self, radius_in):
    self.ro_hfs = radius_in

  def get_local_coordinates(self):
      return self.__s

  def get_global_coordinates(self):
      return self.__s + self.r0_hfs

  def calculate_heat_power(self):
    self.__totalPower = integrate.simps(self.__q, self.__s)
    return self.__totalPower

  def plot_heat_power_density(self):
    plt.plot(self.__s, self.__q)
    plt.xlabel('$s$')
    plt.ylabel('$q(s)$')
    plt.show(block=True)


