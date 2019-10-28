
import numpy as np
cimport numpy as np

from raysect.core.math.function cimport Function2D
from cherab.core.math cimport Vector3D, VectorFunction3D


cdef class MagneticField(VectorFunction3D):

    cdef:
        readonly np.ndarray _r_grid, _z_grid, _br_raw_data, _bz_raw_data, _btor_raw_data
        Function2D _br, _bz, _btor

    cdef Vector3D evaluate(self, double x, double y, double z)
