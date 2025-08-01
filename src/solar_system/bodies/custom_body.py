"""Custom celestial body for user-created objects."""

from dataclasses import dataclass
from typing import Tuple
from .celestial_body import CelestialBody


@dataclass
class CustomBody(CelestialBody):
    """User-created celestial body with custom properties."""

    def update(self, dt: float) -> None:
        """Update CustomBody's position based on its velocity."""
        self.x_position += self.x_velocity * dt
        self.y_position += self.y_velocity * dt
