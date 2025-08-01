"""Main simulation loop for the solar system."""

import pygame
import sys
from typing import List
from .graphics.renderer import Renderer
from .physics.gravity import apply_gravitational_forces
from .physics.collision import detect_collisions, create_impact_marker
from .bodies.celestial_body import CelestialBody
from .bodies.satellite import Satellite
from .bodies.celestial_body import CelestialBody
from .bodies.impact_marker import ImpactMarker
from .graphics.input_dialog import get_text_input
from .scenarios.predefined_systems import (
    create_earth_moon_system,
    create_solar_system,
    create_jupiter_system,
    create_proxima_centauri_system,
    create_empty_system
)
from .config import settings
from .config.settings import *


class SolarSystemSimulation:
    """Main simulation class that manages the solar system."""

    def __init__(self, scenario: str = "earth_moon"):
        """Initialize the simulation with a specific scenario."""
        self.renderer = Renderer()
        self.bodies: List[CelestialBody] = []
        self.impact_markers: List[ImpactMarker] = []
        self.running = True
        self.paused = False
        self.scenario = scenario

        # Satellite creation drag state (right-click)
        self.is_dragging_satellite = False
        self.satellite_drag_start_pos = None
        self.satellite_drag_current_pos = None

        # Custom body creation drag state (left-click)
        self.is_dragging_body = False
        self.body_drag_start_pos = None
        self.body_drag_current_pos = None

        self.velocity_scale_factor = 0.1  # Scale factor for converting pixels to km/s

        # Satellite naming counter (tracks total satellites ever created)
        self.total_satellites_created = 0

        # Time scale control - extended range for solar system viewing
        self.time_scale_values = [0.1, 0.25, 0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]
        self.current_time_scale_index = self.time_scale_values.index(1)  # Default to 1x (normal speed)
        self.time_scale = self.time_scale_values[self.current_time_scale_index]

        # Initialize celestial bodies based on scenario
        self._setup_bodies()

    def _setup_bodies(self) -> None:
        """Set up the initial celestial bodies based on the selected scenario."""
        if self.scenario == "earth_moon":
            self.bodies = create_earth_moon_system()
            self.total_satellites_created = 1  # ISS counts as first satellite
        elif self.scenario == "solar_system":
            self.bodies = create_solar_system()
            self.total_satellites_created = 0  # No satellites in solar system
        elif self.scenario == "jupiter_system":
            self.bodies = create_jupiter_system()
            self.total_satellites_created = 0  # No satellites in Jupiter system
        elif self.scenario == "proxima_centauri":
            self.bodies = create_proxima_centauri_system()
            self.total_satellites_created = 0  # No satellites in Proxima system
        elif self.scenario == "empty":
            self.bodies = create_empty_system()
            self.total_satellites_created = 0  # No satellites in empty system
        else:
            # Default to Earth-Moon system
            self.bodies = create_earth_moon_system()
            self.total_satellites_created = 1

    def _create_satellite_at_position(self, x: float, y: float) -> None:
        """Create a new satellite at the given world coordinates with zero velocity."""
        # Increment counter for unique naming
        self.total_satellites_created += 1

        new_satellite = Satellite(
            name=f"Satellite-{self.total_satellites_created}",
            x_position=x,
            y_position=y,
            x_velocity=0,  # Zero initial velocity as requested
            y_velocity=0,
        )
        self.bodies.append(new_satellite)
        print(f"Created {new_satellite.name} at position ({x:.1f}, {y:.1f}) km")

    def _create_satellite_from_drag(self) -> None:
        """Create a satellite from drag operation with calculated velocity."""
        if not self.satellite_drag_start_pos or not self.satellite_drag_current_pos:
            return

        # Convert start position to world coordinates
        world_x, world_y = self.renderer.screen_to_world(*self.satellite_drag_start_pos)

        # Calculate drag vector in screen pixels
        drag_vector_x = self.satellite_drag_current_pos[0] - self.satellite_drag_start_pos[0]
        drag_vector_y = self.satellite_drag_current_pos[1] - self.satellite_drag_start_pos[1]

        # Convert drag vector to velocity (km/s)
        # Note: Y is flipped because screen Y increases downward but world Y increases upward
        velocity_x = drag_vector_x * self.velocity_scale_factor
        velocity_y = -drag_vector_y * self.velocity_scale_factor  # Flip Y axis

        # Increment counter for unique naming
        self.total_satellites_created += 1

        new_satellite = Satellite(
            name=f"Satellite-{self.total_satellites_created}",
            x_position=world_x,
            y_position=world_y,
            x_velocity=velocity_x,
            y_velocity=velocity_y,
        )
        self.bodies.append(new_satellite)

        # Calculate speed for display
        speed = (velocity_x**2 + velocity_y**2)**0.5
        print(f"Created {new_satellite.name} at ({world_x:.1f}, {world_y:.1f}) km with velocity ({velocity_x:.2f}, {velocity_y:.2f}) km/s (speed: {speed:.2f} km/s)")

    def _create_custom_body_from_drag(self) -> None:
        """Create a custom celestial body from drag operation with user input for properties."""
        if not self.body_drag_start_pos or not self.body_drag_current_pos:
            return

        # Convert start position to world coordinates
        world_x, world_y = self.renderer.screen_to_world(*self.body_drag_start_pos)

        # Calculate drag vector for velocity
        drag_vector_x = self.body_drag_current_pos[0] - self.body_drag_start_pos[0]
        drag_vector_y = self.body_drag_current_pos[1] - self.body_drag_start_pos[1]
        velocity_x = drag_vector_x * self.velocity_scale_factor
        velocity_y = -drag_vector_y * self.velocity_scale_factor

        # Get user input for body properties
        try:
            # Get body name
            name = get_text_input(self.renderer.screen, "Create Celestial Body", "Name:", "CustomBody")
            if name is None:  # User cancelled
                return

            # Get mass (in kg)
            mass_str = get_text_input(self.renderer.screen, "Body Properties", "Mass (kg):", "1e20")
            if mass_str is None:
                return
            mass_kg = float(mass_str)

            # Get radius (in km)
            radius_str = get_text_input(self.renderer.screen, "Body Properties", "Radius (km):", "100")
            if radius_str is None:
                return
            radius_km = float(radius_str)

            # Create the custom body
            new_body = CelestialBody(
                name=name,
                radius_km=radius_km,
                mass_kg=mass_kg,
                x_position=world_x,
                y_position=world_y,
                x_velocity=velocity_x,
                y_velocity=velocity_y,
                color=(255, 100, 100)  # Red-ish color for custom bodies
            )
            self.bodies.append(new_body)

            # Calculate speed for display
            speed = (velocity_x**2 + velocity_y**2)**0.5
            print(f"Created {new_body.name} at ({world_x:.1f}, {world_y:.1f}) km")
            print(f"  Mass: {mass_kg:.2e} kg, Radius: {radius_km:.1f} km")
            print(f"  Velocity: ({velocity_x:.2f}, {velocity_y:.2f}) km/s (speed: {speed:.2f} km/s)")

        except ValueError:
            print("Invalid input for mass or radius. Body creation cancelled.")
        except Exception as e:
            print(f"Error creating custom body: {e}")

    def handle_events(self) -> None:
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEWHEEL:
                # Handle zoom
                self.renderer.handle_zoom_event(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button - custom body
                    self.is_dragging_body = True
                    self.body_drag_start_pos = event.pos
                    self.body_drag_current_pos = event.pos
                elif event.button == 3:  # Right mouse button - satellite
                    self.is_dragging_satellite = True
                    self.satellite_drag_start_pos = event.pos
                    self.satellite_drag_current_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.is_dragging_body:  # Left mouse button release
                    # End dragging and create custom body with input dialog
                    self._create_custom_body_from_drag()
                    self.is_dragging_body = False
                    self.body_drag_start_pos = None
                    self.body_drag_current_pos = None
                elif event.button == 3 and self.is_dragging_satellite:  # Right mouse button release
                    # End dragging and create satellite
                    self._create_satellite_from_drag()
                    self.is_dragging_satellite = False
                    self.satellite_drag_start_pos = None
                    self.satellite_drag_current_pos = None
            elif event.type == pygame.MOUSEMOTION:
                if self.is_dragging_satellite:
                    self.satellite_drag_current_pos = event.pos
                elif self.is_dragging_body:
                    self.body_drag_current_pos = event.pos
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self._setup_bodies()  # Reset simulation
                    self.impact_markers.clear()  # Clear impact markers
                    self.renderer.trails.clear()  # Clear trails
                    # Note: _setup_bodies() already resets total_satellites_created to 1
                elif event.key == pygame.K_l:
                    # Toggle labels
                    settings.SHOW_LABELS = not settings.SHOW_LABELS
                    print(f"Labels {'enabled' if settings.SHOW_LABELS else 'disabled'}")
                elif event.key == pygame.K_t:
                    # Toggle trails
                    settings.SHOW_TRAILS = not settings.SHOW_TRAILS
                    print(f"Trails {'enabled' if settings.SHOW_TRAILS else 'disabled'}")
                elif event.key == pygame.K_c:
                    # Clear trails and impact markers
                    self.renderer.trails.clear()
                    self.impact_markers.clear()
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    # Zoom in with keyboard
                    self.renderer.zoom_in()
                elif event.key == pygame.K_MINUS:
                    # Zoom out with keyboard
                    self.renderer.zoom_out()
                elif event.key == pygame.K_PERIOD or event.key == pygame.K_GREATER:
                    # Increase time scale (speed up simulation)
                    if self.current_time_scale_index < len(self.time_scale_values) - 1:
                        self.current_time_scale_index += 1
                        self.time_scale = self.time_scale_values[self.current_time_scale_index]
                        print(f"Time scale: {self.time_scale:.2f}x")
                elif event.key == pygame.K_COMMA or event.key == pygame.K_LESS:
                    # Decrease time scale (slow down simulation)
                    if self.current_time_scale_index > 0:
                        self.current_time_scale_index -= 1
                        self.time_scale = self.time_scale_values[self.current_time_scale_index]
                        print(f"Time scale: {self.time_scale:.2f}x")
                elif event.key == pygame.K_F11:
                    # Toggle fullscreen
                    self.renderer.toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize (maximize button, etc.)
                self.renderer.handle_resize(event.w, event.h)

    def update_physics(self, dt: float) -> None:
        """Update the physics simulation."""
        if not self.paused:
            # Apply gravitational forces
            apply_gravitational_forces(self.bodies, dt)

            # Update all bodies
            for body in self.bodies:
                body.update(dt)

            # Check for collisions
            collisions = detect_collisions(self.bodies)
            for colliding_body, target_body in collisions:
                # Create impact marker at collision point
                impact_marker = create_impact_marker(colliding_body, target_body)
                self.impact_markers.append(impact_marker)

                # Remove the colliding body
                if colliding_body in self.bodies:
                    self.bodies.remove(colliding_body)
                    print(f"{colliding_body.name} crashed into {target_body.name}!")

    def render(self) -> None:
        """Render the current frame."""
        self.renderer.clear_screen()

        # Draw all celestial bodies
        for body in self.bodies:
            self.renderer.draw_body(body)

        # Draw impact markers
        for marker in self.impact_markers:
            self.renderer.draw_impact_marker(marker)

        # Draw velocity arrows if dragging
        if self.is_dragging_satellite and self.satellite_drag_start_pos and self.satellite_drag_current_pos:
            # Yellow arrow for satellites
            self.renderer.draw_velocity_arrow(
                self.satellite_drag_start_pos,
                self.satellite_drag_current_pos,
                color=(255, 255, 0),  # Yellow
                velocity_scale=self.velocity_scale_factor
            )
        elif self.is_dragging_body and self.body_drag_start_pos and self.body_drag_current_pos:
            # Red arrow for custom bodies
            self.renderer.draw_velocity_arrow(
                self.body_drag_start_pos,
                self.body_drag_current_pos,
                color=(255, 100, 100),  # Red-ish
                velocity_scale=self.velocity_scale_factor
            )

        # Draw information
        self.renderer.draw_info(self.bodies)

        # Draw zoom level
        self._draw_zoom_info()

        # Draw time scale
        self._draw_time_scale_info()

        # Draw instructions
        self._draw_instructions()

        self.renderer.present()

    def _draw_instructions(self) -> None:
        """Draw control instructions on screen."""
        font = pygame.font.Font(None, 20)
        instructions = [
            "SPACE: Pause/Resume",
            "R: Reset simulation",
            "L: Toggle labels",
            "T: Toggle trails",
            "C: Clear trails & impacts",
            "Left-drag: Create custom body",
            "Right-drag: Create satellite",
            "Scroll: Zoom in/out",
            "+/-: Zoom keyboard",
            ",/.: Time scale slower/faster",
            "F11: Toggle fullscreen",
            "ESC: Exit"
        ]

        # Calculate the total height needed and start from bottom
        total_height = len(instructions) * 22
        y_offset = self.renderer.height - total_height - 10  # 10px margin from bottom
        for instruction in instructions:
            text_surface = font.render(instruction, True, (255, 255, 255))
            self.renderer.screen.blit(text_surface, (10, y_offset))
            y_offset += 22

    def _draw_zoom_info(self) -> None:
        """Draw current zoom level."""
        font = pygame.font.Font(None, 24)
        zoom_text = f"Zoom: {self.renderer.zoom:.1f}x"
        text_surface = font.render(zoom_text, True, (255, 255, 255))

        # Position in top-right corner
        x_pos = self.renderer.width - text_surface.get_width() - 10
        self.renderer.screen.blit(text_surface, (x_pos, 10))

    def _draw_time_scale_info(self) -> None:
        """Draw current time scale."""
        font = pygame.font.Font(None, 24)
        # Format time scale display nicely
        if self.time_scale < 1:
            time_text = f"Time: {self.time_scale:.2f}x"
        else:
            time_text = f"Time: {self.time_scale:.0f}x"
        text_surface = font.render(time_text, True, (255, 255, 255))

        # Position in top-right corner, below zoom info
        x_pos = self.renderer.width - text_surface.get_width() - 10
        self.renderer.screen.blit(text_surface, (x_pos, 40))

    def run(self) -> None:
        """Main simulation loop."""
        scenario_descriptions = {
            "earth_moon": "Earth-Moon System with ISS",
            "solar_system": "Complete Solar System with all 8 planets",
            "jupiter_system": "Jupiter System with 4 major moons",
            "proxima_centauri": "Proxima Centauri with 3 exoplanets",
            "empty": "Empty Space"
        }

        print(f"Starting Solar System Simulation: {scenario_descriptions.get(self.scenario, 'Unknown Scenario')}")
        print("Controls:")
        print("  SPACE: Pause/Resume")
        print("  R: Reset simulation")
        print("  L: Toggle labels")
        print("  T: Toggle trails")
        print("  C: Clear trails & impacts")
        print("  Left-drag: Create custom body (with input dialog)")
        print("  Right-drag: Create satellite")
        print("  Mouse Wheel: Zoom in/out")
        print("  +/-: Zoom with keyboard")
        print("  ,/.: Time scale slower/faster")
        print("  F11: Toggle fullscreen")
        print("  ESC: Exit")

        while self.running:
            self.handle_events()
            self.update_physics(PHYSICS_DT * self.time_scale)
            self.render()

        self.renderer.quit()
        print("Simulation ended.")
