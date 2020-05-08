# -*- coding: utf-8 -*-
"""
Created on Fri May 24 08:37:37 2019

@author: Daniel.Iglesias@tokamakenergy.co.uk
"""
from vita.modules.utils.getOption import getOption

from os.path import join as pjoin
import os
import numpy as np
import scipy.io as sio
import vtk
#from vtk.util.misc import vtkGetDataRoot

class PsiRepresentation():
        '''
    Class for creating the mapping of Fiesta equilibrium Psi field, including VTK representations.

    Member functions:
        Psi2D()
        Psi3D()
    '''
    def __init__(self, fiesta):
        self.fiesta_equil = fiesta


    def PsiVTK(mat_contents, path, machine, eq_name) :
        path_out = pjoin('/home/daniel.iglesias/Projects/divertor-physics-interface/Plasma_scenarios/', machine)
    #    path_out = pjoin('C://Users//Daniel.Ibanez//Projects//divertor_physics_interface//', machine)
        if not os.path.exists(path_out):
            os.makedirs(path_out)
        mat_fname = pjoin(path, machine, 'python_responses', eq_name + '.mat')
        print("Processing file: " + mat_fname)
        mat_contents = sio.loadmat(mat_fname)
        sorted(mat_contents.keys())
        
        ###########################################################
        # CREATE ARRAY VALUES
        ###########################################################
        # Just create some fancy looking values for z.
        n = mat_contents['r'].size
        m = mat_contents['z'].size
        l = 13 # Toroidal resolution
        xmin = np.min(mat_contents['r'])
        xmax = np.max(mat_contents['r'])
        ymin = np.min(mat_contents['z'])
        ymax = np.max(mat_contents['z'])
        phimax = 180.0
        x = np.linspace(xmin, xmax, n) # x is the radius
        y = np.linspace(ymin, ymax, m) # y is vertical axis
        x, y = np.meshgrid(x, y)
        x, y = x.flatten(), y.flatten()
        phi = np.linspace(0.0,phimax,l) # toroidal angle
        delta_phi = phimax/(l-1)
        zz = mat_contents['psi_n']
        z = zz.flatten() # CAUTION: using z as the values
        print (len(z))
        
        
        ###########################################################
        # CREATE PLANE
        ###########################################################
        # Create a planar mesh of quadriliterals with nxm points.
        # (SetOrigin and SetPointX only required if the extent
        # of the plane should be the same. For the mapping
        # of the scalar values, this is not required.)
        plane = vtk.vtkPlaneSource()
        plane.SetResolution(n-1,m-1)
        plane.SetOrigin([xmin,ymin,0])  # Lower left corner
        plane.SetPoint1([xmax,ymin,0])
        plane.SetPoint2([xmin,ymax,0])
        plane.Update()
        
        # Map the values to the planar mesh.
        # Assumption: same index i for scalars z[i] and mesh points
        nPoints = plane.GetOutput().GetNumberOfPoints()
        print (nPoints)
        assert(nPoints == len(z))
        # VTK has its own array format. Convert the input
        # array (z) to a vtkFloatArray.
        scalars = vtk.vtkFloatArray()
        scalars.SetNumberOfValues(nPoints)
        for i in range(nPoints):
        #    if z[i] < 1.0:
        #        z[i] = 1.0
        #    if z[i] > 1.5:
        #        z[i] = 1.5
            scalars.SetValue(i, z[i])
        # Assign the scalar array.
        plane.GetOutput().GetPointData().SetScalars(scalars)
        
        ###########################################################
        # WRITE PLANE DATA
        ###########################################################
        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName( pjoin(path_out, 'Psi_n_' + eq_name + '_plane_x-y.vtp') )
        writer.SetInputConnection(plane.GetOutputPort())
        writer.Write() # => Use for example ParaView to see scalars
        
        ###########################################################
        # WRITE MAGNETIC FIELD DATA
        ###########################################################
        BrMat = mat_contents['Br']
        BphiMat = mat_contents['Bphi']
        BzMat = mat_contents['Bz']
        Br = BrMat.flatten()
        Bphi = BphiMat.flatten()
        Bz = BzMat.flatten()
        BthetaMat = mat_contents['Btheta']
        Btheta = BthetaMat.flatten()

        ###########################################################
        # CREATE CYLINDER
        ###########################################################
        structuredGrid = vtk.vtkStructuredGrid()
        dataIndex = 0
        dims = [l,n,m] # theta, radius, Z
        structuredGrid.SetDimensions(dims)
        points = vtk.vtkPoints()
        points.Allocate(n*m*l)
        scalars2 = vtk.vtkFloatArray()
        scalarBtheta = vtk.vtkFloatArray()
        B = vtk.vtkDoubleArray()
        B.SetName("B");
        B.SetNumberOfComponents(3);
        B.SetNumberOfTuples(n*m*l);
        print ("Number of points", structuredGrid.GetNumberOfPoints())
        deltaZ = (ymax-ymin) / (dims[2]-1);
        deltaRad = (xmax-xmin) / (dims[1]-1);
        for k in range(dims[2]) : #( k=0; k<dims[2]; k++)
            x[2] = -1.0 + k*deltaZ
            kOffset = k * dims[0] * dims[1]
            for j in range(dims[1]) : #(j=0; j<dims[1]; j++)
            radius = xmin + j*deltaRad
            jOffset = j * dims[0]
            for i in range(dims[0]) : #(i=0; i<dims[0]; i++)
                dataIndex = j + k * dims[1]
                theta = i * vtk.vtkMath.RadiansFromDegrees(delta_phi)
                x[0] = radius * np.cos(theta)
                x[1] = radius * np.sin(theta)
                offset = i + jOffset + kOffset
                points.InsertPoint(offset,x[0],x[1],x[2])
                scalars2.InsertNextTuple1( z[dataIndex] )
                scalarBtheta.InsertNextTuple1( Btheta[dataIndex] )
                Bx = Br[dataIndex]*np.cos(theta) - Bphi[dataIndex]*np.sin(theta)
                By = Br[dataIndex]*np.sin(theta) + Bphi[dataIndex]*np.cos(theta)
                B.SetTuple3(offset, Bx, By, Bz[dataIndex])
        #        array.SetValue(offset, z[j + k * dims[1] ])
        structuredGrid.SetPoints(points)
        structuredGrid.GetPointData().SetScalars( scalars2 )
    #    structuredGrid.GetPointData().SetScalars( scalarBtheta )
        structuredGrid.GetPointData().SetVectors( B )
        
        ###########################################################
        # WRITE CYLINDER DATA
        ###########################################################
        writer2 = vtk.vtkXMLStructuredGridWriter()
        writer2.SetFileName( pjoin(path_out, 'Psi_n_' + eq_name + '_cylinder.vts') )
        writer2.SetInputData(structuredGrid)
        writer2.Write() # => Use for example ParaView to see scalars
        
        ###########################################################
        # CONVERT TO UNSTRUCTURED GRID
        ###########################################################
        #appendFilter = vtk.vtkAppendFilter()
        #appendFilter.AddInputData(plane.GetOutput())
        #
        #unstructuredGrid = vtk.vtkUnstructuredGrid()
        #unstructuredGrid.ShallowCopy(appendFilter.GetOutput())
        #
        #writer2 = vtk.vtkXMLUnstructuredGridWriter()
        #writer2.SetFileName("UnstructuredGrid.vtu")
        #writer2.SetInputData(unstructuredGrid);
        #writer2.Write();


