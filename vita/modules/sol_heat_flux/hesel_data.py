#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 16 11:14:43 2018

@author: jmbols
"""
import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation
from vita.modules.sol_heat_flux.hesel_parameters import HESELparams
from vita.modules.utils.physics_constants import get_physics_constants

class HESELdata():
    '''
    Class for loading and storing the data output from HESEL stored in an hdf5 file.
    All fields are in SI units unless otherwise specified.

    Member functions:
        _load_file()
        _close_file()
        _evaluate_electron_advection_field()
        _evaluate_ion_advection_field()
        _evaluate_electron_conduction_field()
        _evaluate_ion_conduction_field()
        evaluate_parallel_heat_fluxes()
        get_lcfs_values()
        calculate_lambda_q(case='')
        get_probe_positions()
        _load_probe_data(field_name)
        get_profiles_from_probes()
        load_2d_animation_fields()
        animate_2d_field(fieldname='', show_animation=False, save_movie=True)
        animate_1d_field(fieldname='', show_animation=False, save_movie=True)
    '''
    def __init__(self, filename, ratio=0.25):
        '''
        Initialise the HESEL data object as None-types

        Input: filename, the name of the file to be loaded
               ratio,    the ratio of timesteps to be filtered out to make sure
                         a turbulent steady-state has been reached,
                         e.g., ratio = 0.25 means the first 25% of the data
                         is discarded
        '''
        self.filename = filename
        self.phys_constants = get_physics_constants()
        self.ev_to_k = self.phys_constants["e"]/self.phys_constants["k_b"]

        self.ratio = ratio
        self.file = None
        self.te_probes = None
        self.ti_probes = None
        self.n_probes = None
        self.hesel_params = None
        self.q_parallel_tot = None
        self.q_parallel_e_con = None
        self.q_parallel_e_adv = None
        self.q_parallel_i_con = None
        self.q_parallel_i_adv = None
        self.probe_position = None
        self.n_2d = None
        self.pe_2d = None
        self.te_2d = None
        self.pi_2d = None
        self.ti_2d = None
        self.phi_2d = None
        self.omega_2d = None
        self.n_lcfs = None
        self.te_lcfs_ev = None
        self.ti_lcfs_ev = None
        self.grad_pe_lcfs = None
        self.grad_pi_lcfs = None
        self.lambda_q_tot = None
        self.lambda_q_e_adv = None
        self.lambda_q_e_con = None
        self.lambda_q_i_adv = None
        self.lambda_q_i_con = None

    def __del__(self):
        self._close_file()

    def _load_file(self):
        '''
        Load the file and the HESEL parameters from HESELparameters.py
        '''
        self.file = h5py.File(self.filename, 'r')
        self.hesel_params = HESELparams(self.file)

    def _close_file(self):
        '''
        If the file is open, close the file
        '''
        if self.file is not None:
            self.file.close()
            self.file = None

    def _evaluate_electron_advection_field(self):
        '''
        Function for evaluating the electron advection for each point in time and
        space:

            pe_adv = 3/2*1/tau_d*sqrt((T_i + T_e)/(T_i0 + T_e0))*p_e,

        where the sqrt((T_i + T_e)/(T_i0 + T_e0))*p_e is to take local variations
        into account and 3/2 is from the normalisation used in HESEL.

        input: self,

        return: electron_advecton_mw, a numpy array with the ion advection term for
                each point in space and time [MW]
        '''
        w_to_mw = 1./1.e6

        p_e_probes = self.te_probes*self.n_probes*self.phys_constants["k_b"]

        electron_advection_mw = (3./2.)*self.hesel_params.adv_p_i\
                                         *np.sqrt(
                                             (self.ti_probes+self.te_probes)\
                                             /(self.hesel_params.ti0_ev*self.ev_to_k\
                                             + self.hesel_params.te0_ev*self.ev_to_k)
                                         )*p_e_probes*w_to_mw
        return electron_advection_mw

    def _evaluate_ion_advection_field(self):
        '''
        Function for evaluating the ion advection for each point in time and
        space:

            pi_adv = 3/2*1/tau_d*sqrt((T_i + T_e)/(T_i0 + T_e0))*p_i,

        where the sqrt((T_i + T_e)/(T_i0 + T_e0))*p_i is to take local variations
        into account and 3/2 is from the normalisation used in HESEL.

        input: self,

        return: ion_advecton_mw, a numpy array with the ion advection term for
                each point in space and time [MW]
        '''
        w_to_mw = 1./1.e6

        p_i_probes = self.ti_probes*self.n_probes*self.phys_constants["k_b"]

        ion_advection_mw = (3./2.)*self.hesel_params.adv_p_i\
                                    *np.sqrt(
                                        (self.ti_probes+self.te_probes)\
                                        /(self.hesel_params.ti0_ev*self.ev_to_k\
                                        + self.hesel_params.te0_ev*self.ev_to_k)
                                    )*p_i_probes*w_to_mw
        return ion_advection_mw

    def _evaluate_electron_conduction_field(self):
        '''
        Function for evaluating the electron conduction for each point in time and
        space:

            pe_cond = 3/2*1/tau_{SH,e}*(T_e/T_e0)^(5/2)*p_e,

        where the (T_e/T_e0)^(5/2)*p_e is to take local variations into account
        and 3/2 is from the normalisation used in HESEL.

        input: self,

        return: electron_conduction_mw, a numpy array with the electron conduction
                term for each point in space and time [MW]
        '''
        w_to_mw = 1./1.e6

        p_e_probes = self.ti_probes*self.n_probes*self.phys_constants["k_b"]

        electron_conduction_mw = (3./2.)*self.hesel_params.con_p_e\
                                        *(self.te_probes\
                                          /(self.hesel_params.te0_ev*self.ev_to_k)\
                                          )**(5/2)\
                                          *p_e_probes*w_to_mw
        return electron_conduction_mw

    def _evaluate_ion_conduction_field(self):
        '''
        Function for evaluating the electron conduction for each point in time and
        space:

            pi_cond = 3/2*1/tau_{SH,i}*(T_i/T_e0)^(5/2)*p_i,

        where the (T_i/T_e0)^(5/2)*p_i is to take local variations into account
        (T_i is normalised to T_e0 in HESEL) and 3/2 is from the normalisation used in HESEL.

        input: self,

        return: electron_conduction_mw, a numpy array with the electron conduction
                term for each point in space and time [MW]
        '''
        w_to_mw = 1./1.e6

        p_i_probes = self.ti_probes*self.n_probes*self.phys_constants["k_b"]

        ion_conduction_mw = (3./2.)*self.hesel_params.con_p_i\
                                        *(self.ti_probes\
                                          /(self.hesel_params.te0_ev*self.ev_to_k)\
                                          )**(5/2)\
                                          *p_i_probes*w_to_mw
        return ion_conduction_mw

    def _evaluate_parallel_heat_flux_electron_advection(self):
        '''
        Function for evaluate the contribution to the parallel heat flux from
        the ion advection:

            q_parallel_e_adv = a*<p_e/tau_d>_t,

        where a is the device minor radius, tau_d is the parallel advection loss term
        and <>_t denotes a temporal average. There are fewer probe radial points than
        1D radial points in HESEL, so the heat flux is interpolated after it is evaluated.

        Input: self,

        return: q_parallel_e_adv_mw, a numpy array with the electron advection part
                                     of the parallel heat flux
        '''
        p_e_adv_mw = self._evaluate_electron_advection_field()

        p_e_adv_mw_t_avg = np.mean(p_e_adv_mw, axis=0)

        del p_e_adv_mw

        q_parallel_e_adv_mw = self.hesel_params.minor_radius\
                                * np.interp(self.hesel_params.xaxis,\
                                            self.hesel_params.xaxis_probes,\
                                            p_e_adv_mw_t_avg)
        return q_parallel_e_adv_mw

    def _evaluate_parallel_heat_flux_ion_advection(self):
        '''
        Function for evaluate the contribution to the parallel heat flux from
        the ion advection:

            q_parallel_i_adv = a*<p_i/tau_d>_t,

        where a is the device minor radius, tau_d is the parallel advection loss term
        and <>_t denotes a temporal average. There are fewer probe radial points than
        1D radial points in HESEL, so the heat flux is interpolated after it is evaluated.

        Input: self,

        return: q_parallel_i_adv_mw, a numpy array with the ion advection part
                                     of the parallel heat flux
        '''
        p_i_adv_mw = self._evaluate_ion_advection_field()

        p_i_adv_mw_t_avg = np.mean(p_i_adv_mw, axis=0)

        del p_i_adv_mw

        q_parallel_i_adv_mw = self.hesel_params.minor_radius\
                                * np.interp(self.hesel_params.xaxis,\
                                            self.hesel_params.xaxis_probes,\
                                            p_i_adv_mw_t_avg)
        return q_parallel_i_adv_mw


    def _evaluate_parallel_heat_flux_electron_conduction(self):
        '''
        Function for evaluate the contribution to the parallel heat flux from
        the ion advection:

            q_parallel_e_cond = a*<p_e/tau_{SH,e}>_t,

        where a is the device minor radius, tau_{SH,e} is the parallel conduction loss term
        and <>_t denotes a temporal average. There are fewer probe radial points than
        1D radial points in HESEL, so the heat flux is interpolated after it is evaluated.

        Input: self,

        return: q_parallel_e_cond_mw, a numpy array with the electron conduction part
                                      of the parallel heat flux
        '''
        p_e_cond_mw = self._evaluate_electron_conduction_field()

        p_e_cond_mw_t_avg = np.mean(p_e_cond_mw, axis=0)

        del p_e_cond_mw

        q_parallel_e_cond_mw = self.hesel_params.minor_radius\
                                * np.interp(self.hesel_params.xaxis,\
                                            self.hesel_params.xaxis_probes,\
                                            p_e_cond_mw_t_avg)
        return q_parallel_e_cond_mw

    def _evaluate_parallel_heat_flux_ion_conduction(self):
        '''
        Function for evaluate the contribution to the parallel heat flux from
        the ion advection:

            q_parallel_i_cond = a*<p_i/tau_{SH,i}>_t,

        where a is the device minor radius, tau_{SH,i} is the parallel conduction loss term
        and <>_t denotes a temporal average. There are fewer probe radial points than
        1D radial points in HESEL, so the heat flux is interpolated after it is evaluated.

        Input: self,

        return: q_parallel_i_cond_mw, a numpy array with the ion conduction part
                                      of the parallel heat flux
        '''
        p_i_cond_mw = self._evaluate_ion_conduction_field()

        p_i_cond_mw_t_avg = np.mean(p_i_cond_mw, axis=0)

        del p_i_cond_mw

        q_parallel_i_cond_mw = self.hesel_params.minor_radius\
                                * np.interp(self.hesel_params.xaxis,\
                                            self.hesel_params.xaxis_probes,\
                                            p_i_cond_mw_t_avg)
        return q_parallel_i_cond_mw

    def evaluate_parallel_heat_fluxes(self):
        '''
        Function for evaluating the parallel heat fluxes

        Input: self
        Output: self.q_parallel_tot,   the total parallel heat flux profile in MW/m^2
                self.q_parallel_e_con, the parallel heat flux profile from the
                                       electron conduction in MW/m^2
                self.q_parallel_e_adv, the parallel heat flux profile from the
                                       electron advection in MW/m^2
                self.q_parallel_i_con, the parallel heat flux profile from the
                                       ion conduction in MW/m^2
                self.q_parallel_i_adv, the parallel heat flux profile from the
                                       ion advection in MW/m^2
        '''

        # The profiles need to be loaded from synthetic probe data to evaluate
        # the parallel heat fluxes
        if self.te_probes is None:
            self.get_profiles_from_probes()

        #######################
        # Electron advection  #
        #######################
        self.q_parallel_e_adv = self._evaluate_parallel_heat_flux_electron_advection()

        ##################
        # Ion advection  #
        ##################
        self.q_parallel_i_adv = self._evaluate_parallel_heat_flux_ion_advection()

        #######################
        # Electron conduction #
        #######################
        self.q_parallel_e_con = self._evaluate_parallel_heat_flux_electron_conduction()

        ##################
        # Ion conduction #
        ##################
        self.q_parallel_i_con = self._evaluate_parallel_heat_flux_ion_conduction()

        # Total parallel heat flux
        self.q_parallel_tot = self.q_parallel_e_con + self.q_parallel_e_adv\
                              + self.q_parallel_i_con + self.q_parallel_i_adv

    def get_lcfs_values(self):
        '''
        Function for getting calculating the average LCFS values of the plasma parameters.
        The 1D fields in HESEL have better spatial resolution than the synthetic probes,
        so we use those to evaluate the values at the LCFS

        Input:  self,

        Output: self.n_lcfs,       a float with the average density at the LCFS
                self.te_lcfs_ev,   a float with the the electron temperature at the LCFS in eV
                self.ti_lcfs_ev,   a float with the the ion temperature at the LCFS in eV
                self.grad_pe_lcfs, a float with the the gradient of the electron pressure
                                   at the LCFS
                self.grad_pi_lcfs, a float with the  the gradient of the ion pressure at the LCFS
        '''

        if self.file is None:
            self._load_file()

        i_lcfs = self.hesel_params.lcfs_index

        n_t = self.hesel_params.n_t*self.hesel_params.outmult

        n_1d = np.array(self.hesel_params.n_0*\
                     self.file['/data/var1d/Density-inst']\
                     [int(n_t*self.ratio):n_t, i_lcfs-1:i_lcfs+2])
        self.n_lcfs = np.mean(n_1d, axis=0)[1]

        t_e_1d = np.array(self.hesel_params.te0_ev*\
                      self.file['/data/var1d/Ele-Temp-inst']\
                      [int(n_t*self.ratio):n_t, i_lcfs-1:i_lcfs+2])
        self.te_lcfs_ev = np.mean(t_e_1d, axis=0)[1]

        t_i_1d = np.array(self.hesel_params.te0_ev*\
                      self.file['/data/var1d/Ion-Temp-inst']\
                      [int(n_t*self.ratio):n_t, i_lcfs-1:i_lcfs+2])
        self.ti_lcfs_ev = np.mean(t_i_1d, axis=0)[1]

        self._close_file()

        pe_t_avg = np.mean(t_e_1d*n_1d*self.phys_constants["e"], axis=0)
        del t_e_1d
        pi_temporal_mean = np.mean(t_i_1d*n_1d*self.phys_constants["e"], axis=0)
        del t_i_1d
        del n_1d

        self.grad_pe_lcfs = (pe_t_avg[1+1]-pe_t_avg[1-1])/\
                               (self.hesel_params.xaxis[i_lcfs+1]\
                                -self.hesel_params.xaxis[i_lcfs-1])
        del pe_t_avg
        self.grad_pi_lcfs = (pi_temporal_mean[1+1]-pi_temporal_mean[1-1])/\
                               (self.hesel_params.xaxis[i_lcfs+1]\
                                -self.hesel_params.xaxis[i_lcfs-1])
        del pi_temporal_mean

    def calculate_lambda_q(self, case=''):
        '''
        Function for calculating lambda_q as the weighted average position:

            lambda_q = (int_0^l_x x*q_parallel(x) dx)/(int_0^l_x q_parallel(x) dx),

        where l_x is the length of the domain, x is the radial coordinates and
        q_parallel(x) is the parallel heat flux profile

        Input: self,
               case, a string with which lambda_q to evaluate. Can be:
                     'q_tot', only evaluate lambda_q on q_parallel_tot
                     'q_adv_e', only evaluate lambda_q on q_parallel_e_adv
                     'q_con_e', only evaluate lambda_q on q_parallel_e_con
                     'q_adv_i', only evaluate lambda_q on q_parallel_i_adv
                     'q_con_i', only evaluate lambda_q on q_parallel_i_con
                     If nothing is stated, all of them are evaluated

        Output: self.lambda_q_tot,   a float with lambda_q_tot if 'q_tot' is specified
                self.lambda_q_e_adv, a float with lambda_q_e_adv if 'q_adv_e' is specified
                self.lambda_q_e_con, a float with lambda_q_e_con if 'q_con_e' is specified
                self.lambda_q_i_adv, a float with lambda_q_i_adv if 'q_adv_i' is specified
                self.lambda_q_i_con, a float with lambda_q_i_con if 'q_con_i' is specified

                All of the above are output if anything else or nothing is specified
        '''

        if self.file is None:
            self._load_file()

        if self.q_parallel_e_con is None:
            self.evaluate_parallel_heat_fluxes()

        i_lcfs = self.hesel_params.lcfs_index
        x_axis_from_lcfs = self.hesel_params.xaxis[i_lcfs:]

        if case == 'q_tot':
            q_parallel = self.q_parallel_tot[i_lcfs:]

            self.lambda_q_tot = np.trapz(x_axis_from_lcfs, x_axis_from_lcfs*q_parallel)\
                                /np.trapz(x_axis_from_lcfs, q_parallel)
            del x_axis_from_lcfs
            del q_parallel

        elif case == 'q_adv_e':
            q_parallel = self.q_parallel_e_adv[i_lcfs:]

            self.lambda_q_e_adv = np.trapz(x_axis_from_lcfs, x_axis_from_lcfs*q_parallel)\
                                  /np.trapz(x_axis_from_lcfs, q_parallel)
            del x_axis_from_lcfs
            del q_parallel

        elif case == 'q_con_e':
            q_parallel = self.q_parallel_e_con[i_lcfs:]

            self.lambda_q_e_con = np.trapz(x_axis_from_lcfs, x_axis_from_lcfs*q_parallel)\
                                  /np.trapz(x_axis_from_lcfs, q_parallel)
            del x_axis_from_lcfs
            del q_parallel

        elif case == 'q_adv_i':
            q_parallel = self.q_parallel_i_adv[i_lcfs:]

            self.lambda_q_i_adv = np.trapz(x_axis_from_lcfs, x_axis_from_lcfs*q_parallel)\
                                  /np.trapz(x_axis_from_lcfs, q_parallel)
            del x_axis_from_lcfs
            del q_parallel

        elif case == 'q_con_i':
            q_parallel = self.q_parallel_e_con[i_lcfs:]

            self.lambda_q_i_con = np.trapz(x_axis_from_lcfs, x_axis_from_lcfs*q_parallel)\
                                  /np.trapz(x_axis_from_lcfs, q_parallel)
            del x_axis_from_lcfs
            del q_parallel

        else:
            cases = ['q_tot', 'q_adv_e', 'q_con_e', 'q_adv_i', 'q_con_i']
            for case_all in cases:
                self.calculate_lambda_q(case=case_all)

    def get_probe_positions(self):
        '''
        Function for getting the positions of the synthetic probes used in the simulation.
        The information is stored in the file called myprobe.dat, which is converted to
        a string when loading it into python.

        Probe names are specified with @TIP followed by a space '\t', then the radial
        position, a space '\t' and then the poloidal position.
        The end of the segment containing positions ends with a space '\t' and 'hdf5'.

        Input:  self,

        Output: self.probe_position,  a dictionary with the probename as the key and a list
                                      with the radial and poloidal position of the synthetic probes
                                      [radial_position, poloidal_position]
        '''
        if self.file is None:
            self._load_file()

        probe_positions = {}

        probes_position_data = self.file['/documentation/myprobe.dat']
        probes_position_data = str(probes_position_data[0])

        name_prefix = '@'
        end_indicator = 'thdf5'
        separator = '\\'

        probes_position_data = probes_position_data.split(name_prefix)
        for i in probes_position_data:
            j = i.split(end_indicator)
            # Check if j is just a doc-string or actually contains information about a probe
            if j[0][0] == 'T':
                j = j[0].split(separator)[:-1]
                # j is now a list with four entries. 0 is the probe name, 1 is
                # 'tradial_position', 2 is 'tpoloidal_position' and 3 is an empty entry
                probe_name = j[0]
                # remove the 't' and convert to a float
                probe_radial_position = float(j[1][1:])
                probe_poloidal_position = float(j[2][1:])
                if probe_name not in probe_positions:
                    probe_positions[probe_name] = [probe_radial_position, probe_poloidal_position]

        self.probe_position = probe_positions

    def _load_probe_data(self, field_name):
        '''
        Function for loading the probe synthetic HESEL probe data at the radial position
        radial_probe_position = 0.0 and at poloidal positions that are in increments of
        5 rho_s from poloidal_probe_position = 0.0, which is where we assume that the
        synthetic data is mutually independent.

        The data is sliced so the first self.ratio*n_t time-points are filtered away from the
        signals of each synthetic probe. The output numpy array then consists of the
        concatenated synthetic data from the probes at different poloidal positions as
        specified above.

        input: self,
               field_name,  a string with the name of the field to load. The options are
                            'temperature' for the electron temperature,
                            'temperature_i' for the ion temperature, and
                            'density' for the plasma density (the plasma is assumed quasi-
                            neutral)

        return: field_data, a numpy array with the specified field in SI units
        '''
        # Get probe data
        n_t_probes = self.hesel_params.probes_nt-1

        probe_name_list = []

        if field_name in ('temperature', 'temperature_i'):
            convert_to_si = self.hesel_params.te0_ev*self.ev_to_k
        elif field_name == 'density':
            convert_to_si = self.hesel_params.n_0
        else:
            error_msg = 'Error in HESELdata_load_probe_data(): Field not yet implemented,'
            error_msg += 'options are:\n"temperature"\n"temperature_i"\n"density"\n'
            print(error_msg)
            return -1

        # Decide which probes to load. Only load probes that are at the radial position
        # probe_radial_position = 0.0, and load probes that are at increments of 5 rho_s
        # away from the poloidal position 0.0 (this is where we assume that probe data is
        # independent of each other).
        for key in self.probe_position:
            if self.probe_position[key][0] == 0.0 and self.probe_position[key][1]%5. == 0.0:
                probe_name_list.append(key)

        i = 0
        for probe_name in probe_name_list:
            probe_name = '/data/var1d/fixed-probes/' + probe_name + '_' + field_name
            tmp = np.array(self.file[probe_name])
            field_data_per_probe = convert_to_si\
                                    *tmp[:][int(n_t_probes*self.ratio):n_t_probes]

            tmp_x = len(field_data_per_probe)
            tmp_y = len(field_data_per_probe[0])

            if i == 0:
                field_data = np.empty([len(probe_name_list)*tmp_x, tmp_y])
                field_data[:tmp_x, :] = field_data_per_probe[:tmp_x, :]
            else:
                field_data[i*tmp_x:(i+1)*tmp_x, :] = field_data_per_probe[:tmp_x, :]
            tmp = None
            field_data_per_probe = None
            i += 1

        return field_data

    def get_profiles_from_probes(self):
        '''
        Function for getting n, t_e and t_i profiles from the synthetic probe
        diagnostic in the HESEL hdf5-file. The synthetic probes have lower spatial
        resolution than the 1D fields, but have a higher temporal resolution.

        Input:  self,

        Output: self.n_probes, a numpy array with the probe profile data
                               for the density
                self.te_probes, a numpy array with the probe profile data
                                for the electron temperature
                self.ti_probes, a numpy array with the probe profile data
                                for the ion temperature
        '''
        if self.file is None:
            self._load_file()
        if self.probe_position is None:
            self.get_probe_positions()

        ############################
        ### Electron temperature ###
        ############################
        self.te_probes = self._load_probe_data('temperature')

        #######################
        ### Ion temperature ###
        #######################
        self.ti_probes = self._load_probe_data('temperature_i')

        ###############
        ### Density ###
        ###############
        self.n_probes = self._load_probe_data('density')

        self._close_file()

    def load_2d_animation_fields(self):
        '''
        Load the 2D fields from the HESEL code from xanimation (the spatial resolution
        is 1/4 that of the full 2D profiles)

        Input:  self
        Output: self.n_2d, the 2D field of the density in SI units
                self.pe_2d, the 2D field of the electron pressure in SI units
                self.te_2d, the 2D field of the electron temperature in SI units,
                            calculated as P_e/n
                self.pi_2d, the 2D field of the ion pressure in SI units
                self.ti_2d, the 2D field of the ion temperature in SI units,
                            calculated as P_i/n
                self.phi_2d, the 2D field of the potential in SI units
        '''
        if self.file is None:
            self._load_file()

        self.n_2d = self.hesel_params.n_0*np.array(self.file['/data/xanimation/density'])
        self.pe_2d = self.hesel_params.n_0*self.hesel_params.te0_ev*\
                     np.array(self.file['/data/xanimation/electron_pressure'])
        self.te_2d = self.pe_2d/self.n_2d
        self.pi_2d = self.hesel_params.n_0*self.hesel_params.te0_ev*\
                     np.array(self.file['/data/xanimation/ion_pressure'])
        self.ti_2d = self.pi_2d/self.n_2d
        self.phi_2d = np.array(self.file['/data/xanimation/potential'])
        self.omega_2d = np.array(self.file['/data/xanimation/vorticity'])

    def animate_2d_field(self, fieldname='', show_animation=False, save_movie=True):
        '''
        Function for creating videos of the 2D fields

        Input: self,
               fieldname, a string with the name of the field to make the video of
                          the options are: 'n', 'Te', 'Ti', 'Pe', 'Pi', 'phi', 'omega'
                          default is '', which returns an error
               show_animation, a boolean determining whether or not to show the
                               animation as it is being created
                               default is False
               save_movie, a boolean for whether or not the movie should be saved,
                           default is True

        Output: An animation with the specified field,
                saved in the working directory if save_movie == True
        '''
        if self.n_2d is None:
            self.load_2d_animation_fields()

        if fieldname == 'n':
            field = self.n_2d
        elif fieldname == 'Te':
            field = self.te_2d
        elif fieldname == 'Ti':
            field = self.ti_2d
        elif fieldname == 'Pe':
            field = self.pe_2d
        elif fieldname == 'Pi':
            field = self.pi_2d
        elif fieldname == 'phi':
            field = self.phi_2d
        elif fieldname == 'omega':
            field = self.omega_2d
        else:
            print('Not a valid input, please use one of the following:\n \
                  n, Te, Ti, Pe, Pi, phi or omega')
            return -1

        # The animation resolution is 1/4th of the actual fields,
        # so the axis need to be adjusted accordingly
        xaxis = self.hesel_params.xaxis[0::4]
        yaxis = self.hesel_params.yaxis[0::4]
        # Set tickmarks at every 10th point
        xticks = np.linspace(0, len(xaxis)-1, 10)
        xticks = xticks.astype(int)
        yticks = np.linspace(0, len(yaxis)-1, 10)
        yticks = yticks.astype(int)

        # Make the actual figure
        fig = plt.figure()
        axess = []
        axess.append(fig.add_subplot(1, 1, 1))

        #find min and max in time
        mins = field[:, :, :].min()
        maxs = field[:, :, :].max()

        #set up list of images for animation
        movie = []
        images = []
        n_t = field.shape[0] #number of time slices
        print('time slices = {}'.format(n_t))
        first = 1
        plt.tight_layout()
        for time in range(0, n_t):
            images.clear()
            i = 0

            images.append(axess[i].pcolormesh(field[time, :, :], vmin=mins,\
                          vmax=maxs))
            axess[i].set_xlabel('x / [cm]')
            axess[i].set_ylabel('y / [cm]')
            axess[i].set_title(fieldname)
            i = i + 1
            if first == 1:
                fig.colorbar(images[0], ax=axess[0])
                axess[0].set_xticks(xticks)
                xticks = np.round(xaxis[xticks]*100, 2) # *100 to get it in cm
                axess[0].set_xticklabels(xticks)
                axess[0].set_yticks(yticks)
                yticks = np.round(yaxis[yticks]*100, 2) # *100 to get it in cm
                axess[0].set_yticklabels(yticks)
                first = 0
            #time_title.set_text('t={}'.format(t_array[time]))
            #time_title = axess[0].annotate(r'$t={} $'.format(self.t_array[time]) + r'$\,
            #\Omega^{-1}-1$',xy = (0.1,1.2))
            collected_list = [*images] #apparently a bug in matplotlib forces this solution
            #collected_list.append(time_title)
            movie.append(collected_list)

        plt.tight_layout()
        #run animation
        ani = matplotlib.animation.ArtistAnimation(fig, movie, interval=500,\
                                                   blit=False, repeat_delay=1000)

        if show_animation:
            plt.show()
        if save_movie:
            try:
                ffmpeg_writer = matplotlib.animation.writers['ffmpeg']
                # * bitrate is set to -1 for automatic bit rate, if not a high number
                #   should be set to get good quality
                # * fps sets how fast the animation is played
                #   http://stackoverflow.com/questions/22010586/matplotlib-animation-duration
                # * codec is by default mpeg4, but as this creates large files.
                #   h264 is preferred.
                writer = ffmpeg_writer(bitrate=-1, fps=5, codec="h264")

                print('trying to save')
                ani.save(self.filename[:-17] + 'Videos/' + self.filename[-17:] +\
                         fieldname + '2Dfilm.mp4', writer=writer, dpi=300)
            except Exception as exception:
                print("Save failed: Check ffmpeg path")
                raise exception

        plt.close()
        return 0

    def animate_1d_field(self, fieldname='', show_animation=False, save_movie=True):
        '''
        Function for creating videos of the 1D fields

        Input: self
               fieldname, a string with the name of the field to make the video of
                          the options are: 'n', 'Te', 'Ti', 'Pe', 'Pi'
                          default is '', which returns an error
               show_animation, a boolean determining whether or not to show the
                               animation as it is being created
                               default is False
               save_movie, a boolean for whether or not the movie should be saved,
                           default is True

        Output: An animation with the specified field,
                saved in the working directory if save_movie == True
        '''
        if self.n_probes is None:
            self.get_profiles_from_probes()

        if fieldname == 'n':
            field = self.n_probes
        elif fieldname == 'Te':
            field = self.te_probes
        elif fieldname == 'Ti':
            field = self.ti_probes
        elif fieldname == 'Pe':
            field = self.te_probes*self.n_probes*self.phys_constants["k_b"]
        elif fieldname == 'Pi':
            field = self.ti_probes*self.n_probes*self.phys_constants["k_b"]
        else:
            print('Not a valid input, please use one of the following:\n \
                  n, Te, Ti, Pe or Pi')
            return -1
        fig = plt.figure()
        axess = []
        axess.append(fig.add_subplot(1, 1, 1))

        #find min and max in time
        mins = field[:, :].min()
        maxs = field[:, :].max()

        #set up list of images for animation
        movie = []
        images = []
        n_t = field.shape[0] #number of time slices
        print('time slices = {}'.format(n_t))
        plt.tight_layout()
        for time in range(0, n_t):
            images.clear()
            ax_temp, = axess[0].plot(self.hesel_params.xaxis_probes, field[time, :], color='k')
            images.append(ax_temp)
            axess[0].set_xlabel('x / [m]')
            axess[0].set_ylabel(fieldname)
            axess[0].set_ylim(mins, maxs)
            #time_title.set_text('t={}'.format(t_array[time]))

            #time_title = axess[0].annotate(r'$t={} $'.format(self.t_array[time]) + r'$\,
            #\Omega^{-1}-1$',xy = (0.1,1.2))
            collected_list = [*images] #apparently a bug in matplotlib forces this solution
            movie.append(collected_list)

        plt.tight_layout()
        #run animation
        ani = matplotlib.animation.ArtistAnimation(fig, movie, interval=1000,\
                                                   blit=False, repeat_delay=1000)

        if show_animation:
            plt.show()
        if save_movie:
            try:
                ffmpeg_writer = matplotlib.animation.writers['ffmpeg']
                # * bitrate is set to -1 for automatic bit rate, if not a high number
                #   should be set to get good quality
                # * fps is sets how fast the animation is played
                #   http://stackoverflow.com/questions/22010586/matplotlib-animation-duration
                # * codec is by default mpeg4, but as this creates large files.
                #   h264 is preferred.
                writer = ffmpeg_writer(bitrate=-1, fps=5, codec="h264")

                print('trying to save')
                ani.save(self.filename[:-17] + 'Videos/' + self.filename[-17:] +\
                         fieldname + '1Dfilm.mp4', writer=writer, dpi=300)
            except Exception as exception:
                print("Save failed: Check ffmpeg path")
                raise exception

        plt.close()
        return 0


if __name__ == '__main__':
    # Filename of file to be loaded
#    filename = '/run/user/1000/gvfs/smb-share:server=ait-pcifs02.win.dtu.dk,\
#               share=fys$/FYS-PPFE/Turbulence group/HESEL 2D data/ASDEX/\
#               power_scan_ion_conduction_steep_tanh/B-scan/ASDEX.0010.h5'
#    filename = '/run/user/1000/gvfs/smb-share:server=ait-pcifs02.win.dtu.dk,\
#               share=fys$/FYS-PPFE/Turbulence group/HESEL 2D data/ASDEX/\
#               shots/29302/ASDEX.29302.03.h5'
#    filename = '/run/user/1000/gvfs/smb-share:server=ait-pcifs02.win.dtu.dk,\
#               share=fys$/FYS-PPFE/Turbulence group/HESEL 2D data/ASDEX/\
#               power_scan_ion_conduction_steep_tanh/P-scan/ASDEX.0023.h5'
#    filename = '/media/jmbols/Data/jmbols/ST40/Programme 3/q_scan/ST40.00003.079.h5'
#    filename = '/run/user/1000/gvfs/smb-share:server=ait-pcifs02.win.dtu.dk,share=fys$\
#                /FYS-PPFE/Turbulence group/HESEL 2D data/ITER/ASTRA/00004/ITER.00004.005.h5'
#    filename = '/home/jmbols/Postdoc/ST40/Programme 3/Te(i)_grad_scan/ST40.00003.081.h5'

    FILENAME = '/media/jmbols/Data/jmbols/ST40/Programme 3/L_par_scan/ST40.00003.096.h5'
    HESEL_DATA_OBJECT = HESELdata(FILENAME, ratio=0.25)
    HESEL_DATA_OBJECT.load_2d_animation_fields()

    HESEL_DATA_OBJECT.get_lcfs_values()
    HESEL_DATA_OBJECT.calculate_lambda_q(case='q_tot')

    INDEX_FROM_LCFS = np.where(HESEL_DATA_OBJECT.hesel_params.xaxis_probes >= 0)[0]
    N = HESEL_DATA_OBJECT.n_probes[:, INDEX_FROM_LCFS]
    N_INT = np.trapz(N)
    FINAL_TIME = HESEL_DATA_OBJECT.hesel_params.time_1d*len(N_INT)

    TOTAL_ST40_AREA = 2*np.pi*(HESEL_DATA_OBJECT.hesel_params.minor_radius\
                               +HESEL_DATA_OBJECT.hesel_params.major_radius)\
                               *HESEL_DATA_OBJECT.hesel_params.minor_radius

    AVG_PART_FLUX = np.mean(N_INT)*TOTAL_ST40_AREA
    PART_PR_SEC = AVG_PART_FLUX*1/FINAL_TIME

    print(PART_PR_SEC)

    N_AVG = np.mean(N)
    print(N_AVG)
    print(HESEL_DATA_OBJECT.lambda_q_tot)
    del HESEL_DATA_OBJECT
#    HESEL_data_object.animate_2d_field('n')
#    HESEL_data_object.animate_1d_field('n')
#    HESEL_data_object.animate_2d_field('Te')
#    HESEL_data_object.animate_1d_field('Te')
#    HESEL_data_object.animate_2d_field('omega')
#    HESEL_data_object.animate_2d_field('Te')
#    HESEL_data_object.animate_2d_field('Ti')
#    HESEL_data_object.get_lcfs_values()
#    print(HESEL_data_object.lambda_q_tot)
#    print(HESEL_data_object.te_lcfs_ev)
#    print(HESEL_data_object.ti_lcfs_ev)
