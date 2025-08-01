from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple
import math


@dataclass
class CelestialBody(ABC):
    """Base class for all celestial bodies in the solar system simulation."""
    name: str
    radius_km: float
    mass_kg: float
    x_position: float = 0.0
    y_position: float = 0.0
    x_velocity: float = 0.0
    y_velocity: float = 0.0
    color: Tuple[int, int, int] = (255, 255, 255)  # RGB color for rendering

    def get_position(self) -> Tuple[float, float]:
        """Get the current position as a tuple."""
        return (self.x_position, self.y_position)

    def get_velocity(self) -> Tuple[float, float]:
        """Get the current velocity as a tuple."""
        return (self.x_velocity, self.y_velocity)

    def set_position(self, x: float, y: float) -> None:
        """Set the position of the celestial body."""
        self.x_position = x
        self.y_position = y

    def set_velocity(self, vx: float, vy: float) -> None:
        """Set the velocity of the celestial body."""
        self.x_velocity = vx
        self.y_velocity = vy

    def distance_to(self, other: 'CelestialBody') -> float:
        """Calculate the distance to another celestial body."""
        dx = self.x_position - other.x_position
        dy = self.y_position - other.y_position
        return math.sqrt(dx**2 + dy**2)

    @abstractmethod
    def update(self, dt: float) -> None:
        """Update the celestial body's state. Must be implemented by subclasses."""
        pass
