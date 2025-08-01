from dataclasses import dataclass
from .celestial_body import CelestialBody


@dataclass
class Moon(CelestialBody):
    """Moon celestial body with default values."""
    name: str = "Moon"
    radius_km: float = 1737.4
    mass_kg: float = 7.34767309e22
    x_position: float = 384400.0  # Average distance from Earth in km
    y_position: float = 0.0
    x_velocity: float = 0.0
    y_velocity: float = 1.022  # Average orbital speed in km/s
    color: tuple = (200, 200, 200)  # Gray color for Moon

    def update(self, dt: float) -> None:
        """Update Moon's position based on its velocity."""
        self.x_position += self.x_velocity * dt
        self.y_position += self.y_velocity * dt
