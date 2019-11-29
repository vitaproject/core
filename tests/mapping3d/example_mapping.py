
import time
import numpy as np
from numpy.random import random
import matplotlib.pyplot as plt
from scipy.optimize import brentq
from mayavi import mlab
from raysect.core import Point3D, World
from raysect.primitive import import_ply, export_vtk

from vita.modules.cherab import FieldlineTracer, RK2
from vita.modules.fiesta import Fiesta
from vita.utility import get_resource


# the world scene-graph
world = World()

# add machine components
meshes = {}

centre_column_lower = get_resource("ST40-IVC1", "mesh", "centre_column_lower")
centre_column_lower = import_ply(centre_column_lower, scaling=0.001, parent=world, name="centre_column_lower")
meshes["centre_column_lower"] = centre_column_lower

centre_column_middle = get_resource("ST40-IVC1", "mesh", "centre_column_middle")
centre_column_middle = import_ply(centre_column_middle, scaling=0.001, parent=world, name="centre_column_middle")
meshes["centre_column_middle"] = centre_column_middle

centre_column_upper = get_resource("ST40-IVC1", "mesh", "centre_column_upper")
centre_column_upper = import_ply(centre_column_upper, scaling=0.001, parent=world, name="centre_column_upper")
meshes["centre_column_upper"] = centre_column_upper

divertor_tile_lower = get_resource("ST40-IVC1", "mesh", "divertor_tile_lower")
divertor_tile_lower = import_ply(divertor_tile_lower, scaling=0.001, parent=world, name="divertor_tile_lower")
meshes["divertor_tile_lower"] = divertor_tile_lower

divertor_tile_upper = get_resource("ST40-IVC1", "mesh", "divertor_tile_upper")
divertor_tile_upper = import_ply(divertor_tile_upper, scaling=0.001, parent=world, name="divertor_tile_upper")
meshes["divertor_tile_upper"] = divertor_tile_upper

poloidal_coils_lower = get_resource("ST40-IVC1", "mesh", "poloidal_coils_lower")
poloidal_coils_lower = import_ply(poloidal_coils_lower, scaling=0.001, parent=world, name="poloidal_coils_lower")
meshes["poloidal_coils_lower"] = poloidal_coils_lower

poloidal_coils_upper = get_resource("ST40-IVC1", "mesh", "poloidal_coils_upper")
poloidal_coils_upper = import_ply(poloidal_coils_upper, scaling=0.001, parent=world, name="poloidal_coils_upper")
meshes["poloidal_coils_upper"] = poloidal_coils_upper

vessel_lower = get_resource("ST40-IVC1", "mesh", "vessel_lower")
vessel_lower = import_ply(vessel_lower, scaling=0.001, parent=world, name="vessel_lower")
meshes["vessel_lower"] = vessel_lower

vessel_upper = get_resource("ST40-IVC1", "mesh", "vessel_upper")
vessel_upper = import_ply(vessel_upper, scaling=0.001, parent=world, name="vessel_upper")
meshes["vessel_upper"] = vessel_upper

vessel = get_resource("ST40-IVC1", "mesh", "vessel")
vessel = import_ply(vessel, scaling=0.001, parent=world, name="vessel")
meshes["vessel"] = vessel

# load the equilibrium
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
radial_min = lcfs_radius
radial_max = lcfs_radius + 0.1

mesh_masks = {}
null_intersections = 0

t_start = time.time()
num_of_fieldlines = 50000
for i in range(num_of_fieldlines):

    seed_radius = radial_min + (random() * 0.1)
    seed_angle = random() * 45
    seed_point = Point3D(seed_radius * np.cos(np.deg2rad(seed_angle)),
                         seed_radius * np.sin(np.deg2rad(seed_angle)),
                         0)

    end_point, intersection, _ = field_tracer.trace(world, seed_point, max_length=15)

    if intersection is not None:
        try:
            mask = mesh_masks[intersection.primitive.name]
        except KeyError:
            mask = set()
            mesh_masks[intersection.primitive.name] = mask

        mask.add(intersection.primitive_coords[0])

    else:
        null_intersections += 1

    if not i % 1000:
        print(i)

t_end = time.time()

print("Meshes collided with:")
for mesh_name in mesh_masks.keys():
    print(mesh_name)
print("Number of null intersections")
print(null_intersections)

print()
print("execution: {}".format(t_end-t_start))

for mesh_name in mesh_masks.keys():

    mesh_primitive = meshes[mesh_name]
    num_tris = mesh_primitive.data.triangles.shape[0]
    mesh_mask = np.zeros(num_tris)

    for tri_id in mesh_masks[mesh_name]:
        mesh_mask[tri_id] = 1.0

    export_vtk(mesh_primitive, mesh_name+".vtk", triangle_data={"fieldline-mask":mesh_mask})
