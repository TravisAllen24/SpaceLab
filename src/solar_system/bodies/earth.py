from dataclasses import dataclass
from .celestial_body import CelestialBody


@dataclass
class Earth(CelestialBody):
    """Earth celestial body with default values."""
    name: str = "Earth"
    radius_km: float = 6371.0
    mass_kg: float = 5.972e24
    x_position: float = 0.0
    y_position: float = 0.0
    x_velocity: float = 0.0
    y_velocity: float = 0.0
    color: tuple = (0, 100, 255)  # Blue color for Earth

    def update(self, dt: float) -> None:
        """Update Earth's position based on its velocity."""
        self.x_position += self.x_velocity * dt
        self.y_position += self.y_velocity * dt
