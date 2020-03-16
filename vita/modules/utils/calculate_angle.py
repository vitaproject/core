#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 10:05:02 2020

@author: jmbols
"""
import numpy as np

def calculate_angle(v_1, v_2):
    '''
    Function for calculating the angle with respect to the normal of v_1
    between two vectors.

    Parameters
    ----------
    v_1_vectors : 2-x-1 np.array
        2D vector of the form (x, y)
    v_2 : 2-x-1 np.array
        2D vector of the form (x, y)

    Returns
    -------
    angle : float
        The angle between the two vectors

    '''

    def _angle(v_1, v_2):
        '''
        Calculate the angle between two vectors defined as:

            cos(angle) = (v_1 dot v_2)/(||v_1|| * ||v_2||),

        where ||v|| is the length of the vector.

        Parameters
        ----------
        v_1 : 2-x-1 np.array
            Array with x and y of the first vector
        v_2 : 2-x-1 np.array
            Array with x and y of the second vector

        Returns
        -------
        angle : float
            A float with the angle between the two vectors

        '''
        return np.arccos(np.dot(v_1, v_2)/\
                         (np.sqrt(np.dot(v_1, v_1))*np.sqrt(np.dot(v_2, v_2))))

    alpha_s = _angle(v_1, v_2)
    if alpha_s < np.pi/2.:
        alpha_i = np.pi/2. - alpha_s
    else:
        alpha_i = alpha_s - np.pi/2.

    return alpha_i
