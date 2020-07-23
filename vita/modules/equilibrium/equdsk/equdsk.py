#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 09:53:55 2019

Addapted from: ReadEQDSK

Original AUTHOR: Leonardo Pigatto
Maintainer: jmbols

DESCRIPTION
Python function to read EQDSK files

CALLING SEQUENCE
out = ReadEQDSK(in_filename)

CHANGE HISTORY:
-started on 29/09/2015 - porting from Matlab
-16/10/2015 - generators introduced for reading input file
-06/2017 - modified to work with Python 3
-09/2017 - changes applied to version in /local/lib
-02/2018 - added  backwards compatibility with python 2
-15/07/2020 - changed to comply with PEP8
NOTES:

"""
try:
    import builtins                  # <- python 3
except ImportError:
    import __builtin__ as builtins   # <- python 2.

import re
from itertools import islice
import numpy as np
import matplotlib.pyplot as plt
#from pyTokamak.formats.geqdsk import file_numbers,file_tokens

# Other imports
from vita.modules.utils import intersection

class Equdsk():
    '''
    Class docsting
    '''
    def __init__(self, in_filename):
        self.comment = None # info about run
        self.switch = None
        self.nr_box = None # presumably the number of radial points
        self.nz_box = None # presumably the number of vertical points
        self.r_box_length = None
        self.z_box_length = None
        self.r0_exp = None
        self.r_box_left = None # presumably the position of the left of the box
        self.z_mid = None # presumably the position of the midplane
        self.r_axis = None
        self.z_axis = None
        self.psi_axis = None
        self.psi_edge = None
        self.b0_exp = None # presumably the magnetic field strength at the centre
        self.i_p = None # presumably plasma current
        self.T = None # poloidal flux function
        self.plasma_p = None # plasma pressure
        self.TTprime = None
        self.pprime = None
        self.psi = None # presumably the psi-map
        self.q = None
        self.n_lcfs = None # number of points for the LCFS boundary
        self.n_limits = None # number of points for the limiter boundary
        self.r_lcfs = None
        self.z_lcfs = None
        self.r_limits = None # radial limiter points
        self.z_limits = None # poloidal limiter points
        self.r_grid = None
        self.r_vec = None
        self.z_grid = None
        self.z_vec = None
        self.psi_grid = None
        self.rho_psi = None

        self.psi_n = None
        self.b_r = None
        self.b_z = None
        self.b_z = None

        self.read_eqdsk(in_filename)

    def read_eqdsk(self, in_filename):
        '''
        Function for reading the equdsk variables given a filename

        Parameters
        ----------
        in_filename : string
            A string with the equdsk filename to load

        Raises
        ------
        IOError
            Raises error if the array is not loaded.

        Returns
        -------
        None
        '''

        fin = open(in_filename, "r")

        desc = fin.readline()
        data = desc.split()
        self.switch = int(data[-3])
        self.nr_box = int(data[-2])
        self.nz_box = int(data[-1])
        self.comment = data[0:-3]

        token = file_numbers(fin)

        #first line
        self.r_box_length = float(token.__next__())
        self.z_box_length = float(token.__next__())
        self.r0_exp = float(token.__next__())
        self.r_box_left = float(token.__next__())
        self.z_mid = float(token.__next__()) #(maxygrid+minygrid)/2

        #second line
        self.r_axis = float(token.__next__())
        self.z_axis = float(token.__next__())
        self.psi_axis = float(token.__next__()) # psi_axis-psi_edge
        self.psi_edge = float(token.__next__()) # psi_edge-psi_edge (=0)
        self.b0_exp = float(token.__next__()) # normalizing magnetic field in chease

        #third line
        #ip is first element, all others are already stored
        self.i_p = float(token.__next__())

        """ DEFINING USEFUL FUNCTIONS TO READ ARRAYS """
        def consume(iterator, n):
        		#Advance iterator n steps ahead
            next(islice(iterator, n, n), None)

        def read_array(n, name="Unknown"):
            data = np.zeros([n])
            try:
                for i in np.arange(n):
                    data[i] = float(token.__next__())
            except:
                raise IOError("Failed reading array '"+name+"' of size ", n)
            return data

        def read_2d(nr, nz, name="Unknown"):
            data = np.zeros([nr, nz])
            for i in np.arange(nr):
                data[i, :] = read_array(nz, name+"["+str(i)+"]")
            return data

        #fourth line - nothing or already stored
        #advance to next significant token
        consume(token, 9)

        #T (or T - poloidal flux function)
        self.T = read_array(self.nr_box, "T")

        #p (pressure)
        self.plasma_p = read_array(self.nr_box, "p")

        #TT'
        self.TTprime = read_array(self.nr_box, "TTprime")

        #p'
        self.pprime = read_array(self.nr_box, "pprime")

        #psi
        self.psi = read_2d(self.nr_box, self.nz_box, "psi")

        #q safety factor
        self.q = read_array(self.nr_box, "safety_factor")

        #n of points for the lcfs and limiter boundary
        self.n_lcfs = int(token.__next__())
        self.n_limits = int(token.__next__())

        #rz lcfs coordinates
        if self.n_lcfs > 0:
            self.r_lcfs = np.zeros([self.n_lcfs])
            self.z_lcfs = np.zeros([self.n_lcfs])
            for i in range(self.n_lcfs):
                self.r_lcfs[i] = float(token.__next__())
                self.z_lcfs[i] = float(token.__next__())
        else:
            self.r_lcfs = [0]
            self.z_lcfs = [0]

        	#rz limits
        if self.n_limits > 0:
            self.r_limits = np.zeros([self.n_limits])
            self.z_limits = np.zeros([self.n_limits])
            for i in range(self.n_limits):
                self.r_limits[i] = float(token.__next__())
                self.z_limits[i] = float(token.__next__())
        else:
            self.r_limits = [0]
            self.z_limits = [0]

        # construct r-z mesh
        self.r_grid = np.zeros([self.nr_box, self.nz_box])
        self.z_grid = self.r_grid.copy()
        for i in range(self.nr_box):
            self.r_grid[i, :] = self.r_box_left + self.r_box_length*i/float(self.nr_box-1)
        for j in range(self.nz_box):
            self.z_grid[:, j] = (self.z_mid-0.5*self.z_box_length)\
                + self.z_box_length*j/float(self.nz_box-1)

        self.r_vec = self.r_grid[:, 0]
        self.z_vec = self.z_grid[0, :]

        #psi grid for radial prifiles
        self.psi_grid = np.linspace(self.psi_axis, self.psi_edge, self.nr_box)

        #corresponding s=sqrt(psi_bar)
        self.rho_psi = np.sqrt(abs(self.psi_grid-self.psi_axis)/abs(self.psi_edge-self.psi_axis))

        self.psi_n = self.psi/self.psi_edge

        # self.b_r = 1./self.r_vec*self.TTprime

        fin.close()

    def get_midplane_lcfs(self, psi_p=1.0001):
        '''
        Function for getting the inner and outer radial position of the LCFS at the midplane

        input: self,  a reference to the object itself
               psi_p, the flux surface of the LCFS, standard is psi_p = 1.005
               (otherwise the field-line is located inside the LCFS)

        return: Rcross, a list with the outer and inner radial position of the mid-plane LCFS
        '''

        r_vec, z_vec = self.r_grid, self.z_grid
        # Get contour
        cont = plt.contour(r_vec, z_vec, self.psi_n, [psi_p])
        cont = cont.allsegs[0]

        # Loop over the contours
        if len(cont) > 1:
            r_lcfs = []
        for c_i in cont:
            is_core = any(c_i[:, 1] > 0)*any(c_i[:, 1] < 0)
            if is_core:
                func1 = np.array((c_i[:, 0], c_i[:, 1]))
                func2 = np.array((np.array([0., np.max(r_vec)]), np.array([0., 0.])))
                (_, _), (r_lcfs_int, _) = intersection(func1, func2)
                if len(cont) > 1:
                    r_lcfs.append(r_lcfs_int[0])
                else:
                    r_lcfs = r_lcfs_int
        r_lcfs = np.array(r_lcfs)

        plt.close() # plt.contour opens a plot, close it

        return r_lcfs

def file_numbers(fp):
    """Generator to get numbers from a text file"""
    toklist = []
    while True:
        line = fp.readline()
        if not line:
            break
		# Match numbers in the line using regular expression
        pattern = r'[+-]?\d*[\.]?\d+(?:[Ee][+-]?\d+)?'
        toklist = re.findall(pattern, line)
        for tok in toklist:
            yield tok
