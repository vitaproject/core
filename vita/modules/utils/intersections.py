#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 11:34:55 2019

@author: jeppe olsen

Based on:
Sukhbinder
5 April 2017
https://github.com/sukhbinder/intersection
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
        X1 = np.c_[x1[:-1],x1[1:]]
        Y1 = np.c_[y1[:-1],y1[1:]]
        ij1 = []
        ij2 = []
        min_x1 = X1.min(axis=1)
        max_x1 = X1.max(axis=1)
        min_y1 = Y1.min(axis=1)
        max_y1 = Y1.max(axis=1)
        for k in range(n2):
            k1 = k + 1
            intersect = np.where(\
                                 (min_x1 <= max(x2[k],x2[k1]))\
                                 & (max_x1 >= min(x2[k],x2[k1]))\
                                 & (min_y1 <= max(y2[k],y2[k1]))\
                                 & (max_y1 >= min(y2[k],y2[k1])))
            intersect = np.array(intersect)
            if intersect.size != 0:
                ij1.append(intersect[0])
                ij2.append(np.repeat(k,len(intersect[0])))

        if (len(ij1) and len(ij2))>0:
            i = np.concatenate(ij1)
            j = np.concatenate(ij2)
        else:
            i = []
            j = []
    else:
        X2 = np.c_[x2[:-1],x2[1:]]
        Y2 = np.c_[y2[:-1],y2[1:]]
        ij1 = []
        ij2 = []
        min_x2 = X2.min(axis=1)
        max_x2 = X2.max(axis=1)
        min_y2 = Y2.min(axis=1)
        max_y2 = Y2.max(axis=1)
        for k in range(n1):
            k1 = k + 1
            intersect = np.where(\
                                 (min_x2 <= max(x1[k],x1[k1]))\
                                 & (max_x2 >= min(x1[k],x1[k1]))\
                                 & (min_y2 <= max(y1[k],y1[k1]))\
                                 & (max_y2 >= min(y1[k],y1[k1])))
            intersect = np.array(intersect)
            if intersect.size != 0:
                ij1.append(intersect[0])
                ij2.append(np.repeat(k,len(intersect[0])))
        
        if (len(ij1) and len(ij2))>0:
            i = np.concatenate(ij2) 
            j = np.concatenate(ij1)       
        else:
            i = []
            j = []

    return (i,j)

def intersection(func1,func2):
    """
    Function for calculated the intersection between two curves.
    Computes the (x,y) locations where two curves intersect.
    
    
    """
    (i, j) = getRectangleIntersections(func1,func2)
    
    if len(i)>0:
        x1 = func1[0,:]
        y1 = func1[1,:]
        x2 = func2[0,:]
        y2 = func2[1,:]
    
        dxy1=np.diff(np.c_[x1,y1],axis=0)
        dxy2=np.diff(np.c_[x2,y2],axis=0)
        
        remove = np.isfinite(np.sum(dxy1[i,:] + dxy2[j,:],axis=1)) | np.array(j <= i + 1)
        i = i[remove]
        j = j[remove]

        n = len(i)    
        T = np.zeros((4, n))
        AA = np.zeros((4, 4, n))
        AA[0:2, 2, :] = -1
        AA[2:4, 3, :] = -1
        AA[0::2, 0, :] = dxy1[i, :].T
        AA[1::2, 1, :] = dxy2[j, :].T
    
        BB=np.zeros((4,n))
        BB[0, :] = -x1[i].ravel()
        BB[1, :] = -x2[j].ravel()
        BB[2, :] = -y1[i].ravel()
        BB[3, :] = -y2[j].ravel()
    
        for ii in range(n):
            try:
                T[:,ii]=np.linalg.solve(AA[:,:,ii],BB[:,ii])
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
    phi1 = np.linspace(3, 10, 2000)
    phi2 = np.linspace(3, 10, 2000)
    x1 = a*phi1 - b*np.sin(phi1)
    y1 = a - b*np.cos(phi1)
    
    
    x2=a*phi1 - b*np.sin(phi1)
    y2= a - b*np.cos(phi1)
#    x2=phi2
#    y2=np.sin(phi2)+2
    func1 = np.array([x1, y1])
    func2 = np.array([x2, y2])
    x,y=intersection(func1,func2)
    plt.plot(x1,y1,c='r')
    plt.plot(x2,y2,c='g')
    plt.plot(x,y,'*k')
    plt.show()