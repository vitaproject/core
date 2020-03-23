#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 17/12/2019

@author: james bland, based on code of jmbols
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import interp2d
from scipy.constants import mu_0
from scipy.constants import e as e_charge
# %%


class ParticlePath():
    '''
    Class for determining the path of a charged particle in a magnetic field
    given a Fiesta equilibrium.

    Member functions:
        follow_path(p_0, max_time, max_points, rtol, break_at_limiter)
    '''

    def __init__(self, charge_mass_ratio, fiesta, charge=e_charge):
        '''
        Class constructor, initialses variables and the interpolation functions
        to determine the B field, the gradient of magnitude of the B field, and
        the curl of the B field unit vector.
        '''
        self.fiesta = fiesta
        self.r_vec = fiesta.r_vec
        self.z_vec = fiesta.z_vec

        self.ze_m = charge_mass_ratio
        self.full_charge = charge

        self.r_vec = self.r_vec.reshape(-1)
        self.z_vec = self.z_vec.reshape(-1)

        self.interp_b_r = interp2d(self.r_vec, self.z_vec, self.fiesta.b_r, kind='cubic')
        self.interp_b_z = interp2d(self.r_vec, self.z_vec, self.fiesta.b_z, kind='cubic')

        b_mag = np.sqrt(self.fiesta.b_r**2 + self.fiesta.b_phi**2 + self.fiesta.b_z**2)
        grad_b_z, grad_b_r = np.gradient(b_mag, self.z_vec, self.r_vec)
        self.interp_grad_b_z = interp2d(self.r_vec, self.z_vec, grad_b_z, kind='cubic')
        self.interp_grad_b_r = interp2d(self.r_vec, self.z_vec, grad_b_r, kind='cubic')

        r_grid = np.tile(self.r_vec, (len(self.z_vec), 1))

        grad_b_r_dz, _ = np.gradient(self.fiesta.b_r/b_mag, self.z_vec, self.r_vec)
        grad_b_phi_dz, _ = np.gradient(self.fiesta.b_phi/b_mag, self.z_vec, self.r_vec)
        _, grad_b_z_dr = np.gradient(self.fiesta.b_z/b_mag, self.z_vec, self.r_vec)
        _, grad_r_b_phi_dr = np.gradient(r_grid*(self.fiesta.b_phi/b_mag),
                                         self.z_vec, self.r_vec)

        curl_b_dir = np.array([-grad_b_phi_dz, grad_b_r_dz-grad_b_z_dr, (1/r_grid)*grad_r_b_phi_dr])

        self.interp_curl_b_dir_r = interp2d(self.r_vec, self.z_vec, curl_b_dir[0, :, :].squeeze(),
                                            kind='cubic')
        self.interp_curl_b_dir_phi = interp2d(self.r_vec, self.z_vec, curl_b_dir[1, :, :].squeeze(),
                                              kind='cubic')
        self.interp_curl_b_dir_z = interp2d(self.r_vec, self.z_vec, curl_b_dir[2, :, :].squeeze(),
                                            kind='cubic')

    def exact_b_phi(self, r_pos):
        '''
        calculate the exact Bphi value dependent on the radial position
        '''
        return mu_0 * self.fiesta.i_rod / (2 * np.pi * r_pos)

    def follow_path(self, p_0, max_time=1e-4, max_points=1000, rtol=1e-13,
                    break_at_limiter=True):
        '''
        Function following the path of a particle in a magnetic field given a
        starting point, in accordance to the guiding centre method presented by
        Otto in his thesis.  Have assumed d/dt A_star is 0.  Solves the set of
        coupled ODEs for the vector position, parallel velocity and magnetic moment

        input: self,        the object parameters
               p_0,         a tuple with the initial position and velocity of the particle
               max_time, a float with the maximum time
               max_points,  an integer with the maximum number of points
                            used when solving the ODE
               rtol,             a float with the maximum relative error tolerance
               break_at_limiter, a boolean with true if you don't want the ODE solver
                                 to continue after the field line intersects the vessel limits

        return: field_line, a dictionary with the r, phi, z, v_parallel and the
        (magnetic) moment components of the particle along its path
        '''

        def dlorentz_dt(time, vec):
            '''
            The function describing the ode to solve in order to track the
            location of patricle in a magnetic field (in accordance to the
            lorentz equation)

            input: Time, time variable
                   Vec,  vector of the form [r, phi, z, v_r, v_phi, v_z]

            return: DVecDt, the right-hand side of the ode to solve
            '''

            d_vec_dt = np.zeros(len(vec))

            d_vec_dt[:3] = vec[3:]

            b_r_local = self.interp_b_r(vec[0], vec[2])
            b_phi_local = self.exact_b_phi(vec[0])
            b_z_local = self.interp_b_z(vec[0], vec[2])

            d_vec_dt[3] = self.ze_m*(vec[4]*b_z_local - vec[5]*b_phi_local)
            d_vec_dt[4] = self.ze_m*(vec[5]*b_r_local - vec[3]*b_z_local)
            d_vec_dt[5] = self.ze_m*(vec[3]*b_phi_local - vec[4]* b_r_local)

            return d_vec_dt

        def dvec_dt(time, vec):
            '''
            The function describing the ode to solve in order to track the
            location of patricle in a magnetic field (in accordance with the
            guiding centre particle equation)

            input: Time, time variable
                   Vec,  vector of the form [r, phi, z, v_para, moment]

            return: DVecDt, the right-hand side of the ode to solve
            '''

            pos_vec = vec[:3]

            v_para = vec[3]

            mag_moment = vec[4]

            b_0 = np.array([self.interp_b_r(pos_vec[0], pos_vec[2]),
                            self.exact_b_phi(pos_vec[0]),
                            self.interp_b_z(pos_vec[0], pos_vec[2])]).reshape(-1)

            grad_b_0 = np.array([self.interp_grad_b_r(pos_vec[0], pos_vec[2]),
                                 np.zeros(1),
                                 self.interp_grad_b_z(pos_vec[0], pos_vec[2])]).reshape(-1)

            b_mag_local = np.sqrt(np.sum(b_0**2))

            dir_local = b_0 / b_mag_local

            curl_dir_local = np.array([self.interp_curl_b_dir_r(pos_vec[0], pos_vec[2]),
                                       self.interp_curl_b_dir_phi(pos_vec[0], pos_vec[2]),
                                       self.interp_curl_b_dir_z(pos_vec[0], pos_vec[2])]).reshape(-1)

            b_star = b_0 + np.multiply((v_para /self.ze_m), curl_dir_local)

            b_star_para = np.dot(b_star, dir_local)

            e_star = -(mag_moment/(self.full_charge))*grad_b_0

            d_r_dt = v_para*(b_star/b_star_para) + (np.cross(e_star.reshape(1, -1),
                                                             dir_local.reshape(1, -1))/b_star_para)

            d_v_para_dt = self.ze_m * np.dot(b_star, e_star) / b_star_para

            d_mu_dt = 0

            d_vec_dt = np.zeros(len(vec))

            d_vec_dt[0:3] = d_r_dt

            d_vec_dt[3] = d_v_para_dt

            d_vec_dt[4] = d_mu_dt

            return d_vec_dt

        def event(time, vec):
            '''
            Function for determining whether the solution to the ODE passes a wall,
            which terminates the ODE solver

            input: l_dist, np.array with the distance along the magnetic field-line
                   x_vec,  vector with the R, phi and Z initial positions

            return: intersect_wall, returns 0 if any wall surface is intersected,
                                    otherwise returns a float (the event function of
                                    solve_ivp only looks for events = 0)

            '''

            displacement = 0.001
            inner_wall = np.min(self.fiesta.r_limiter) - displacement
            lower_wall = np.min(self.fiesta.z_limiter) - displacement
            outer_wall = np.max(self.fiesta.r_limiter) + displacement
            upper_wall = np.max(self.fiesta.z_limiter) + displacement

            intersect_wall = (vec[0] - inner_wall)*(vec[2] - lower_wall)\
                             *(vec[0] - outer_wall)*(vec[2] - upper_wall)

            return intersect_wall


        def event2(time, vec):
            '''
            Function for determining whether the solution to the ODE passes a wall,
            which terminates the ODE solver

            input: l_dist, np.array with the distance along the magnetic field-line
                   x_vec,  vector with the R, phi and Z initial positions

            return: intersect_wall, returns 0 if any wall surface is intersected,
                                    otherwise returns a float (the event function of
                                    solve_ivp only looks for events = 0)
            '''

            displacement = 0.01
            inner_wall2 = np.min(self.fiesta.r_limiter) - displacement
            lower_wall2 = np.min(self.fiesta.z_limiter) - displacement
            outer_wall2 = np.max(self.fiesta.r_limiter) + displacement
            upper_wall2 = np.max(self.fiesta.z_limiter) + displacement

            intersect_wall = (vec[0] - inner_wall2)*(vec[2] - lower_wall2)\
                             *(vec[0] - outer_wall2)*(vec[2] - upper_wall2)

            return intersect_wall

        if break_at_limiter:
            event.terminal = True

        time_points = np.linspace(0.0, max_time, max_points)

        ivp_solution = solve_ivp(fun=dvec_dt, t_span=tuple([0.0, max_time]),
                                 y0=p_0, t_eval=time_points,
                                 rtol=rtol, atol=1e-13,
                                 events=event, method='RK45')

        field_line = {}
        field_line['time'] = np.array(ivp_solution.t[:])
        field_line['r'] = ivp_solution.y[0, :]
        field_line['phi'] = ivp_solution.y[1, :]
        field_line['z'] = ivp_solution.y[2, :]
        field_line['v_para'] = ivp_solution.y[3, :]
        field_line['moment'] = ivp_solution.y[4, :]

        num_points = len(field_line['time'])

        v_perp = np.zeros(num_points)
        b_mag = np.zeros(num_points)
        b_dir = np.zeros((num_points, 3))

        for i in range(num_points):

            b_r_local = self.interp_b_r(field_line['r'][i], field_line['z'][i])[0]
            b_phi_local = self.exact_b_phi(field_line['r'][i])
            b_z_local = self.interp_b_z(field_line['r'][i], field_line['z'][i])[0]

            b_mag[i] = np.sqrt(b_r_local**2 + b_phi_local**2 + b_z_local**2)

            v_perp[i] = np.sqrt(2 * b_mag[i] * np.abs(field_line['moment'][i])\
                        * (self.ze_m /self.full_charge))

            b_dir[i, :] = np.array([b_r_local, b_phi_local, b_z_local]) / b_mag[i]


        field_line['v_perp'] = v_perp
        field_line['B_mag'] = b_mag

        if ivp_solution.t_events[0].size != 0 and num_points > 3:
            '''
            if particle undergoes collision, redo last time steps using the
            lorentz formula equation
            '''
            max_time = max_time * 0.05

            time_points = np.linspace(0.0, max_time, max_points)

            start_vec = np.zeros(6)

            start_vec[:3] = np.array([field_line['r'][-2], 0, field_line['z'][-2]])

            d_r = start_vec[:3] - np.array([field_line['r'][-3], 0, field_line['z'][-3]])

            d_r = d_r / np.sqrt(np.sum(d_r**2))

            start_vec[3:] = field_line['v_para'][-2] * b_dir[-2, :]\
                            + v_perp[-2] * np.cross(d_r, b_dir[-2, :])

            ivp_solution = solve_ivp(fun=dlorentz_dt, t_span=tuple([0.0, max_time]),
                                     y0=start_vec, t_eval=time_points,
                                     rtol=rtol, atol=1e-13,
                                     events=event2, method='RK45')

            field_line['r_lorentz'] = ivp_solution.y[0, :]
            field_line['phi_lorentz'] = ivp_solution.y[1, :]
            field_line['z_lorentz'] = ivp_solution.y[2, :]
            field_line['r_tot'] = np.concatenate((field_line['r'][:-2], ivp_solution.y[0, :]))
            field_line['phi_tot'] = np.concatenate((field_line['phi'][:-2], ivp_solution.y[1, :]))
            field_line['z_tot'] = np.concatenate((field_line['z'][:-2], ivp_solution.y[2, :]))

        else:
            field_line['r_lorentz'] = np.array([])
            field_line['phi_lorentz'] = np.array([])
            field_line['z_lorentz'] = np.array([])
            field_line['r_tot'] = field_line['r']
            field_line['phi_tot'] = field_line['phi']
            field_line['z_tot'] = field_line['z']

        return field_line
