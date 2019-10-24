
import numpy as np
from raysect.core import World, Point3D
from cherab.core.math.function import VectorFunction3D


class Method:

    def step(self, point, field, *args):
        raise NotImplementedError("The inheriting class must implement this step function.")


class Euler(Method):

    def __init__(self, step_size=1E-6):
        self.step_size = step_size

    def step(self, point, field):

        vector = field(point.x, point.y, point.z).normalise()

        new_point = point + vector * self.step_size

        return new_point


class RK2(Method):

    def __init__(self, step_size=1E-6):
        self.step_size = step_size

    def step(self, point, field):

        vector = field(point.x, point.y, point.z).normalise()

        point_star = point + vector * self.step_size
        new_vector = field(point_star.x, point_star.y, point_star.z).normalise()

        new_point = point + (vector + new_vector) * 0.5 * self.step_size

        return new_point


class RK4(Method):

    pass


class FieldlineTracer:

    def __init__(self, field, method=Euler()):

        if not issubclass(type(field), VectorFunction3D):
            raise TypeError('The specified field must be of type VectorFunction3D().')

        self.field = field
        self.method = method

    def trace(self, world, seed_point, max_length=100, save_trajectory=False, save_resolution=0.001):

        if not isinstance(world, World):
            raise TypeError('The world variable must be a Raysect scene-graph of type World().')

        if not isinstance(seed_point, Point3D):
            raise TypeError('The seed_point variable must be a Raysect point of type Point3D().')

        trajectory = [seed_point.copy()]
        last_point = seed_point
        last_saved_point = seed_point.copy()

        field = self.field

        distance_travelled = 0
        while distance_travelled < max_length:

            new_point = self.method.step(last_point, field)
            distance_travelled += last_point.distance_to(new_point)

            if save_trajectory and last_saved_point.distance_to(new_point) > save_resolution:
                last_saved_point = new_point
                trajectory.append(last_saved_point)

            last_point = new_point

        end_point = last_point

        if save_trajectory:

            num_segments = len(trajectory)
            trajectory_array = np.zeros((num_segments, 3))
            for ith_position, position in enumerate(trajectory):
                trajectory_array[ith_position, 0] = position.x
                trajectory_array[ith_position, 1] = position.y
                trajectory_array[ith_position, 2] = position.z

            return end_point, trajectory_array
        else:
            return end_point, None

