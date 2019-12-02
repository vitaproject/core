#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 12:28:22 2019

@author: Daniel.Ibanez
"""
import math
import numpy as np
from vita.modules.sol_heat_flux.eich import Eich

def run_midplane_power(midplane_model, plasma, plot=False):
    '''
    Function for running the specified mid-plane model

    Input: midplane_model, a string with the type of model to use for the heat-flux
                           evaluation
           plasma,         the plasma settings defined in the .json input file

    return: footprint,     an object of the midplane_model class specified
    '''
    print(plasma)
    print(plasma['sol'])
    if midplane_model == 'Eich':
        footprint = Eich(5*plasma['sol']['lambda_q'], plasma['sol']['S'])# lambda_q=2., S=0.1
    else:
        raise NotImplementedError(
            "The midplane_model {} is not yet implemented.".format(midplane_model))

    footprint.R0 = 1.7
    aux_power = plasma['heating']['NBI-power'] + plasma['heating']['Ohmic-power']\
                + plasma['heating']['rf-power']
    print("Auxiliary heating = {}".format(aux_power))

    if plasma['isotopes'] == "DT":
        alpha_power = aux_power*0.20
        print("Alpha heating = {}".format(alpha_power))

    else:
        alpha_power = 0.
    print("Total heating = {}".format(aux_power + alpha_power))

    footprint.q0 = (aux_power + alpha_power)/(0.00245419*2.*footprint.R0*math.pi)
    print("Peak power density is {}".format(footprint.q0), "MW/m2")
    print("Total footprint Power is ", footprint.q0*0.00245419, "MW/m")
    print("Total Power is ", footprint.q0*0.00245419*2.*footprint.R0*math.pi*(.55/1.7), "MW")
    x_coord = np.linspace(-0.001, 0.020, 100)
    footprint.set_coordinates(x_coord)

    footprint.calculate_heat_flux_density("hfs")

    footprint.xlabel = r'$s\quad [m]$'
    footprint.ylabel = r'$q//(s)\quad [MW/m^2]$'
    if plot:
        footprint.plot_heat_power_density()
    print(footprint.calculate_heat_power())

    return footprint
