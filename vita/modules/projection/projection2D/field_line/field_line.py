#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 15:38:46 2019

@author: jmbols
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import interp2d
from scipy.constants import mu_0 as mu0
import matplotlib.pyplot as plt
from vita.utility import get_resource
from vita.modules.equilibrium.fiesta.fiesta_interface import Fiesta

class FieldLine():
    '''
    Class for following a magnetic field line given a Fiesta equilibrium.

    Member functions:
        follow_field_in_plane(p_0, max_length, max_points, rtol)
    '''
    def __init__(self, fiesta):
        self.fiesta_equil = fiesta

    def follow_field_in_plane(self, p_0, max_length=10.0, max_points=2000, rtol=2e-10,
                              break_at_limiter=True):
        '''
        Function following the magnetic field-lines given a starting point

        solves the set of coupled ODEs:

            d/dl R   = B_r / (|B|)
            d/dl phi = B_phi / (R |B|)
            d/dl Z   = B_z / (|B|),

        where B_r, B_phi, B_z are the cylindrical components of the magnetic field, |B| is the
        magnitude of the magnetic field, R, phi and Z are the cylindrical
        positions of the field line
        and l is the length along the magnetic field line

        input: self,        the object parameters
               p_0,         a tuple with the initial position of the field-line to be tracked
               maxl_length, a float with the maximum length of the field lines used for
                            solving the set of ODE's
               max_points,  an integer with the maximum number of radial points
                            used when solving the ODE
               rtol,             a float with the maximum relative error tolerance
               break_at_limiter, a boolean with true if you don't want the ODE solver
                                 to continue after the field line intersects the vessel limits

        return: field_line, a dictionary with the R, phi and Z components along the field line
        '''

        def dx_dl(_l_dist, x_vec):
            '''
            The function describing the ode to solve in order to track the magnetic field lines

            input: l_dist, np.array with the distance along the magnetic field-line
                   x_vec,  vector with the R, phi and Z initial positions

            return: dx_dl_rhs, the right-hand side of the ode to solve
            '''
            r_init = x_vec[0]
            z_init = x_vec[2]

            br_interp = interp2d(self.fiesta_equil.r_vec, self.fiesta_equil.z_vec,
                                 self.fiesta_equil.b_r)
            bz_interp = interp2d(self.fiesta_equil.r_vec, self.fiesta_equil.z_vec,
                                 self.fiesta_equil.b_z)
            br_init = br_interp(r_init, z_init)[0]
            br_interp = None
            bz_init = bz_interp(r_init, z_init)[0]
            bz_interp = None
            bphi_init = self.fiesta_equil.i_rod*mu0 / (2*np.pi*r_init)

            b_mag = np.sqrt(br_init**2 + bphi_init**2 + bz_init**2)

            dx_dl_rhs = np.zeros(3)
            dx_dl_rhs[0] = br_init / b_mag
            dx_dl_rhs[1] = bphi_init / (r_init * b_mag)
            dx_dl_rhs[2] = bz_init / b_mag

            return dx_dl_rhs

        # We don't want to find min and max at each solve_ivp timestep and
        # we want to be able to calculate the exact point of intersection hence
        # the addition or subtraction of 0.00025 (no intersection occurs if we
        # terminate the evaluation at the point of intersection)
        displacement = 0.00025
        inner_wall = min(self.fiesta_equil.r_limiter) - displacement
        lower_wall = min(self.fiesta_equil.z_limiter) - displacement
        outer_wall = max(self.fiesta_equil.r_limiter) + displacement
        upper_wall = max(self.fiesta_equil.z_limiter) + displacement

        def event(_l_dist, x_vec):
            '''
            Function for determining whether the solution to the ODE passes a wall,
            which terminates the ODE solver

            input: l_dist, np.array with the distance along the magnetic field-line
                   x_vec,  vector with the R, phi and Z initial positions

            return: intersect_wall, returns 0 if any wall surface is intersected,
                                    otherwise returns a float (the event function of
                                    solve_ivp only looks for events = 0)
            '''
            intersect_wall = (x_vec[0] - inner_wall)*(x_vec[2] - lower_wall)\
                             *(x_vec[0] - outer_wall)*(x_vec[2] - upper_wall)
            return intersect_wall
        if break_at_limiter:
            event.terminal = True

        dist_along_fieldline = np.linspace(0.0, max_length, max_points)

        ivp_solution = solve_ivp(fun=dx_dl, t_span=tuple([0.0, max_length]),
                                 y0=p_0, t_eval=dist_along_fieldline,
                                 events=event, rtol=rtol)

        field_line = {}
        field_line['l'] = np.array(ivp_solution.t[:])
        field_line['R'] = ivp_solution.y[0, :]
        field_line['phi'] = ivp_solution.y[1, :]
        field_line['Z'] = ivp_solution.y[2, :]

        return field_line

if __name__ == '__main__':
    FILEPATH = get_resource("ST40-IVC1", "equilibrium", "eq_006_2T_export")
    #FILEPATH = '/home/jmbols/Postdoc/ST40/Programme 1/Equilibrium/eq001_limited.mat
    FIESTA = Fiesta(FILEPATH)
    FIELD_LINE = FieldLine(FIESTA)
    #print(FIELD_LINE.fiesta_equil.r_vec)
    LCFS_INDEX = [0.18, 0.75, 0.79]
    FIELD_LINE_DICTS = {}
    for i in LCFS_INDEX:
        P_0 = [i, 0, 0]
        FIELD_LINE_DICT = FIELD_LINE.follow_field_in_plane(p_0=P_0, max_length=200.0)
        FIELD_LINE_DICTS[i] = FIELD_LINE_DICT
        plt.plot(FIELD_LINE_DICT['R'], FIELD_LINE_DICT['Z'])
