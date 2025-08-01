"""Impact marker for collision sites."""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class ImpactMarker:
    """Represents an impact site where a satellite collided with a celestial body."""
    x_position: float
    y_position: float
    color: Tuple[int, int, int] = (255, 0, 0)  # Red color
    size: int = 5  # Size of the X marker in pixels
