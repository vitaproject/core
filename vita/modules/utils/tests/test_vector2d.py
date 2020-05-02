
import unittest
import math

from vita.modules.utils.Vector2 import Vector2


# create zero and unit vectors
zero, x, y = Vector2.zeroAndUnits()


class TestVector2(unittest.TestCase):

    def test_init(self):
        """Testing class initialisation"""

        self.assertTrue(x + y == Vector2(1,  1))

    def test_zeroAndUnits(self):
        """Testing initialisation through the zeroAndUnits() utility method"""

        self.assertTrue(zero != x and zero != y and x != y, 'Vector2 did not initialise correctly')

    def test_close(self):
        """Testing Vector2.close()"""

        self.assertFalse(Vector2.close(1, 2), 'Vector2.close() failed')
        self.assertTrue(Vector2.close(1, 1+1e-100), 'Vector2.close() failed')

    def test_repr(self):
        """Testing Vector2.__repr__()"""

        self.assertTrue(repr(x + y * 2) == 'Vector2(1, 2)', 'Vector2().__repr__() string miss-match')

    def test_add(self):
        """Testing Vector2.__add__()"""

        self.assertTrue(x + y == Vector2(1, 1), 'Vector2 __add__() failed')

        X = x
        X = X + x
        self.assertTrue(x == Vector2(1, 0) and X == Vector2(2, 0), 'Vector2 __iadd__() failed')

        self.assertFalse(x + y == Vector2(1+1e-6, 1), 'Vector2 __add__() failed')

    def test_neg(self):
        """Testing Vector2.__neg__()"""

        self.assertTrue(- y == Vector2(0, -1), 'Vector2 __neg__() failed')

    def test_sub(self):
        """Testing Vector2.__sub__()"""

        self.assertTrue(x - y == Vector2(1, -1), 'Vector2 __sub__() failed')

        X = x
        X = X - x
        self.assertTrue(x == Vector2(1, 0) and X == Vector2(0, 0), 'Vector2 __isub__() failed')

    def test_mul(self):
        """Testing Vector2.__mul__()"""

        self.assertTrue(x * 2 + y * 3 == Vector2(2, 3), 'Vector2 __mul__() failed')

        X = x
        X = X * 2
        self.assertTrue(x == Vector2(1, 0) and X == Vector2(2, 0), 'Vector2 __imul__() failed')

    def test_eq(self):
        """Testing Vector2.__eq__()"""

        self.assertTrue(x * 2 + y - x - y == x, 'Vector2 __eq__() failed')

        self.assertTrue(x + y + x * 2 + y * 2 == x * 3 + y * 3, 'Vector2 __eq__() failed')

        self.assertTrue((x + y * 2) * 2 == x * 2 + y * 4, 'Vector2 __eq__() failed')

    def test_truediv(self):
        """Testing Vector2.__truediv__()"""

        self.assertTrue((x * 4 + y * 2) / 2 == x * 2 + y)

        X = x * 4
        X = X / 2
        self.assertTrue(x == Vector2(1, 0) and X == Vector2(2, 0))

    def test_nonzero(self):
        """Testing Vector2.nonZero()"""

        self.assertTrue(Vector2.nonZero(Vector2.closeRadius()))

    def test_close_radius(self):
        """Testing Vector2.closeRadius()"""

        self.assertTrue(Vector2.closeRadius() < 1)

    def test_close(self):
        """Testing Vector2.close()"""

        self.assertTrue(Vector2.close(0, Vector2.closeRadius() / 2))

    def test_abs(self):
        """Testing Vector2.__abs__()"""

        self.assertTrue(abs(x * 3 + y * 4) == 5)

    def test_length(self):
        """Testing Vector2.length()"""

        self.assertTrue((x * 3 + y * 4).length() == 5)

    def test_length2(self):
        """Testing Vector2.length2()"""

        self.assertTrue((x * 3 + y * 4).length2() == 25)

    def test_distance(self):
        """Testing Vector2.distance()"""

        self.assertTrue((x * 3 + y * 4).distance (-(x * 3 + y * 4)) ==  10)

    def test_distance2(self):
        """Testing Vector2.distance2()"""

        self.assertTrue((x * 3 + y * 4).distance2(-(x * 3 + y * 4)) == 100)

    def test_normalise(self):
        """Testing Vector2.normalize()"""

        self.assertTrue((x * 3 + y * 4).clone().normalize() == x * 0.6 + y * 0.8)

    def test_Normalise(self):
        """Testing Vector2.Normalize()"""

        self.assertTrue((x * 3 + y * 4).Normalize() == x * 0.6 + y * 0.8)

    def test_dot(self):
        """Testing Vector2.dot()"""

        self.assertTrue((x * 2 + y).dot(x + y * 3) == 5)

    def test_area(self):
        """Testing Vector2.area()"""

        self.assertTrue((x + y).area(-x + y) == 2)

    def test_trig_utilties(self):
        """Testing Vector2 cos() and sin() utilities"""

        r2 = math.sqrt(2)
        r3 = math.sqrt(3)
        yr3 = y * r3

        self.assertTrue(Vector2.close((x + y).cos(y), 1 / r2))
        self.assertTrue(Vector2.close(x.cos(x + yr3), 0.5))

        self.assertTrue(Vector2.close((x + y).sin(y), 1 / r2))
        self.assertTrue(Vector2.close( x.sin(x + yr3), r3 / 2))

    def test_vector2_rotations(self):
        """Testing Vector2 rotation utilities"""

        self.assertTrue(x.clone().r90() == y)

        self.assertTrue(x.clone().r180() == -x)

        self.assertTrue(x.clone().r270() == -y)

        self.assertTrue(x.R90() == y)

        self.assertTrue(x.R180() == -x)

        self.assertTrue(x.R270() == -y)

    def test_swap(self):
        """Testing Vector2.swap()"""

        self.assertTrue((x + y * 2).swap() == y + x * 2)

        z = x + y * 2
        Z = z.Swap()
        self.assertTrue(z != Z)

    def test_clone(self):
        """Testing Vector2.clone()"""

        z = x + y * 2
        Z = z.clone()
        self.assertTrue(z == Z)

    def test_angle(self):
        """Testing Vector2.angle()"""

        dr = math.radians

        for i in range(-179, +179):  # anticlockwise angle from x
            self.assertTrue(Vector2.close(x.angle(x * math.cos(dr(i)) + y * math.sin(dr(i))), dr(i)))

    def test_smallestAngleToNormalPlane(self):
        """Testing Vector2.smallestAngleToNormalPlane()"""

        dr = math.radians

        # first vector is y, second vector is 0 degrees anti-clockwise from x axis
        self.assertTrue(Vector2.close(dr(0), y.smallestAngleToNormalPlane(x)))
        self.assertTrue(Vector2.close(dr(+45), y.smallestAngleToNormalPlane(x + y)))  # +45
        self.assertTrue(Vector2.close(dr(+90), y.smallestAngleToNormalPlane(y)))  # +90
        self.assertTrue(Vector2.close(dr(+45), y.smallestAngleToNormalPlane(-x + -y)))  # +135
        self.assertTrue(Vector2.close(dr(0), y.smallestAngleToNormalPlane(-x)))  # +180
        self.assertTrue(Vector2.close(dr(+45), y.smallestAngleToNormalPlane(-x + -y)))  # +225
        self.assertTrue(Vector2.close(dr(+90), y.smallestAngleToNormalPlane(-y)))  # +270
        self.assertTrue(Vector2.close(dr(+45), y.smallestAngleToNormalPlane(-x + -y)))  # +315
        self.assertTrue(Vector2.close(dr(0), y.smallestAngleToNormalPlane(x)))  # +360

        p2 = math.pi / 2
        p4 = math.pi / 4

        # original tests
        self.assertTrue(Vector2.close(y.smallestAngleToNormalPlane(y), p2))
        self.assertTrue(Vector2.close(y.smallestAngleToNormalPlane(y * 2), p2))
        self.assertTrue(Vector2.close(y.smallestAngleToNormalPlane(x), 0))
        self.assertTrue(Vector2.close(y.smallestAngleToNormalPlane(-x), 0))
        self.assertTrue(Vector2.close((x + y).smallestAngleToNormalPlane(x), p4))
        self.assertTrue(Vector2.close((x - y).smallestAngleToNormalPlane(x), p4))
