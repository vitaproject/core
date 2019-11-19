#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 09:37:50 2019

@author: jmbols
"""
import numpy as np
import matplotlib.pyplot as plt
from vita.modules.fiesta.fiesta_interface import Fiesta
from vita.modules.utils import intersection

def map_psi(fiesta_equil, divertor_pos, nr_segments=1000, end_segment=1./10.):
    '''
    Function for mapping the radial and poloidal positions to a given surface.

    Input: fiesta_equil, an object of the Fiesta class with the desired equilibrium
           divertor_pos, a 2-by-n numpy array with the coordinates for the surface we
                         wish to calculate the intersection with, where divertor_pos[0]
                         is the radial coordinates and divertor_pos[1] are the poloidal
                         coordinates
           nr_segments,  an integer with the number of contours we wish to evaluate,
                         essentially giving the resolution
           end_segment,  a float with the last psi_n you wish to evaluate, so
                         e.g. end_segment = 1./10 will set the last contour to
                         psi_n = 1.1

    return: psi_map,     a dictionary with:
                         'psi_n', the normalised flux surface position,
                         'R_omp', the radial position at the OMP,
                         'Z_omp', the vertical position at the OMP (all 0),
                         'R_div, the radial position of the intersection with
                         the specified surface,
                         'Z_div', the radial position of the intersection with
                         the specified surface
    '''
    r_vec, z_vec = np.meshgrid(fiesta_equil.r_vec, fiesta_equil.z_vec)

    lcfs_psi_n = 1
    psi_p = []
    for i in range(nr_segments):
        psi_p.append(lcfs_psi_n+i/nr_segments*end_segment)

    cont = plt.contour(r_vec, z_vec, fiesta_equil.psi_n, psi_p)
    cont = cont.allsegs
#    plt.close()

    r_omp = []
    z_omp = []
    omp_pos = np.array((np.array([0.0, 1.0]), np.array([0.0, 0.0])))
    r_div = []
    z_div = []
    psi = []
    i = 0
    for c_i in cont:
        c_i = c_i[0]
        is_core = any(c_i[:, 1] > 0)*any(c_i[:, 1] < 0)
        if is_core:
            psi_contour = np.array((c_i[:, 0], c_i[:, 1]))
            (_, _), (r_omp_intersect, z_omp_intersect) = intersection(psi_contour, omp_pos)
            (_, _), (r_div_intersect, z_div_intersect) = intersection(psi_contour, divertor_pos)
            r_omp.append(r_omp_intersect[1])
            z_omp.append(z_omp_intersect[1])
            r_div.append(r_div_intersect)
            z_div.append(z_div_intersect)
            psi.append(psi_p[i])
        i += 1

    psi_map = {}
    psi_map['R_div'] = r_div
    psi_map['Z_div'] = z_div
    psi_map['R_omp'] = r_omp
    psi_map['Z_omp'] = z_omp
    psi_map['psi_n'] = psi
    return psi_map

if __name__ == '__main__':
    FIESTA = Fiesta('/media/jmbols/Data/jmbols/ST40/Programme 3/Equilibrium/eq_0002.mat')
    NR_SEGMENTS = 1000
    END_SEGMENT = 1/10
    DIVERTOR_POS = np.array((np.array([0.375, 0.675]), np.array([-0.78, -0.885])))
    PSI_MAP = map_psi(FIESTA, DIVERTOR_POS, NR_SEGMENTS, END_SEGMENT)
    plt.plot(PSI_MAP['R_div'], PSI_MAP['R_omp'])
