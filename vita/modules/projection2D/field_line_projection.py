#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 15:37:52 2019

@author: jmbols
"""
import numpy as np
from vita.modules.utils import intersection, calculate_angle

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

def project_heat_flux(heat_flux_profile_omp, surface_position, equilibrium, b_pol):
    '''
    Function for projecting a heat flux from the OMP to a given surface (without taking diffusion
    into account), defined as:

        q_{parallel, div} = x_omp/x_div * q_{parallel, omp}/(f_x/sin(theta)),

    where q_{parallel, div} is the parallel (to magnetic field lines) heat flux
    at the divertor, q_{parallel, omp} is the parallel heat flux at the OMP,
    x_omp is the radial coordinates at the OMP, x_div is the radial coordinates
    at the divertor, f_x is the flux expansion and theta is the incidence angle

    Parameters
    ----------
    heat_flux_profile_omp : 2-by-n numpy array
        Here heat_flux_profile_omp[0] is the radial coordinates
        of each point at the OMP and heat_flux_profile_omp[1]
        is the parallel heat flux at the corresponding radial points
    surface_position : 2-by-m numpy array
        Here surface_position[0] is the radial coordinates
        and surface_position[1] is the poloidal positions
    equilibrium : python dictionary
        Here the radial points at the omp are the keys
        and a dictionary with the R-Z coordinates of the individual
        field lines as values.
    b_pol : cherab.core.math.Interpolate2DCubic
        Function for interpolating the poloidal magnetic field from
        a fiesta equilibrium, given an (r, z)-point

    Returns
    -------
    heat_flux_at_intersection : 3-by-n numpy array
        Here heat_flux_at_intersection[0] is the radial coordinates of each
        point at the target, heat_flux_at_intersection[1] is the vertical coordinates
        of each point at the target, and heat_flux_profile_omp[2]
        is the parallel heat flux at the corresponding positions
    '''
    x_after_lcfs = heat_flux_profile_omp[0]
    field_lines = equilibrium

    f_x = []
    angle = []
    intersection_x = []
    intersection_y = []
    _v_2 = np.array([surface_position[0, 1] - surface_position[0, 0],
                     surface_position[1, 1] - surface_position[1, 0]])
    for i in field_lines:
        func1 = np.array((field_lines[i]['R'], field_lines[i]['Z']))
        (i_func1, _), (x_at_surface, y_at_surface) = intersection(func1,
                                                                  (surface_position))
        if np.isnan(x_at_surface):
            break

        _x_component = field_lines[i]['R'][int(i_func1)]-field_lines[i]['R'][int(i_func1)+1]
        _y_component = field_lines[i]['Z'][int(i_func1)]-field_lines[i]['Z'][int(i_func1)+1]
        _v_1 = [_x_component, _y_component]

        f_x.append(_flux_expansion(b_pol,
                                   (i, 0),
                                   (x_at_surface[0], y_at_surface[0])))
        angle.append(calculate_angle(_v_1, _v_2))

        intersection_x.append(x_at_surface[0])
        intersection_y.append(y_at_surface[0])

    intersection_x = np.array(intersection_x)
    intersection_y = np.array(intersection_y)

    q_div = x_after_lcfs/intersection_x * \
          heat_flux_profile_omp[1, :len(intersection_x)]/(f_x/np.sin(angle))

    heat_flux_at_intersection = np.array([intersection_x, intersection_y, q_div])

    return heat_flux_at_intersection
