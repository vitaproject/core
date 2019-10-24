
# cython: language_level=3


from raysect.core cimport World, Point3D
from cherab.core.math.function cimport VectorFunction3D


cdef class Method:

    cdef Point3D step(self, Point3D point, VectorFunction3D field)


cdef class Euler(Method):

    cdef public double step_size


cdef class RK2(Method):

    cdef public double step_size


cdef class FieldlineTracer:

    cdef:
        readonly VectorFunction3D field
        readonly Method method

    cpdef tuple trace(self, World world, Point3D seed_point, double max_length=*, bint save_trajectory=*, double save_resolution=*)
