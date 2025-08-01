"""Collision detection for celestial bodies."""

import math
from typing import List, Tuple, Optional
from ..bodies.celestial_body import CelestialBody
from ..bodies.satellite import Satellite
from ..bodies.earth import Earth
from ..bodies.moon import Moon
from ..bodies.custom_body import CustomBody
from ..bodies.impact_marker import ImpactMarker


def distance_between_bodies(body1: CelestialBody, body2: CelestialBody) -> float:
    """Calculate the distance between two celestial bodies."""
    dx = body2.x_position - body1.x_position
    dy = body2.y_position - body1.y_position
    return math.sqrt(dx * dx + dy * dy)


def check_collision(body1: CelestialBody, body2: CelestialBody) -> bool:
    """Check if two celestial bodies have collided."""
    distance = distance_between_bodies(body1, body2)
    # Collision occurs when distance is less than the sum of their radii
    return distance <= (body1.radius_km + body2.radius_km)


def detect_collisions(bodies: List[CelestialBody]) -> List[Tuple[CelestialBody, CelestialBody]]:
    """Detect all collisions between celestial bodies."""
    collisions = []

    # Check all pairs of bodies for collisions
    for i, body1 in enumerate(bodies):
        for j, body2 in enumerate(bodies):
            if i >= j:  # Avoid checking the same pair twice and self-collision
                continue

            if check_collision(body1, body2):
                # Determine which body should be removed based on mass
                if should_body_survive_collision(body1, body2):
                    collisions.append((body2, body1))  # body2 gets destroyed, impacts body1
                else:
                    collisions.append((body1, body2))  # body1 gets destroyed, impacts body2

    return collisions


def should_body_survive_collision(body1: CelestialBody, body2: CelestialBody) -> bool:
    """Determine if body1 should survive a collision with body2."""
    # Earth and Moon are "immovable" - they always survive unless hit by something much larger
    if isinstance(body1, (Earth, Moon)):
        # Earth/Moon survive unless hit by something 10x more massive
        return body2.mass_kg < body1.mass_kg * 10

    if isinstance(body2, (Earth, Moon)):
        # Earth/Moon survive unless hit by something 10x more massive
        return body1.mass_kg < body2.mass_kg * 10

    # For other bodies, the more massive one survives
    # If masses are very close (within 20%), both get destroyed
    mass_ratio = max(body1.mass_kg, body2.mass_kg) / min(body1.mass_kg, body2.mass_kg)
    if mass_ratio < 1.2:  # Very similar masses - mutual destruction
        return False  # Neither survives (we'll handle this special case)

    # More massive body survives
    return body1.mass_kg > body2.mass_kg
def create_impact_marker(colliding_body: CelestialBody, target: CelestialBody) -> ImpactMarker:
    """Create an impact marker at the collision point."""
    # Calculate the impact point on the surface of the target body
    dx = colliding_body.x_position - target.x_position
    dy = colliding_body.y_position - target.y_position
    distance = math.sqrt(dx * dx + dy * dy)

    if distance == 0:
        # Body is exactly at the center, place marker at arbitrary point on surface
        impact_x = target.x_position + target.radius_km
        impact_y = target.y_position
    else:
        # Normalize the direction vector and place marker on the surface
        unit_x = dx / distance
        unit_y = dy / distance
        impact_x = target.x_position + unit_x * target.radius_km
        impact_y = target.y_position + unit_y * target.radius_km

    return ImpactMarker(x_position=impact_x, y_position=impact_y)