# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 09:51:09 2019

@author: Daniel.Iglesias@tokamakenergy.co.uk
"""
import scipy.integrate as integrate
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from vita.modules.utils.getOption import getOption


class HeatLoad():
    '''
    Base function for storing heat flux profiles.

    Member functions:
        __call__(s) : integrate the heat-flux over s

        calculate_heat_flux_density
        set_coordinates(s_in)
        set_edge_radius(radius_in)
        get_local_coordinates()
        get_global_coordinates()
        calculate_heat_power()
        plot_heat_power_density()
    '''
    def __init__(self, r0_lfs=0., r0_hfs=0.):
        self.f_x = 1.  # edge radius at outboard equatorial midplane
        self.f_x_in_out = 1.  # edge radius at outboard equatorial midplane
        self.r0_hfs = r0_hfs  # edge radius at outboard equatorial midplane
        self.r0_lfs = r0_lfs  # edge radius at inboard equatorial midplane
        self._s = []  # equatorial midplane coordinate array
        self._q = []  # heat flux density profile
        self._total_power = 0.
        self.model_type = None
        self.s_disconnected_dn_max = 0.001
        self._s_disconnected_dn_inboard = 0.001
        self._interp_func = None

    def __call__(self, s):
        if not self._interp_func:

            if len(self._s) > 0 and len(self._q) > 0:
                self._interp_func = interp1d(self._s, self._q)
            else:
                raise RuntimeError("Heatflux model not evaluated yet.")

        return self._interp_func(s)

    def calculate_heat_flux_density(self):
        '''
        Function for calculating the heat flux profile. Needs to be implemented
        by the inhering class.

        Raises
        ------
        NotImplementedError

        Returns
        -------
        None.

        '''
        raise NotImplementedError("The inheriting class must implement this virtual function.")

    def set_coordinates(self, s_in):
        '''
        Function for setting the local coordinates.

        Parameters
        ----------
        s_in : list or 1-by-n numpy array
            array of local coordinates.

        Returns
        -------
        None.

        '''
        if self.model_type == "Eich":
            self._s = s_in
        else:
            print("Warning: The HeatFlux model in use does not allow setting coordinates")

    def set_edge_radius(self, radius_in):
        '''
        Function for setting the position of the high field side LCFS

        Parameters
        ----------
        radius_in : float
            position of the high field side LCFS.

        Returns
        -------
        None.

        '''
        self.r0_hfs = radius_in

    def get_local_coordinates(self):
        '''
        Function for getting the local coordinates

        Returns
        -------
        _s : list or 1-by-n numpy array
            An array with the local coordinates.

        '''
        return self._s

    def get_global_coordinates(self, location='lfs'):
        '''
        Function for getting the global coordinates, i.e. the local coordinates
        plus the position of the LCFS for the LFS and the position of the LCFS
        minus the local position on the HFS

        Returns
        -------
        _s_global : list or 1-by-n numpy array
            An array with the global coordinates.

        '''
        if location == 'lfs':
            _s_global = self._s + self.r0_lfs
        elif location == 'hfs':
            _s_global = self.r0_hfs - self._s
        else:
            raise NotImplementedError("Location not implemented. Please use 'lfs' or 'hfs'")
        return _s_global

    def calculate_heat_power(self):
        '''
        Function for calculating the integral of the power profile as a function
        of s

            heat_power = p_tot/(2*pi*(R_0+a)) = int_0^L_perp q(s) ds

        Returns
        -------
        heat_power : float
            The integral of the heat flux profile with respect to s

        '''
        self._total_power = integrate.simps(self._q, self._s)
        return self._total_power

    def plot_heat_power_density(self):
        '''
        Function for plotting the heat flux profile

        Returns
        -------
        None.

        '''
        plt.plot(self._s, self._q)
        plt.xlabel('$s$')
        plt.ylabel('$q(s)$')

        imageFile = getOption('imageFile')
        if imageFile :
          plt.savefig(imageFile)
        else :
          plt.show()

