"""Predefined celestial bodies for different scenarios."""

import math
from ..bodies.earth import Earth
from ..bodies.moon import Moon
from ..bodies.satellite import Satellite
from ..bodies.custom_body import CustomBody


def create_earth_moon_system():
    """Create the Earth-Moon system with ISS."""
    bodies = []

    # Earth at center
    earth = Earth()
    bodies.append(earth)

    # Moon orbiting Earth
    moon = Moon()
    bodies.append(moon)

    # ISS satellite
    iss = Satellite(
        name="ISS",
        radius_km=0.1,
        mass_kg=420000,
        x_position=6771,  # Earth radius + 400km altitude
        y_position=0,
        x_velocity=0,
        y_velocity=7.66,  # Orbital velocity
        color=(255, 255, 0)  # Yellow
    )
    bodies.append(iss)

    return bodies


def create_solar_system():
    """Create the complete solar system with all 8 planets in varied positions."""
    bodies = []

    # Sun at center
    sun = CustomBody(
        name="Sun",
        radius_km=696340,  # Actual sun radius
        mass_kg=1.989e30,  # Actual sun mass
        x_position=0,
        y_position=0,
        x_velocity=0,
        y_velocity=0,
        color=(255, 255, 100)  # Bright yellow
    )
    bodies.append(sun)

    # Mercury - at 45 degrees
    mercury_angle = math.radians(45)
    mercury_distance = 57909050
    mercury = CustomBody(
        name="Mercury",
        radius_km=2439.7,
        mass_kg=3.301e23,
        x_position=mercury_distance * math.cos(mercury_angle),
        y_position=mercury_distance * math.sin(mercury_angle),
        x_velocity=-47.36 * math.sin(mercury_angle),
        y_velocity=47.36 * math.cos(mercury_angle),
        color=(150, 150, 150)  # Gray
    )
    bodies.append(mercury)

    # Venus - at 120 degrees
    venus_angle = math.radians(120)
    venus_distance = 108208000
    venus = CustomBody(
        name="Venus",
        radius_km=6051.8,
        mass_kg=4.867e24,
        x_position=venus_distance * math.cos(venus_angle),
        y_position=venus_distance * math.sin(venus_angle),
        x_velocity=-35.02 * math.sin(venus_angle),
        y_velocity=35.02 * math.cos(venus_angle),
        color=(255, 200, 100)  # Yellow-orange
    )
    bodies.append(venus)

    # Earth - at 200 degrees
    earth_angle = math.radians(200)
    earth_distance = 149597870
    earth = CustomBody(
        name="Earth",
        radius_km=6371,
        mass_kg=5.972e24,
        x_position=earth_distance * math.cos(earth_angle),
        y_position=earth_distance * math.sin(earth_angle),
        x_velocity=-29.78 * math.sin(earth_angle),
        y_velocity=29.78 * math.cos(earth_angle),
        color=(0, 100, 255)  # Blue
    )
    bodies.append(earth)

    # Mars - at 300 degrees
    mars_angle = math.radians(300)
    mars_distance = 227943824
    mars = CustomBody(
        name="Mars",
        radius_km=3390,
        mass_kg=6.39e23,
        x_position=mars_distance * math.cos(mars_angle),
        y_position=mars_distance * math.sin(mars_angle),
        x_velocity=-24.07 * math.sin(mars_angle),
        y_velocity=24.07 * math.cos(mars_angle),
        color=(255, 100, 100)  # Red
    )
    bodies.append(mars)

    # Jupiter - at 80 degrees
    jupiter_angle = math.radians(80)
    jupiter_distance = 778299000
    jupiter = CustomBody(
        name="Jupiter",
        radius_km=69911,
        mass_kg=1.898e27,
        x_position=jupiter_distance * math.cos(jupiter_angle),
        y_position=jupiter_distance * math.sin(jupiter_angle),
        x_velocity=-13.07 * math.sin(jupiter_angle),
        y_velocity=13.07 * math.cos(jupiter_angle),
        color=(255, 200, 150)  # Orange-ish
    )
    bodies.append(jupiter)

    # Saturn - at 160 degrees
    saturn_angle = math.radians(160)
    saturn_distance = 1429400000
    saturn = CustomBody(
        name="Saturn",
        radius_km=58232,
        mass_kg=5.683e26,
        x_position=saturn_distance * math.cos(saturn_angle),
        y_position=saturn_distance * math.sin(saturn_angle),
        x_velocity=-9.68 * math.sin(saturn_angle),
        y_velocity=9.68 * math.cos(saturn_angle),
        color=(255, 220, 150)  # Light orange
    )
    bodies.append(saturn)

    # Uranus - at 240 degrees
    uranus_angle = math.radians(240)
    uranus_distance = 2870658186
    uranus = CustomBody(
        name="Uranus",
        radius_km=25362,
        mass_kg=8.681e25,
        x_position=uranus_distance * math.cos(uranus_angle),
        y_position=uranus_distance * math.sin(uranus_angle),
        x_velocity=-6.80 * math.sin(uranus_angle),
        y_velocity=6.80 * math.cos(uranus_angle),
        color=(100, 200, 255)  # Light blue
    )
    bodies.append(uranus)

    # Neptune - at 30 degrees
    neptune_angle = math.radians(30)
    neptune_distance = 4498396441
    neptune = CustomBody(
        name="Neptune",
        radius_km=24622,
        mass_kg=1.024e26,
        x_position=neptune_distance * math.cos(neptune_angle),
        y_position=neptune_distance * math.sin(neptune_angle),
        x_velocity=-5.43 * math.sin(neptune_angle),
        y_velocity=5.43 * math.cos(neptune_angle),
        color=(50, 100, 255)  # Deep blue
    )
    bodies.append(neptune)

    return bodies


