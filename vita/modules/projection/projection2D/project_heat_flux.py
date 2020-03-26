#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 09:11:19 2020

@author: jmbols
"""
import numpy as np

def project_heat_flux(x_pos_omp, heat_flux_profile, map_dict):
    '''
    Function for mapping the heat flux from the OMP to the divertor. The heat
    flux at a different position is given by:

        q_parallel_surf = R_omp/R_surf*q_parallel_omp/(f_x/cos(alpha)),

    where R_omp, is the radial coordinate at the OMP, R_surf is the radial coordinates
    at the surface, q_parallel_omp is the parallel heat flux at the OMP, alpha
    is the incidence angle of the field-lines with respect to the normal of the
    surface, and f_x is the flux expansion:
        
        f_x = R_omp*B_pol(R_omp, Z_omp)/(R_surf*B_pol(R_surf, Z_surf)),

    where Z_omp is the vertical position of the OMP (usually 0), Z_surf is
    the vertical position of the surface, and B_pol is the poloidal magnetic
    field and the given coordinates.

    Parameters
    ----------
    x_pos_omp : n-by-1 np.array
        Radial coordinates at the OMP
    heat_flux_profile : n-by-1 np.array
        Parallel heat flux at the given coordinates
    map_dict : dictionary
        Python dictionary with:
            keys: float
                x_pos_omp[i], each position at the omp has a corresponding mapped position
            values: dictionary
                dictionary with keys:
                    "R_pos" : float, radial position of the surface
                    "Z_pos" : float, vertical position of the surface
                    "f_x"   : float, flux expansion at the given R, Z position
                    "alpha" : float, incidence angle with respect to the normal
                                     of the surface
                

    Returns
    -------
    q_surf : n-by-1 np.array
        parallel heat flux at the surface position

    '''
    q_surf = np.zeros(len(x_pos_omp))
    for i in range(len(x_pos_omp)):
        q_surf[i] = x_pos_omp[i]/map_dict[x_pos_omp[i]]["R_pos"] * \
                    heat_flux_profile[i]/(map_dict[x_pos_omp[i]]["f_x"]\
                                          /np.cos(map_dict[x_pos_omp[i]]["alpha"]))

    return q_surf