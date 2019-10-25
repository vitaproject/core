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

def getRectangleIntersections(func1, func2):
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
    x1 = func1[0,:]
    y1 = func1[1,:]
    x2 = func2[0,:]
    y2 = func2[1,:]
    
    n1 = len(x1)-1
    n2 = len(x2)-1
    
    if n1 >= n2:
        x1_segment = np.c_[x1[:-1],x1[1:]]
        y1_segment = np.c_[y1[:-1],y1[1:]]
        intersect_fun1 = []
        intersect_fun2 = []
        min_x1 = x1_segment.min(axis=1)
        max_x1 = x1_segment.max(axis=1)
        min_y1 = y1_segment.min(axis=1)
        max_y1 = y1_segment.max(axis=1)
        for k in range(n2):
            k1 = k + 1
            intersect = np.where(\
                                 (min_x1 <= max(x2[k],x2[k1]))\
                                 & (max_x1 >= min(x2[k],x2[k1]))\
                                 & (min_y1 <= max(y2[k],y2[k1]))\
                                 & (max_y1 >= min(y2[k],y2[k1])))
            intersect = np.array(intersect)
            if intersect.size != 0:
                intersect_fun1.append(intersect[0])
                intersect_fun2.append(np.repeat(k,len(intersect[0])))

        if (len(intersect_fun1) and len(intersect_fun2))>0:
            i = np.concatenate(intersect_fun1)
            j = np.concatenate(intersect_fun2)
        else:
            i = []
            j = []
    else:
        x2_segment = np.c_[x2[:-1],x2[1:]]
        y2_segment = np.c_[y2[:-1],y2[1:]]
        intersect_fun1 = []
        intersect_fun2 = []
        min_x2 = x2_segment.min(axis=1)
        max_x2 = x2_segment.max(axis=1)
        min_y2 = y2_segment.min(axis=1)
        max_y2 = y2_segment.max(axis=1)
        for k in range(n1):
            k1 = k + 1
            intersect = np.where(\
                                 (min_x2 <= max(x1[k],x1[k1]))\
                                 & (max_x2 >= min(x1[k],x1[k1]))\
                                 & (min_y2 <= max(y1[k],y1[k1]))\
                                 & (max_y2 >= min(y1[k],y1[k1])))
            intersect = np.array(intersect)
            if intersect.size != 0:
                intersect_fun2.append(intersect[0])
                intersect_fun1.append(np.repeat(k,len(intersect[0])))
        
        if (len(intersect_fun1) and len(intersect_fun2))>0:
            i = np.concatenate(intersect_fun1) 
            j = np.concatenate(intersect_fun2)       
        else:
            i = []
            j = []

    return (i,j)

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
            
    return: 
    '''
    (i, j) = getRectangleIntersections(func1,func2)
    
    if len(i)>0:
        x1 = func1[0,:]
        y1 = func1[1,:]
        x2 = func2[0,:]
        y2 = func2[1,:]
    
        dxy1=np.diff(np.c_[x1,y1],axis=0)
        dxy2=np.diff(np.c_[x2,y2],axis=0)
        
        remove = np.isfinite(np.sum(dxy1[i,:] + dxy2[j,:],axis=1))
        i = i[remove]
        j = j[remove]

        n = len(i)
        T = np.zeros((4, n))
        A = np.zeros((4, 4, n))
        A[0:2, 2, :] = -1
        A[2:4, 3, :] = -1
        A[0::2, 0, :] = dxy1[i, :].T
        A[1::2, 1, :] = dxy2[j, :].T
    
        B=np.zeros((4,n))
        B[0, :] = -x1[i].ravel()
        B[1, :] = -x2[j].ravel()
        B[2, :] = -y1[i].ravel()
        B[3, :] = -y2[j].ravel()
        
        if robust:
            overlap = np.zeros((n), dtype=bool)
            for ii in range(n):
                try:
                    T[:,ii]=np.linalg.solve(A[:,:,ii],B[:,ii])
                except:
                    T[1,ii]=np.nan
                    eps = np.finfo(float).eps
                    g = []
                    g.append(dxy1[i[ii],:])
                    g.append(func2[:,j[ii]]-func1[:,j[ii]])
                    g = np.array(g)
                    overlap[ii] = 1./np.linalg.cond(g) < eps

            in_range = (T[0,:] >=0) & (T[1,:] >=0) & (T[0,:] <=1) & (T[1,:] <=1)
        
            if np.any(overlap):
                ia = i[overlap];
                ja = j[overlap];
                # set x0 and y0 to middle of overlapping region.
                T[2,overlap] = (np.max(
                                       (np.min((x1[ia],x1[ia+1]),axis=0),
                                        np.min((x2[ja],x2[ja+1]),axis=0)),axis=0) 
                                + np.min(
                                       (np.max((x1[ia],x1[ia+1]),axis=0),
                                        np.max((x2[ja],x2[ja+1]),axis=0)),axis=0)
                                )/2
                T[3,overlap] = (np.max(
                                       (np.min((y1[ia],y1[ia+1]),axis=0),
                                        np.min((y2[ja],y2[ja+1]),axis=0)),axis=0)
                                + np.min(
                                       (np.max((y1[ia],y1[ia+1]),axis=0),
                                        np.max((y2[ja],y2[ja+1]),axis=0)),axis=0)
                                )/2
                selected = in_range | overlap
            else:
                selected = in_range;
            xy0=T[2:,selected]
        else:
             for ii in range(n):
                try:
                    T[:,ii]=np.linalg.solve(A[:,:,ii],B[:,ii])
                except:
                    T[:,ii]=np.nan
             in_range= (T[0,:] >=0) & (T[1,:] >=0) & (T[0,:] <=1) & (T[1,:] <=1)
             xy0=T[2:,in_range]

        xy0=xy0.T
        return xy0[:,0],xy0[:,1]
    else:
        print("Warning: Curves do not overlap")
        return np.nan, np.nan


if __name__ == '__main__':

    # a piece of a prolate cycloid, and am going to find
    a, b = 1, 2
    phi1 = np.linspace(3, 10, 1000)
    phi2 = np.linspace(3, 10, 2000)
    x1 = a*phi1 - b*np.sin(phi1)
    y1 = a - b*np.cos(phi1)
    
    
    x2=a*phi1 - b*np.sin(phi1)
    y2= a - b*np.cos(phi1) + 0.1
#    x2=phi2
#    y2=np.sin(phi2)+2
    func1 = np.array([x1, y1])
    func2 = np.array([x2, y2])
    x,y=intersection(func1,func2,False)
    plt.plot(x1,y1,c='r')
    plt.plot(x2,y2,c='g')
    plt.plot(x,y,'*k')
    plt.show()