
import time
import numpy as np
from numpy.random import random
import matplotlib.pyplot as plt
from scipy.optimize import brentq
import scipy.integrate as integrate
from scipy.interpolate import interp1d
from mayavi import mlab
from raysect.core import Point3D, World, rotate_z
from raysect.primitive import import_ply, export_vtk

from vita.modules.sol_heat_flux.eich import Eich
from vita.modules.cherab import FieldlineTracer, RK2
from vita.modules.fiesta import Fiesta
from vita.utility import get_resource


# the world scene-graph
world = World()


##########################
# add machine components #
meshes = {}

vessel = get_resource("ST40-IVC2", "mesh", "vessel")
vessel = import_ply(vessel, scaling=0.001, parent=world, name="vessel")
meshes["vessel"] = vessel

vessel_lower = get_resource("ST40-IVC2", "mesh", "vessel_lower")
vessel_lower = import_ply(vessel_lower, scaling=0.001, parent=world, name="vessel_lower")
meshes["vessel_lower"] = vessel_lower

vessel_upper = get_resource("ST40-IVC2", "mesh", "vessel_upper")
vessel_upper = import_ply(vessel_upper, scaling=0.001, parent=world, name="vessel_upper")
meshes["vessel_upper"] = vessel_upper

centre_column = get_resource("ST40-IVC2", "mesh", "centre_column")
centre_column = import_ply(centre_column, scaling=0.001, parent=world, name="centre_column")
meshes["centre_column"] = centre_column

poloidal_coil_lower_45 = get_resource("ST40-IVC2", "mesh", "poloidal_coil_lower_45")
poloidal_coil_lower_45 = import_ply(poloidal_coil_lower_45, scaling=0.001, name="poloidal_coil_lower_45")
meshes["poloidal_coil_lower_45"] = poloidal_coil_lower_45
for i in range(8):
    poloidal_coil_lower_45.instance(parent=world, transform=rotate_z(i * 45), name="poloidal_coil_lower_45")

poloidal_coil_upper_45 = get_resource("ST40-IVC2", "mesh", "poloidal_coil_upper_45")
poloidal_coil_upper_45 = import_ply(poloidal_coil_upper_45, scaling=0.001, name="poloidal_coil_upper_45")
meshes["poloidal_coil_upper_45"] = poloidal_coil_upper_45
for i in range(8):
    poloidal_coil_upper_45.instance(parent=world, transform=rotate_z(i * 45), name="poloidal_coil_upper_45")

limiter_lower_45 = get_resource("ST40-IVC2", "mesh", "limiter_lower_45")
limiter_lower_45 = import_ply(limiter_lower_45, scaling=0.001, name="limiter_lower_45")
meshes["limiter_lower_45"] = limiter_lower_45
for i in range(8):
    limiter_lower_45.instance(parent=world, transform=rotate_z(i * 45), name="limiter_lower_45")

limiter_upper_45 = get_resource("ST40-IVC2", "mesh", "limiter_upper_45")
limiter_upper_45 = import_ply(limiter_upper_45, scaling=0.001, name="limiter_upper_45")
meshes["limiter_upper_45"] = limiter_upper_45
for i in range(8):
    limiter_upper_45.instance(parent=world, transform=rotate_z(i * 45), name="limiter_upper_45")

divertor_tile_lower_45 = get_resource("ST40-IVC2", "mesh", "divertor_tile_lower_45")
divertor_tile_lower_45 = import_ply(divertor_tile_lower_45, scaling=0.001, name="divertor_tile_lower_45")
meshes["divertor_tile_lower_45"] = divertor_tile_lower_45
for i in range(8):
    divertor_tile_lower_45.instance(parent=world, transform=rotate_z(i * 45), name="divertor_tile_lower_45")

divertor_tile_upper_45 = get_resource("ST40-IVC2", "mesh", "divertor_tile_upper_45")
divertor_tile_upper_45 = import_ply(divertor_tile_upper_45, scaling=0.001, name="divertor_tile_upper_45")
meshes["divertor_tile_upper_45"] = divertor_tile_upper_45
for i in range(8):
    divertor_tile_upper_45.instance(parent=world, transform=rotate_z(i * 45), name="divertor_tile_upper_45")

