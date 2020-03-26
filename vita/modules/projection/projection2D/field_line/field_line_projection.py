#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 09:13:19 2020

@author: jmbols
"""
import os
import numpy as np
from vita.modules.projection.projection2D.field_line.field_line import FieldLine
from vita.modules.utils import intersection, calculate_angle, load_pickle
from cherab.core.math import Interpolate2DCubic

def _flux_expansion(b_pol, points_omp, points_div):
    '''
    Function for evaluating the flux expansion, defined as:

        f_x = x_omp*b_pol(x_omp, y_omp)/(x_div*b_pol(x_div, y_div)),

    where x_omp is the radial coordinate at the OMP, y_omp is the vertical
    coordinate at the OMP (usually 0) and x_div and y_div are the corresponding
    coordinates at the divertor.

    Parameters
    ----------
    b_pol : cherab.core.math.Interpolate2DCubic
        Function for interpolating the poloidal magnetic field from a fiesta
        equilibrium, given an (r, z)-point
    points_omp : 2-x-1 list
        List containing a point at the outboard mid-plane
    points_div : 2-x-1 list
        List containing the point at the corresponding flux surface at the
        divertor.

    Returns
    -------
    f_x : float
        The flux expansion at the divertor point specified

    '''
    return points_omp[0]*b_pol(points_omp[0], points_omp[1])\
            /(points_div[0]*b_pol(points_div[0], points_div[1]))

def project_field_lines(x_axis_omp, surface_coords, fiesta):
    '''
    Function mapping the field-lines from the specified coordinates at the
    OMP to the specified coordinates at a given surface. Currently the surface
    is assumed to be represented by a 1D polynomial function, y = ax + b.

    Parameters
    ----------
    x_axis_omp : n-x-1 np.array
        Numpy array with the radial coordinates we wish to map at the OMP
    fiesta : Fiesta
        A Fiesta object with the 2D equilibrium we wish to map
    divertor_coords : 2-x-2 np.array
        A 2-x-2 numpy array containg the corner points of the divertor in the
        2D projection

    Returns
    -------
    divertor_map : dictionary
        A dictionary containing:
            "R_div" : an n-x-1 array
                with the R-coordinates at the divertor tile
                corresponding to the same psi_n as at the OMP
            "Z_div" : an n-x-1 array
                with the Z-coordinates at the divertor tile
                corresponding to the same psi_n as at the OMP
            "Angles" : an n-x-1 array
                with the angles between the field lines and the divertor tile
                corresponding to the same psi_n as at the OMP
            "Flux_expansion" : an n-x-1 array
                with the flux expasion at the divertor tile
                corresponding to the same psi_n as at the OMP

    '''
    # Interpolate b_pol (to be used when evaluating the flux expansion)
    b_pol = np.sqrt(fiesta.b_r**2 + fiesta.b_theta**2 + fiesta.b_z**2).T
    b_pol_interp = Interpolate2DCubic(fiesta.r_vec, fiesta.z_vec, b_pol)

    field_lines = {}
    
    if os.path.exists("Random_filename"):
        field_lines = load_pickle("Random_filename")
    else:
        field_line = FieldLine(fiesta)
        for i in x_axis_omp:
            p_0 = [i, 0, 0]
            field_line_dict = field_line.follow_field_in_plane(p_0=p_0, max_length=15.0)
            field_lines[i] = field_line_dict

    _v_2 = np.array([surface_coords[0, 1] - surface_coords[0, 0],
                     surface_coords[1, 1] - surface_coords[1, 0]])

    divertor_map = {}
    for i in field_lines:
        func1 = np.array((field_lines[i]['R'], field_lines[i]['Z']))
        (i_func1, _), (x_at_surface, y_at_surface) = intersection(func1,
                                                                  (surface_coords))
        if np.isnan(x_at_surface):
            break

        _x_component = field_lines[i]['R'][int(i_func1)]-field_lines[i]['R'][int(i_func1)+1]
        _y_component = field_lines[i]['Z'][int(i_func1)]-field_lines[i]['Z'][int(i_func1)+1]
        _v_1 = [_x_component, _y_component]

        temp_dict = {}
        temp_dict["R_pos"] = x_at_surface[0]
        temp_dict["Z_pos"] = y_at_surface[0]
        temp_dict["alpha"] = calculate_angle(_v_1, _v_2)
        temp_dict["f_x"] = _flux_expansion(b_pol_interp,
                                           (i, 0),
                                           (x_at_surface[0], y_at_surface[0]))
        divertor_map[i] = temp_dict

    return divertor_map
