from dataclasses import dataclass
from typing import Tuple
from .celestial_body import CelestialBody


@dataclass
class Satellite(CelestialBody):
    """Artificial satellite that can orbit around other celestial bodies."""

    def update(self, dt: float) -> None:
        """Update Satellite's position based on its velocity."""
        self.x_position += self.x_velocity * dt
        self.y_position += self.y_velocity * dt
