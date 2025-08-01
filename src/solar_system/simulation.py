"""Main simulation loop for the solar system."""

import pygame
import sys
from typing import List
from .graphics.renderer import Renderer
from .physics.gravity import apply_gravitational_forces
from .physics.collision import detect_collisions, create_impact_marker
from .bodies.celestial_body import CelestialBody
from .bodies.earth import Earth
from .bodies.moon import Moon
from .bodies.satellite import Satellite
from .bodies.impact_marker import ImpactMarker
from .config.settings import *


class SolarSystemSimulation:
    """Main simulation class that manages the solar system."""

    def __init__(self):
        """Initialize the simulation."""
        self.renderer = Renderer()
        self.bodies: List[CelestialBody] = []
        self.impact_markers: List[ImpactMarker] = []
        self.running = True
        self.paused = False

        # Satellite creation drag state
        self.is_dragging = False
        self.drag_start_pos = None
        self.drag_current_pos = None
        self.velocity_scale_factor = 0.1  # Scale factor for converting pixels to km/s

        # Satellite naming counter (tracks total satellites ever created)
        self.total_satellites_created = 0

        # Initialize celestial bodies
        self._setup_bodies()

    def _setup_bodies(self) -> None:
        """Set up the initial celestial bodies."""
        # Create Earth at center
        earth = Earth()

        # Create Moon orbiting Earth (much further out)
        moon = Moon()

        # Create a satellite in low Earth orbit
        # For circular orbit: v = sqrt(GM/r) where r = Earth_radius + altitude
        # Earth mass: 5.972e24 kg, radius: 6371 km
        # For 400km altitude: r = 6371 + 400 = 6771 km
        # v = sqrt(6.674e-11 * 5.972e24 / 6771000) ≈ 7.66 km/s
        satellite = Satellite(
            name="ISS",
            radius_km=0.1,  # Very small
            mass_kg=420000,  # ISS mass in kg
            x_position=6771,  # Earth radius + 400km altitude
            y_position=0,
            x_velocity=0,
            y_velocity=9,  # Correct orbital velocity
            color=(255, 255, 0)  # Yellow
        )

        self.bodies = [earth, moon, satellite]

        # ISS counts as the first satellite created
        self.total_satellites_created = 1

    def _create_satellite_at_position(self, x: float, y: float) -> None:
        """Create a new satellite at the given world coordinates with zero velocity."""
        # Increment counter for unique naming
        self.total_satellites_created += 1

        new_satellite = Satellite(
            name=f"Satellite-{self.total_satellites_created}",
            radius_km=0.1,  # Small satellite
            mass_kg=1000,  # 1 ton satellite
            x_position=x,
            y_position=y,
            x_velocity=0,  # Zero initial velocity as requested
            y_velocity=0,
            color=(0, 255, 255)  # Cyan to distinguish from ISS
        )
        self.bodies.append(new_satellite)
        print(f"Created {new_satellite.name} at position ({x:.1f}, {y:.1f}) km")

    def _create_satellite_from_drag(self) -> None:
        """Create a satellite from drag operation with calculated velocity."""
        if not self.drag_start_pos or not self.drag_current_pos:
            return

        # Convert start position to world coordinates
        world_x, world_y = self.renderer.screen_to_world(*self.drag_start_pos)

        # Calculate drag vector in screen pixels
        drag_vector_x = self.drag_current_pos[0] - self.drag_start_pos[0]
        drag_vector_y = self.drag_current_pos[1] - self.drag_start_pos[1]

        # Convert drag vector to velocity (km/s)
        # Note: Y is flipped because screen Y increases downward but world Y increases upward
        velocity_x = drag_vector_x * self.velocity_scale_factor
        velocity_y = -drag_vector_y * self.velocity_scale_factor  # Flip Y axis

        # Increment counter for unique naming
        self.total_satellites_created += 1

        new_satellite = Satellite(
            name=f"Satellite-{self.total_satellites_created}",
            radius_km=0.1,  # Small satellite
            mass_kg=1000,  # 1 ton satellite
            x_position=world_x,
            y_position=world_y,
            x_velocity=velocity_x,
            y_velocity=velocity_y,
            color=(0, 255, 255)  # Cyan to distinguish from ISS
        )
        self.bodies.append(new_satellite)

        # Calculate speed for display
        speed = (velocity_x**2 + velocity_y**2)**0.5
        print(f"Created {new_satellite.name} at ({world_x:.1f}, {world_y:.1f}) km with velocity ({velocity_x:.2f}, {velocity_y:.2f}) km/s (speed: {speed:.2f} km/s)")

    def handle_events(self) -> None:
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEWHEEL:
                # Handle zoom
                self.renderer.handle_zoom_event(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:  # Right mouse button
                    # Start dragging for satellite creation
                    self.is_dragging = True
                    self.drag_start_pos = event.pos
                    self.drag_current_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3 and self.is_dragging:  # Right mouse button release
                    # End dragging and create satellite
                    self._create_satellite_from_drag()
                    self.is_dragging = False
                    self.drag_start_pos = None
                    self.drag_current_pos = None
            elif event.type == pygame.MOUSEMOTION:
                if self.is_dragging:
                    # Update drag position
                    self.drag_current_pos = event.pos
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self._setup_bodies()  # Reset simulation
                    self.impact_markers.clear()  # Clear impact markers
                    # Note: _setup_bodies() already resets total_satellites_created to 1
                elif event.key == pygame.K_l:
                    # Toggle labels
                    import solar_system.config.settings as settings
                    settings.SHOW_LABELS = not settings.SHOW_LABELS
                elif event.key == pygame.K_t:
                    # Toggle trails
                    import solar_system.config.settings as settings
                    settings.SHOW_TRAILS = not settings.SHOW_TRAILS
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
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

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
            for satellite, target in collisions:
                # Create impact marker at collision point
                impact_marker = create_impact_marker(satellite, target)
                self.impact_markers.append(impact_marker)

                # Remove the satellite
                self.bodies.remove(satellite)
                print(f"{satellite.name} crashed into {target.name}!")

    def render(self) -> None:
        """Render the current frame."""
        self.renderer.clear_screen()

        # Draw all celestial bodies
        for body in self.bodies:
            self.renderer.draw_body(body)

        # Draw impact markers
        for marker in self.impact_markers:
            self.renderer.draw_impact_marker(marker)

        # Draw velocity arrow if dragging
        if self.is_dragging and self.drag_start_pos and self.drag_current_pos:
            self.renderer.draw_velocity_arrow(
                self.drag_start_pos,
                self.drag_current_pos,
                velocity_scale=self.velocity_scale_factor
            )

        # Draw information
        self.renderer.draw_info(self.bodies)

        # Draw zoom level
        self._draw_zoom_info()

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
            "Right-drag: Create satellite",
            "Scroll: Zoom in/out",
            "+/-: Zoom keyboard",
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

    def run(self) -> None:
        """Main simulation loop."""
        print("Starting Solar System Simulation...")
        print("Controls:")
        print("  SPACE: Pause/Resume")
        print("  R: Reset simulation")
        print("  L: Toggle labels")
        print("  T: Toggle trails")
        print("  C: Clear trails & impacts")
        print("  Right-drag: Create satellite with velocity")
        print("  Mouse Wheel: Zoom in/out")
        print("  +/-: Zoom with keyboard")
        print("  ESC: Exit")

        while self.running:
            self.handle_events()
            self.update_physics(PHYSICS_DT * TIME_SCALE)
            self.render()

        self.renderer.quit()
        print("Simulation ended.")
