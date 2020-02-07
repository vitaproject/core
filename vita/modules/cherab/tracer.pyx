
# cython: language_level=3

import numpy as np
cimport numpy as np
from raysect.core cimport World, Point3D, Vector3D
from raysect.core.ray cimport Ray as CoreRay
from raysect.core.intersection cimport Intersection
from cherab.core.math.function.vectorfunction3d cimport VectorFunction3D


cdef class Method:

    cdef Point3D step(self, Point3D point, VectorFunction3D field):
        raise NotImplementedError("The inheriting class must implement this step function.")


cdef class Euler(Method):
    """
    A basic Euler solver for vector field tracing.

    :param float step_size: the spatial step size for the solver.
    """

    cdef double step_size

    def __init__(self, step_size=1E-6):
        self.step_size = step_size

    cdef Point3D step(self, Point3D point, VectorFunction3D field):

        cdef:
            Vector3D vector

        vector = field.evaluate(point.x, point.y, point.z).normalise()
        return point.add(vector.mul(self.step_size))


cdef class RK2(Method):
    """
    A basic Runge-Kutta solver of order 2 for vector field tracing.

    :param float step_size: the spatial step size for the solver.
    """

    cdef double step_size

    def __init__(self, step_size=1E-6):
        self.step_size = step_size

    cdef Point3D step(self, Point3D point, VectorFunction3D field):

        cdef:
            Point3D p2
            Vector3D v1, v2

        v1 = field.evaluate(point.x, point.y, point.z).normalise()

        p2 = point.add(v1.mul(self.step_size))
        v2 = field.evaluate(p2.x, p2.y, p2.z).normalise()

        return point.add(v1.add(v2).mul(0.5 * self.step_size))


cdef class RK4(Method):
    """
    A basic Runge-Kutta solver of order 4 for vector field tracing.

    :param float step_size: the spatial step size for the solver.
    """

    cdef double step_size

    def __init__(self, step_size=1E-6):
        self.step_size = step_size

    cdef Point3D step(self, Point3D point, VectorFunction3D field):

        cdef:
            Point3D pk, pk2
            Vector3D va, vb, vc, vd, v_temp

        pk = point

        va = field.evaluate(pk.x, pk.y, pk.z).normalise()
        va = va.mul(2 * self.step_size)

        vb = field.evaluate(pk.x + va.x/2, pk.y + va.y/2, pk.z + va.z/2)
        vb = vb.mul(2 * self.step_size)

        vc = field.evaluate(pk.x + vb.x/2, pk.y + vb.y/2, pk.z + vb.z/2)
        vc = vc.mul(2 * self.step_size)

        vd = field.evaluate(pk.x + vc.x/2, pk.y + vc.y/2, pk.z + vc.z/2)
        vd = vd.mul(2 * self.step_size)

        v_temp = va.add(vb.mul(2)).add(vc.mul(2)).add(vd).div(6)
        pk2 = pk.add(v_temp)

        return pk2


cdef class FieldlineTracer:
    """
    A class for field line tracing.

    Designed to trace a vector field function with configurable accuracy. Once initialised
    with a vector field and solver method, the trace() function can be called repeatably.

    :param VectorFunction3D field: the vector field to trace.
    :param Method method: a configurable method for solving for the next step along the field
      line. Typically a Runge-Kutta style ODE solver.
    """

    cdef:
        Method method
        VectorFunction3D field

    def __init__(self, field, method=Euler()):

        if not issubclass(type(field), VectorFunction3D):
            raise TypeError('The specified field must be of type VectorFunction3D().')

        if not isinstance(method, Method):
            raise TypeError('The specified field line tracing method variable must be of type Method().')

        self.field = field
        self.method = method

    cpdef tuple trace(self, World world, Point3D seed_point, double max_length=100,
                      bint save_trajectory=False, double save_resolution=0.001):
        """
        Traces the vector vector field for a given seed point and world scenegraph.
        
        :param World world: the Raysect scenegraph being traced.
        :param Point3D seed_point: the seed point for initialising the tracing.
        :param float max_length: the maximum length for fieldline tracing.
        :param bool save_trajectory: boolean flag to toggle whether the 3D trajectory
          will be saved. Caution, this can generate large amounts of data.
        :param float save_resolution: the spatial resolution for trajectory saving if
          the save_trajectory toggle is turned on.
        """

        cdef:
            list trajectory
            Point3D last_point, last_saved_point, new_point, end_point, position, hit_point
            Vector3D direction
            VectorFunction3D field
            double distance_travelled, segment_distance
            int num_segments, ith_position
            np.ndarray trajectory_array
            Intersection intersection
            CoreRay ray

        if not isinstance(world, World):
            raise TypeError('The world variable must be a Raysect scene-graph of type World().')

        if not isinstance(seed_point, Point3D):
            raise TypeError('The seed_point variable must be a Raysect point of type Point3D().')

        trajectory = [seed_point.copy()]
        last_point = seed_point
        last_saved_point = seed_point.copy()

        field = self.field

        ray = CoreRay()

        distance_travelled = 0
        while distance_travelled < max_length:

            new_point = self.method.step(last_point, field)

            segment_distance = last_point.distance_to(new_point)
            direction = last_point.vector_to(new_point).normalise()

            ray.origin = last_point
            ray.direction = direction
            ray.max_distance = segment_distance

            intersection = world.hit(ray)

            if intersection is not None:

                hit_point = intersection.hit_point.transform(intersection.primitive_to_world)
                distance_travelled += segment_distance

                if save_trajectory:
                    trajectory.append(hit_point.copy())

                break

            else:

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

            return end_point, intersection, trajectory_array
        else:
            return end_point, intersection, None

