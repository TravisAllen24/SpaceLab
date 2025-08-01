"""Mathematical utility functions for the solar system simulation."""

import math
from typing import Tuple


def magnitude(x: float, y: float) -> float:
    """Calculate the magnitude of a 2D vector."""
    return math.sqrt(x**2 + y**2)


def normalize(x: float, y: float) -> Tuple[float, float]:
    """Normalize a 2D vector to unit length."""
    mag = magnitude(x, y)
    if mag == 0:
        return (0.0, 0.0)
    return (x / mag, y / mag)


def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate distance between two points."""
    return magnitude(x2 - x1, y2 - y1)


def degrees_to_radians(degrees: float) -> float:
    """Convert degrees to radians."""
    return degrees * math.pi / 180.0


def radians_to_degrees(radians: float) -> float:
    """Convert radians to degrees."""
    return radians * 180.0 / math.pi
