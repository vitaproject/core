
"""
Vita 3D mapping demonstration
-----------------------------

This file uses an example equilibrium from Cherab to demonstrate how to:

 * define a 2D power footprint
 * map the power using 2D methods to an interface surface
 * map the power in 3D from the interface surface to a mesh representing the machine wall
"""


import numpy as np
from raysect.core import Point2D, World, rotate_z
from raysect.primitive.mesh import Mesh
from cherab.core.math import VectorAxisymmetricMapper
import matplotlib.pyplot as plt
from scipy.optimize import brentq
from cherab.tools.equilibrium import example_equilibrium, plot_equilibrium
from cherab.tools.primitives import axisymmetric_mesh_from_polygon
from vita.modules.sol_heat_flux.eich import Eich
from vita.modules.projection.cherab import FieldlineTracer, RK2, InterfaceSurface, sample_power_at_surface


# populate and return an example equilibrium object.
equilibrium = example_equilibrium()
psi_n = equilibrium.psi_normalised
LCFS_RADIUS = 2.5770656337922073


# specify and load heatflux profile
footprint = Eich(2.5E-3, 0.0001E-3)  # lambda_q=2.5, S=0.5
x = np.linspace(-1, 10, 100)*1E-3
footprint.set_coordinates(x)
footprint.s_disconnected_dn_max = 2.1
footprint.fx_in_out = 5.
footprint.calculate_heat_flux_density("lfs")
footprint.plot_heat_power_density()


# setup and instance an interface surface
POINT_A = Point2D(1.7753, -1.250)
POINT_B = Point2D(1.90911, -1.27081)
power_profile = sample_power_at_surface(POINT_A, POINT_B, equilibrium, footprint,
                                        lcfs_radii_min=2.3, lcfs_radii_max=2.7)
interface_power = 1e6  # 1MW
angle_period = 45

interface_surface = InterfaceSurface(POINT_A, POINT_B, power_profile, interface_power)
interface_surface.histogram_plot()

# map the 2D magnetic field into 3D, instance a field line tracer
b_field = VectorAxisymmetricMapper(equilibrium.b_field)
field_tracer = FieldlineTracer(b_field, method=RK2(step_size=0.0001, direction='negative'))


# the world scene-graph
world = World()


def make_mesh(polygon, num_toroidal_segments=100, segments_implemented=100):
    """Inline function the make a simple mesh from a 2D polygon segment"""

    DEG2RAD = 2 * np.pi / 360

    num_poloidal_vertices = len(polygon)
    theta = 360 / num_toroidal_segments
    vertices = np.zeros((num_poloidal_vertices * (segments_implemented + 1), 3))
    vertices_mv = vertices
    polygon_mv = polygon

    for i in range(segments_implemented+1):
        for j in range(num_poloidal_vertices):

            r = polygon_mv[j, 0]
            z = polygon_mv[j, 1]
            x = r * np.cos(i * theta * DEG2RAD)
            y = r * np.sin(i * theta * DEG2RAD)

            vid = i * num_poloidal_vertices + j
            vertices_mv[vid, 0] = x
            vertices_mv[vid, 1] = y
            vertices_mv[vid, 2] = z

    # assemble mesh triangles
    triangles = []
    for i in range(segments_implemented):  # -1 from above
        for j in range(num_poloidal_vertices-1):

            v1_id = i * num_poloidal_vertices + j
            v2_id = i * num_poloidal_vertices + j + 1
            v3_id = i * num_poloidal_vertices + num_poloidal_vertices + j
            v4_id = i * num_poloidal_vertices + num_poloidal_vertices + j + 1

            triangles.append([v1_id, v2_id, v4_id])
            triangles.append([v4_id, v3_id, v1_id])

    return Mesh(vertices=vertices, triangles=triangles, smoothing=False)


# generate a simple 45 degree mesh segment (effectively a flat floor)
num_pol = 100
num_tor = 1000
polygon_r = np.linspace(1.75, 1.95, num_pol)
polygon_z = np.array([-1.335 for _ in range(num_pol)])
polygon = np.array(list(zip(polygon_r, polygon_z)))
mesh = make_mesh(polygon, num_toroidal_segments=num_tor, segments_implemented=int(num_tor*45/360))
mesh.name = 'Simple_Divertor'
# instance the mesh 8 times (i.e. clone and rotate)
for i in range(8):
    mesh.instance()
    mesh.instance(parent=world, transform=rotate_z(i * 45), name=mesh.name)


# map power onto the divertor tile
interface_surface.map_power(interface_power, angle_period, field_tracer, world,
                            num_of_fieldlines=30000, debug_output=True)

# plot the interface surface over the equilibrium
interface_surface.plot(equilibrium)

