import math, sys

class Vector2(object):
  """Vectors in 2 dimensional euclidean space"""

  def __init__(this, x = 0, y = 0):
    """Create a vector"""
    this.x = x
    this.y = y

  def __repr__(this):
    """String representation of a vector"""
    return this.__class__.__name__ + f'({this.x}, {this.y})'

  def __neg__(this):
    """Rotate a copy of a vector by 180 degrees"""
    return this.clone().r180()

  def __abs__(this):
    """Length of a vector"""
    return this.length()

  def __eq__(this, other):
    """Whether two vectors are equal within a radius of floating point epsilon"""
    return Vector2.close(this.x, other.x) and Vector2.close(this.y, other.y)

  def __iadd__(this, other):
    """Add the second vector to the first vector"""
    this.x += other.x
    this.y += other.y
    return this

  def __add__(this, other):
    """Add the second vector to a copy of the first vector"""
    return Vector2(this.x + other.x, this.y + other.y)

  def __isub__(this, other):
    """Subtract the second vector from the first vector"""
    this.x -= other.x
    this.y -= other.y
    return this

  def __sub__(this, other):
    """Subtract the second vector from a copy of the first vector"""
    return Vector2(this.x - other.x, this.y - other.y)

  def __imul__(this, scalar):
    """Multiply a vector by a scalar"""
    this.x *= scalar
    this.y *= scalar
    return this

  def __mul__(this, scalar):
    """Multiply a copy of vector by a scalar"""
    return Vector2(this.x * scalar, this.y * scalar)

  def __itruediv__(this, scalar):
    """Divide a vector by a scalar"""
    this.x /= scalar
    this.y /= scalar
    return this

  def __truediv__(this, scalar):
    """Divide a copy of a vector by a scalar"""
    return Vector2(this.x / scalar, this.y / scalar)

  def zeroAndUnits():
    """Create the useful vectors: zero=(0,0), x=(1,0), y=(0,1)"""
    return Vector2(0, 0), Vector2(1, 0), Vector2(0, 1),

  def clone(this):
    """Clone a vector to allow it to be modified by other operations"""
    return Vector2(this.x, this.y)

  def closeRadius():
    """Two numbers are equal if they are less than this far apart"""
    return 1e-10

  def close(a, b):
    """Whether two numbers are close"""
    delta = Vector2.closeRadius()
    return a > b - delta and a < b + delta

  def nonZero(n):
    """Whether a number is non zero"""
    return not Vector2.close(n, 0)

  def length(this):
    """Length of a vector."""
    return math.sqrt(this.x**2 + this.y**2)

  def length2(this):
    """Length squared of a vector."""
    return this.x**2 + this.y**2

  def distance(this, other):
    """Distance between the points identified by two vectors when placed on the same point."""
    return math.sqrt((this.x-other.x)**2 + (this.y-other.y)**2)

  def distance2(this, other):
    """Distance squared between the points identified
       by two vectors when placed on the same point."""
    return (this.x-other.x)**2 + (this.y-other.y)**2

  def normalize(this):
    """Normalize a vector."""
    l = this.length()
    assert(Vector2.nonZero(l))
    return this / l

  def Normalize(this):
    """Normalize a copy of vector."""
    l = this.length()
    assert(Vector2.nonZero(l))
    return this.clone() / l

  def dot(this, other):
    """Dot product of two vectors."""
    return this.x * other.x + this.y * other.y

  def area(this, other):
    """Signed area of the parallelogram defined by the two vectors. The area is negative if the second vector appears to the right of the first if they are both placed at the origin and the observer stands against the z-axis in a left handed coordinate system."""
    return this.x * other.y - this.y * other.x

  def cos(this, other):
    """cos(angle between two vectors)."""
    return this.dot(other) / this.length() / other.length()

  def sin(this, other):
    """sin(angle between two vectors)."""
    return this.area(other) / this.length() / other.length()

  def angle(o, p):
    """Angle in radians anticlockwise that the first vector must be rotated to point along the second vector normalized to the range: -pi to +pi."""
    c = o.cos(p);
    s = o.sin(p);
    a = math.acos(c);
    return a if s > 0 else -a

  def smallestAngleToNormalPlane(a, b):
    """The smallest angle between the second vector and a plane normal to the first vector"""
    r = abs(a.angle(b))
    p = math.pi / 2
    return p - r if r < p else r - p

  def r90(this):
    """Rotate a vector by 90 degrees anticlockwise."""
    this.x, this.y = -this.y, this.x
    return this

  def R90(this):
    """Rotate a copy of a vector by 90 degrees anticlockwise."""
    return Vector2(-this.y, this.x)

  def r180(this):
    """Rotate a vector by 180 degrees."""
    this.x, this.y = -this.x, -this.y
    return this

  def R180(this):
    """Rotate  a copy of a vector by 180 degrees."""
    return Vector2(-this.x, -this.y)

  def r270(this):
    """Rotate a copy of a vector by 270 degrees anticlockwise."""
    this.x, this.y = this.y, -this.x
    return this

  def R270(this):
    """Rotate a vector by 270 degrees anticlockwise."""
    return Vector2(this.y, -this.x)

  def swap(this):
    """Swap the components of a vector"""
    this.x, this.y = this.y, this.x
    return this

  def Swap(this):
    """Swap the components of a copy of a vector"""
    return Vector2(this.y, this.x)
