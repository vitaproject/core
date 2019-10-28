
import numpy as np
from libc.math cimport sqrt, atan2

from raysect.core.math cimport new_vector3d
from raysect.core.math import rotate_z
from cherab.core.math import Interpolate2DCubic


cdef double RAD2DEG = 360 / (2 * np.pi)


cdef class MagneticField(VectorFunction3D):

    def __init__(self, r_grid, z_grid, br, bz, btor):
        """
        A magnetic field 3D vector function.

        :param r_grid:
        :param z_grid:
        :param br:
        :param bz:
        :param btor:
        """

        self._r_grid = r_grid
        self._z_grid = z_grid
        self._br_raw_data = br
        self._bz_raw_data = bz
        self._btor_raw_data = btor

        self._br = Interpolate2DCubic(self._r_grid, self._z_grid, self._br_raw_data, extrapolate=True)
        self._bz = Interpolate2DCubic(self._r_grid, self._z_grid, self._bz_raw_data, extrapolate=True)
        self._btor = Interpolate2DCubic(self._r_grid, self._z_grid, self._btor_raw_data, extrapolate=True)

    cdef Vector3D evaluate(self, double x, double y, double z):

        cdef:
            double r, theta
            double br, bz, btor
            Vector3D b_vector

        r = sqrt(x*x + y*y)
        theta = atan2(y, x) * RAD2DEG

        br = self._br.evaluate(r, z)
        bz = self._bz.evaluate(r, z)
        btor = self._btor.evaluate(r, z)

        b_vector = new_vector3d(br, btor, bz)

        # TODO - replace this transform with direct manipulation
        return b_vector.transform(rotate_z(theta))
