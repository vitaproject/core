#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 10 14:24:20 2020

@author: jmbols
"""
import numpy as np

def get_div_coords(divertor_coords):
    # Define the 1D polynomial that represents the divertor
    for divertor_coord in divertor_coords:
        divertor_x = divertor_coord[0]
        divertor_y = divertor_coord[1]

        divertor_func = np.polyfit(divertor_x, divertor_y, 1)
        divertor_polyfit = np.poly1d(divertor_func)

        # Define a 1D polynomial for a surface just above the divertor (to be used
        # for evaluating the angle of incidence)
        divertor_func_above = [divertor_func[0], divertor_func[1] + 0.001]
        divertor_polyfit_above = np.poly1d(divertor_func_above)

        # Define a 1D polynomial for a surface just below the divertor (to be used
        # for evaluating the angle of incidence)
        divertor_func_below = [divertor_func[0], divertor_func[1] - 0.001]
        divertor_polyfit_below = np.poly1d(divertor_func_below)
    