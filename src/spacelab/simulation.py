"""Main simulation loop for the solar system."""

import pygame
import sys
from typing import List
from .graphics.renderer import Renderer
from .audio.audio_manager import AudioManager
from .config.settings_manager import SettingsManager
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
        self.settings_manager = SettingsManager()
        self.renderer = Renderer()
        self.audio_manager = AudioManager()
        self.bodies: List[CelestialBody] = []
        self.impact_markers: List[ImpactMarker] = []
        self.running = True
        self.paused = False
        self.scenario = scenario

        # Menu state system
        self.menu_open = False
        self.menu_state = "main"  # "main", "settings", "audio", "graphics", "gameplay"
        self.menu_selection = 0
        self.available_scenarios = ["earth_moon", "solar_system", "jupiter_system", "proxima_centauri", "empty"]
        self.scenario_names = {
            "earth_moon": "Earth-Moon System with ISS",
            "solar_system": "Complete Solar System",
            "jupiter_system": "Jupiter System with 4 moons",
            "proxima_centauri": "Proxima Centauri System",
            "empty": "Empty Space"
        }

        # Settings menu options
        self.main_menu_options = ["Select Scenario", "Settings", "Controls", "Resume", "Quit"]
        self.settings_menu_options = ["Audio", "Graphics", "Gameplay", "Reset to Defaults", "Back"]
        self.audio_menu_options = ["Music Volume", "Sound Effects Volume", "Audio Enabled", "Back"]
        self.graphics_menu_options = ["Fullscreen", "Show Labels", "Show Trails", "Show FPS", "Back"]
        self.gameplay_menu_options = ["Trail Length", "Max Time Scale", "Physics Method", "Back"]
        self.controls_menu_options = [
            "SPACE/P: Pause/Resume",
            "ESC: Open menu",
            "Q: Quit simulation",
            "R: Reset simulation",
            "L: Toggle labels",
            "T: Toggle trails",
            "C: Clear trails & impacts",
            "M: Mute/Unmute music",
            "Left-drag: Create custom body",
            "Right-drag: Create satellite",
            "Mouse wheel: Zoom in/out",
            "+/-: Zoom with keyboard",
            ",/.: Time scale slower/faster",
            "F11: Toggle fullscreen",
            "Back"
        ]

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

        # Apply all settings from the settings manager
        self._apply_all_settings()

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

    def _handle_menu_input(self, key) -> None:
        """Handle input for the menu system."""
        if key == pygame.K_UP:
            self._navigate_menu(-1)
        elif key == pygame.K_DOWN:
            self._navigate_menu(1)
        elif key == pygame.K_LEFT:
            self._adjust_setting(-1)
        elif key == pygame.K_RIGHT:
            self._adjust_setting(1)
        elif key == pygame.K_RETURN:
            self._select_menu_option()
        elif key == pygame.K_ESCAPE:
            self._go_back_menu()

    def _navigate_menu(self, direction: int) -> None:
        """Navigate up/down in the current menu."""
        if self.menu_state == "main":
            options_count = len(self.main_menu_options)
        elif self.menu_state == "scenario":
            options_count = len(self.available_scenarios)
        elif self.menu_state == "settings":
            options_count = len(self.settings_menu_options)
        elif self.menu_state == "controls":
            options_count = len(self.controls_menu_options)
        elif self.menu_state == "audio":
            options_count = len(self.audio_menu_options)
        elif self.menu_state == "graphics":
            options_count = len(self.graphics_menu_options)
        elif self.menu_state == "gameplay":
            options_count = len(self.gameplay_menu_options)
        else:
            options_count = 1

        self.menu_selection = (self.menu_selection + direction) % options_count

    def _adjust_setting(self, direction: int) -> None:
        """Adjust settings with left/right arrows."""
        if self.menu_state == "audio":
            option = self.audio_menu_options[self.menu_selection]
            if option == "Music Volume":
                current = self.settings_manager.get("music_volume")
                new_volume = max(0.0, min(1.0, current + direction * 0.1))
                self.settings_manager.set("music_volume", new_volume)
                self.audio_manager.set_volume(new_volume)
            elif option == "Sound Effects Volume":
                current = self.settings_manager.get("sound_effects_volume")
                new_volume = max(0.0, min(1.0, current + direction * 0.1))
                self.settings_manager.set("sound_effects_volume", new_volume)
            elif option == "Audio Enabled":
                enabled = self.settings_manager.get("audio_enabled")
                self.settings_manager.set("audio_enabled", not enabled)
                if not enabled:
                    self.audio_manager.toggle_mute()

        elif self.menu_state == "graphics":
            option = self.graphics_menu_options[self.menu_selection]
            if option == "Show Labels":
                current = self.settings_manager.get("show_labels")
                self.settings_manager.set("show_labels", not current)
                settings.SHOW_LABELS = not current
            elif option == "Show Trails":
                current = self.settings_manager.get("show_trails")
                self.settings_manager.set("show_trails", not current)
                settings.SHOW_TRAILS = not current
            elif option == "Show FPS":
                current = self.settings_manager.get("show_fps")
                self.settings_manager.set("show_fps", not current)
            elif option == "Fullscreen":
                self.renderer.toggle_fullscreen()
                self.settings_manager.set("fullscreen", self.renderer.is_fullscreen)

        elif self.menu_state == "gameplay":
            option = self.gameplay_menu_options[self.menu_selection]
            if option == "Trail Length":
                current = self.settings_manager.get("trail_length")
                new_length = max(0, min(500, current + direction * 10))
                self.settings_manager.set("trail_length", new_length)
            elif option == "Max Time Scale":
                scales = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]
                current = self.settings_manager.get("max_time_scale")
                try:
                    current_index = scales.index(current)
                    new_index = max(0, min(len(scales) - 1, current_index + direction))
                    self.settings_manager.set("max_time_scale", scales[new_index])
                except ValueError:
                    self.settings_manager.set("max_time_scale", 1024)
            elif option == "Physics Method":
                methods = ["single_step", "multi_step", "patched_conic"]
                current = self.settings_manager.get("physics_method")
                try:
                    current_index = methods.index(current)
                    new_index = (current_index + direction) % len(methods)
                    new_method = methods[new_index]
                    self.settings_manager.set("physics_method", new_method)
                    # Update the settings module directly
                    settings.PHYSICS_INTEGRATION_METHOD = new_method
                    print(f"Physics method changed to: {new_method}")
                except ValueError:
                    self.settings_manager.set("physics_method", "multi_step")
                    settings.PHYSICS_INTEGRATION_METHOD = "multi_step"

    def _select_menu_option(self) -> None:
        """Handle menu option selection."""
        if self.menu_state == "main":
            option = self.main_menu_options[self.menu_selection]
            if option == "Select Scenario":
                self.menu_state = "scenario"
                try:
                    self.menu_selection = self.available_scenarios.index(self.scenario)
                except ValueError:
                    self.menu_selection = 0
            elif option == "Settings":
                self.menu_state = "settings"
                self.menu_selection = 0
            elif option == "Controls":
                self.menu_state = "controls"
                self.menu_selection = 0
            elif option == "Resume":
                self.menu_open = False
                self.paused = False
            elif option == "Quit":
                self.running = False

        elif self.menu_state == "scenario":
            selected_scenario = self.available_scenarios[self.menu_selection]
            self.switch_scenario(selected_scenario)
            self.menu_open = False
            self.paused = False

        elif self.menu_state == "settings":
            option = self.settings_menu_options[self.menu_selection]
            if option == "Audio":
                self.menu_state = "audio"
                self.menu_selection = 0
            elif option == "Graphics":
                self.menu_state = "graphics"
                self.menu_selection = 0
            elif option == "Gameplay":
                self.menu_state = "gameplay"
                self.menu_selection = 0
            elif option == "Reset to Defaults":
                self.settings_manager.reset_to_defaults()
                self._apply_all_settings()
                print("Settings reset to defaults")
            elif option == "Back":
                self.menu_state = "main"
                self.menu_selection = 1  # Settings option

        elif self.menu_state == "controls":
            option = self.controls_menu_options[self.menu_selection]
            if option == "Back":
                self.menu_state = "main"
                self.menu_selection = 2  # Controls option

        elif self.menu_state in ["audio", "graphics", "gameplay"]:
            option_lists = {
                "audio": self.audio_menu_options,
                "graphics": self.graphics_menu_options,
                "gameplay": self.gameplay_menu_options
            }
            option = option_lists[self.menu_state][self.menu_selection]
            if option == "Back":
                # Map submenu states to their index in settings menu
                submenu_mapping = {"audio": 0, "graphics": 1, "gameplay": 2}
                menu_selection = submenu_mapping.get(self.menu_state, 0)
                self.menu_state = "settings"
                self.menu_selection = menu_selection

    def _go_back_menu(self) -> None:
        """Handle ESC key in menus (go back)."""
        if self.menu_state == "main":
            self.menu_open = False
            # Don't change pause state when closing menu
        elif self.menu_state == "scenario":
            self.menu_state = "main"
            self.menu_selection = 0  # Select Scenario option
        elif self.menu_state == "settings":
            self.menu_state = "main"
            self.menu_selection = 1  # Settings option
        elif self.menu_state == "controls":
            self.menu_state = "main"
            self.menu_selection = 2  # Controls option
        elif self.menu_state in ["audio", "graphics", "gameplay"]:
            self.menu_state = "settings"
            submenu_index = {"audio": 0, "graphics": 1, "gameplay": 2}
            self.menu_selection = submenu_index.get(self.menu_state, 0)

    def _apply_all_settings(self) -> None:
        """Apply all settings from the settings manager."""
        settings.SHOW_LABELS = self.settings_manager.get("show_labels")
        settings.SHOW_TRAILS = self.settings_manager.get("show_trails")
        self.audio_manager.set_volume(self.settings_manager.get("music_volume"))

        # Apply physics method setting
        physics_method = self.settings_manager.get("physics_method")
        settings.PHYSICS_INTEGRATION_METHOD = physics_method

        # Apply other settings as needed
        if self.settings_manager.get("fullscreen") != self.renderer.is_fullscreen:
            self.renderer.toggle_fullscreen()

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
                    # Handle menu navigation based on current menu state
                    self._handle_menu_input(event.key)
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
                        self.settings_manager.set("show_labels", not self.settings_manager.get("show_labels"))
                        settings.SHOW_LABELS = self.settings_manager.get("show_labels")
                        print(f"Labels {'enabled' if settings.SHOW_LABELS else 'disabled'}")
                    elif event.key == pygame.K_t:
                        # Toggle trails
                        self.settings_manager.set("show_trails", not self.settings_manager.get("show_trails"))
                        settings.SHOW_TRAILS = self.settings_manager.get("show_trails")
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
                        self.settings_manager.set("fullscreen", self.renderer.is_fullscreen)
                    elif event.key == pygame.K_ESCAPE:
                        # Open main menu
                        self.menu_open = True
                        self.menu_state = "main"
                        self.menu_selection = 3  # Default to "Resume" (0=Scenario, 1=Settings, 2=Controls, 3=Resume)
                        self.paused = True  # Pause simulation when menu opens
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
        """Draw simplified control instructions on screen."""
        font = self.renderer.get_font('red_alert_small')
        instruction_text = "ESC: Menu"

        text_surface = font.render(instruction_text, True, (255, 255, 255))
        # Position in bottom-left corner with some margin
        self.renderer.screen.blit(text_surface, (10, self.renderer.height - 30))

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
        """Draw the menu system."""
        if not self.menu_open:
            return

        # Get the current menu options based on state
        if self.menu_state == "main":
            options = self.main_menu_options
        elif self.menu_state == "scenario":
            options = [self.scenario_names.get(scenario, scenario) for scenario in self.available_scenarios]
        elif self.menu_state == "settings":
            options = self.settings_menu_options
        elif self.menu_state == "controls":
            options = self.controls_menu_options
        elif self.menu_state == "audio":
            options = self.audio_menu_options
        elif self.menu_state == "graphics":
            options = self.graphics_menu_options
        elif self.menu_state == "gameplay":
            options = self.gameplay_menu_options
        else:
            options = ["Unknown State"]

        # Use the renderer's new menu drawing method
        self.renderer.draw_menu(
            self.menu_state,
            self.menu_selection,
            options,
            self.settings_manager,
            self.audio_manager
        )

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
