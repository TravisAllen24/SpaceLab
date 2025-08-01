from dataclasses import dataclass
from typing import Tuple
from .celestial_body import CelestialBody


@dataclass
class Satellite(CelestialBody):
    """Artificial satellite that can orbit around other celestial bodies."""

