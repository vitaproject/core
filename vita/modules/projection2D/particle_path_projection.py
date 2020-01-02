#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 17/12/2019

@author: james bland, based on code of jmbols
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import interp2d
import matplotlib.pyplot as plt
from scipy.constants import mu_0, m_p, m_n
from scipy.constants import e as e_charge
import scipy.io as sio
# %%


class ParticlePath():
    '''
    Class for determining the path of a charged particle in a magnetic field
    given a Fiesta equilibrium.

    Member functions:
        follow_path(p_0, max_time, max_points, rtol, break_at_limiter)
    '''
    
    def __init__(self, Ze_m, Data, Charge=e_charge):
        ''' 
        Class constructor, initialses variables and the interpolation functions
        to determine the B field, the gradient of magnitude of the B field, and
        the curl of the B field unit vector.    
        '''
        self.r = None
        self.z = None
        self.Br = None
        self.Bz = None
        self.Bphi = None
        self.psi = None
        self.R_limits = None
        self.Z_limits = None
        self.irod = None 
        self.Ze_m = Ze_m
        self.FullCharge = Charge

        AttrList = self.__dict__.keys()
        for key in AttrList:
            if getattr(self,key) is None:
               if key in Data:
                   setattr(self,key,Data[key])
               else:
                   raise Exception('class attribute' + key + ' not set')
        
        self.r = self.r.reshape(-1)
        self.z = self.z.reshape(-1)
        self.irod = self.irod[0]
        
        self.interp_Br = interp2d(self.r, self.z, self.Br, kind ='cubic')
        self.interp_Bphi = interp2d(self.r, self.z, self.Bphi, kind ='cubic')
        self.interp_Bz = interp2d(self.r, self.z, self.Bz, kind ='cubic')
                   
        Bmag = np.sqrt(self.Br**2 + self.Bphi**2 + self.Bz**2)
        GradBZ,GradBR = np.gradient(Bmag, self.z, self.r)
        self.interp_GradBZ = interp2d(self.r, self.z, GradBZ,kind = 'cubic')
        self.interp_GradBR = interp2d(self.r, self.z, GradBR,kind = 'cubic')
        
        Rgrid = np.tile(self.r,(len(self.z),1))

        GradBrDz,GradBrDr = np.gradient(self.Br/Bmag, self.z, self.r)
        GradBphiDz,GradBphiDr = np.gradient(self.Bphi/Bmag, self.z, self.r)
        GradBzDz,GradBzDr = np.gradient(self.Bz/Bmag, self.z, self.r)
        GradRBphiDz,GradRBphiDr = np.gradient(Rgrid * (self.Bphi/Bmag) , self.z, self.r)
        
        CurlBdir = np.array([-GradBphiDz,GradBrDz-GradBzDr,(1/Rgrid)*GradRBphiDr])
        
        self.interp_CurlBdirR = interp2d(self.r, self.z, CurlBdir[0,:,:].squeeze(), kind = 'cubic')
        self.interp_CurlBdirPhi = interp2d(self.r, self.z, CurlBdir[1,:,:].squeeze(), kind = 'cubic')
        self.interp_CurlBdirZ = interp2d(self.r, self.z, CurlBdir[2,:,:].squeeze(), kind = 'cubic')


    def exact_Bphi(self, Rpos):
        '''
        calculate the exact Bphi value dependent on the radial position
        '''
        return mu_0 * self.irod / (2 * np.pi * Rpos)


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

        def dlorentz_dt( Time, Vec):
            '''
            The function describing the ode to solve in order to track the
            location of patricle in a magnetic field (in accordance to the 
            lorentz equation)
        
            input: Time, time variable
                   Vec,  vector of the form [r, phi, z, v_r, v_phi, v_z]
        
            return: DVecDt, the right-hand side of the ode to solve
            '''
            
            DVecDt = np.zeros(len(Vec))
            
            DVecDt[:3] = Vec[3:]
             
            BrHere = self.interp_Br(Vec[0], Vec[2])
            BphiHere = self.exact_Bphi(Vec[0])
            BzHere = self.interp_Bz(Vec[0], Vec[2])
                         
            DVecDt[3] = self.Ze_m*(Vec[4]*BzHere - Vec[5]*BphiHere)    
            DVecDt[4] = self.Ze_m*(Vec[5]*BrHere - Vec[3]*BzHere)     
            DVecDt[5] = self.Ze_m*(Vec[3]*BphiHere - Vec[4]* BrHere)  
            
            return DVecDt
        
        

        def dvec_dt(Time, Vec):
            '''
            The function describing the ode to solve in order to track the
            location of patricle in a magnetic field (in accordance with the 
            guiding centre particle equation)

            input: Time, time variable
                   Vec,  vector of the form [r, phi, z, v_para, moment]

            return: DVecDt, the right-hand side of the ode to solve
            '''

            PosVec = Vec[:3]
            
            Vpara = Vec[3]
            
            MagMoment = Vec[4]
                                    
            B0 = np.array([self.interp_Br(PosVec[0],PosVec[2]),
                           self.exact_Bphi(PosVec[0]),
                           self.interp_Bz(PosVec[0],PosVec[2])]).reshape(-1)
            
            GradB0 =  np.array([self.interp_GradBR(PosVec[0],PosVec[2]),
                                np.zeros(1),
                                self.interp_GradBZ(PosVec[0],PosVec[2])]).reshape(-1)
            
            BmagHere = np.sqrt(np.sum(B0**2))
            
            DirHere = B0 / BmagHere
            
            CurlDirHere = np.array([self.interp_CurlBdirR(PosVec[0],PosVec[2]),
                                    self.interp_CurlBdirPhi(PosVec[0],PosVec[2]),
                                    self.interp_CurlBdirZ(PosVec[0],PosVec[2])]).reshape(-1)
            
            Bstar = B0 + np.multiply((Vpara /self.Ze_m), CurlDirHere)
            
            BstarPara = np.dot(Bstar,DirHere)
            
            Estar = -(MagMoment / (self.FullCharge)) * GradB0
            
            dR_dt = Vpara * (Bstar / BstarPara) + (np.cross(Estar.reshape(1,-1),DirHere.reshape(1,-1))/ BstarPara)
            
            dVpara_dt = self.Ze_m * np.dot(Bstar,Estar) / BstarPara
            
            dMu_dt = 0
                        
            DVec_dt = np.zeros(len(Vec))
            
            DVec_dt[0:3]= dR_dt
            
            DVec_dt[3] = dVpara_dt
            
            DVec_dt[4] = dMu_dt
               
            return DVec_dt 



        def event(Time, Vec):
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
            inner_wall = np.min(self.R_limits) - displacement
            lower_wall = np.min(self.Z_limits) - displacement
            outer_wall = np.max(self.R_limits) + displacement
            upper_wall = np.max(self.Z_limits) + displacement
            
            intersect_wall = (Vec[0] - inner_wall)*(Vec[2] - lower_wall)\
                 *(Vec[0] - outer_wall)*(Vec[2] - upper_wall)

            return intersect_wall
 

        def event2(Time, Vec):
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
            inner_wall2 = np.min(self.R_limits) - displacement
            lower_wall2 = np.min(self.Z_limits) - displacement
            outer_wall2 = np.max(self.R_limits) + displacement
            upper_wall2 = np.max(self.Z_limits) + displacement
            
            intersect_wall = (Vec[0] - inner_wall2)*(Vec[2] - lower_wall2)\
                 *(Vec[0] - outer_wall2)*(Vec[2] - upper_wall2)

            return intersect_wall

         
        if break_at_limiter:
            event.terminal = True

        time_points = np.linspace(0.0, max_time, max_points)

        ivp_solution = solve_ivp(fun=dvec_dt, t_span=tuple([0.0, max_time]),
                                 y0=p_0, t_eval=time_points,
                                 rtol=rtol, atol =1e-13,
                                 events=event, method='RK45')

        field_line = {}
        field_line['time'] = np.array(ivp_solution.t[:])
        field_line['r'] = ivp_solution.y[0, :]
        field_line['phi'] = ivp_solution.y[1, :]
        field_line['z'] = ivp_solution.y[2, :]
        field_line['v_para'] = ivp_solution.y[3, :]
        field_line['moment'] = ivp_solution.y[4, :]
        
        NumPoints = len(field_line['time'])
        
        VPerp = np.zeros(NumPoints)
        BMag = np.zeros(NumPoints)
        BDir = np.zeros((NumPoints, 3))
        
        for ii in range(NumPoints):
            
            BrHere = self.interp_Br(field_line['r'][ii], field_line['z'][ii])[0]
            BphiHere = self.exact_Bphi(field_line['r'][ii])[0]
            BzHere = self.interp_Bz(field_line['r'][ii], field_line['z'][ii])[0]
            
            BMag[ii] = np.sqrt(BrHere**2 + BphiHere**2 + BzHere**2)
            
            VPerp[ii] = np.sqrt( 2 * BMag[ii] * np.abs(field_line['moment'][ii]) \
                        * (self.Ze_m /self.FullCharge))
            
            BDir[ii,:] = np.array([BrHere, BphiHere, BzHere]) / BMag[ii]            
            
            
        field_line['v_perp'] = VPerp
        field_line['B_mag'] = BMag
    
        if ivp_solution.t_events[0].size != 0 and NumPoints > 3:
            '''
            if particle undergoes collision, redo last time steps using the 
            lorentz formula equation
            '''
            max_time = max_time * 0.05
            max_points = max_points
            
            time_points = np.linspace(0.0, max_time, max_points)
            
            StartVec = np.zeros(6)
            
            StartVec[:3] = np.array([field_line['r'][-2], 0, field_line['z'][-2]])
            
            dr = StartVec[:3] - np.array([field_line['r'][-3], 0, field_line['z'][-3]]) 
            
            dr = dr / np.sqrt(np.sum(dr**2))
    
            
            StartVec[3:] = field_line['v_para'][-2] * BDir[-2, :] + \
                           VPerp[-2] * np.cross(dr, BDir[-2, :])
        
            ivp_solution = solve_ivp(fun=dlorentz_dt, t_span=tuple([0.0, max_time]),
                                     y0= StartVec, t_eval=time_points,
                                     rtol=rtol, atol =1e-13,
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
    
    
    


if __name__ == '__main__':
    
   
    FILEPATH = 'C:/Users/James.Bland/Documents/PythonCode/ParticleTracking/eq_0002_150R_300Z_export.mat'
    DATA = sio.loadmat(FILEPATH)
     
    ParticleMass = m_n + m_p
     
    Ze_m = e_charge / ParticleMass
     
    PathObj = ParticlePath(Ze_m, DATA, Charge= e_charge)
    

    
    # %%
    
    InitialPos = np.array([0.728, 0, 0])
            
    BHere = np.array([float(PathObj.interp_Br(InitialPos[0],InitialPos[2])),
                      float(PathObj.exact_Bphi(InitialPos[0])),
                      float(PathObj.interp_Bz(InitialPos[0],InitialPos[2]))])
        
    BMag = np.sqrt(np.sum(BHere**2))
    
    BDir = BHere / BMag
    
    VPara0 = 5e5
    
    MagMo0 = 1e-15 
        
    InitialVec = np.concatenate([InitialPos, np.array([VPara0, MagMo0])])
    
    OUT = PathObj.follow_path(InitialVec)
    
       
# %%
    
    plt.plot(OUT['r_tot'], OUT['z_tot'])
    plt.plot(DATA['R_limits'].T, DATA['Z_limits'].T)
    plt.plot(DATA['lcfs_polygon'][0,:], DATA['lcfs_polygon'][1,:])
    plt.xlabel('r')
    plt.ylabel('z')
    plt.show()
    
    plt.plot(OUT['time'], OUT['v_para'])
    plt.ylabel('vpara')
    plt.show()
    
    plt.plot(OUT['time'], OUT['v_perp'])
    plt.ylabel('vperp')
    plt.show()
    
    plt.plot(OUT['time'], OUT['moment'])
    plt.ylabel('Magnetic moment')
    plt.show()
    
    plt.plot(OUT['time'], OUT['v_para']**2 + OUT['v_perp']**2)
    plt.ylabel('Kinetic Energy')
    plt.show()
    
    plt.plot(OUT['r_lorentz'], OUT['z_lorentz'])
    plt.show()
    
    
    
    
    