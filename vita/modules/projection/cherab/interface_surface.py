
import vtk
import time
from math import atan2, sqrt, fabs
import numpy as np
from numpy.random import random
import matplotlib.pyplot as plt

import scipy.integrate as integrate
from scipy.interpolate import interp1d
from scipy.optimize import brentq

from raysect.core import Point2D, Point3D, rotate_z
from raysect.primitive import export_vtk
from cherab.tools.equilibrium import EFITEquilibrium, plot_equilibrium
from cherab.core.math import Interpolate1DCubic

from vita.modules.sol_heat_flux.mid_plane_heat_flux import HeatLoad


class InterfaceSurface:
    """
    Class for mapping power from an interface surface in the divertor onto the walls.

    :param Point2D point_a: A 2D point representing the start of the interface surface.
    :param Point2D point_b: A 2D point representing the end of the interface surface.
    :param ndarray power_profile: A an array of power values representing the power
      profile along the interface surface. These points are equally spaced and will be
      re-normalised to give an integral of one over the surface.
    """

    def __init__(self, point_a, point_b, power_profile, total_power):

        if not isinstance(point_a, Point2D):
            raise TypeError("Variable point_a must be a Point2D")

        if not isinstance(point_b, Point2D):
            raise TypeError("Variable point_b must be a Point2D")

        if not point_b.x >= point_a.x:
            raise ValueError("Point B must be the outer radial point, or vertically aligned with Point A.")

        surface_length = point_a.distance_to(point_b)
        if not point_a.distance_to(point_b) > 0:
            raise ValueError("Point A and Point B cannot be co-located.")

        if not isinstance(power_profile, np.ndarray) or not len(power_profile.shape) == 1:
            raise TypeError("Variable power_profile must be a 1D numpy array.")
        power_profile = np.array(power_profile)  # explicit copy for internal editing

        if not isinstance(total_power, (float, int)) or total_power < 0:
            raise TypeError("Variable total_power must be float > 0.")

        self._point_a = point_a
        self._point_b = point_b
        self._interface_vector = point_a.vector_to(point_b)
        self._interface_distance = point_a.distance_to(point_b)

        num_samples = power_profile.shape[0]

        x_samples = np.linspace(0, surface_length, num=num_samples)
        self._x_samples = x_samples

        # explicitly normalise distribution
        integral = integrate.simps(power_profile, x_samples)
        power_profile /= integral
        self._power_profile = power_profile

        dx = x_samples[1] - x_samples[0]
        q_cumulative_values = []
        for i in range(num_samples):
            if i == 0:
                q_cumulative_values.append(0)
            else:
                q_cumulative_values.append(q_cumulative_values[i - 1] + (power_profile[i] * dx))

        self._q_to_x_func = interp1d(q_cumulative_values, x_samples, fill_value="extrapolate")

    def map_power(self, power, angle_period, field_tracer, world,
                  num_of_fieldlines=50000, max_tracing_length=15, phi_offset=0, debug_output=False,
                  debug_count=10000, write_output=True):
        """
        Map the power from this surface onto the wall tiles.

        :param float power: The total power that will be mapped onto the tiles using the
          specified distribution.
        :param float angle_period: the spatial period for the interface surface in degrees,
          e.g. 45 degrees. Exploiting cylindrical symmetry will enable a significant speed up
          of the calculations.
        :param FieldlineTracer field_tracer: a pre-configured field line tracer object.
        :param World world; A world scenegraph to be mapped. This scenegraph must contain all the
          desired meshes for power tracking calculations.
        :param int num_of_fieldlines: the number of fieldlines to launch in the mapping process.
          Defaults to 50000 fieldlines.
        :param float max_tracing_length: the maximum length for tracing fieldlines.
        :param float phi_offset: the angular range offset for collision point mapping.
          Important for cases where the periodic divertor tiles straddle phi=0.
        :param bool debug_output: toggle to print extra debug information output, such as the meshes
          collided with and the amount of lost power.
        """

        if not (isinstance(power, (float, int)) and power > 0):
            raise TypeError("The interface power must be a float/int > 0.")

        if not (isinstance(angle_period, (float, int)) and 0 < angle_period <= 360):
            raise TypeError("The angle period must be a float/int between (0, 360].")

        if 360 % angle_period:
            raise ValueError("The angle period must be divisible into 360 degrees an integer number of times.")

        if not (isinstance(num_of_fieldlines, int) and num_of_fieldlines > 0):
            raise TypeError("The number of fieldlines to trace must be an integer > 0.")

        # reduce power when exploiting  cylindrical symmetry
        reduction_factor = 360 / angle_period
        total_power = power / reduction_factor
        power_per_fieldline = total_power / num_of_fieldlines

        meshes = {}
        mesh_powers = {}
        mesh_hitpoints = {}
        mesh_seedpoints = {}
        null_intersections = 0
        lost_power = 0

        t_start = time.time()
        for i in range(num_of_fieldlines):

            seed_point_2d = self._generate_sample_point()
            seed_angle = random() * angle_period
            seed_point = Point3D(seed_point_2d.x * np.cos(np.deg2rad(seed_angle)),
                                 seed_point_2d.x * np.sin(np.deg2rad(seed_angle)),
                                 seed_point_2d.y)

            end_point, intersection, _ = field_tracer.trace(world, seed_point, max_length=max_tracing_length)

            # log the collision information for power tallies
            if intersection is not None:

                # catch primitive for later if we haven't encountered it before
                try:
                    meshes[intersection.primitive.name]
                except KeyError:
                    meshes[intersection.primitive.name] = intersection.primitive

                # extract power array for intersected mesh and save results
                try:
                    powers = mesh_powers[intersection.primitive.name]
                except KeyError:
                    mesh = intersection.primitive
                    powers = np.zeros((mesh.data.triangles.shape[0]))
                    mesh_powers[intersection.primitive.name] = powers

                tri_id = intersection.primitive_coords[0]
                powers[tri_id] += power_per_fieldline

                # save hit points for saving to a separate vtk file
                try:
                    hitpoints = mesh_hitpoints[intersection.primitive.name]
                except KeyError:
                    hitpoints = []
                    mesh_hitpoints[intersection.primitive.name] = hitpoints

                # save seed points for separate analysis
                try:
                    seedpoints = mesh_seedpoints[intersection.primitive.name]
                except KeyError:
                    seedpoints = []
                    mesh_seedpoints[intersection.primitive.name] = seedpoints

                # map the hit point back to the starting sector (angular period)
                hit_point = intersection.hit_point.transform(intersection.primitive_to_world)
                phi = np.rad2deg(atan2(hit_point.y, hit_point.x)) - phi_offset
                phase_phi = phi - phi % angle_period
                mapped_point = hit_point.transform(rotate_z(-phase_phi))
                hitpoints.append((mapped_point.x, mapped_point.y, mapped_point.z))

                seedpoints.append(seed_point)

            else:
                null_intersections += 1
                lost_power += power_per_fieldline

            if not i % debug_count and debug_output:
                print("Tracing fieldline {}.".format(i))

        t_end = time.time()

        if debug_output:
            print("Meshes collided with:")
            for mesh_name, mesh_values in mesh_powers.items():
                power_fraction = mesh_values.sum() / total_power * 100
                print('{} - {:.4G}%'.format(mesh_name, power_fraction))
            print("Fraction of lost power - {:.4G}%".format(lost_power/total_power))

            print()
            print("execution time: {}".format(t_end - t_start))
            print()

        if write_output:

            for mesh_name in mesh_powers.keys():

                mesh_primitive = meshes[mesh_name]
                powers = mesh_powers[mesh_name]
                hitpoints = np.array(mesh_hitpoints[mesh_name])

                output_filename = mesh_name + ".vtk"
                self._write_mesh_power_vtk(output_filename, powers, mesh_primitive)

                point_filename = mesh_name + ".vtp"
                self._write_mesh_points_vtk(point_filename, hitpoints, power_per_fieldline)

        return mesh_powers, mesh_hitpoints, mesh_seedpoints

    def _generate_sample_point(self):

        # sample a point along surface proportional to power
        x = self._q_to_x_func(random())
        interface_vector = self._interface_vector.normalise()
        sample_point = self._point_a + interface_vector * x

        return sample_point

    def _write_mesh_power_vtk(self, filename, powers, mesh_primitive):

        # normalise power per area
        for i in range(powers.shape[0]):
            if powers[i] > 0:
                triangle = mesh_primitive.data.triangle(i)
                p1 = mesh_primitive.data.vertex(triangle[0])
                p2 = mesh_primitive.data.vertex(triangle[1])
                p3 = mesh_primitive.data.vertex(triangle[2])
                v12 = p1.vector_to(p2)
                v13 = p1.vector_to(p3)
                tri_area = v12.cross(v13).length / 2
                powers[i] /= tri_area

        export_vtk(mesh_primitive, filename, triangle_data={"power": powers})

    def _write_mesh_points_vtk(self, filename, points, power_per_point):

        # setup points and vertices
        vtk_points = vtk.vtkPoints()
        vtk_vertices = vtk.vtkCellArray()
        vtk_point_values = vtk.vtkDoubleArray()
        vtk_point_values.SetName("CollisionEnergies")

        for i in range(points.shape[0]):
            id = vtk_points.InsertNextPoint(points[i, 0], points[i, 1], points[i, 2])
            vtk_vertices.InsertNextCell(1)
            vtk_vertices.InsertCellPoint(id)
            vtk_point_values.InsertNextValue(power_per_point)

        polydata = vtk.vtkPolyData()
        polydata.SetPoints(vtk_points)
        polydata.SetVerts(vtk_vertices)
        polydata.GetCellData().SetScalars(vtk_point_values)
        polydata.Modified()
        if vtk.VTK_MAJOR_VERSION <= 5:
            polydata.Update()

        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName(filename)
        if vtk.VTK_MAJOR_VERSION <= 5:
            writer.SetInput(polydata)
        else:
            writer.SetInputData(polydata)
        writer.Write()

    def plot(self, equilibrium):
        """
        Plot the interface surface line across the equilibrium.

        :param EFITEquilibrium equilibrium: the equilibrium to plot.
        """

        sample_points = []
        num_samples = self._power_profile.shape[0]
        point_a = self._point_a
        point_b = self._point_b
        interface_vector = point_a.vector_to(point_b)
        for i in range(num_samples):
            seed_point = point_a + interface_vector * i / num_samples
            sample_points.append([seed_point.x, seed_point.y])

        interface_distance = point_a.distance_to(point_b)
        sample_distances = np.linspace(0, interface_distance, num=num_samples)

        sample_points = np.array(sample_points)
        plot_equilibrium(equilibrium, detail=False)
        plt.plot(sample_points[:, 0], sample_points[:, 1])

        plt.figure()
        plt.plot(sample_distances, self._power_profile)

    def histogram_plot(self):

        num_samples = 10000
        samples = []
        for i in range(num_samples):
            sample = self._generate_sample_point()
            x = self._point_a.distance_to(sample)
            samples.append(x)

        fig, ax = plt.subplots()
        n, bins, patches = ax.hist(samples, 50, range=[0, self._interface_distance], density=1)
        ax.set_xlabel('Interface distance (m)')
        ax.set_ylabel('Sample density')
        ax.set_title(r'Sample Histogram along interface surface')
        # Save file and figure:
        np.savetxt("interface-histogram.txt", samples)
        fig.savefig('interface-histogram.png')

    def poloidal_trajectory_plot(self, field_tracer, world, equilibrium,
                                 num_of_fieldlines=5, max_tracing_length=15):

        if not (isinstance(num_of_fieldlines, int) and num_of_fieldlines > 0):
            raise TypeError("The number of fieldlines to trace must be an integer > 0.")

        point_a = Point3D(self._point_a.x, 0, self._point_a.y)
        point_b = Point3D(self._point_b.x, 0, self._point_b.y)
        interface_vector = point_a.vector_to(point_b)

        plot_equilibrium(equilibrium, detail=False)

        for i in range(num_of_fieldlines):

            sample_point = point_a + interface_vector * i / num_of_fieldlines

            _, _, trajectory = field_tracer.trace(world, sample_point,
                                                  max_length=max_tracing_length, save_trajectory=True)

            rz_trajectory = np.zeros((trajectory.shape[0], 2))
            for i in range(trajectory.shape[0]):
                r = sqrt(trajectory[i, 0]**2 + trajectory[i, 1]**2)
                z = trajectory[i, 2]
                rz_trajectory[i, :] = r, z

            plt.plot(rz_trajectory[:, 0], rz_trajectory[:, 1], 'g')


