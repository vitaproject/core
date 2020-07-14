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


# from vtk.util.misc import vtkGetDataRoot

class PsiRepresentation():
    '''
    Class for creating the mapping of Fiesta equilibrium Psi field, including VTK representations.

    Member functions:
        Psi2D()
        Psi3D()
    '''

    def __init__(self, fiesta):
        self.fiesta_equil = fiesta
        self.zMin = 0.
        self.zMax = 0.
        self.map3D = vtk.vtkStructuredGrid()
        self.map2D = vtk.vtkPlaneSource()

    def psiVTK(self, scale=1.):
        mat_contents = sio.loadmat(self.fiesta_equil)
        sorted(mat_contents.keys())

        ###########################################################
        # CREATE ARRAY VALUES
        ###########################################################
        # Just create some fancy looking values for z.
        n = mat_contents['r'].size
        m = mat_contents['z'].size
        l = 13  # Toroidal resolution
        xmin = np.min(mat_contents['r']) * scale
        xmax = np.max(mat_contents['r']) * scale
        ymin = np.min(mat_contents['z']) * scale
        ymax = np.max(mat_contents['z']) * scale
        phimax = 180.0
        x = np.linspace(xmin, xmax, n)  # x is the radius
        y = np.linspace(ymin, ymax, m)  # y is vertical axis
        x, y = np.meshgrid(x, y)
        x, y = x.flatten(), y.flatten()
        phi = np.linspace(0.0, phimax, l)  # toroidal angle
        delta_phi = phimax / (l - 1)
        zz = mat_contents['psi_n']
        z = zz.flatten()  # CAUTION: using z as the values
        self.zMin = np.min(z)
        self.zMax = np.max(z)

        print(len(z))

        ###########################################################
        # CREATE PLANE
        ###########################################################
        # Create a planar mesh of quadriliterals with nxm points.
        # (SetOrigin and SetPointX only required if the extent
        # of the self.map2D should be the same. For the mapping
        # of the scalar values, this is not required.)
        self.map2D.SetResolution(n - 1, m - 1)
        self.map2D.SetOrigin([xmin, ymin, 0])  # Lower left corner
        self.map2D.SetPoint1([xmax, ymin, 0])
        self.map2D.SetPoint2([xmin, ymax, 0])
        self.map2D.Update()

        # Map the values to the planar mesh.
        # Assumption: same index i for scalars z[i] and mesh points
        nPoints = self.map2D.GetOutput().GetNumberOfPoints()
        print(nPoints)
        assert (nPoints == len(z))
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
        self.map2D.GetOutput().GetPointData().SetScalars(scalars)

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
        dataIndex = 0
        dims = [l, n, m]  # theta, radius, Z
        self.map3D.SetDimensions(dims)
        points = vtk.vtkPoints()
        points.Allocate(n * m * l)
        scalars2 = vtk.vtkFloatArray()
        scalarBtheta = vtk.vtkFloatArray()
        B = vtk.vtkDoubleArray()
        B.SetName("B");
        B.SetNumberOfComponents(3);
        B.SetNumberOfTuples(n * m * l);
        print("Number of points", self.map3D.GetNumberOfPoints())
        deltaZ = (ymax - ymin) / (dims[2] - 1);
        deltaRad = (xmax - xmin) / (dims[1] - 1);
        for k in range(dims[2]):  # ( k=0; k<dims[2]; k++)
            x[2] = ymin + k * deltaZ
            kOffset = k * dims[0] * dims[1]
            for j in range(dims[1]):  # (j=0; j<dims[1]; j++)
                radius = xmin + j * deltaRad
                jOffset = j * dims[0]
                for i in range(dims[0]):  # (i=0; i<dims[0]; i++)
                    dataIndex = j + k * dims[1]
                    theta = i * vtk.vtkMath.RadiansFromDegrees(delta_phi)
                    x[0] = radius * np.cos(theta)
                    x[1] = radius * np.sin(theta)
                    offset = i + jOffset + kOffset
                    points.InsertPoint(offset, x[0], x[1], x[2])
                    scalars2.InsertNextTuple1(z[dataIndex])
                    scalarBtheta.InsertNextTuple1(Btheta[dataIndex])
                    Bx = Br[dataIndex] * np.cos(theta) - Bphi[dataIndex] * np.sin(theta)
                    By = Br[dataIndex] * np.sin(theta) + Bphi[dataIndex] * np.cos(theta)
                    B.SetTuple3(offset, Bx, By, Bz[dataIndex])
            #        array.SetValue(offset, z[j + k * dims[1] ])
        self.map3D.SetPoints(points)
        self.map3D.GetPointData().SetScalars(scalars2)
        #    self.map3D .GetPointData().SetScalars( scalarBtheta )
        self.map3D.GetPointData().SetVectors(B)

        ###########################################################
        # CONVERT TO UNSTRUCTURED GRID
        ###########################################################
        # appendFilter = vtk.vtkAppendFilter()
        # appendFilter.AddInputData(self.map2D.GetOutput())
        #
        # unstructuredGrid = vtk.vtkUnstructuredGrid()
        # unstructuredGrid.ShallowCopy(appendFilter.GetOutput())
        #
        # writer2 = vtk.vtkXMLUnstructuredGridWriter()
        # writer2.SetFileName("UnstructuredGrid.vtu")
        # writer2.SetInputData(unstructuredGrid);
        # writer2.Write();

    def write_files(self, path_out, eq_name):
        ###########################################################
        # WRITE PLANE DATA
        ###########################################################
        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName(pjoin(path_out, 'Psi_n_' + eq_name + '_2D_x-y.vtp'))
        writer.SetInputConnection(self.map2D.GetOutputPort())
        writer.Write()  # => Use for example ParaView to see scalars

        ###########################################################
        # WRITE CYLINDER DATA
        ###########################################################
        writer2 = vtk.vtkXMLStructuredGridWriter()
        writer2.SetFileName(pjoin(path_out, 'Psi_n_' + eq_name + '_3D.vts'))
        writer2.SetInputData(self.map3D)
        writer2.Write()  # => Use for example ParaView to see scalars

    def visualize2D(self, axis=0):
        ###########################################################
        # VISUALIZATION
        ###########################################################
        # This is a bit annoying: ensure a proper color-lookup.
        colorSeries = vtk.vtkColorSeries()
        colorSeries.SetColorScheme(vtk.vtkColorSeries.BREWER_DIVERGING_SPECTRAL_10)
        lut = vtk.vtkColorTransferFunction()
        lut.SetColorSpaceToHSV()
        nColors = colorSeries.GetNumberOfColors()
        for i in range(0, nColors):
            color = colorSeries.GetColor(i)
            color = [c / 255.0 for c in color]
            t = self.zMin + float(self.zMax - self.zMin) / (nColors - 1) * i
            lut.AddRGBPoint(t, color[0], color[1], color[2])

        # Mapper.
        # mapper = vtk.vtkPolyDataMapper()
        # mapper.SetInputConnection(self.map2D.GetOutputPort())
        # mapper.ScalarVisibilityOn()
        # mapper.SetScalarModeToUsePointData()
        # mapper.SetLookupTable(lut)
        # mapper.SetColorModeToMapScalars()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(self.map2D.GetOutput())
        mapper.SetScalarRange(self.map2D.GetOutput().GetScalarRange())
        mapper.SetLookupTable(lut)
        mapper.SetColorModeToMapScalars()

        # Actor.
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        # Renderer.
        renderer = vtk.vtkRenderer()
        renderer.SetBackground([0.5] * 3)

        # Axis
        if axis == 1:
            transform = vtk.vtkTransform()
            transform.Translate(0.0, 0.0, 0.0)
            transform.Scale(2., 2., 2.)
            axes = vtk.vtkAxesActor()
            #  The axes are positioned with a user transform
            axes.SetUserTransform(transform)
            renderer.AddActor(axes)

        # Render window and interactor.
        renderWindow = vtk.vtkRenderWindow()
        renderWindow.SetWindowName('Psi')
        renderWindow.AddRenderer(renderer)
        renderer.AddActor(actor)
        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        interactor.SetRenderWindow(renderWindow)
        renderWindow.Render()
        interactor.Start()

    def visualize3D(self, axis=0):
        ###########################################################
        # VISUALIZATION
        ###########################################################
        # This is a bit annoying: ensure a proper color-lookup.
        colorSeries = vtk.vtkColorSeries()
        colorSeries.SetColorScheme(vtk.vtkColorSeries.BREWER_DIVERGING_SPECTRAL_10)
        lut = vtk.vtkColorTransferFunction()
        lut.SetColorSpaceToHSV()
        nColors = colorSeries.GetNumberOfColors()
        for i in range(0, nColors):
            color = colorSeries.GetColor(i)
            color = [c / 255.0 for c in color]
            t = self.zMin + float(self.zMax - self.zMin) / (nColors - 1) * i
            lut.AddRGBPoint(t, color[0], color[1], color[2])

        # Mapper.
        # mapper = vtk.vtkPolyDataMapper()
        # mapper.SetInputConnection(self.map2D.GetOutputPort())
        # mapper.ScalarVisibilityOn()
        # mapper.SetScalarModeToUsePointData()
        # mapper.SetLookupTable(lut)
        # mapper.SetColorModeToMapScalars()

        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputData(self.map3D)
        mapper.SetScalarRange(self.map3D.GetScalarRange())
        mapper.SetLookupTable(lut)
        mapper.SetColorModeToMapScalars()

        # Actor.
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        # Renderer.
        renderer = vtk.vtkRenderer()
        renderer.SetBackground([0.5] * 3)

        # Axis
        if axis == 1:
            transform = vtk.vtkTransform()
            transform.Translate(0.0, 0.0, 0.0)
            transform.Scale(2., 2., 2.)
            axes = vtk.vtkAxesActor()
            #  The axes are positioned with a user transform
            axes.SetUserTransform(transform)
            renderer.AddActor(axes)

        # Render window and interactor.
        renderWindow = vtk.vtkRenderWindow()
        renderWindow.SetWindowName('Psi')
        renderWindow.AddRenderer(renderer)
        renderer.AddActor(actor)
        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        interactor.SetRenderWindow(renderWindow)
        renderWindow.Render()
        interactor.Start()
