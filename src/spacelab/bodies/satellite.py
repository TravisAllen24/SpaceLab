from typing import Tuple
from dataclasses import dataclass
from .celestial_body import CelestialBody


@dataclass
class Satellite(CelestialBody):
    """Artificial satellite that can orbit around other celestial bodies."""
    radius_km: float = 0.1  # Small satellite
    mass_kg: float = 1000.0  # 1 ton satellite
    color: Tuple[int, int, int] = (0, 255, 255)  # Cyan color