def create_jupiter_system():
    """Create Jupiter and its major moons in varied orbital positions."""
    bodies = []

    # Jupiter at center
    jupiter = CustomBody(
        name="Jupiter",
        radius_km=69911,
        mass_kg=1.898e27,
        x_position=0,
        y_position=0,
        x_velocity=0,
        y_velocity=0,
        color=(255, 200, 150)  # Orange-ish
    )
    bodies.append(jupiter)

    # Io - at 90 degrees
    io_angle = math.radians(90)
    io_distance = 421700
    io = CustomBody(
        name="Io",
        radius_km=1821.6,
        mass_kg=8.93e22,
        x_position=io_distance * math.cos(io_angle),
        y_position=io_distance * math.sin(io_angle),
        x_velocity=-17.33 * math.sin(io_angle),
        y_velocity=17.33 * math.cos(io_angle),
        color=(255, 255, 150)  # Yellow-white
    )
    bodies.append(io)

    # Europa - at 180 degrees
    europa_angle = math.radians(180)
    europa_distance = 671034
    europa = CustomBody(
        name="Europa",
        radius_km=1560.8,
        mass_kg=4.8e22,
        x_position=europa_distance * math.cos(europa_angle),
        y_position=europa_distance * math.sin(europa_angle),
        x_velocity=-13.74 * math.sin(europa_angle),
        y_velocity=13.74 * math.cos(europa_angle),
        color=(200, 200, 255)  # Icy blue-white
    )
    bodies.append(europa)

    # Ganymede - at 270 degrees
    ganymede_angle = math.radians(270)
    ganymede_distance = 1070412
    ganymede = CustomBody(
        name="Ganymede",
        radius_km=2634.1,
        mass_kg=1.48e23,
        x_position=ganymede_distance * math.cos(ganymede_angle),
        y_position=ganymede_distance * math.sin(ganymede_angle),
        x_velocity=-10.88 * math.sin(ganymede_angle),
        y_velocity=10.88 * math.cos(ganymede_angle),
        color=(150, 150, 150)  # Gray
    )
    bodies.append(ganymede)

    # Callisto - at 45 degrees
    callisto_angle = math.radians(45)
    callisto_distance = 1882709
    callisto = CustomBody(
        name="Callisto",
        radius_km=2410.3,
        mass_kg=1.08e23,
        x_position=callisto_distance * math.cos(callisto_angle),
        y_position=callisto_distance * math.sin(callisto_angle),
        x_velocity=-8.20 * math.sin(callisto_angle),
        y_velocity=8.20 * math.cos(callisto_angle),
        color=(100, 100, 100)  # Dark gray
    )
    bodies.append(callisto)

    return bodies


def create_proxima_centauri_system():
    """Create Proxima Centauri system with known exoplanets."""
    bodies = []

    # Proxima Centauri (red dwarf star)
    proxima = CustomBody(
        name="Proxima Centauri",
        radius_km=100000,  # About 1/7th of Sun's radius
        mass_kg=2.446e29,  # About 0.123 solar masses
        x_position=0,
        y_position=0,
        x_velocity=0,
        y_velocity=0,
        color=(255, 150, 100)  # Red-orange for red dwarf
    )
    bodies.append(proxima)

    # Proxima Centauri b (potentially habitable exoplanet) - at 45 degrees
    proxima_b_angle = math.radians(45)
    proxima_b_distance = 7500000  # 0.05 AU in km (very close orbit)
    proxima_b = CustomBody(
        name="Proxima b",
        radius_km=7160,  # Slightly larger than Earth
        mass_kg=7.6e24,  # About 1.27 Earth masses
        x_position=proxima_b_distance * math.cos(proxima_b_angle),
        y_position=proxima_b_distance * math.sin(proxima_b_angle),
        x_velocity=-60.0 * math.sin(proxima_b_angle),  # Fast orbit due to close distance
        y_velocity=60.0 * math.cos(proxima_b_angle),
        color=(100, 150, 200)  # Blue-ish (potentially habitable)
    )
    bodies.append(proxima_b)

    # Proxima Centauri c (larger, outer planet) - at 180 degrees
    proxima_c_angle = math.radians(180)
    proxima_c_distance = 22350000  # 1.49 AU in km
    proxima_c = CustomBody(
        name="Proxima c",
        radius_km=10000,  # Estimated larger size
        mass_kg=4.25e25,  # About 7 Earth masses (super-Earth)
        x_position=proxima_c_distance * math.cos(proxima_c_angle),
        y_position=proxima_c_distance * math.sin(proxima_c_angle),
        x_velocity=-15.0 * math.sin(proxima_c_angle),  # Slower orbit
        y_velocity=15.0 * math.cos(proxima_c_angle),
        color=(150, 100, 80)  # Brown-ish (cold super-Earth)
    )
    bodies.append(proxima_c)

    # Proxima Centauri d (recently discovered, very close) - at 270 degrees
    proxima_d_angle = math.radians(270)
    proxima_d_distance = 2400000  # 0.016 AU in km (extremely close)
    proxima_d = CustomBody(
        name="Proxima d",
        radius_km=3500,  # About half Earth's size
        mass_kg=1.2e24,  # About 0.2 Earth masses
        x_position=proxima_d_distance * math.cos(proxima_d_angle),
        y_position=proxima_d_distance * math.sin(proxima_d_angle),
        x_velocity=-120.0 * math.sin(proxima_d_angle),  # Very fast orbit
        y_velocity=120.0 * math.cos(proxima_d_angle),
        color=(200, 100, 100)  # Red-ish (very hot due to proximity)
    )
    bodies.append(proxima_d)

    return bodies


def create_empty_system():
    """Create an empty system."""
    return []
