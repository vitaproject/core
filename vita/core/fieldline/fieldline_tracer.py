

from scipy.integrate import ode
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


class RK4(Method):

    pass


class FieldlineTracer:

    def __init__(self, field, method=Euler()):

        if not isinstance(field, VectorFunction3D):
            raise TypeError('The specified field must be of type VectorFunction3D().')

        self.field = field
        self.method = method

    def trace(self, world, seed_point, max_steps=1E7, save_trajectory=False):

        if not isinstance(world, World):
            raise TypeError('The world variable must be a Raysect scene-graph of type World().')

        if not isinstance(seed_point, Point3D):
            raise TypeError('The seed_point variable must be a Raysect point of type Point3D().')

        trajectory = [seed_point.copy()]

        field = self.field

        steps = 0
        while steps < max_steps:
            new_point = self.method.step(seed_point, field)

            if save_trajectory:
                trajectory.append(new_point.copy())

            steps += 1

        end_point = new_point

        if save_trajectory:
            return end_point, trajectory
        else:
            return end_point, None

