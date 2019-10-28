
import numpy as np
import matplotlib.pyplot as plt
from mayavi import mlab
from raysect.core import Point3D, World
from raysect.primitive import import_ply

from vita.core import FieldlineTracer, RK2
from vita.modules.fiesta import Fiesta


# the world scene-graph
world = World()
import_ply("Simple_40-7001_IVC_STEP_190522.ply", scaling=0.001, parent=world)


fiesta = Fiesta('eq_0002_export.mat')
b_field = fiesta.b_field


seed_points = [
    Point3D(0.507, 0, 0),
    Point3D(0.6, 0, 0),
    Point3D(0.7, 0, 0),
    Point3D(0.733, 0, -0.01)
]


field_tracer = FieldlineTracer(b_field, method=RK2(step_size=0.0001))

end_point, trajectory1 = field_tracer.trace(world, seed_points[0], save_trajectory=True, max_length=3)
end_point, trajectory2 = field_tracer.trace(world, seed_points[1], save_trajectory=True, max_length=5)
end_point, trajectory3 = field_tracer.trace(world, seed_points[2], save_trajectory=True, max_length=15)
end_point, trajectory4 = field_tracer.trace(world, seed_points[3], save_trajectory=True, max_length=15)

# mlab.plot3d([0, 0.005, 0.001], [0, 0, 0], [0, 0, 0], tube_radius=0.0005, color=(1, 0, 0))
# mlab.plot3d([0, 0, 0], [0, 0.005, 0.001], [0, 0, 0], tube_radius=0.0005, color=(0, 1, 0))
# mlab.plot3d([0, 0, 0], [0, 0, 0], [0, 0.005, 0.001], tube_radius=0.0005, color=(0, 0, 1))


from raysect_mayavi import visualise_scenegraph
visualise_scenegraph(world)

mlab.plot3d(trajectory1[:, 0], trajectory1[:, 1], trajectory1[:, 2], tube_radius=0.0005, color=(1, 0, 0))
mlab.plot3d(trajectory2[:, 0], trajectory2[:, 1], trajectory2[:, 2], tube_radius=0.0005, color=(0.5, 0.5, 0))
mlab.plot3d(trajectory3[:, 0], trajectory3[:, 1], trajectory3[:, 2], tube_radius=0.0005, color=(0, 1, 0))
mlab.plot3d(trajectory4[:, 0], trajectory4[:, 1], trajectory4[:, 2], tube_radius=0.0005, color=(0, 0, 1))

