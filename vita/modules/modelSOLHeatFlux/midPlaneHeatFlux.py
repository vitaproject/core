# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 09:51:09 2019

@author: Daniel.Iglesias@tokamak.energy.co.uk
"""
import scipy.integrate as integrate
import matplotlib.pyplot as plt

class HeatLoad():
  def __init__(self):
    self.fx = 1. # flux expansion
    self.qb = 0. # background heat
    self.R0 = 0. # edge radius at equatorial midplane
    self.__s = [] # equatorial midplane coordinate array
    self.__q = [] # heat flux density profile
    self.__totalPower = 0.
    self.model_type = None
    
  def setCoordinates(self,s_in=[]):
    if self.model_type=="Eich":
        self.__s = s_in
    else:
        print("Warning: The HeatFlux model in use does not allow setting coordinates")
        return -1
  
  def getLocalCoordinates(self):
      return self.__s

  def getGlobalCoordinates(self):
      return self.__s + self.R0

  def setEdgeRadius(self, radius_in):
    self.R0 = radius_in

  def setFluxExpansion(self, fx_in):
    self.fx = fx_in
    
  def setBackgroundHeat(self, qb_in):
    self.qb = qb_in

  def calculateHeatPower(self):
    self.__totalPower = integrate.simps(self.__q, self.__s)
    return self.__totalPower

  def plotHeatPowerDensity(self):
    plt.plot(self.__s, self.__q)
    plt.xlabel('$s$')
    plt.ylabel('$q(s)$')
    plt.show


