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
import time


def getRectangleCorners(func1, func2):
    '''
    
    '''
    x1 = func1[0]
    y1 = func1[1]
    x2 = func2[0]
    y2 = func2[1]
    if n1 >= n2
		ijc = np.empty(1,n2);
		min_x1 = mvmin(x1);
		max_x1 = mvmax(x1);
		min_y1 = mvmin(y1);
		max_y1 = mvmax(y1);
		for k = 1:n2
			k1 = k + 1;
			ijc{k} = find( ...
				min_x1 <= max(x2(k),x2(k1)) & max_x1 >= min(x2(k),x2(k1)) & ...
				min_y1 <= max(y2(k),y2(k1)) & max_y1 >= min(y2(k),y2(k1)));
			ijc{k}(:,2) = k;
		end
		ij = vertcat(ijc{:});
		i = ij(:,1);
		j = ij(:,2);
	else
		% Curve 2 has more segments, loop over segments of curve 1.
		ijc = cell(1,n1);
		min_x2 = mvmin(x2);
		max_x2 = mvmax(x2);
		min_y2 = mvmin(y2);
		max_y2 = mvmax(y2);
		for k = 1:n1
			k1 = k + 1;
			ijc{k}(:,2) = find( ...
				min_x2 <= max(x1(k),x1(k1)) & max_x2 >= min(x1(k),x1(k1)) & ...
				min_y2 <= max(y1(k),y1(k1)) & max_y2 >= min(y1(k),y1(k1)));
			ijc{k}(:,1) = k;
		end
		ij = vertcat(ijc{:});
		i = ij(:,1);
		j = ij(:,2);
	end
    # Get number of rectangles for the two functions we are investigating
    x1 = func1[0,:]
    x2 = func2[0,:]
    y1 = func1[1,:]
    y2 = func2[1,:]
    
    n1 = len(x1)-1
    n2 = len(x2)-1
    
    # Get the line-segments of the rectangles
    X1 = np.c_[x1[:-1],x1[1:]]
    Y1 = np.c_[y1[:-1],y1[1:]]
    X2 = np.c_[x2[:-1],x2[1:]]
    Y2 = np.c_[y2[:-1],y2[1:]]
    
    # Sort the line segments to get the min and max values (functions are not 
    # necessarily monotonically increasing or decreasing) and ensure that
    # the two segments have the same number of elements
    S1 = np.tile(X1.min(axis=1),(n2,1)).T
    T1 = np.tile(Y1.min(axis=1),(n2,1)).T
    
    lower_left_corner_func1 = (S1, T1)
    S1 = None
    T1 = None
    
    S2 = np.tile(X2.max(axis=1),(n1,1))
    T2 = np.tile(Y2.max(axis=1),(n1,1))
    
    upper_right_corner_func2 = (S2, T2)
    S2 = None
    T2 = None
    
    S3 = np.tile(X1.max(axis=1),(n2,1)).T
    T3 = np.tile(Y1.max(axis=1),(n2,1)).T
    
    upper_right_corner_func1 = (S3, T3)
    S3 = None
    T3 = None
    
    S4 = np.tile(X2.min(axis=1),(n1,1))
    T4 = np.tile(Y2.min(axis=1),(n1,1))
    
    lower_left_corner_func2 = (S4, T4)
    S4 = None
    T4 = None
    
    rectangle_corners = {}
    rectangle_corners['lower_left_corner_func1'] = lower_left_corner_func1
    rectangle_corners['upper_right_corner_func1'] = upper_right_corner_func1
    rectangle_corners['lower_left_corner_func2'] = lower_left_corner_func2
    rectangle_corners['upper_right_corner_func2'] = upper_right_corner_func2
    
    return rectangle_corners

def _rectangle_intersection_(func1, func2):        
    
    rectangle_corners = getRectangleCorners(func1, func2)
    lower_left_corner_func1 = rectangle_corners['lower_left_corner_func1']
    upper_right_corner_func1 = rectangle_corners['upper_right_corner_func1']
    lower_left_corner_func2 = rectangle_corners['lower_left_corner_func2']
    upper_right_corner_func2 = rectangle_corners['upper_right_corner_func2']

    C1=np.less_equal(lower_left_corner_func1[0], upper_right_corner_func2[0])
    C2=np.greater_equal(upper_right_corner_func1[0], lower_left_corner_func2[0])
    C3=np.less_equal(lower_left_corner_func1[1], upper_right_corner_func2[1])
    C4=np.greater_equal(upper_right_corner_func1[1], lower_left_corner_func2[1])
    
    ii,jj=np.nonzero(C1 & C2 & C3 & C4)
    print(ii,jj)
    return ii,jj

def intersection(x1,y1,x2,y2):
    """
    INTERSECTIONS Intersections of curves.
    Computes the (x,y) locations where two curves intersect.  The curves
    can be broken with NaNs or have vertical segments.
    usage:
    x,y=intersection(x1,y1,x2,y2)
    Example:
    a, b = 1, 2
    phi = np.linspace(3, 10, 100)
    x1 = a*phi - b*np.sin(phi)
    y1 = a - b*np.cos(phi)
    x2=phi
    y2=np.sin(phi)+2
    x,y=intersection(x1,y1,x2,y2)
    plt.plot(x1,y1,c='r')
    plt.plot(x2,y2,c='g')
    plt.plot(x,y,'*k')
    plt.show()
    """
    func1 = np.array([x1,y1])
    func2 = np.array([x2,y2])
    ii,jj=_rectangle_intersection_(func1,func2)
    n=len(ii)

    dxy1=np.diff(np.c_[x1,y1],axis=0)
    dxy2=np.diff(np.c_[x2,y2],axis=0)

    T=np.zeros((4,n))
    AA=np.zeros((4,4,n))
    AA[0:2,2,:]=-1
    AA[2:4,3,:]=-1
    AA[0::2,0,:]=dxy1[ii,:].T
    AA[1::2,1,:]=dxy2[jj,:].T

    BB=np.zeros((4,n))
    BB[0,:]=-x1[ii].ravel()
    BB[1,:]=-x2[jj].ravel()
    BB[2,:]=-y1[ii].ravel()
    BB[3,:]=-y2[jj].ravel()

    for i in range(n):
        try:
            T[:,i]=np.linalg.solve(AA[:,:,i],BB[:,i])
        except:
            T[:,i]=np.NaN


    in_range= (T[0,:] >=0) & (T[1,:] >=0) & (T[0,:] <=1) & (T[1,:] <=1)

    xy0=T[2:,in_range]
    xy0=xy0.T
    return xy0[:,0],xy0[:,1]


if __name__ == '__main__':

    # a piece of a prolate cycloid, and am going to find
    a, b = 1, 2
    phi1 = np.linspace(3, 10, 2000)
    phi2 = np.linspace(3, 10, 100)
    x1 = a*phi1 - b*np.sin(phi1)
    y1 = a - b*np.cos(phi1)

    x2=phi2
    y2=np.sin(phi2)+2
    t_start = time.clock()
    x,y=intersection(x1,y1,x2,y2)
    print(time.clock() - t_start)
    plt.plot(x1,y1,c='r')
    plt.plot(x2,y2,c='g')
    plt.plot(x,y,'*k')
    plt.show()