centre_column_tiles_lower_45 = get_resource("ST40-IVC2", "mesh", "centre_column_tiles_lower_45")
centre_column_tiles_lower_45 = import_ply(centre_column_tiles_lower_45, scaling=0.001, name="centre_column_tiles_lower_45")
meshes["centre_column_tiles_lower_45"] = centre_column_tiles_lower_45
for i in range(8):
    centre_column_tiles_lower_45.instance(parent=world, transform=rotate_z(i * 45), name="centre_column_tiles_lower_45")

centre_column_tiles_upper_45 = get_resource("ST40-IVC2", "mesh", "centre_column_tiles_upper_45")
centre_column_tiles_upper_45 = import_ply(centre_column_tiles_upper_45, scaling=0.001, name="centre_column_tiles_upper_45")
meshes["centre_column_tiles_upper_45"] = centre_column_tiles_upper_45
for i in range(8):
    centre_column_tiles_upper_45.instance(parent=world, transform=rotate_z(i * 45), name="centre_column_tiles_upper_45")


########################
# load the equilibrium #
eq002 = get_resource("ST40", "equilibrium", "eq002")
fiesta = Fiesta(eq002)
b_field = fiesta.b_field
field_tracer = FieldlineTracer(b_field, method=RK2(step_size=0.0001))


def get_lcfs_radius():

    equilibrium = fiesta.to_cherab_equilibrium()
    psin2d = equilibrium.psi_normalised

    def psin(r, offset=0):
        return psin2d(r, 0) - 1 + offset

    r_lcfs = brentq(psin, 0.7, 0.9, args=(0,))

    return r_lcfs


lcfs_radius = get_lcfs_radius()


##############################
# setup the heatflux profile #

footprint = Eich(2.5, 0.5)  # lambda_q=2.5, S=0.5

x = np.linspace(-1, 10, 100)
footprint.set_coordinates(x)
footprint.s_disconnected_dn_max = 2.1
footprint.fx_in_out = 5.
footprint.calculate_heat_flux_density("lfs")

# sampling power function outside LCFS
s_vals = np.linspace(0, 10, 1000)
q_vals = np.array([footprint(s) for s in s_vals])

s_vals /= 100
integral = integrate.simps(q_vals, s_vals)
q_vals /= integral

ds = s_vals[1] - s_vals[0]
q_cumulative_values = []
for i in range(q_vals.shape[0]):
    if i == 0:
        q_cumulative_values.append(0)
    else:
        q_cumulative_values.append(q_cumulative_values[i-1] + (q_vals[i] * ds))

# plt.ion()
# plt.plot(s_vals, q_vals)
# plt.figure()
# plt.plot(q_cumulative_values, s_vals)

q_to_s_func = interp1d(q_cumulative_values, s_vals, fill_value="extrapolate")

TOTAL_POWER = 1E6 / 8  # 1MW
NUM_OF_FIELDLINES = 300  # 50000


##############################
# calculate heatflux mapping #

mesh_powers = {}
null_intersections = 0
lost_power = 0

power_per_fieldline = TOTAL_POWER / NUM_OF_FIELDLINES

t_start = time.time()
for i in range(NUM_OF_FIELDLINES):

    seed_radius = q_to_s_func(random()) + lcfs_radius
    seed_angle = random() * 45
    seed_point = Point3D(seed_radius * np.cos(np.deg2rad(seed_angle)),
                         seed_radius * np.sin(np.deg2rad(seed_angle)),
                         0)

    end_point, intersection, _ = field_tracer.trace(world, seed_point, max_length=15)

    if intersection is not None:
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

    # if not i % 1000:
    print(i)

t_end = time.time()

print("Meshes collided with:")
for mesh_name in mesh_powers.keys():
    print(mesh_name)
print("Number of null intersections")
print(null_intersections)

print()
print("execution: {}".format(t_end-t_start))

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

    export_vtk(mesh_primitive, mesh_name+".vtk", triangle_data={"power": powers})
