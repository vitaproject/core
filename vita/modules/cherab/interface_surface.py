
import time
import numpy as np
from numpy.random import random
import matplotlib.pyplot as plt

import scipy.integrate as integrate
from scipy.interpolate import interp1d
from scipy.optimize import brentq

from raysect.core import Point2D, Point3D
from raysect.primitive import export_vtk
from cherab.tools.equilibrium import EFITEquilibrium, plot_equilibrium

from vita.modules.sol_heat_flux.mid_plane_heat_flux import HeatLoad


class InterfaceSurface:

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
                  num_of_fieldlines=50000, max_tracing_length=15, debug_output=False):

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

                try:
                    powers = mesh_powers[intersection.primitive.name]
                except KeyError:
                    mesh = intersection.primitive
                    powers = np.zeros((mesh.data.triangles.shape[0]))
                    mesh_powers[intersection.primitive.name] = powers

                tri_id = intersection.primitive_coords[0]
                powers[tri_id] += power_per_fieldline

            else:
                null_intersections += 1
                lost_power += power_per_fieldline

            if not i % 10000 and debug_output:
                print("Tracing fieldline {}.".format(i))

        t_end = time.time()

        if debug_output:
            print("Meshes collided with:")
            for mesh_name in mesh_powers.keys():
                print(mesh_name)
            print()
            print("Number of null intersections - {}".format(null_intersections))
            print("Amount of lost power - {} W".format(lost_power))
            print()
            print("execution time: {}".format(t_end - t_start))
            print()

        for mesh_name in mesh_powers.keys():

            mesh_primitive = meshes[mesh_name]
            powers = mesh_powers[mesh_name]

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

            export_vtk(mesh_primitive, mesh_name + ".vtk", triangle_data={"power": powers})

    def _generate_sample_point(self):

        # sample a point along surface proportional to power
        x = self._q_to_x_func(random())
        sample_point = self._point_a + self._interface_vector * x

        return sample_point

    def plot(self, equilibrium):

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


def sample_power_at_surface(point_a, point_b, equilibrium, heat_load,
                            s_min=-0.01, s_max=0.1, num_samples=1000,
                            lcfs_radii_min=0.7, lcfs_radii_max=0.9):

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

        r_lcfs = brentq(psin, 0.7, 0.9, args=(0,))

        return r_lcfs

    lcfs_radius = get_lcfs_radius()

    # sampling power function outside LCFS
    s_vals = np.linspace(s_min, s_max, num_samples)
    s_vals_cm = s_vals * 100  # convert array to cm for HeatLoad units
    q_vals = np.array([heat_load(s) for s in s_vals_cm])
    r_vals = s_vals + lcfs_radius
    psin_vals = np.array([psin2d(r, 0) for r in r_vals])

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
    psin_to_q_func = interp1d(psin_vals, q_vals, fill_value="extrapolate")  # q(psi_n)

    # generate interface surface mapping functions
    interface_vector = point_a.vector_to(point_b)

    powers_along_interface = []
    for i in range(num_samples):
        sample_point = point_a + interface_vector * i / num_samples
        psin = psin2d(sample_point.x, sample_point.y)
        q = psin_to_q_func(psin)
        powers_along_interface.append(q)

    return np.array(powers_along_interface)
