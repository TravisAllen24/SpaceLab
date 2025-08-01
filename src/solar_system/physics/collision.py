"""Collision detection for celestial bodies."""

import math
from typing import List, Tuple, Optional
from ..bodies.celestial_body import CelestialBody
from ..bodies.satellite import Satellite
from ..bodies.earth import Earth
from ..bodies.moon import Moon
from ..bodies.impact_marker import ImpactMarker


def distance_between_bodies(body1: CelestialBody, body2: CelestialBody) -> float:
    """Calculate the distance between two celestial bodies."""
    dx = body2.x_position - body1.x_position
    dy = body2.y_position - body1.y_position
    return math.sqrt(dx * dx + dy * dy)


def check_collision(satellite: Satellite, target: CelestialBody) -> bool:
    """Check if a satellite has collided with a target celestial body."""
    distance = distance_between_bodies(satellite, target)
    # Collision occurs when distance is less than the sum of their radii
    return distance <= (satellite.radius_km + target.radius_km)


def detect_collisions(bodies: List[CelestialBody]) -> List[Tuple[Satellite, CelestialBody]]:
    """Detect all collisions between satellites and other celestial bodies."""
    collisions = []

    satellites = [body for body in bodies if isinstance(body, Satellite)]
    targets = [body for body in bodies if isinstance(body, (Earth, Moon))]

    for satellite in satellites:
        for target in targets:
            if check_collision(satellite, target):
                collisions.append((satellite, target))

    return collisions


def create_impact_marker(satellite: Satellite, target: CelestialBody) -> ImpactMarker:
    """Create an impact marker at the collision point."""
    # Calculate the impact point on the surface of the target body
    dx = satellite.x_position - target.x_position
    dy = satellite.y_position - target.y_position
    distance = math.sqrt(dx * dx + dy * dy)

    if distance == 0:
        # Satellite is exactly at the center, place marker at arbitrary point on surface
        impact_x = target.x_position + target.radius_km
        impact_y = target.y_position
    else:
        # Normalize the direction vector and place marker on the surface
        unit_x = dx / distance
        unit_y = dy / distance
        impact_x = target.x_position + unit_x * target.radius_km
        impact_y = target.y_position + unit_y * target.radius_km

    return ImpactMarker(x_position=impact_x, y_position=impact_y)
