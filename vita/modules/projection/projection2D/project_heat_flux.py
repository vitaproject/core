#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 09:11:19 2020

@author: jmbols
"""
import numpy as np


def project_heat_flux(x_pos_omp, heat_flux_profile, map_dict):
    """
    Function for mapping the heat flux from the OMP to the divertor. The heat
    flux at a different position is given by:

    .. math::

       q_{parallel_surf} = \\frac{R_{omp}}{R_{surf}} * \\frac{q_{parallel_omp}}{(f_x/\\cos(\\alpha))},

    where :math:`R_{omp}`, is the radial coordinate at the OMP, :math:`R_{surf}` is the radial
    coordinates at the surface, :math:`q_{parallel_omp}` is the parallel heat flux at the OMP,
    :math:`\\alpha` is the incidence angle of the field-lines with respect to the normal of the
    surface, and :math:`f_x` is the flux expansion:

    .. math::

       f_x = R_{omp}*B_{pol}(R_{omp}, Z_{omp})/(R_{surf}*B_{pol}(R_{surf}, Z_{surf})),

    where :math:`Z_{omp}` is the vertical position of the OMP (usually 0), :math:`Z_{surf}` is
    the vertical position of the surface, and :math:`B_{pol}` is the poloidal magnetic
    field and the given coordinates.

    :param np.ndarray x_pos_omp: Radial coordinates at the OMP
    :param np.ndarray heat_flux_profile: Parallel heat flux at the given coordinates
    :param dict map_dict: a python dictionary with:

            keys: float
                x_pos_omp[i], each position at the omp has a corresponding mapped position
            values: dictionary
                dictionary with keys:
                    "R_pos" : float, radial position of the surface
                    "Z_pos" : float, vertical position of the surface
                    "f_x"   : float, flux expansion at the given R, Z position
                    "alpha" : float, incidence angle with respect to the normal
                                     of the surface
                
    :rtype: np.ndarray
    :return: q_surf, the parallel heat flux at the surface position

    """

    q_surf = np.zeros(len(x_pos_omp))
    for i in range(len(x_pos_omp)):
        q_surf[i] = x_pos_omp[i]/map_dict[x_pos_omp[i]]["R_pos"] * \
                    heat_flux_profile[i]/(map_dict[x_pos_omp[i]]["f_x"]\
                                          /np.cos(map_dict[x_pos_omp[i]]["alpha"]))

    return q_surf