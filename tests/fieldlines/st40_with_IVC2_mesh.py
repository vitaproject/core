
import numpy as np
from mayavi import mlab
from raysect.core import Point3D, World, rotate_z
from raysect.primitive import import_ply
from vita.modules.projection.cherab import FieldlineTracer, RK2, RK4, load_wall_configuration
from vita.modules.equilibrium.fiesta import Fiesta
from vita.utility import get_resource


# the world scene-graph
world = World()

##########################
# add machine components #

config_file = get_resource("ST40-IVC1", "configuration", 'st40_ivc1_config')
load_wall_configuration(config_file, world)


eq002 = get_resource("ST40-IVC1", "equilibrium", "eq_006_2T_export")
fiesta = Fiesta(eq002)
b_field = fiesta.b_field
lcfs = fiesta.get_midplane_lcfs()[1]


seed_points = [
    Point3D(0.75, 0, 0),
    Point3D(lcfs + 0.001, 0, 0),
    Point3D(lcfs + 0.01, 0, 0),
    Point3D(lcfs + 0.02, 0, -0.01)
]


field_tracer = FieldlineTracer(b_field, method=RK2(step_size=0.0001))

end_point, _, trajectory1 = field_tracer.trace(world, seed_points[0], save_trajectory=True, max_length=15)
end_point, _, trajectory2 = field_tracer.trace(world, seed_points[1], save_trajectory=True, max_length=15)
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

