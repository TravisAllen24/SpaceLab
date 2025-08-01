"""Main simulation loop for the solar system."""

import pygame
import sys
from typing import List
from .graphics.renderer import Renderer
from .physics.gravity import apply_gravitational_forces
from .bodies.celestial_body import CelestialBody
from .bodies.earth import Earth
from .bodies.moon import Moon
from .bodies.satellite import Satellite
from .config.settings import *


class SolarSystemSimulation:
    """Main simulation class that manages the solar system."""

    def __init__(self):
        """Initialize the simulation."""
        self.renderer = Renderer()
        self.bodies: List[CelestialBody] = []
        self.running = True
        self.paused = False

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
            y_velocity=7.66,  # Correct orbital velocity
            color=(255, 255, 0)  # Yellow
        )

        self.bodies = [earth, moon, satellite]

    def handle_events(self) -> None:
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEWHEEL:
                # Handle zoom
                self.renderer.handle_zoom_event(event)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self._setup_bodies()  # Reset simulation
                elif event.key == pygame.K_l:
                    # Toggle labels
                    import solar_system.config.settings as settings
                    settings.SHOW_LABELS = not settings.SHOW_LABELS
                elif event.key == pygame.K_t:
                    # Toggle trails
                    import solar_system.config.settings as settings
                    settings.SHOW_TRAILS = not settings.SHOW_TRAILS
                elif event.key == pygame.K_c:
                    # Clear trails
                    self.renderer.trails.clear()
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

    def render(self) -> None:
        """Render the current frame."""
        self.renderer.clear_screen()

        # Draw all celestial bodies
        for body in self.bodies:
            self.renderer.draw_body(body)

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
            "C: Clear trails",
            "Scroll: Zoom in/out",
            "+/-: Zoom keyboard",
            "ESC: Exit"
        ]

        y_offset = self.renderer.height - 180
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
        print("  C: Clear trails")
        print("  Mouse Wheel: Zoom in/out")
        print("  +/-: Zoom with keyboard")
        print("  ESC: Exit")

        while self.running:
            self.handle_events()
            self.update_physics(PHYSICS_DT * TIME_SCALE)
            self.render()

        self.renderer.quit()
        print("Simulation ended.")
