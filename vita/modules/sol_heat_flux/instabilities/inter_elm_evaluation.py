#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 11:44:16 2020

@author: jmbols
"""

import numpy as np
from vita.modules.sol_heat_flux.instabilities.tokamak_params import TokamakParameters

class InterELM(TokamakParameters):
    def __init__(self, machine_params, pedestal_params, lambda_q_fit):
        TokamakParameters.__init__(self, machine_params, pedestal_params)
        self.lambda_q_fit = lambda_q_fit

    def _evaluate_lambda_q(self):
        if self.lambda_q_fit == "MAST":
            lambda_q_low = (4.57-0.54)*self.machine_params["I_p"]**(-0.64-0.15)\
                            *self.machine_params["P_sol"]**(0.22-0.08)
            lambda_q_high = (4.57+0.54)*self.machine_params["I_p"]**(-0.64+0.15)\
                            *self.machine_params["P_sol"]**(0.22+0.08)
            lambda_q = (4.57)*self.machine_params["I_p"]**(-0.64)\
                            *self.machine_params["P_sol"]**(0.22)

            return [lambda_q_low, lambda_q, lambda_q_high]

        elif self.lambda_q_fit == "Multi-machine-Eich-2013":
            lambda_q_low = (0.63-0.08)*self.machine_params["B_pol"]**(-1.19-0.08)
            lambda_q_high = (0.63+0.08)*self.machine_params["B_pol"]**(-1.19+0.08)
            lambda_q = (0.63)*self.machine_params["B_pol"]**(-1.19)

            return [lambda_q_low, lambda_q, lambda_q_high]