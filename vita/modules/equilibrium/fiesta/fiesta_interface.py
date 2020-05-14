#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 09:53:55 2019

@author: jmbols
"""
from matplotlib import pyplot as plt
import numpy as np
import scipy.io as sio
# Other imports
from vita.modules.utils import intersection


class Fiesta():
    '''
    Class for tracing the magnetic field lines given a FIESTA equlibrium

    :param str filename: the path to the FIESTA MATLAB save file.

    :ivar VectorFunction3D b_field: A 3D vector function of the magnetic field.

    member functions:
    '''
    def __init__(self, filename):
        self.filename = filename
        self.read_fiesta_model()

    @property
    def b_field(self):
        """
        Function for getting the magnetic a 3D vector function of the magnetic
        field
        """

        try:
            from vita.modules.projection.cherab import MagneticField
        except ImportError:
            raise RuntimeError("CHERAB integration not installed.")

        return MagneticField(self.r_vec, self.z_vec,
                             np.swapaxes(self.b_r, 0, 1), np.swapaxes(self.b_z, 0, 1),
                             np.swapaxes(self.b_phi, 0, 1))

    def read_fiesta_model(self):
        '''
        Function for reading the FIESTA equilibrium data from a .mat file

        input: self, a reference the object itself

        output: self.r_limiter, a numpy array with the radial coordinates of the vessel limits
                self.z_limiter, a numpy array with the vertical coordinates of the vessel limits
                self.r_vec,     a numpy array with the radial grid coordinates
                self.z_vec,     a numpy array with the vertical grid coordinates
                self.psi_n,
                self.b_r,       a numpy array with the radial magnetic field component
                self.b_z        a numpy array with the vertical field component
                self.b_phi,     a numpy array with the toroidal field component
                self.b_theta,   a numpy array with the poloidal magnetic field component
                self.i_rod      a float with the current in the rod
        '''
        # Read data from .mat file
        mat = sio.loadmat(self.filename, mat_dtype=True, squeeze_me=True)

        # Get vessel limits
        self.r_limiter = mat['R_limits']
        self.z_limiter = mat['Z_limits']

        # Get grid data
        self.r_vec = mat['r']
        self.z_vec = mat['z']

        # Get magnetic data
        self.psi = mat['psi']
        self.psi_n = mat['psi_n']
        self.psi_axis = mat['psi_a']
        self.psi_lcfs = mat['psi_b']
        self.mag_axis = mat['mag_axis']
        self.b_r = mat['Br']
        self.b_z = mat['Bz']
        self.b_phi = mat['Bphi']
        self.b_theta = mat['Btheta']
        self.b_vac_radius = mat['b_vacuum_radius']
        self.b_vac = mat['b_vacuum_magnitude']
        self.i_rod = mat['irod']
        self.x_points = mat['xpoints']
        self.f_profile = mat['f_profile']
        self.q_profile = mat['q_profile']
        self.lcfs_polygon = mat['lcfs_polygon']

    def get_midplane_lcfs(self, psi_p=1.005):
        '''
        Function for getting the inner and outer radial position of the LCFS at the midplane

        input: self,  a reference to the object itself
               psi_p, the flux surface of the LCFS, standard is psi_p = 1.005
               (otherwise the field-line is located inside the LCFS)

        return: Rcross, a list with the outer and inner radial position of the mid-plane LCFS
        '''

        r_vec, z_vec = np.meshgrid(self.r_vec, self.z_vec)
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

    def to_cherab_equilibrium(self):
        """
        Function for converting this Fiesta object to a CHERAB equilibrium.

        rtype: EFITEquilibrium
        """

        try:
            from raysect.core import Point2D
            from cherab.tools.equilibrium import EFITEquilibrium

        except ImportError:
            raise RuntimeError("CHERAB integration not installed.")

        r_vec = self.r_vec
        z_vec = self.z_vec
        psi = np.swapaxes(self.psi, 0, 1)
        psi_axis = self.psi_axis
        psi_lcfs = self.psi_lcfs
        magnetic_axis = Point2D(self.mag_axis[0], self.mag_axis[1])

        x_points = []
        for point in self.x_points:
            x_points.append(Point2D(point[0], point[1]))

        strike_points = []

        f_profile = self.f_profile
        q_profile = self.q_profile

        b_vacuum_radius = self.b_vac_radius
        b_vacuum_magnitude = self.b_vac

        lcfs_polygon = self.lcfs_polygon  # shape 2xM, indexing to remove duplicated point
        if np.all(lcfs_polygon[:, 0] == lcfs_polygon[:, -1]):
            lcfs_polygon = lcfs_polygon[:, 0:-1]

        limiter_polygon = np.array([self.r_limiter, self.z_limiter])  # 2xM

        time = 0.0

        equilibrium = EFITEquilibrium(r_vec, z_vec, psi, psi_axis, psi_lcfs,
                                      magnetic_axis, x_points, strike_points,
                                      f_profile, q_profile, b_vacuum_radius, b_vacuum_magnitude,
                                      lcfs_polygon, limiter_polygon, time)

        return equilibrium


if __name__ == '__main__':
    from vita.utility import get_resource

    #EQUIL = get_resource("ST40-IVC1", "equilibrium", "eq_006_2T_export")
    EQUIL = get_resource("ST40", "equilibrium", "limited_eq001_export")
    FIESTA_EQUIL = Fiesta(EQUIL)
    print(FIESTA_EQUIL.get_midplane_lcfs())
