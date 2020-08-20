#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 11:42:44 2020

@author: jmbols
"""
import numpy as np
from vita.modules.sol_heat_flux.instabilities.tokamak_params import TokamakParameters

class ELM(TokamakParameters):
    '''
    Class for determining the size, wetted area, and transport time from the OMP
    to the divertor for ELMs, given a set of machine and pedestal parameters
    '''
    def __init__(self, machine_params, pedestal_params, lambda_q=2.0e-3):
        TokamakParameters.__init__(self, machine_params, pedestal_params)
        self.size = self._determine_elm_size()
        self.tau_parallel = self._determine_parallel_transport_time()
        self.tau_ir = self._determine_tau_ir()
        self.ped_energy = self._calculate_pedestal_energy()
        self.elm_energy = self.size*self.ped_energy
        self.lambda_q = lambda_q

    def _determine_elm_size(self):
        '''
        The size of an ELM has been found to be scale with the collisionality
        at the pedestal. The scaling is:

            Delta W_ELM/W_ped = a*log(nu_ee^*),

        where Delta W_ELM/W_ped is the relative size of the ELM, a is a fitting
        parameter and nu_ee^* is the collisionality. The parameters for the fit
        are taken from Fig. 14 in [1]

        [1] A W Leonard 2014 Phys. Plasmas 21, 090501
            Edge-localised-modes in tokamaks

        Returns
        -------
        Delta W_ELM/W_ped : float
            The relative ELM size with respect to the stored pedestal energy.

        '''
        delta_w_elm = [0.2, 0.075]
        log_nu_ee = [np.log(0.06), 0]
        delta_w_elm_fit = np.polyfit(log_nu_ee, delta_w_elm, 1)
        fit_delta_w_elm = np.poly1d(delta_w_elm_fit)

        return fit_delta_w_elm(np.log(self.collisionality))

    def _determine_parallel_transport_time(self):
        '''
        The time it takes for the ions to travel from the OMP to the divertor
        is given by the distance they travel divided by the speed with which they
        travel. The distance from the OMP to the divertor is assumed to be

            L_parallel = 2 pi q_95 R_0

        where q_95 is the safety factor, and R_0 is the major radius. The ions
        are assumed to propagate at the ion sound speed, defined as

            c_s = sqrt(e(T_e + T_i)/m_i),

        where e is the elementary charge, T_e(i) is the electron (ion) temperature
        in eV at the middle of the pedestal (assumed to be half the pedestal top value),
        and m_i is the ion mass.

        The parallel transport time is thus

            tau_parallel = L_parallel/c_s

        Returns
        -------
        tau_parallel : float
            The parallel transport time of the ions in SI

        '''
        return 2*np.pi*self.machine_params["q_95"]*self.machine_params["R_0"]\
            /np.sqrt(self.physics_constants["e"]\
                     *(self.pedestal_params["t_e"]/2+self.pedestal_params["t_i"]/2)\
                     /self.physics_constants["m_p"])
                #N.B. this needs to be ion mass, not proton mass

    def _determine_tau_ir(self):
        '''
        The rise time of the ELM at the divertor is found to scale with the
        parallel transit time of the ions from the OMP to the divertor.
        The scaling is taken from Fig. 17 in [1], where I have read three
        points on the graph and made a linear fit.
        The linear fit model breaks down at 80 microseconds, since the rise time
        of the ELM heat flux cannot be smaller than the parallel transit time,
        which occurs at this point.

        [1] A W Leonard 2014 Phys. Plasmas 21, 090501
            Edge-localised-modes in tokamaks

        Returns
        -------
        tau_IR : float
            The rise time of the ELM in SI

        '''
        if self.tau_parallel < 80e-6:
            return self.tau_parallel

        tau_parallel_in_mu_s = [100, 200, 250]
        tau_ir_in_mu_s = [150, 400, 600]
        tau_ir_fit = np.polyfit(tau_parallel_in_mu_s, tau_ir_in_mu_s, 1)
        fit_tau_ir = np.poly1d(tau_ir_fit)

        return fit_tau_ir(self.tau_parallel*1e6)*1e-6

    def _calculate_pedestal_energy(self):
        '''
        The ELM energy is typically normalised with the pedestal energy, which
        is defined as

            W_ped = 3/2*n_e,ped*(T_e,ped + T_i,ped)*e*V_plasma,

        where n_e,ped is the density at the top of the pedestal in SI units,
        T_e(i),ped is the electron (ion) temperature at the top of the pedestal
        in eV, e is the elementary charge and V_plasma is the volume of the
        plasma inside the LCFS

        Returns
        -------
        w_ped : float
            The stored pedestal energy in SI

        '''
        w_ped = 3/2*self.pedestal_params["n"]*(self.pedestal_params["t_e"]\
                                               + self.pedestal_params["t_i"])\
                                              *self.physics_constants["e"]\
                                              *self.machine_params["V"]
        return w_ped

    def _calculate_wetted_area(self):
        '''
        ELM wetted area depends on mode number. However, it has been found to be
        in the range of 3-6 times the inter-ELM wetted area[1]. Assuming this,
        we calculate the range of the ELM wetted area as

            A_ELM = [3, 6]*lambda_q

        [1] A J Thornton et al. 2017 Plasma Phys. Control. Fusion 59 014047
            The role of ELM filaments in setting the ELM wetted area in MAST
            and the implications for future devices

        Returns
        -------
        A_ELM : 2-by-1 np.array
            A numpy array with the ranges for the wetted area of the ELM, based
            on the inter-ELM wetted area.

        '''
        return np.array([3, 6])*self.lambda_q
