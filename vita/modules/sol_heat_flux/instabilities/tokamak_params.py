#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 11:17:41 2020

@author: jmbols
"""
import numpy as np
from vita.modules.utils.physics_constants import get_physics_constants

class TokamakParameters():
    '''
    Class for storing parameters of the tokamak we are examining

    The inputs are:
        machine params, a dict with:
            V, plasma volume
            R_0, major radius
            a, minor radius
            q_95, safety factor
        pedestal params, a dict with:
            t_e, electron temperature at the pedestal
            t_i, ion temperature at the pedestal
            n, density at the pedestal
            Z, charge number
    '''
    def __init__(self, machine_params, pedestal_params):
        self.pedestal_params = pedestal_params
        self.machine_params = machine_params
        self.physics_constants = get_physics_constants()
        self.lambda_debye = self._calculate_debye_length()
        self.coulomb_log = self._calculate_coulomb_logarithm()
        self.lambda_ee = self._calculate_electron_collision_mfp()
        self.collisionality = self._calculate_collisionality()

    def _calculate_debye_length(self):
        '''
        The debye length is defined as:

            lambda_D = sqrt(epsilon_0*T_e/(n_e*Z*e)),

        where epsilon_0 is the permittivity of free space, T_e is the electron
        temperature in eV, n_e is the electron density in SI, Z is the charge
        number, and e is the elementary charge.

        Returns
        -------
        lambda_D : float
            The debye length in SI of the plasma with the given parameters

        '''
        return np.sqrt(self.physics_constants["epsilon_0"]*self.pedestal_params["t_e"]\
                               /(self.pedestal_params["n"]*self.pedestal_params["Z"]\
                                 *self.physics_constants["e"]))

    def _calculate_coulomb_logarithm(self):
        '''
        The Coulomb logarithm is defined as:

            log(Lambda) = log(12*pi*n_e*lambda_D^3/Z),

        where n_e is the electron density in SI, lambda_D is the debye length,
        and Z is the charge number

        Returns
        -------
        log(Lambda) : float
            The Coulomb logarithm of the plasma with the given parameters

        '''
        return np.log(12*np.pi*self.pedestal_params["n"]*self.lambda_debye**3\
                      /self.pedestal_params["Z"])

    def _calculate_electron_collision_mfp(self):
        '''
        The electron-electron Coulomb collision mean free path is defined as:

            lambda_ee = 1.2*10^16 * (T_e^2/(n_e Z)) * (17/log(Lambda)),

        where the 1.2*10^16 is from various physics constants, T_e is the
        electron temperature in eV, n_e is the electron density in SI,
        Z is the charge number of the plasma, and log(Lambda) is the Coulomb logarithm.

        Returns
        -------
        lambda_ee : float
            The electron-electron Coulomb collision mean free path in SI

        '''
        return 1.2e16*(self.pedestal_params["t_e"]**2/(self.pedestal_params["n"]\
                                                       *self.pedestal_params["Z"]))\
                     *(17/self.coulomb_log)

    def _calculate_collisionality(self):
        '''
        The collisionality is defined as:

            nu_ee^* = R_0 q_95 (a/R_0)^(-3/2)*(lambda_ee)^(-1),

        where R_0 is the major radius, q_95 is the safety factor, a is the minor
        radius, and lambda_ee is electron-electron Coulomb collision mean free
        path.

        Returns
        -------
        nu_ee^* : float
            The plasma collisionality.

        '''
        return self.machine_params["R_0"]*self.machine_params["q_95"]\
                             *(self.machine_params["a"]/self.machine_params["R_0"])**(-3/2)\
                             *self.lambda_ee**(-1)
