#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 11:21:29 2019

@author: jmbols
"""
import numpy as np
from cherab.core.math import Interpolate2DCubic

def _shooting_algorithm(x_lims, function, function_z_from_r,
                        psi_target, tol=1.e-8, n_max=50,
                        location='lfs'):
    '''
    Function implementing the shooting algorithm.
    Given the function psi = f(r), where psi is known and f is a known function
    this algorithm determines the corresponding r. Assuming a straight divertor,
    we have psi = f(r, a r + b), which means that f is only a function of r.
    The algorithm is as follows:
        1. Define the midpoint as x_mid = (x_lower + x_upper)/2.
        2. Evaluate f(x_mid)
        3. Check if f(x_mid) - y is larger than the specified tolerance
        4. If no, then break and return x_mid. If yes then check if
           f(x_mid) - y < 0.
        5. If f(x_mid) - y < 0, set x_mid = x_lower, else set x_mid = x_upper
           if the location is set to lfs, if it is hfs it is opposite, otherwise
           return an error
        6. Repeat until n iteration or the error is below the tolerance

    Parameters
    ----------
    x_lims : 2-x-1 list
        List of floating points with x_lims[0] being the lower limit guess
        and x_lims[1] being the upper limit guess
    function : cherab.core.math.Interpolate2DCubic
        Function that interpolates a fiesta equilibrium and gives a normalised psi
        given an (r, z) point,
    function_z_from_r : np.poly1d
        Function for getting a z-coordinate at the divertor given an r-coordinate
        (we assume that the divertor can be described as a polynomial function)
    psi_target : float
        The psi we are trying to evaluate r and z for.
    tol : float
        The error tolerance for abs(psi_target - function(r, z)).
        Default is 1.e-8.
    n_max : integer
        Maximum number of iterations allowed.
        Default is 50
    location : string
        Which position to look at. Either 'lfs' or 'hfs'.
        Default is lfs

    Returns
    -------
    x_mid : float
        The radial coordinate of psi_target.

    '''
    x_lower = x_lims[0]
    x_upper = x_lims[1]
    for i in range(n_max):
        x_mid = (x_lower + x_upper)/2
        psi = function(x_mid, function_z_from_r(x_mid))
        if abs(psi - psi_target) > tol:
            if location == 'lfs':
                if (psi - psi_target) < 0.:
                    x_lower = x_mid
                else:
                    x_upper = x_mid
            elif location == 'hfs':
                if (psi - psi_target) < 0.:
                    x_upper = x_mid
                else:
                    x_lower = x_mid
        else:
            break
    if i==49:
        print("Warning: map_psi_omp_to_divertor._shooting_algorithm\n Convergence not reached")
    return x_mid

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

def _calculate_angles(v_1_vectors, v_2):
    '''
    Function for calculating the angles between the normalised psi calculated
    at the divertor and the divertor itself.
    The angle specified is calculated as the magnitude of the angle between the
    normal of the divertor and the normalised psi contour.

    Parameters
    ----------
    v_1_vectors : n-x-1 list of 2-x-1 np.arrays
        List of vectors of the field-lines close to the divertor interface
    v_2 : 2-x-1 np.array
        Vector for the divertor coordinates

    Returns
    -------
    angles : n-x-1 np.array
        Array of angles between the divertor and the normalised psi calculated
        at the divertor.

    '''

    def _angle(v_1, v_2):
        '''
        Calculate the angle between two vectors defined as:

            cos(angle) = (v_1 dot v_2)/(||v_1|| * ||v_2||),

        where ||v|| is the length of the vector.

        Parameters
        ----------
        v1 : 2-x-1 np.array
            Array with x and y of the first vector
        v2 : 2-x-1 np.array
            Array with x and y of the first vector

        Returns
        -------
        angle : float
            A float with the angle between the two vectors

        '''
        return np.arccos(np.dot(v_1, v_2)/\
                         (np.sqrt(np.dot(v_1, v_1))*np.sqrt(np.dot(v_2, v_2))))

    angles = []
    for v_1 in v_1_vectors:
        alpha_s = _angle(v_1, v_2)
        if alpha_s < np.pi/2.:
            alpha_i = np.pi/2. - alpha_s
        else:
            alpha_i = alpha_s - np.pi/2.
        angles.append(alpha_i)

    angles = np.array(angles)

    return angles

def map_psi_omp_to_divertor(x_axis_omp, divertor_coords, fiesta, location='lfs'):
    """
    Function mapping the normalised psi from the specified coordinates at the
    OMP to the specified coordinates at the divertor. Currently the divertor is
    assumed to be represented by a 1D polynomial function, y = ax + b.

    :param np.ndarray x_axis_omp: Numpy array with the radial coordinates we wish to map at the OMP
    :param Fiesta fiesta: A Fiesta object with the 2D equilibrium we wish to map
    :param np.ndarray divertor_coords: A 2-x-2 numpy array containg the corner
                                       points of the divertor in the 2D projection
    :param string location: a string with the location to evaluate, either 'hfs'
                            or 'lfs'. Default is 'lfs'
    :rtype: dict
    :return: A dictionary containing:

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
    """

    # Define the 1D polynomial that represents the divertor
    divertor_x = divertor_coords[0]
    divertor_y = divertor_coords[1]

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

    # Interpolate psi_n
    psi_n_interp = Interpolate2DCubic(fiesta.r_vec, fiesta.z_vec, fiesta.psi_n.T)

    # Interpolate b_pol (to be used when evaluating the flux expansion)
    b_pol = fiesta.b_theta.T #np.sqrt(fiesta.b_r**2 + fiesta.b_theta**2 + fiesta.b_z**2).T
    b_pol_interp = Interpolate2DCubic(fiesta.r_vec, fiesta.z_vec, b_pol)

    r_div = []
    r_div_above = []
    r_div_below = []
    flux_expansion = []
    for point in x_axis_omp:
        # Evaluate which flux surface the point at the OMP is on
        psi_n = psi_n_interp(point, 0)

        # Evaluate the corresponding point at the divertor
        r_mid = _shooting_algorithm(divertor_x, psi_n_interp,
                                    divertor_polyfit, psi_n, location=location)

        # Evaluate the corresponding point just above the divertor (for
        # calculating the angle of incidence)
        r_above = _shooting_algorithm(divertor_x, psi_n_interp,
                                      divertor_polyfit_above, psi_n, location=location)

        # Evaluate the corresponding point just below the divertor (for
        # calculating the angle of incidence)
        r_below = _shooting_algorithm(divertor_x, psi_n_interp,
                                      divertor_polyfit_below, psi_n, location=location)

        # Calculate the flux expansion
        f_x = _flux_expansion(b_pol_interp, [point, 0],
                              [r_mid, divertor_polyfit(r_mid)])

        r_div.append(r_mid)
        r_div_above.append(r_above)
        r_div_below.append(r_below)
        flux_expansion.append(f_x)

    r_div = np.array(r_div)
    r_div_above = np.array(r_div_above)
    r_div_below = np.array(r_div_below)
    flux_expansion = np.array(flux_expansion)

    # Determine the vectors at each of the corresponding points at the divertor
    v_1_x = r_div_above - r_div_below
    v_1_y = divertor_polyfit_above(r_div_above) - divertor_polyfit_below(r_div_below)
    v_1_vecs = np.array([v_1_x, v_1_y]).T
    # Determine the divertor vector
    v_2 = np.array([divertor_x[1] - divertor_x[0], divertor_y[1] - divertor_y[0]])

    # Calculate the angle between the vectors and thus the angle of incidence
    # defined as the positive angle with respect to the surface normal of the
    # divertor
    angles = _calculate_angles(v_1_vecs, v_2)

    divertor_map = {}
    for i in range(len(r_div)):
        temp_dict = {}
        temp_dict["R_pos"] = r_div[i]
        temp_dict["Z_pos"] = divertor_polyfit(r_div[i])
        temp_dict["alpha"] = angles[i]
        temp_dict["f_x"] = flux_expansion[i]
        divertor_map[x_axis_omp[i]] = temp_dict

    return divertor_map