# TODO - this should be replaced with Jeppe's mapping functions
def sample_power_at_surface(point_a, point_b, equilibrium, heat_load,
                            s_min=-0.01, s_max=0.1, num_samples=1000,
                            lcfs_radii_min=0.7, lcfs_radii_max=0.9, side="LFS"):
    """
    Sample the power profile from an upstream heat profile along an interface surface in the divertor.

    :param Point2D point_a: A 2D point representing the start of the interface surface.
    :param Point2D point_b: A 2D point representing the end of the interface surface.
    :param EFITEquilibrium equilibrium: the equilibrium to use for the mapping.
    :param HeatLoad heat_load: the upstream mid-plane heat profile.
    :param float s_min: the lower range for heat profile sampling.
    :param float s_max: the upper range for heat profile sampling.
    :param int num_samples: the number of heat profile samples over the range.
    :param float lcfs_radii_min: lower bound for lcfs radius search.
    :param float lcfs_radii_max: upper bound for lcfs radius search.
    :param str side: the LFS or HFS of the tokamak (default='HFS').
    """

    if not isinstance(point_a, Point2D):
        raise TypeError("Variable point_a must be a Point2D")

    if not isinstance(point_b, Point2D):
        raise TypeError("Variable point_b must be a Point2D")

    if not point_b.x >= point_a.x:
        raise ValueError("Point B must be the outer radial point, or vertically aligned with Point A.")

    if not point_a.distance_to(point_b) > 0:
        raise ValueError("Point A and Point B cannot be co-located.")

    if not isinstance(equilibrium, EFITEquilibrium):
        raise TypeError("The specified equilibrium must be an EFITEquilibrium.")

    if not isinstance(heat_load, HeatLoad):
        raise TypeError("The specified heat_load variable must be of type HeatLoad, e.g. Eich().)")

    if not (isinstance(num_samples, int) and num_samples > 0):
        raise TypeError("The number of spatial samples num_samples must be an integer > 0.")

    psin2d = equilibrium.psi_normalised

    # TODO - this is bad, needs to be refactored somehow
    def get_lcfs_radius():

        def psin(r, offset=0):
            return psin2d(r, 0) - 1 + offset

        r_lcfs = brentq(psin, lcfs_radii_min, lcfs_radii_max, args=(0,))

        return r_lcfs

    lcfs_radius = get_lcfs_radius()

    # sampling power function outside LCFS
    s_vals = np.linspace(s_min, s_max, num_samples)
    q_vals = []
    for s in s_vals:
        try:
            q_vals.append(heat_load(s))
        except ValueError:
            q_vals.append(0)

    if side == "LFS":
        r_vals = lcfs_radius + s_vals
    else:
        r_vals = lcfs_radius - s_vals
    # print('r_vals', r_vals)

    # sample psi over footprint, but handle case where psi goes beyond equilibrium domain
    psin_vals = []
    psi_last = 0
    for r in r_vals:
        try:
            psi = psin2d(r, 0)
            if psi < psi_last:
                break
            psin_vals.append(psi)
            psi_last = psi
        except ValueError:
            break
    psi_q_vals = q_vals[:len(psin_vals)]
    psin_vals = np.array(psin_vals)
    psin_to_r = Interpolate1DCubic(psin_vals, r_vals[:len(psin_vals)])

    integral = integrate.simps(q_vals, s_vals)
    q_vals /= integral

    ds = s_vals[1] - s_vals[0]
    q_cumulative_values = []
    for i in range(q_vals.shape[0]):
        if i == 0:
            q_cumulative_values.append(0)
        else:
            q_cumulative_values.append(q_cumulative_values[i - 1] + (q_vals[i] * ds))

    # generate midplane mapping functions
    psin_to_q_func = interp1d(psin_vals, psi_q_vals, fill_value=0)  # q(psi_n)
    # psin_to_q_func = Interpolate1DCubic(psin_vals, psi_q_vals)  # q(psi_n)

    # generate interface surface mapping functions
    interface_vector = point_a.vector_to(point_b)

    powers_along_interface = []
    interface_psin = []
    for i in range(num_samples):

        p_before = point_a + interface_vector * (i - 0.5) / num_samples
        psin_before = psin2d(p_before.x, p_before.y)
        p_after = point_a + interface_vector * (i + 0.5) / num_samples
        psin_after = psin2d(p_after.x, p_after.y)
        dx_interface = p_before.distance_to(p_after)

        midplane_r_before = psin_to_r(psin_before)
        midplane_r_after = psin_to_r(psin_after)
        ds_midplane = fabs(midplane_r_after - midplane_r_before)

        sample_point = point_a + interface_vector * i / num_samples
        psin = psin2d(sample_point.x, sample_point.y)

        radius_at_interface = sample_point.x
        radius_at_midplane = psin_to_r(psin)
        flux_expansion_factor = (ds_midplane / dx_interface) * (radius_at_midplane / radius_at_interface)

        interface_psin.append(psin)
        q = psin_to_q_func(psin) * flux_expansion_factor
        powers_along_interface.append(q)

    return np.array(powers_along_interface)
