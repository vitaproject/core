#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 11:34:55 2019

@author: jeppe olsen

Based on a MatLab script by Douglas Schwarz found at
"https://se.mathworks.com/matlabcentral/fileexchange/11837-fast-and-robust-curve-intersections"
"""
import numpy as np
import matplotlib.pyplot as plt

def _get_rectangle_intersections(func1, func2):
    '''
    Function dividing two functions of [x,y] coordinates into rectangles
    corresponding to the number of elements in each function and evaluating
    the indices where the rectangles intersect.

    input: func1, a numpy array with the two numpy arrays corresponding to x and y
                  for the first function
           func2, a numpy array with the two numpy arrays corresponding to x and y
                  for the second function

    return: (i, j), a tuple where
                    i is a numpy array with the indices for the
                    intersections in the first function and
                    j is a numpy array with the indices for the
                    intersections in the second function
    '''
    x_1 = np.ma.array(func1[0, :], mask=np.isnan(func1[0, :]))
    y_1 = np.ma.array(func1[1, :], mask=np.isnan(func1[1, :]))
    x_2 = np.ma.array(func2[0, :], mask=np.isnan(func2[0, :]))
    y_2 = np.ma.array(func2[1, :], mask=np.isnan(func2[1, :]))

    n_1 = len(x_1)-1
    n_2 = len(x_2)-1

    if n_1 >= n_2:
        x1_segment = np.c_[x_1[:-1], x_1[1:]]
        y1_segment = np.c_[y_1[:-1], y_1[1:]]
        intersect_fun1 = []
        intersect_fun2 = []
        min_x1 = x1_segment.min(axis=1)
        max_x1 = x1_segment.max(axis=1)
        min_y1 = y1_segment.min(axis=1)
        max_y1 = y1_segment.max(axis=1)
        for k in range(n_2):
            k_1 = k + 1
            intersect = np.where(\
                                 (min_x1 <= max(x_2[k], x_2[k_1]))\
                                 & (max_x1 >= min(x_2[k], x_2[k_1]))\
                                 & (min_y1 <= max(y_2[k], y_2[k_1]))\
                                 & (max_y1 >= min(y_2[k], y_2[k_1])))
            intersect = np.array(intersect)
            if intersect.size != 0:
                intersect_fun1.append(intersect[0])
                intersect_fun2.append(np.repeat(k, len(intersect[0])))

        if (len(intersect_fun1) and len(intersect_fun2)) > 0:
            i = np.array(np.concatenate(intersect_fun1))
            j = np.array(np.concatenate(intersect_fun2))
        else:
            i = np.array([])
            j = np.array([])
    else:
        x2_segment = np.c_[x_2[:-1], x_2[1:]]
        y2_segment = np.c_[y_2[:-1], y_2[1:]]
        intersect_fun1 = []
        intersect_fun2 = []
        min_x2 = x2_segment.min(axis=1)
        max_x2 = x2_segment.max(axis=1)
        min_y2 = y2_segment.min(axis=1)
        max_y2 = y2_segment.max(axis=1)
        for k in range(n_1):
            k_1 = k + 1
            intersect = np.where(\
                                 (min_x2 <= max(x_1[k], x_1[k_1]))\
                                 & (max_x2 >= min(x_1[k], x_1[k_1]))\
                                 & (min_y2 <= max(y_1[k], y_1[k_1]))\
                                 & (max_y2 >= min(y_1[k], y_1[k_1])))
            intersect = np.array(intersect)
            if intersect.size != 0:
                intersect_fun2.append(intersect[0])
                intersect_fun1.append(np.repeat(k, len(intersect[0])))

        if (len(intersect_fun1) and len(intersect_fun2)) > 0:
            i = np.array(np.concatenate(intersect_fun1))
            j = np.array(np.concatenate(intersect_fun2))
        else:
            i = np.array([])
            j = np.array([])

    return (i, j)

def intersection(func1, func2, robust=True):
    '''
    Function for calculated the intersection between two curves.
    Computes the (x,y) locations where two curves intersect.

    The theory is;
    Given two line segments, L1 and L2,

    with L1 endpoints:  (x1(1),y1(1)) and (x1(2),y1(2))
    and  L2 endpoints:  (x2(1),y2(1)) and (x2(2),y2(2))

    we can write four equations with four unknowns and then solve them.  The
    four unknowns are t1, t2, x0 and y0, where (x0,y0) is the intersection of
    L1 and L2, t1 is the distance from the starting point of L1 to the
    intersection relative to the length of L1 and t2 is the distance from the
    starting point of L2 to the intersection relative to the length of L2.
    So, the four equations are

        (x1(2) - x1(1))*t1 = x0 - x1(1)
        (x2(2) - x2(1))*t2 = x0 - x2(1)
        (y1(2) - y1(1))*t1 = y0 - y1(1)
        (y2(2) - y2(1))*t2 = y0 - y2(1)

    Rearranging and writing in matrix form gives

        [x1(2)-x1(1)       0       -1   0;      [t1;      [-x1(1);
              0       x2(2)-x2(1)  -1   0;   *   t2;   =   -x2(1);
         y1(2)-y1(1)       0        0  -1;       x0;       -y1(1);
              0       y2(2)-y2(1)   0  -1]       y0]       -y2(1)]

    Let's call that A*T = B.  We can solve for T with T = A\B.

    Once we have our solution we just have to look at t1 and t2 to determine
    whether L1 and L2 intersect.  If 0 <= t1 < 1 and 0 <= t2 < 1 then the two
    line segments cross and we can include (x0,y0) in the output.

    To avoid having to do this for every line segment, it is checked if the line
    segments can possibly intersect by dividing line segments into rectangles
    and testing for an overlap between the triangles.

    input: func1, a numpy array with the two numpy arrays corresponding to x and y
                  for the first function
           func2, a numpy array with the two numpy arrays corresponding to x and y
                  for the second function

    return: i,    a numpy array of floats with the sum of the indices and distances
                  [0; 1[ to the intersections of func1
            j,    a numpy array of floats with the sum of the indices and distances
                  [0; 1[ to the intersections of func2
            x0,   a numpy array with the x positions of the intersections
            y0,   a numpy array with the y positions of the intersections
    '''
    (i, j) = _get_rectangle_intersections(func1, func2)

    if not i.size == 0:
        x_1 = func1[0, :]
        y_1 = func1[1, :]
        x_2 = func2[0, :]
        y_2 = func2[1, :]

        dxy1 = np.diff(np.c_[x_1, y_1], axis=0)
        dxy2 = np.diff(np.c_[x_2, y_2], axis=0)

        remove = np.isfinite(np.sum(dxy1[i, :] + dxy2[j, :], axis=1))
        i = i[remove]
        j = j[remove]

        n_intersect = len(i)
        vector_t = np.zeros((4, n_intersect))
        matrix_a = np.zeros((4, 4, n_intersect))
        matrix_a[0:2, 2, :] = -1
        matrix_a[2:4, 3, :] = -1
        matrix_a[0::2, 0, :] = dxy1[i, :].T
        matrix_a[1::2, 1, :] = dxy2[j, :].T

        vector_b = np.zeros((4, n_intersect))
        vector_b[0, :] = -x_1[i].ravel()
        vector_b[1, :] = -x_2[j].ravel()
        vector_b[2, :] = -y_1[i].ravel()
        vector_b[3, :] = -y_2[j].ravel()

        if robust:
            overlap = np.zeros((n_intersect), dtype=bool)
            for k in range(n_intersect):
                try:
                    vector_t[:, k] = np.linalg.solve(matrix_a[:, :, k], vector_b[:, k])
                except:
                    vector_t[1, k] = np.nan
                    eps = np.finfo(float).eps
                    condition_matrix = []
                    condition_matrix.append(dxy1[i[k], :])
                    condition_matrix.append(func2[:, j[k]]-func1[:, j[k]])
                    condition_matrix = np.array(condition_matrix)
                    overlap[k] = 1./np.linalg.cond(condition_matrix) < eps

            in_range = (vector_t[0, :] >= 0) & (vector_t[1, :] >= 0)\
                        & (vector_t[0, :] <= 1) & (vector_t[1, :] <= 1)

            if np.any(overlap):
                i_a = i[overlap]
                j_a = j[overlap]
                # set x0 and y0 to middle of overlapping region.
                vector_t[2, overlap] = (np.max(
                    (np.min((x_1[i_a], x_1[i_a+1]), axis=0),
                     np.min((x_2[j_a], x_2[j_a+1]), axis=0)), axis=0)
                                        + np.min(
                                            (np.max((x_1[i_a], x_1[i_a+1]), axis=0),
                                             np.max((x_2[j_a], x_2[j_a+1]), axis=0)), axis=0)
                                        )/2
                vector_t[3, overlap] = (np.max(
                    (np.min((y_1[i_a], y_1[i_a+1]), axis=0),
                     np.min((y_2[j_a], y_2[j_a+1]), axis=0)), axis=0)
                                        + np.min(
                                            (np.max((y_1[i_a], y_1[i_a+1]), axis=0),
                                             np.max((y_2[j_a], y_2[j_a+1]), axis=0)), axis=0)
                                        )/2
                selected = in_range | overlap
            else:
                selected = in_range
            xy0 = vector_t[2:, selected]
        else:
            for k in range(n_intersect):
                try:
                    vector_t[:, k] = np.linalg.solve(matrix_a[:, :, k], vector_b[:, k])
                except:
                    vector_t[:, k] = np.nan
            in_range = (vector_t[0, :] >= 0) & (vector_t[1, :] >= 0)\
                        & (vector_t[0, :] <= 1) & (vector_t[1, :] <= 1)
            xy0 = vector_t[2:, in_range]

        i = i[in_range] + vector_t[0, in_range]
        j = j[in_range] + vector_t[1, in_range]
        xy0 = xy0.T
        x_0 = xy0[:, 0]
        y_0 = xy0[:, 1]

        if not x_0.size == 0 or not y_0.size == 0:
            return (i, j), (x_0, y_0)

        print("Warning: Curves do not overlap")
        return (np.nan, np.nan), (np.nan, np.nan)
    else:
        print("Warning: Curves do not overlap")
        return (np.nan, np.nan), (np.nan, np.nan)


if __name__ == '__main__':

    # a piece of a prolate cycloid, and am going to find
    A, B = 1, 2
    PHI_1 = np.linspace(3, 10, 1000)
    PHI_2 = np.linspace(3, 10, 2000)
    X_1 = A*PHI_1 - B*np.sin(PHI_1)
    Y_1 = A - B*np.cos(PHI_1)

    X_2 = A*PHI_1 - B*np.sin(PHI_1) + 0.1
    Y_2 = A - B*np.cos(PHI_1)
#    x2=phi2
#    y2=np.sin(phi2)+2
    FUNC_1 = np.array([X_1, Y_1])
    FUNC_2 = np.array([X_2, Y_2])
    (I, J), (X, Y) = intersection(FUNC_1, FUNC_2, False)
    plt.plot(X_1, Y_1, c='r')
    plt.plot(X_2, Y_2, c='g')
    plt.plot(X, Y, '*k')
    plt.show()
