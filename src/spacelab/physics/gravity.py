"""Physics calculations for the solar system simulation."""

import math
from typing import List, Tuple
from ..bodies.celestial_body import CelestialBody


# Gravitational constant (adjusted for km, kg, s units)
G = 6.67430e-11 * 1e-9  # Convert from m³/kg⋅s² to km³/kg⋅s²


def calculate_gravitational_force(body1: CelestialBody, body2: CelestialBody) -> Tuple[float, float]:
    """
    Calculate gravitational force between two celestial bodies.

    Returns:
        Tuple[float, float]: Force components (fx, fy) acting on body1
    """
    # Calculate distance vector
    dx = body2.x_position - body1.x_position
    dy = body2.y_position - body1.y_position
    distance = math.sqrt(dx**2 + dy**2)

    # Avoid division by zero
    if distance == 0:
        return (0.0, 0.0)

    # Calculate gravitational force magnitude
    force_magnitude = G * body1.mass_kg * body2.mass_kg / (distance**2)

    # Calculate force components (unit vector * magnitude)
    fx = force_magnitude * dx / distance
    fy = force_magnitude * dy / distance

    return (fx, fy)


def calculate_total_force(body: CelestialBody, other_bodies: List[CelestialBody]) -> Tuple[float, float]:
    """
    Calculate total gravitational force acting on a body from all other bodies.

    Args:
        body: The body to calculate forces for
        other_bodies: List of other bodies exerting gravitational force

    Returns:
        Tuple[float, float]: Total force components (fx, fy)
    """
    total_fx = 0.0
    total_fy = 0.0

    for other_body in other_bodies:
        if other_body != body:  # Don't calculate force from itself
            fx, fy = calculate_gravitational_force(body, other_body)
            total_fx += fx
            total_fy += fy

    return (total_fx, total_fy)


def apply_gravitational_forces(bodies: List[CelestialBody], dt: float) -> None:
    """
    Apply gravitational forces to update velocities of all bodies.

    Args:
        bodies: List of all celestial bodies in the simulation
        dt: Time step in seconds
    """
    # Calculate forces for each body
    forces = []
    for body in bodies:
        other_bodies = [b for b in bodies if b != body]
        fx, fy = calculate_total_force(body, other_bodies)
        forces.append((fx, fy))

    # Apply forces to update velocities
    for i, body in enumerate(bodies):
        fx, fy = forces[i]

        # F = ma, so a = F/m
        ax = fx / body.mass_kg
        ay = fy / body.mass_kg

        # Update velocities: v = v0 + at
        body.x_velocity += ax * dt
        body.y_velocity += ay * dt
