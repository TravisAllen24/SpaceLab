"""Basic orbit example demonstrating a satellite orbiting Earth."""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from solar_system.bodies.earth import Earth
from solar_system.bodies.satellite import Satellite
from solar_system.simulation import SolarSystemSimulation


def create_basic_orbit_simulation():
    """Create a simple Earth-satellite orbit simulation."""

    # Create simulation
    sim = SolarSystemSimulation()

    # Clear default bodies and add custom setup
    sim.bodies.clear()

    # Earth at center
    earth = Earth()

    # Satellite in circular orbit
    satellite = Satellite(
        name="Test Satellite",
        radius_km=0.01,
        mass_kg=1000,
        x_position=500,  # 500 km from Earth
        y_position=0,
        x_velocity=0,
        y_velocity=7.61,  # Orbital velocity for 500km altitude
        color=(255, 0, 0)  # Red
    )

    sim.bodies = [earth, satellite]

    return sim


if __name__ == "__main__":
    print("Running basic orbit example...")
    simulation = create_basic_orbit_simulation()
    simulation.run()
