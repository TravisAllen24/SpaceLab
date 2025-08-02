"""Main simulation loop for the solar system."""

import pygame
import sys
from typing import List
from .graphics.renderer import Renderer
from .audio.audio_manager import AudioManager
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
    create_empty_system,
    # Import predefined bodies
    earth, moon, iss, sun, mercury, venus, mars, jupiter, saturn, uranus, neptune,
    jupiter_center, io, europa, ganymede, callisto, proxima, proxima_b, proxima_c, proxima_d
)
from .config import settings
from .config.settings import *


class SolarSystemSimulation:
    """Main simulation class that manages the solar system."""

    def __init__(self, scenario: str = "earth_moon"):
        """Initialize the simulation with a specific scenario."""
        self.renderer = Renderer()
        self.audio_manager = AudioManager()
        self.bodies: List[CelestialBody] = []
        self.impact_markers: List[ImpactMarker] = []
        self.running = True
        self.paused = False
        self.scenario = scenario

        # Menu state
        self.menu_open = False
        self.menu_selection = 0
        self.available_scenarios = ["earth_moon", "solar_system", "jupiter_system", "proxima_centauri", "empty"]
        self.scenario_names = {
            "earth_moon": "Earth-Moon System with ISS",
            "solar_system": "Complete Solar System",
            "jupiter_system": "Jupiter System with 4 moons",
            "proxima_centauri": "Proxima Centauri System",
            "empty": "Empty Space"
        }

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

        # Time tracking
        self.simulation_time_elapsed = 0.0  # Total simulation time in seconds
        self.real_time_start = pygame.time.get_ticks()  # Start time in milliseconds

        # Initialize celestial bodies based on scenario
        self._setup_bodies()

        # Start background music for the scenario
        self.audio_manager.play_scenario_music(self.scenario)

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

    def switch_scenario(self, new_scenario: str) -> None:
        """Switch to a new scenario and reset the simulation."""
        self.scenario = new_scenario
        self._setup_bodies()
        self.impact_markers.clear()
        self.renderer.trails.clear()
        self.simulation_time_elapsed = 0.0
        self.real_time_start = pygame.time.get_ticks()
        self.audio_manager.play_scenario_music(self.scenario)
        print(f"Switched to scenario: {self.scenario_names.get(new_scenario, new_scenario)}")

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

            # Check if the name matches a predefined body
            predefined_bodies = {
                "earth": earth,
                "moon": moon,
                "iss": iss,
                "sun": sun,
                "mercury": mercury,
                "venus": venus,
                "mars": mars,
                "jupiter": jupiter,
                "saturn": saturn,
                "uranus": uranus,
                "neptune": neptune,
                "io": io,
                "europa": europa,
                "ganymede": ganymede,
                "callisto": callisto,
                "proxima": proxima,
                "proxima b": proxima_b,
                "proxima c": proxima_c,
                "proxima d": proxima_d
            }

            if name.lower() in predefined_bodies:
                # Use predefined body but with drag position and velocity
                template_body = predefined_bodies[name.lower()]
                new_body = CelestialBody(
                    name=template_body.name,
                    radius_km=template_body.radius_km,
                    mass_kg=template_body.mass_kg,
                    x_position=world_x,
                    y_position=world_y,
                    x_velocity=velocity_x,
                    y_velocity=velocity_y,
                    color=template_body.color
                )
                self.bodies.append(new_body)

                # Calculate speed for display
                speed = (velocity_x**2 + velocity_y**2)**0.5
                print(f"Created predefined body {new_body.name} at ({world_x:.1f}, {world_y:.1f}) km")
                print(f"  Mass: {new_body.mass_kg:.2e} kg, Radius: {new_body.radius_km:.1f} km")
                print(f"  Velocity: ({velocity_x:.2f}, {velocity_y:.2f}) km/s (speed: {speed:.2f} km/s)")
                return

            # Get mass (in kg) for custom body
            mass_str = get_text_input(self.renderer.screen, "Body Properties", "Mass (kg):", "1e20")
            if mass_str is None:
                return
            mass_kg = float(mass_str)

            # Get radius (in km) for custom body
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
                if self.menu_open:
                    # Handle menu navigation
                    if event.key == pygame.K_UP:
                        self.menu_selection = (self.menu_selection - 1) % len(self.available_scenarios)
                    elif event.key == pygame.K_DOWN:
                        self.menu_selection = (self.menu_selection + 1) % len(self.available_scenarios)
                    elif event.key == pygame.K_RETURN:
                        # Select scenario and close menu
                        selected_scenario = self.available_scenarios[self.menu_selection]
                        self.switch_scenario(selected_scenario)
                        self.menu_open = False
                        self.paused = False  # Resume simulation
                    elif event.key == pygame.K_ESCAPE:
                        # Close menu without changing scenario
                        self.menu_open = False
                        # Don't change pause state when closing menu
                else:
                    # Handle normal game controls
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_p:
                        self.paused = not self.paused
                    elif event.key == pygame.K_r:
                        self._setup_bodies()  # Reset simulation
                        self.impact_markers.clear()  # Clear impact markers
                        self.renderer.trails.clear()  # Clear trails
                        self.simulation_time_elapsed = 0.0  # Reset elapsed time
                        self.real_time_start = pygame.time.get_ticks()  # Reset real time tracker
                        self.audio_manager.play_scenario_music(self.scenario)  # Restart music
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
                    elif event.key == pygame.K_m:
                        # Toggle mute
                        self.audio_manager.toggle_mute()
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
                        # Open menu instead of exiting
                        self.menu_open = True
                        self.paused = True  # Pause simulation when menu opens
                        # Set menu selection to current scenario
                        try:
                            self.menu_selection = self.available_scenarios.index(self.scenario)
                        except ValueError:
                            self.menu_selection = 0
                    elif event.key == pygame.K_q:
                        # Q key to quit directly
                        self.running = False
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize (maximize button, etc.)
                self.renderer.handle_resize(event.w, event.h)

    def update_physics_single_step(self, dt: float) -> None:
        """Update the physics simulation."""
        if not self.paused:
            # Apply gravitational forces
            apply_gravitational_forces(self.bodies, dt)

            # Update all bodies
            for body in self.bodies:
                body.update(dt)

            # Update simulation time
            self.simulation_time_elapsed += dt

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

    def update_physics_multi_step(self, total_dt: float, base_dt: float) -> None:
        """Update physics using multiple smaller steps for better stability."""
        if not self.paused:
            # Calculate how many steps we need, but cap it to prevent excessive lag
            max_steps_per_frame = settings.MAX_PHYSICS_STEPS_PER_FRAME
            num_steps = max(1, min(int(total_dt / base_dt), max_steps_per_frame))
            actual_dt = total_dt / num_steps

            # Run multiple physics steps
            for _ in range(num_steps):
                # Apply gravitational forces
                apply_gravitational_forces(self.bodies, actual_dt)

                # Update all bodies
                for body in self.bodies:
                    body.update(actual_dt)

                # Check for collisions (only need to check once per frame, not every substep)
                # We'll do this after all substeps are complete

            # Update simulation time
            self.simulation_time_elapsed += total_dt

            # Check for collisions after all physics steps
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

        # Draw elapsed time
        self._draw_elapsed_time_info()

        # Draw simulation status
        self._draw_simulation_status()

        # Draw instructions
        self._draw_instructions()

        # Draw scenario menu (if open)
        self._draw_scenario_menu()

        self.renderer.present()

    def _draw_instructions(self) -> None:
        """Draw control instructions on screen."""
        font = self.renderer.get_font('red_alert_small')
        instructions = [
            "SPACE/P: Pause/Resume",
            "ESC: Open scenario menu",
            "Q: Quit simulation",
            "R: Reset simulation",
            "L: Toggle labels",
            "T: Toggle trails",
            "C: Clear trails & impacts",
            "M: Mute/Unmute music",
            "Left-drag: Create custom body",
            "Right-drag: Create satellite",
            "Scroll: Zoom in/out",
            "+/-: Zoom keyboard",
            ",/.: Time scale slower/faster",
            "F11: Toggle fullscreen"
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
        font = self.renderer.get_font('red_alert_small')
        zoom_text = f"Zoom: {self.renderer.zoom:.1f}x"
        text_surface = font.render(zoom_text, True, (255, 255, 255))

        # Position in top-right corner
        x_pos = self.renderer.width - text_surface.get_width() - 10
        self.renderer.screen.blit(text_surface, (x_pos, 10))

    def _draw_time_scale_info(self) -> None:
        """Draw current time scale."""
        font = self.renderer.get_font('red_alert_small')
        # Format time scale display nicely
        if self.time_scale < 1:
            time_text = f"Time: {self.time_scale:.2f}x"
        else:
            time_text = f"Time: {self.time_scale:.0f}x"
        text_surface = font.render(time_text, True, (255, 255, 255))

        # Position in top-right corner, below zoom info
        x_pos = self.renderer.width - text_surface.get_width() - 10
        self.renderer.screen.blit(text_surface, (x_pos, 40))

    def _draw_elapsed_time_info(self) -> None:
        """Draw elapsed simulation time."""
        font = self.renderer.get_font('red_alert_small')

        # Convert seconds to a more readable format
        total_seconds = int(self.simulation_time_elapsed)

        # Calculate years, days, hours, minutes, seconds
        years = total_seconds // (365 * 24 * 3600)
        remaining = total_seconds % (365 * 24 * 3600)
        days = remaining // (24 * 3600)
        remaining = remaining % (24 * 3600)
        hours = remaining // 3600
        remaining = remaining % 3600
        minutes = remaining // 60
        seconds = remaining % 60

        # Format based on the largest time unit
        if years > 0:
            time_text = f"Elapsed: {years}y {days}d {hours}h"
        elif days > 0:
            time_text = f"Elapsed: {days}d {hours}h {minutes}m"
        elif hours > 0:
            time_text = f"Elapsed: {hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            time_text = f"Elapsed: {minutes}m {seconds}s"
        else:
            time_text = f"Elapsed: {seconds}s"

        text_surface = font.render(time_text, True, (255, 255, 255))

        # Position in top-right corner, below time scale info
        x_pos = self.renderer.width - text_surface.get_width() - 10
        self.renderer.screen.blit(text_surface, (x_pos, 70))

    def _draw_simulation_status(self) -> None:
        """Draw simulation status (playing/paused)."""
        font = self.renderer.get_font('red_alert_small')

        if self.paused:
            status_text = "PAUSED"
            color = (255, 100, 100)  # Red-ish for paused
        else:
            status_text = "PLAYING"
            color = (100, 255, 100)  # Green-ish for playing

        text_surface = font.render(status_text, True, color)

        # Position in top-right corner, below elapsed time info
        x_pos = self.renderer.width - text_surface.get_width() - 10
        self.renderer.screen.blit(text_surface, (x_pos, 100))

    def _draw_scenario_menu(self) -> None:
        """Draw the scenario selection menu."""
        if not self.menu_open:
            return

        # Create semi-transparent overlay
        overlay = pygame.Surface((self.renderer.width, self.renderer.height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.renderer.screen.blit(overlay, (0, 0))

        # Menu dimensions
        menu_width = 400
        menu_height = 350
        menu_x = (self.renderer.width - menu_width) // 2
        menu_y = (self.renderer.height - menu_height) // 2

        # Draw menu background
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        pygame.draw.rect(self.renderer.screen, (40, 40, 60), menu_rect)
        pygame.draw.rect(self.renderer.screen, (100, 100, 120), menu_rect, 3)

        # Draw title
        title_font = self.renderer.get_font('red_alert_large')
        title_text = title_font.render("SELECT SCENARIO", True, (255, 255, 255))
        title_x = menu_x + (menu_width - title_text.get_width()) // 2
        self.renderer.screen.blit(title_text, (title_x, menu_y + 20))

        # Draw scenario options
        option_font = self.renderer.get_font('red_alert_medium')
        start_y = menu_y + 80

        for i, scenario in enumerate(self.available_scenarios):
            scenario_name = self.scenario_names[scenario]

            # Highlight selected option
            if i == self.menu_selection:
                highlight_rect = pygame.Rect(menu_x + 10, start_y + i * 40 - 5, menu_width - 20, 35)
                pygame.draw.rect(self.renderer.screen, (80, 80, 100), highlight_rect)
                color = (255, 255, 100)  # Yellow for selected
            else:
                color = (200, 200, 200)  # Gray for unselected

            # Current scenario indicator
            if scenario == self.scenario:
                indicator = "► "
            else:
                indicator = "  "

            option_text = option_font.render(f"{indicator}{scenario_name}", True, color)
            self.renderer.screen.blit(option_text, (menu_x + 20, start_y + i * 40))

        # Draw instructions
        instruction_font = self.renderer.get_font('red_alert_small')
        instructions = [
            "↑↓: Navigate    ENTER: Select    ESC: Cancel"
        ]

        instruction_y = menu_y + menu_height - 40
        for instruction in instructions:
            instruction_text = instruction_font.render(instruction, True, (180, 180, 180))
            instruction_x = menu_x + (menu_width - instruction_text.get_width()) // 2
            self.renderer.screen.blit(instruction_text, (instruction_x, instruction_y))
            instruction_y += 20

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
        print(f"Physics Integration Method: {settings.PHYSICS_INTEGRATION_METHOD}")
        if settings.PHYSICS_INTEGRATION_METHOD == "multi_step":
            print(f"Max Physics Steps Per Frame: {settings.MAX_PHYSICS_STEPS_PER_FRAME}")
        print("Controls:")
        print("  SPACE/P: Pause/Resume")
        print("  ESC: Open scenario menu")
        print("  Q: Quit simulation")
        print("  R: Reset simulation")
        print("  L: Toggle labels")
        print("  T: Toggle trails")
        print("  C: Clear trails & impacts")
        print("  M: Mute/Unmute music")
        print("  Left-drag: Create custom body (with input dialog)")
        print("  Right-drag: Create satellite")
        print("  Mouse Wheel: Zoom in/out")
        print("  +/-: Zoom with keyboard")
        print("  ,/.: Time scale slower/faster")
        print("  F11: Toggle fullscreen")

        while self.running:
            self.handle_events()

            # Choose physics integration method based on settings
            if settings.PHYSICS_INTEGRATION_METHOD == "multi_step":
                # Use multiple smaller steps for better stability at high time scales
                total_dt = PHYSICS_DT * self.time_scale
                self.update_physics_multi_step(total_dt, PHYSICS_DT)
            elif settings.PHYSICS_INTEGRATION_METHOD == "single_step":
                # Use single large step (faster but less stable at high time scales)
                self.update_physics_single_step(PHYSICS_DT * self.time_scale)
            elif settings.PHYSICS_INTEGRATION_METHOD == "patched_conic":
                raise NotImplementedError("Patched conic integration not implemented yet")
            else:
                print(f"Unknown physics integration method: {settings.PHYSICS_INTEGRATION_METHOD}")
                sys.exit(1)

            self.render()

        self.audio_manager.cleanup()
        self.renderer.quit()
        print("Simulation ended.")
