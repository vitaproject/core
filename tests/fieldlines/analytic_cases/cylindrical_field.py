
from math import sqrt
import numpy as np
from mayavi import mlab
from raysect.core import Point3D, Vector3D, rotate_z, World
from cherab.core.math import PythonVectorFunction3D

from vita.modules.projection.cherab import FieldlineTracer, RK2, RK4


def vectorfunction3d(x, y, z):

    r = sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)

    b_mag = 1 / r

    b_vec = Vector3D(r * np.cos(phi), r * np.sin(phi), 0)
    b_vec = b_vec.transform(rotate_z(90))
    b_vec = b_vec.normalise() * b_mag

    return b_vec


world = World()
b_field = PythonVectorFunction3D(vectorfunction3d)


field_tracer1 = FieldlineTracer(b_field, method=RK2(step_size=0.0001))
field_tracer2 = FieldlineTracer(b_field, method=RK4(step_size=0.0001))

mlab.plot3d([0, 0.5, 1], [0, 0, 0], [0, 0, 0], tube_radius=0.001, color=(1, 0, 0))
mlab.plot3d([0, 0, 0], [0, 0.5, 1], [0, 0, 0], tube_radius=0.001, color=(0, 1, 0))
mlab.plot3d([0, 0, 0], [0, 0, 0], [0, 0.5, 1], tube_radius=0.001, color=(0, 0, 1))

seed_point = Point3D(1, 0, 0)
end_point, _, trajectory1 = field_tracer1.trace(world, seed_point, save_trajectory=True, max_length=50)
end_point, _, trajectory2 = field_tracer2.trace(world, seed_point, save_trajectory=True, max_length=50)

mlab.plot3d(trajectory1[:, 0], trajectory1[:, 1], trajectory1[:, 2], tube_radius=0.0005, color=(1, 0, 0))
mlab.plot3d(trajectory2[:, 0], trajectory2[:, 1], trajectory2[:, 2], tube_radius=0.0005, color=(0.5, 0.5, 0))

print()
print('radius 1')
r = sqrt(trajectory1[-1][0]**2 + trajectory1[-1][1]**2)
print('RK2 radial drift', r)

r =  sqrt(trajectory2[-1][0]**2 + trajectory2[-1][1]**2)
print('RK4 radial drift', r)


seed_point = Point3D(0.5, 0, 0)
end_point, _, trajectory1 = field_tracer1.trace(world, seed_point, save_trajectory=True, max_length=50)
end_point, _, trajectory2 = field_tracer2.trace(world, seed_point, save_trajectory=True, max_length=50)
print()
print('radius 0.5')
r = sqrt(trajectory1[-1][0]**2 + trajectory1[-1][1]**2)
print('RK2 radial drift', r)
r =  sqrt(trajectory2[-1][0]**2 + trajectory2[-1][1]**2)
print('RK4 radial drift', r)


seed_point = Point3D(1.5, 0, 0)
end_point, _, trajectory1 = field_tracer1.trace(world, seed_point, save_trajectory=True, max_length=50)
end_point, _, trajectory2 = field_tracer2.trace(world, seed_point, save_trajectory=True, max_length=50)
print()
print('radius 0.5')
r = sqrt(trajectory1[-1][0]**2 + trajectory1[-1][1]**2)
print('RK2 radial drift', r)
r =  sqrt(trajectory2[-1][0]**2 + trajectory2[-1][1]**2)
print('RK4 radial drift', r)
