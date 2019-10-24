#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 09:53:55 2019

@author: jmbols
"""

from scipy.integrate import solve_ivp
from scipy.interpolate import interp2d
from scipy.constants import mu_0 as mu0
from matplotlib import pyplot as plt
import numpy as np
import scipy.io as sio
# Other imports
from intersections import intersection

class FieldLines(object):
    '''
    Class for tracing the magnetic field lines given a FIESTA equlibrium
    
    member functions:
    '''
    def __init__(self, filename):
        self.filename = filename
        self.readFiestaModel()
        
    def readFiestaModel(self):
        '''
        Function for reading the FIESTA equilibrium data from a .mat file
        
        input: self, a reference the object itself
        
        output: self.R_limiter, the radial coordinates of the vessel limits
                self.Z_limiter, the vertical coordinates of the vessel limits
                self.r,         the radial grid coordinates
                self.z,         the vertical grid coordinates
                self.psi_n,     
        '''
        # Read data from .mat file
        mat = sio.loadmat(self.filename, mat_dtype=True, squeeze_me=True)
        
        # Get vessel limits
        self.R_limiter = mat['R_limits']
        self.Z_limiter = mat['Z_limits']
        
        # Get grid data
        self.r = mat['r']
        self.z = mat['z']
    
        # Get magnetic data
        self.psi_n = mat['psi_n']
        self.Br = mat['Br']
        self.Bz = mat['Bz']
        self.irod = mat['irod']
        
    def getMidplaneLCFS(self, psi_p=1.0):
        '''
        Function for getting the inner and outer radial position of the LCFS at the midplane
        
        input: self, a reference to the object itself
        
        return: Rcross, a list with the outer and inner radial position of the mid-plane LCFS
        '''
        
        R, Z = np.meshgrid(self.r, self.z)
        # Get contour
        cont = plt.contour(R, Z, self.psi_n, [psi_p])
        cont = cont.allsegs[0]

        # Loop over the contours
        for i in range(len(cont)):
            c_ = cont[i]
            is_core = any(c_[:,1]>0) * any(c_[:,1]<0)
            if is_core:
                Rcross, _, _, _ = intersection(c_[:,0],c_[:,1],np.array([0.,1.]),np.array([0.,0.]))

        return Rcross  
        
    def followFieldinPlane(self, p0, maxl=10.0, nr=2000, rtol=2e-10):
        '''
        Function following the magnetic field-lines given a starting point
        
        solves the set of coupled ODEs:
            
            d/dl R   = B_r / (|B|)
            d/dl phi = B_phi / (R |B|)
            d/dl Z   = B_z / (|B|),
            
        where B_r, B_phi, B_z are the cylindrical components of the magnetic field, |B| is the
        magnitude of the magnetic field, R, phi and Z are the cylindrical positions of the field line
        and l is the length along the magnetic field line
        
        input: self, the object parameters
               p0,   a tuple with the initial position of the field-line to be tracked
               maxl, a float with the maximum length of the field lines used for solving the set of ODE's
               nr,   an integer with the maximum number of radial points used when solving the ODE
               rtol, a float with the maximum relative error tolerance
            
        return: field_line, a dictionary with the R, phi and Z components along the field line
            
        use:
        '''
        
        def dXdl(l, x):
            '''
            The function describing the ode to solve in order to track the magnetic field lines
            
            input: l, np.array with the distance along the magnetic field-line
                   x, vector with the R, phi and Z initial positions
                
            return: dXdl_rhs, the right-hand side of the ode to solve
            '''
            R_init = x[0]
            Z_init = x[2]
            
            Br_interp = interp2d(self.r, self.z, self.Br)
            Bz_interp = interp2d(self.r, self.z, self.Bz)
            Br_init = Br_interp(R_init, Z_init)[0]
            Br_interp = None
            Bz_init = Bz_interp(R_init, Z_init)[0]
            Bz_interp = None
            Bphi_init = self.irod*mu0 / (2*np.pi*R_init)
            
            B_mag = np.sqrt(Br_init**2 + Bphi_init**2 + Bz_init**2)
            
            dXdl_rhs = np.zeros(3)
            dXdl_rhs[0] = Br_init / B_mag
            dXdl_rhs[1] = Bphi_init / (R_init * B_mag)
            dXdl_rhs[2] = Bz_init / B_mag
            
            return dXdl_rhs
            
        dist_along_fieldline = np.linspace(0.0, maxl, nr)
        
        X = solve_ivp(fun = dXdl, t_span = tuple([0.0, maxl]), y0 = p0, t_eval = dist_along_fieldline, rtol=rtol)
        
        field_line = {}
        field_line['l'] = np.array(X.t[:])
        field_line['R'] = X.y[0,:]
        field_line['phi'] = X.y[1,:]
        field_line['Z'] = X.y[2,:]
        
        return field_line


if __name__ == '__main__':
    filepath = '/home/jmbols/Postdoc/ST40/Programme 1/Equilibrium/eq001_limited.mat'
    field_line = FieldLines(filepath)
    p0 = [0.7,0,0]
    field_line_dict = field_line.followFieldinPlane(p0=p0, maxl=10.0)
    plt.plot(field_line_dict['R'],field_line_dict['Z'])
    
