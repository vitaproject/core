
import numpy as np
import matplotlib.pyplot as plt
from raysect.core import Point3D, World, rotate_z
from raysect.primitive import import_ply
from cherab.tools.equilibrium import plot_equilibrium

from vita.modules.projection.cherab import FieldlineTracer, RK2, RK4
from vita.modules.equilibrium.fiesta import Fiesta
from vita.utility import get_resource


# the world scene-graph
world = World()

##########################
# add machine components #

vessel = get_resource("ST40-IVC2", "mesh", "vessel")
vessel = import_ply(vessel, scaling=0.001, parent=world, name="vessel")

vessel_lower = get_resource("ST40-IVC2", "mesh", "vessel_lower")
vessel_lower = import_ply(vessel_lower, scaling=0.001, parent=world, name="vessel_lower")

vessel_upper = get_resource("ST40-IVC2", "mesh", "vessel_upper")
vessel_upper = import_ply(vessel_upper, scaling=0.001, parent=world, name="vessel_upper")

centre_column = get_resource("ST40-IVC2", "mesh", "centre_column")
centre_column = import_ply(centre_column, scaling=0.001, parent=world, name="centre_column")

poloidal_coil_lower_45 = get_resource("ST40-IVC2", "mesh", "poloidal_coil_lower_45")
poloidal_coil_lower_45 = import_ply(poloidal_coil_lower_45, scaling=0.001, name="poloidal_coil_lower_45")
for i in range(8):
    poloidal_coil_lower_45.instance(parent=world, transform=rotate_z(i * 45), name="poloidal_coil_lower_45")

poloidal_coil_upper_45 = get_resource("ST40-IVC2", "mesh", "poloidal_coil_upper_45")
poloidal_coil_upper_45 = import_ply(poloidal_coil_upper_45, scaling=0.001, name="poloidal_coil_upper_45")
for i in range(8):
    poloidal_coil_upper_45.instance(parent=world, transform=rotate_z(i * 45), name="poloidal_coil_upper_45")

limiter_lower_45 = get_resource("ST40-IVC2", "mesh", "limiter_lower_45")
limiter_lower_45 = import_ply(limiter_lower_45, scaling=0.001, name="limiter_lower_45")
for i in range(8):
    limiter_lower_45.instance(parent=world, transform=rotate_z(i * 45), name="limiter_lower_45")

limiter_upper_45 = get_resource("ST40-IVC2", "mesh", "limiter_upper_45")
limiter_upper_45 = import_ply(limiter_upper_45, scaling=0.001, name="limiter_upper_45")
for i in range(8):
    limiter_upper_45.instance(parent=world, transform=rotate_z(i * 45), name="limiter_upper_45")

divertor_tile_lower_45 = get_resource("ST40-IVC2", "mesh", "divertor_tile_lower_45")
divertor_tile_lower_45 = import_ply(divertor_tile_lower_45, scaling=0.001, name="divertor_tile_lower_45")
for i in range(8):
    divertor_tile_lower_45.instance(parent=world, transform=rotate_z(i * 45), name="divertor_tile_lower_45")

divertor_tile_upper_45 = get_resource("ST40-IVC2", "mesh", "divertor_tile_upper_45")
divertor_tile_upper_45 = import_ply(divertor_tile_upper_45, scaling=0.001, name="divertor_tile_upper_45")
for i in range(8):
    divertor_tile_upper_45.instance(parent=world, transform=rotate_z(i * 45), name="divertor_tile_upper_45")

centre_column_tiles_lower_45 = get_resource("ST40-IVC2", "mesh", "centre_column_tiles_lower_45")
centre_column_tiles_lower_45 = import_ply(centre_column_tiles_lower_45, scaling=0.001, name="centre_column_tiles_lower_45")
for i in range(8):
    centre_column_tiles_lower_45.instance(parent=world, transform=rotate_z(i * 45), name="centre_column_tiles_lower_45")

centre_column_tiles_upper_45 = get_resource("ST40-IVC2", "mesh", "centre_column_tiles_upper_45")
centre_column_tiles_upper_45 = import_ply(centre_column_tiles_upper_45, scaling=0.001, name="centre_column_tiles_upper_45")
for i in range(8):
    centre_column_tiles_upper_45.instance(parent=world, transform=rotate_z(i * 45), name="centre_column_tiles_upper_45")


eq002 = get_resource("ST40", "equilibrium", "eq002")
fiesta = Fiesta(eq002)
b_field = fiesta.b_field


1.08333333
seed_point = Point3D(0.733, 0, -0.01)


field_tracer_rk2 = FieldlineTracer(b_field, method=RK2(step_size=0.0001))
field_tracer_rk4 = FieldlineTracer(b_field, method=RK4(step_size=0.0001))

_, _, trajectory_rk2 = field_tracer_rk2.trace(world, seed_point, save_trajectory=True, max_length=15)
_, _, trajectory_rk4 = field_tracer_rk4.trace(world, seed_point, save_trajectory=True, max_length=15)

rk2_radial_trajectory = np.zeros((trajectory_rk2.shape[0], 2))
for i in range(trajectory_rk2.shape[0]):
    r = np.sqrt(trajectory_rk2[i, 0]**2 + trajectory_rk2[i, 1]**2)
    rk2_radial_trajectory[i, 0] = r
    rk2_radial_trajectory[i, 1] = trajectory_rk2[i, 2]

rk4_radial_trajectory = np.zeros((trajectory_rk4.shape[0], 2))
for i in range(trajectory_rk4.shape[0]):
    r = np.sqrt(trajectory_rk4[i, 0]**2 + trajectory_rk4[i, 1]**2)
    rk4_radial_trajectory[i, 0] = r
    rk4_radial_trajectory[i, 1] = trajectory_rk4[i, 2]

equilibrium = fiesta.to_cherab_equilibrium()
plot_equilibrium(equilibrium, detail=False)

plt.plot(rk2_radial_trajectory[:, 0], rk2_radial_trajectory[:, 1], 'g-')
plt.plot(rk4_radial_trajectory[:, 0], rk4_radial_trajectory[:, 1], 'r-')
plt.show()

