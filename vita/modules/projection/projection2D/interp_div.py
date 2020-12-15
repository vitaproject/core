#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 10 14:24:20 2020

@author: jmbols
"""
import numpy as np
import matplotlib.pyplot as plt

def get_div_coords(divertor_coords):
    function_below = []
    function_fit = []
    function_above = []
    # Define the 1D polynomial that represents the divertor
    for i in range(len(divertor_coords[0, :])-1):
        divertor_x = [divertor_coords[0, i], divertor_coords[0, i+1]]
        divertor_y = [divertor_coords[1, i], divertor_coords[1, i+1]]

        divertor_func = np.polyfit(divertor_x, divertor_y, 1)
        divertor_polyfit = np.poly1d(divertor_func)

        # Define a 1D polynomial for a surface just above the divertor (to be used
        # for evaluating the angle of incidence)
        divertor_func_above = [divertor_func[0] + 0.001, divertor_func[1] + 0.001]
        divertor_polyfit_above = np.poly1d(divertor_func_above)

        # Define a 1D polynomial for a surface just below the divertor (to be used
        # for evaluating the angle of incidence)
        divertor_func_below = [divertor_func[0] - 0.001, divertor_func[1] - 0.001]
        divertor_polyfit_below = np.poly1d(divertor_func_below)
        
        function_below.append(divertor_polyfit_below)
        function_fit.append(divertor_polyfit)
        function_above.append(divertor_polyfit_above)
    
    
    return function_below, function_fit,  function_above
        

def get_z_from_r(divertor_x, function_x, r):
    index = np.where((divertor_x - r) > 0)[0][0]
    print(index)
    function = function_x[index]
    z = r#function(r)
    return z

if __name__ == '__main__':
    #divertor_coords_x = [0.252, 0.332, 0.3321, 0.368]
    #divertor_coords_y = [-0.426, -0.621, -0.710, -0.806]
    divertor_coords_x = [0.226, 0.314, 0.365, 0.406]
    divertor_coords_y = [-0.425, -0.621, -0.708, -0.811]
    divertor_coords = np.array([divertor_coords_x, divertor_coords_y])

    x = np.linspace(0.227, 0.400, 100)

    func_below, func_fit, func_above = get_div_coords(divertor_coords)
    
    z = []
    for i in x:
        z.append(get_z_from_r(np.array(divertor_coords_x), func_fit, i))
    plt.plot(divertor_coords_x, divertor_coords_y)
    plt.plot(x, z)
    
 #   r = 5
  #  function_z_from_r = get_z_from_r(r)