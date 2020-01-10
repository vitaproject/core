
import numpy as np
from mayavi import mlab
from raysect.core import Point3D, World, rotate_z
from raysect.primitive import import_ply

from vita.modules.cherab import FieldlineTracer, RK2
from vita.modules.fiesta import Fiesta
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


seed_points = [
    Point3D(0.507, 0, 0),
    Point3D(0.6, 0, 0),
    Point3D(0.7, 0, 0),
    Point3D(0.733, 0, -0.01)
]


field_tracer = FieldlineTracer(b_field, method=RK2(step_size=0.0001))

end_point, _, trajectory1 = field_tracer.trace(world, seed_points[0], save_trajectory=True, max_length=3)
end_point, _, trajectory2 = field_tracer.trace(world, seed_points[1], save_trajectory=True, max_length=5)
end_point, _, trajectory3 = field_tracer.trace(world, seed_points[2], save_trajectory=True, max_length=15)
end_point, _, trajectory4 = field_tracer.trace(world, seed_points[3], save_trajectory=True, max_length=15)

# mlab.plot3d([0, 0.005, 0.001], [0, 0, 0], [0, 0, 0], tube_radius=0.0005, color=(1, 0, 0))
# mlab.plot3d([0, 0, 0], [0, 0.005, 0.001], [0, 0, 0], tube_radius=0.0005, color=(0, 1, 0))
# mlab.plot3d([0, 0, 0], [0, 0, 0], [0, 0.005, 0.001], tube_radius=0.0005, color=(0, 0, 1))


from raysect_mayavi import visualise_scenegraph
visualise_scenegraph(world)

mlab.plot3d(trajectory1[:, 0], trajectory1[:, 1], trajectory1[:, 2], tube_radius=0.0005, color=(1, 0, 0))
mlab.plot3d(trajectory2[:, 0], trajectory2[:, 1], trajectory2[:, 2], tube_radius=0.0005, color=(0.5, 0.5, 0))
mlab.plot3d(trajectory3[:, 0], trajectory3[:, 1], trajectory3[:, 2], tube_radius=0.0005, color=(0, 1, 0))
mlab.plot3d(trajectory4[:, 0], trajectory4[:, 1], trajectory4[:, 2], tube_radius=0.0005, color=(0, 0, 1))

