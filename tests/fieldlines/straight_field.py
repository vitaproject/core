

import numpy as np
import matplotlib.pyplot as plt
from mayavi import mlab
from raysect.core import World, Point3D, Vector3D
from cherab.core.math import ConstantVector3D

from vita.modules.projection.cherab import FieldlineTracer, Euler


# the world scene-graph
world = World()

b_field = ConstantVector3D(Vector3D(0, 1.5, 0))

field_tracer = FieldlineTracer(b_field, method=Euler(step_size=0.001))

start_point = Point3D(0, 0, 0)
end_point, trajectory = field_tracer.trace(world, start_point, save_trajectory=True, max_steps=1000)


num_segments = len(trajectory)
x = np.zeros(num_segments)
y = np.zeros(num_segments)
z = np.zeros(num_segments)
for ith_position, position in enumerate(trajectory):
    x[ith_position] = position.x
    y[ith_position] = position.y
    z[ith_position] = position.z


mlab.plot3d(x, y, z, tube_radius=0.0005, color=(1, 0, 0))

# mlab.plot3d([0, 0.005, 0.001], [0, 0, 0], [0, 0, 0], tube_radius=0.0005, color=(1, 0, 0))
# mlab.plot3d([0, 0, 0], [0, 0.005, 0.001], [0, 0, 0], tube_radius=0.0005, color=(0, 1, 0))
# mlab.plot3d([0, 0, 0], [0, 0, 0], [0, 0.005, 0.001], tube_radius=0.0005, color=(0, 0, 1))

plt.show()
