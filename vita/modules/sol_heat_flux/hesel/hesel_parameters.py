#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 13:25:03 2018

@author: jmbols
"""
import numpy as np
import h5py
from vita.modules.utils.physics_constants import get_physics_constants

class HESELparams():
    '''
    Class for loading parameters from the HESEL .hdf5 file
    All parameters are in SI units unless otherwise specified.

    Member functions:
        read_hesel_output(self, file)
        calculate_sound_speed(self)
        calculate_ion_gyrofrequency()
        calculate_ion_gyroradius()
        calculate_debye_length()
        calculate_coulomb_logarithm()
        get_x_axis_rhos()
        get_y_axis_rhos()
        get_lcfs_index()
        get_wall_index()
        get_x_axis_probes()
    '''
    def __init__(self, file):
        self.read_hesel_output(file)

        self._phys_constants = get_physics_constants()

        self.c_s = self.calculate_sound_speed()
        self.omega_ci = self.calculate_ion_gyrofrequency()
        self.rho_s = self.calculate_ion_gyroradius()
        self.lambda_debye = self.calculate_debye_length()
        self.coulomb_logarithm = self.calculate_coulomb_logarithm()

        self.d_x = self.dx_rhos*self.rho_s
        self.xaxis_rhos = self.get_x_axis_rhos()
        self.xaxis = self.xaxis_rhos*self.rho_s
        self.lx_rhos = (self.xmax_rhos-self.xmin_rhos)

        self.lcfs_index = self.get_lcfs_index()
        self.wall_index = self.get_wall_index()

        self.animation_lcfs_index = int(self.lcfs_index/4)
        self.animation_wall_index = int(self.wall_index/4)

        self.d_y = self.dy_rhos*self.rho_s
        self.yaxis_rhos = self.get_y_axis_rhos()
        self.yaxis = self.yaxis_rhos*self.rho_s
        self.ly_rhos = self.dy_rhos*self.n_y

        self.adv_p_e = self.adv_p_e_omega_ci*self.omega_ci

        self.adv_p_i = self.adv_p_i_omega_ci*self.omega_ci

        self.con_p_e = self.con_p_e_omega_ci*self.omega_ci
        self.con_p_i = self.con_p_i_omega_ci*self.omega_ci

        self.xaxis_probes = self.get_x_axis_probes()
        self.xaxis_probes_rhos = self.xaxis_probes/(self.rho_s)

        self.time_1d = (1./self.omega_ci)*self.time1d_omega_ci
        self.time_2d = (1./self.omega_ci)*self.time2d_omega_ci

    def read_hesel_output(self, file):
        '''
        Function for reading the output from the HESEL .hdf5 file.
        All data is in SI units unless otherwise specified.

        Input: self,
               file, the loaded HESEL .hdf5 file

        Output: self.n_x,              an integer with the number of radial grid points
                self.n_y,              an integer with the number of poloidal grid points
                self.n_t,              an integer with the number of temporal points
                self.outmult,          an integer with the number of timesteps per output
                self.xmin_rhos,        a float with the minimum radial position
                                       of the domain in [rho_s]
                self.xmax_rhos,        a float with the maximum radial position
                                       of the domain in [rho_s]
                self.n_0,              a float with reference plasma density [m^{-3}]
                self.te0_eV,           a float with reference plasma electron temperature [eV]
                self.ti0_eV,           a float with reference plasma ion temperature [eV]
                self.background_n,     a float with the background density [m^{-3}]
                self.background_t,     a float with the background temperatures
                                       (both ele and ion) [eV]
                self.plasma_z,         an integer with the plasma charge number
                self.b0_omp,           a float with the magnitude of the magnetic
                                       field at the OMP [T]
                self.ion_mass_number,  an integer with the ion mass number
                self.minor_radius,     a float with the device minor radius [m]
                self.major_radius,     a float with the device major radius [m]
                self.plasma_q,         a float with the plasma safety factor
                self.parallel_conn_length,      a float with the parallel connection length [m]
                self.parallel_conn_length_wall, a float with the parallel connection length
                                                of the wall region [m]
                self.mach_number,      a float with the parallel mach number at the OMP
                self.edge_width_rhos,  a float with the width of the edge region [rho_s]
                self.sol_width_rhos,   a float with the width of the SOL region [rho_s]
                self.wall_region_width_rhos,    a float with the width of the
                                                wall region [rho_s]
                self.time1d_omega_ci,  a float with the time-step used in HESEL [1/omega_ci]
                self.time2d_omega_ci,  a float with the output time-step used for 2D fields in HESEL
                self.probes_nt,        an integer with the number of output times
                                       for the 1D probe arrays
                self.probes_nx,        an integer with the radial number of probes
                                       in the 1D probe arrays
                self.dx_rhos,          a float with the radial resolution of the domain [rho_s]
                self.dy_rhos,          a float with the poloidal resolution of the domain [rho_s]
                self.adv_p_e_omega_ci, a float with 9/2*1/(omega_ci*tau_s), i.e. the normalised
                                       constant part of the parallel advection term
                self.adv_p_i_omega_ci, a float with 9/2*1/(omega_ci*tau_s), i.e. the normalised
                                       constant part of the parallel advection term
                self.con_p_e_omega_ci, a float with 1/(omega_ci*tau_{SH,e}), i.e. the normalised
                                       const. part of the parallel electron Spitzer-Härm conduction
                self.con_p_i_omega_ci, a float with 1/(omega_ci*tau_{SH,i}), i.e. the const.
                                       normalised part of the parallel ion Spitzer-Härm conduction
                '''
        self.n_x = len(file['/data/var2d/Density'][0][0])
        self.n_y = len(file['/data/var2d/Density'][0])
        self.n_t = len(file['/data/var2d/Density'])

        self.outmult = file['/params/structure_param'].attrs['otmult']

        self.xmin_rhos = file['/params/structure_param'].attrs['xmin']
        self.xmax_rhos = file['/params/structure_param'].attrs['xmax']

        self.n_0 = 1e19*file['/params/structure_param'].attrs['ne0']
        self.te0_ev = file['/params/structure_param'].attrs['Te0']
        self.ti0_ev = file['/params/structure_param'].attrs['Ti0']
        self.background_n = file['/params/structure_param'].attrs['background_n']
        self.background_t = file['/params/structure_param'].attrs['background_t']
        self.plasma_z = file['/params/structure_param'].attrs['Z']
        self.b0_omp = file['/params/structure_param'].attrs['B0']
        self.ion_mass_number = file['/params/structure_param'].attrs['A']
        self.minor_radius = file['/params/structure_param'].attrs['r0']
        self.major_radius = file['/params/structure_param'].attrs['R0']
        self.plasma_q = file['/params/structure_param'].attrs['q']
        self.parallel_conn_length = file['/params/structure_param'].attrs['Lp']
        self.parallel_conn_length_wall = file['/params/structure_param'].attrs['Lpwall']
        self.mach_number = file['/params/structure_param'].attrs['Mp']
        self.edge_width_rhos = file['/params/structure_param'].attrs['edge']
        self.sol_width_rhos = file['/params/structure_param'].attrs['SOL']
        self.wall_region_width_rhos = file['/params/structure_param'].attrs['wall']

        self.time1d_omega_ci = file['/params/structure_param'].attrs['out_time']
        self.time2d_omega_ci = self.time1d_omega_ci*file['/params/structure_param'].attrs['otmult']

        self.probes_nt = len(file['/data/var1d/fixed-probes/TIP0_density'])
        self.probes_nx = len(file['/data/var1d/fixed-probes/TIP0_density'][0])

        self.dx_rhos = file['/params/structure_param'].attrs['dx']
        self.dy_rhos = file['/params/structure_param'].attrs['dy']

        self.adv_p_e_omega_ci = file['/params/structure_param'].attrs['adv_p']
        self.adv_p_i_omega_ci = file['/params/structure_param'].attrs['adv_P']
        self.con_p_e_omega_ci = file['/params/structure_param'].attrs['con_p']
        self.con_p_i_omega_ci = file['/params/structure_param'].attrs['con_P']

    def calculate_sound_speed(self):
        '''
        Function for calculating the ion sound speed at electron temperature:

            c_s = sqrt(e Te/m_i),

        where e is the elementary charge, Te is the reference electron temperature in eV and
        m_i is the ion mass.

        Input: self,

        return: c_s, the ion sound speed at electron temperature
        '''
        return np.sqrt(self._phys_constants["e"]*self.te0_ev\
                       /(self.ion_mass_number*self._phys_constants["m_p"]))

    def calculate_ion_gyrofrequency(self):
        '''
        Function for calculating the ion gyrofrequency at electron temperature:

            omega_ci = Z e B_0/m_i,

        where Z is the charge number, e is the elementary charge,
        B_0 is the magnetic field strength at the outer midplane and
        m_i is the ion mass.

        Input: self,

        return: omega_ci, the ion sound speed at electron temperature
        '''
        return self.plasma_z*self._phys_constants["e"]*self.b0_omp\
                /(self.ion_mass_number*self._phys_constants["m_p"])

    def calculate_ion_gyroradius(self):
        '''
        Function for calculating the ion gyrofrequency at electron temperature:

            rho_s = c_s/omega_ci,

        where c_s is the ion sound speed at electron temperature and
        omega_ci is the ion gyrofrequency at electron temperature

        Input: self,

        return: rho_s, the ion gyroradius at electron temperature
        '''
        return self.c_s/self.omega_ci

    def calculate_debye_length(self):
        '''
        Function for calculating the plasma debye length:

            lambda_debye = sqrt(epsilon Te0/(n_0 e)),

        where epsilon is the vacuum permittivity, Te is the reference electron temperature in eV,
        n0 is the reference plasma density and e is the elementary charge

        Input: self,

        return: lambda_debye, the plasma debye length
        '''
        return np.sqrt(self._phys_constants["epsilon_0"]*self.te0_ev\
                       /(self.n_0*self._phys_constants["e"]))

    def calculate_coulomb_logarithm(self):
        '''
        Function for calculating the Coulomb logarithm:

            log(Lambda_coulomb) = log(12 pi n_0 lambda_debye^3/Z),

        n0 is the reference plasma density, lambda_debye is the plasma debye length and
        Z is the plasma charge number

        Input: self,

        return: log(Lambda_coulomb), the plasma coulomb logarithm
        '''
        return np.log(12.*np.pi*self.n_0*self.lambda_debye**3/self.plasma_z)

    def get_x_axis_rhos(self):
        '''
        Function for getting the x-axis of the HESEL output, normalised so 0 is at the LCFS

        Input: self,

        return: x_axis, a numpy array with the radial positions of the grid points [rho_s]
        '''
        return self.dx_rhos*np.linspace(0, self.n_x-1, self.n_x)-self.edge_width_rhos

    def get_y_axis_rhos(self):
        '''
        Function for getting the y-axis of the HESEL output

        Input: self,

        return: y_axis, a numpy array with the poloidal positions of the grid points [rho_s]
        '''
        return self.dy_rhos*np.linspace(0, self.n_y-1, self.n_y)

    def get_lcfs_index(self):
        '''
        Function for calculating the index of the LCFS position in the HESEL output

        Input: self,

        return: lcfs_index, an integer with the index of the LCFS
        '''
        return int(self.edge_width_rhos/self.dx_rhos)

    def get_wall_index(self):
        '''
        Function for calculating the index where the wall region starts

        Input: self,

        return: wall_index, an integer with the index of where the wall region starts
        '''
        return int((self.edge_width_rhos+self.edge_width_rhos)/self.dx_rhos)

    def get_x_axis_probes(self):
        '''
        Function for getting the x-axis for the synthetic probes in HESEL, normalised
        so the LCFS is at 0

        Input: self,

        return: x_axis_probes_rhos, a numpy array with the synthetic probe positions
        '''
        return np.linspace(1, self.probes_nx, self.probes_nx)\
                            *(self.lx_rhos/self.probes_nx)*self.rho_s\
                              - self.edge_width_rhos*self.rho_s

if __name__ == '__main__':
    # Filename of file to be loaded
    FILENAME = '/media/jmbols/Data/jmbols/ST40/Programme 3/L_par_scan/ST40.00003.096.h5'

    # Load data
    FILE = h5py.File(FILENAME, 'r')
    HESEL_PARAMS = HESELparams(FILE)
    print(HESEL_PARAMS.n_t)
