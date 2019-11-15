
import numpy as np
import matplotlib.pyplot as plt
from mayavi import mlab
from raysect.core import Point3D, World

from vita.modules.cherab import FieldlineTracer, RK2
from vita.modules.fiesta import Fiesta
from vita.utility import get_resource


eq002 = get_resource("ST40", "equilibrium", "eq002")
fiesta = Fiesta(eq002)
b_field = fiesta.b_field


seed_points = [
    Point3D(0.507, 0, 0),
    Point3D(0.6, 0, 0),
    Point3D(0.7, 0, 0),
    Point3D(0.733, 0, -0.01)
]

# the world scene-graph
world = World()


field_tracer = FieldlineTracer(b_field, method=RK2(step_size=0.0001))

end_point, trajectory = field_tracer.trace(world, seed_points[0], save_trajectory=True, max_length=15)
mlab.plot3d(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2], tube_radius=0.0005, color=(1, 0, 0))

end_point, trajectory = field_tracer.trace(world, seed_points[1], save_trajectory=True, max_length=15)
mlab.plot3d(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2], tube_radius=0.0005, color=(0.5, 0.5, 0))

end_point, trajectory = field_tracer.trace(world, seed_points[2], save_trajectory=True, max_length=15)
mlab.plot3d(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2], tube_radius=0.0005, color=(0, 1, 0))

end_point, trajectory = field_tracer.trace(world, seed_points[3], save_trajectory=True, max_length=15)
mlab.plot3d(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2], tube_radius=0.0005, color=(0, 0, 1))

# mlab.plot3d([0, 0.005, 0.001], [0, 0, 0], [0, 0, 0], tube_radius=0.0005, color=(1, 0, 0))
# mlab.plot3d([0, 0, 0], [0, 0.005, 0.001], [0, 0, 0], tube_radius=0.0005, color=(0, 1, 0))
# mlab.plot3d([0, 0, 0], [0, 0, 0], [0, 0.005, 0.001], tube_radius=0.0005, color=(0, 0, 1))

plt.show()

