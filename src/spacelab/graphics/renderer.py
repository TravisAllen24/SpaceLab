"""Pygame rendering system for the solar system simulation."""

import pygame
import random
import os
from typing import List, Tuple
from ..bodies.celestial_body import CelestialBody
from ..config import settings
from ..config.settings import *


class Renderer:
    """Handles all pygame rendering operations."""

    def __init__(self, width: int = WINDOW_WIDTH, height: int = WINDOW_HEIGHT):
        """Initialize the renderer with pygame."""
        pygame.init()
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.width = width
        self.height = height
        self.is_fullscreen = False
        self.windowed_size = (width, height)  # Store original windowed size

        # Load custom fonts
        self._load_custom_fonts()

        # Trail system
        self.trails = {}  # Dictionary to store trails for each body

        # Zoom system
        self.zoom = ZOOM_FACTOR

        # Star field
        self.stars = self._generate_stars()

    def _generate_stars(self) -> List[Tuple[int, int, Tuple[int, int, int], int]]:
        """Generate random stars for the background based on current screen size."""
        stars = []
        num_stars = STAR_COUNT

        for _ in range(num_stars):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)

            # Choose a base color and apply brightness variation
            base_color = random.choice(STAR_COLORS)
            brightness_factor = random.uniform(0.3, 1.0)
            color = tuple(int(c * brightness_factor) for c in base_color)

            # 10% chance for larger, brighter stars
            if random.random() < 0.1:
                size = 2
                # Make larger stars a bit brighter
                color = tuple(min(255, int(c * 1.2)) for c in color)
            else:
                size = 1

            stars.append((x, y, color, size))

        return stars

    def _load_custom_fonts(self) -> None:
        """Load custom fonts from the fonts directory."""
        # Get the path to the fonts directory in media folder
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to spacelab, then into media/fonts
        spacelab_dir = os.path.dirname(current_dir)
        fonts_dir = os.path.join(spacelab_dir, "media", "fonts")

        # Initialize font dictionaries
        self.custom_fonts = {}
        self.fallback_font = None

        try:
            # Look for Red Alert font files
            red_alert_inet_path = os.path.join(fonts_dir, "C&C Red Alert [INET].ttf")
            red_alert_lan_path = os.path.join(fonts_dir, "C&C Red Alert [LAN].ttf")

            # Load the INET version as primary, LAN as backup
            if os.path.exists(red_alert_inet_path):
                self.custom_fonts['red_alert_small'] = pygame.font.Font(red_alert_inet_path, 14)
                self.custom_fonts['red_alert_medium'] = pygame.font.Font(red_alert_inet_path, 18)
                self.custom_fonts['red_alert_large'] = pygame.font.Font(red_alert_inet_path, 24)
                self.custom_fonts['red_alert_title'] = pygame.font.Font(red_alert_inet_path, 36)
                print(f"Loaded custom font: C&C Red Alert [INET]")
            elif os.path.exists(red_alert_lan_path):
                self.custom_fonts['red_alert_small'] = pygame.font.Font(red_alert_lan_path, 14)
                self.custom_fonts['red_alert_medium'] = pygame.font.Font(red_alert_lan_path, 18)
                self.custom_fonts['red_alert_large'] = pygame.font.Font(red_alert_lan_path, 24)
                self.custom_fonts['red_alert_title'] = pygame.font.Font(red_alert_lan_path, 36)
                print(f"Loaded custom font: C&C Red Alert [LAN]")
            else:
                print("Custom Red Alert font files not found, using system fonts")

        except Exception as e:
            print(f"Error loading custom fonts: {e}")

        # Set up fallback font (system default)
        self.fallback_font = pygame.font.Font(None, 16)

    def get_font(self, font_name: str = 'red_alert_medium') -> pygame.font.Font:
        """Get a font by name, falling back to system font if not available."""
        return self.custom_fonts.get(font_name, self.fallback_font)

    def draw_starfield(self) -> None:
        """Draw the starry background."""
        for x, y, color, size in self.stars:
            pygame.draw.circle(self.screen, color, (x, y), size)

    def world_to_screen(self, x_km: float, y_km: float) -> Tuple[int, int]:
        """Convert world coordinates (km) to screen coordinates (pixels)."""
        center_x = self.width // 2
        center_y = self.height // 2
        screen_x = int(center_x + x_km * SCALE_FACTOR * self.zoom)
        screen_y = int(center_y - y_km * SCALE_FACTOR * self.zoom)  # Flip Y axis
        return (screen_x, screen_y)

    def screen_to_world(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """Convert screen coordinates (pixels) to world coordinates (km)."""
        center_x = self.width // 2
        center_y = self.height // 2
        world_x = (screen_x - center_x) / (SCALE_FACTOR * self.zoom)
        world_y = (center_y - screen_y) / (SCALE_FACTOR * self.zoom)  # Flip Y axis back
        return (world_x, world_y)

    def calculate_render_radius(self, body: CelestialBody) -> int:
        """Calculate the radius for rendering a celestial body."""
        # Scale the radius with zoom - no cap, allowing true size when zoomed in
        scaled_radius = max(int(body.radius_km * SCALE_FACTOR * self.zoom), MIN_RENDER_RADIUS)
        return scaled_radius

    def zoom_in(self) -> None:
        """Zoom in by multiplying zoom level."""
        old_zoom = self.zoom
        self.zoom = min(self.zoom * 1.2, MAX_ZOOM)  # 20% increase each step
        # Clear trails when zoom changes to prevent distortion
        if self.zoom != old_zoom:
            self.trails.clear()

    def zoom_out(self) -> None:
        """Zoom out by dividing zoom level."""
        old_zoom = self.zoom
        self.zoom = max(self.zoom / 1.2, MIN_ZOOM)  # 20% decrease each step
        # Clear trails when zoom changes to prevent distortion
        if self.zoom != old_zoom:
            self.trails.clear()

    def handle_zoom_event(self, event) -> None:
        """Handle mouse wheel zoom events."""
        if event.type == pygame.MOUSEWHEEL:
            if event.y > 0:  # Scroll up
                self.zoom_in()
            elif event.y < 0:  # Scroll down
                self.zoom_out()

    def toggle_fullscreen(self) -> None:
        """Toggle between fullscreen and windowed mode."""
        if self.is_fullscreen:
            # Switch to windowed mode
            self.screen = pygame.display.set_mode(self.windowed_size)
            self.width, self.height = self.windowed_size
            self.is_fullscreen = False
            print("Switched to windowed mode")
        else:
            # Switch to fullscreen mode
            # Get current display info
            info = pygame.display.Info()
            fullscreen_size = (info.current_w, info.current_h)
            self.screen = pygame.display.set_mode(fullscreen_size, pygame.FULLSCREEN)
            self.width, self.height = fullscreen_size
            self.is_fullscreen = True
            print(f"Switched to fullscreen mode ({self.width}x{self.height})")

        # Regenerate stars for new screen size
        self.stars = self._generate_stars()
        # Clear trails to prevent distortion
        self.trails.clear()

    def handle_resize(self, new_width: int, new_height: int) -> None:
        """Handle window resize events (including maximize button)."""
        if not self.is_fullscreen:
            # Update windowed size if not in fullscreen
            self.windowed_size = (new_width, new_height)

        # Update screen dimensions
        self.width = new_width
        self.height = new_height

        # Recreate the display surface with new size
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((new_width, new_height), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)

        # Regenerate stars for new screen size
        self.stars = self._generate_stars()
        # Clear trails to prevent distortion
        self.trails.clear()

        print(f"Window resized to {new_width}x{new_height}")

    def draw_body(self, body: CelestialBody) -> None:
        """Draw a single celestial body with label."""
        screen_pos = self.world_to_screen(body.x_position, body.y_position)
        radius = self.calculate_render_radius(body)

        # Draw the body
        pygame.draw.circle(self.screen, body.color, screen_pos, radius)

        # Draw outline
        pygame.draw.circle(self.screen, (255, 255, 255), screen_pos, radius, 1)

        # Draw label if enabled
        if settings.SHOW_LABELS:
            self._draw_body_label(body, screen_pos, radius)

        # Update trail
        if settings.SHOW_TRAILS:
            self._update_trail(body, screen_pos)

    def _draw_body_label(self, body: CelestialBody, screen_pos: Tuple[int, int], radius: int) -> None:
        """Draw a label next to the celestial body."""
        font = self.get_font('red_alert_small')
        text_surface = font.render(body.name, True, LABEL_COLOR)

        # Position label to the right and slightly above the body
        label_x = screen_pos[0] + radius + LABEL_OFFSET
        label_y = screen_pos[1] - text_surface.get_height() // 2

        # Keep label on screen
        if label_x + text_surface.get_width() > self.width:
            label_x = screen_pos[0] - text_surface.get_width() - LABEL_OFFSET
        if label_y < 0:
            label_y = 0
        if label_y + text_surface.get_height() > self.height:
            label_y = self.height - text_surface.get_height()

        # Draw semi-transparent background for better readability
        label_rect = pygame.Rect(label_x - 2, label_y - 1,
                                text_surface.get_width() + 4,
                                text_surface.get_height() + 2)

        # Create a surface for the background with alpha
        bg_surface = pygame.Surface((label_rect.width, label_rect.height))
        bg_surface.set_alpha(LABEL_BACKGROUND_ALPHA)
        bg_surface.fill(LABEL_BACKGROUND_COLOR)
        self.screen.blit(bg_surface, (label_rect.x, label_rect.y))

        # Draw the text
        self.screen.blit(text_surface, (label_x, label_y))

    def _update_trail(self, body: CelestialBody, screen_pos: Tuple[int, int]) -> None:
        """Update the trail for a celestial body."""
        # Use object ID instead of name to ensure uniqueness for each body instance
        body_id = id(body)
        if body_id not in self.trails:
            self.trails[body_id] = []

        trail = self.trails[body_id]
        trail.append(screen_pos)

        # Limit trail length (0 means unlimited)
        if TRAIL_LENGTH > 0 and len(trail) > TRAIL_LENGTH:
            trail.pop(0)

        # Draw trail
        if len(trail) > 1:
            pygame.draw.lines(self.screen, TRAIL_COLOR, False, trail, 1)

    def draw_info(self, bodies: List[CelestialBody]) -> None:
        """Draw information text on screen."""
        font = self.get_font('red_alert_small')
        y_offset = 10

        for body in bodies:
            text = f"{body.name}: ({body.x_position:.0f}, {body.y_position:.0f}) km"
            text_surface = font.render(text, True, (255, 255, 255))
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 30

    def clear_screen(self) -> None:
        """Clear the screen with background color and draw stars."""
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_starfield()

    def draw_impact_marker(self, marker) -> None:
        """Draw a red X marker at an impact site."""
        screen_pos = self.world_to_screen(marker.x_position, marker.y_position)

        # Don't draw if off screen
        if (screen_pos[0] < -50 or screen_pos[0] > self.width + 50 or
            screen_pos[1] < -50 or screen_pos[1] > self.height + 50):
            return

        # Draw X marker
        size = marker.size
        x, y = screen_pos

        # Draw the X with two lines
        pygame.draw.line(self.screen, marker.color,
                        (x - size, y - size), (x + size, y + size), 2)
        pygame.draw.line(self.screen, marker.color,
                        (x - size, y + size), (x + size, y - size), 2)

    def draw_velocity_arrow(self, start_pos, end_pos, color=(255, 255, 0), velocity_scale=0.1) -> None:
        """Draw an arrow showing velocity direction and magnitude."""
        import math

        # Don't draw if positions are the same
        if start_pos == end_pos:
            return

        # Calculate arrow components
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        length = math.sqrt(dx * dx + dy * dy)

        # Don't draw very short arrows
        if length < 5:
            return

        # Draw main arrow line
        pygame.draw.line(self.screen, color, start_pos, end_pos, 3)

        # Draw arrowhead
        if length > 10:  # Only draw arrowhead if arrow is long enough
            angle = math.atan2(dy, dx)
            arrowhead_length = min(length * 0.3, 15)  # Arrowhead size proportional to arrow length, max 15px
            arrowhead_angle = 0.5  # Angle of arrowhead sides

            # Calculate arrowhead points
            arrowhead1_x = end_pos[0] - arrowhead_length * math.cos(angle - arrowhead_angle)
            arrowhead1_y = end_pos[1] - arrowhead_length * math.sin(angle - arrowhead_angle)
            arrowhead2_x = end_pos[0] - arrowhead_length * math.cos(angle + arrowhead_angle)
            arrowhead2_y = end_pos[1] - arrowhead_length * math.sin(angle + arrowhead_angle)

            # Draw arrowhead lines
            pygame.draw.line(self.screen, color, end_pos, (arrowhead1_x, arrowhead1_y), 3)
            pygame.draw.line(self.screen, color, end_pos, (arrowhead2_x, arrowhead2_y), 3)

        # Draw velocity magnitude text
        velocity_magnitude = length * velocity_scale
        font = pygame.font.Font(None, 24)
        speed_text = f"{velocity_magnitude:.1f} km/s"
        text_surface = font.render(speed_text, True, color)

        # Position text near the middle of the arrow
        text_x = (start_pos[0] + end_pos[0]) // 2
        text_y = (start_pos[1] + end_pos[1]) // 2 - 20  # Offset above the arrow

        # Keep text on screen
        if text_x + text_surface.get_width() > self.width:
            text_x = self.width - text_surface.get_width()
        if text_x < 0:
            text_x = 0
        if text_y < 0:
            text_y = text_y + 40  # Move below arrow if above screen

        self.screen.blit(text_surface, (text_x, text_y))

    def draw_menu(self, menu_state: str, menu_selection: int, options: List[str], settings_manager, audio_manager) -> None:
        """Draw the menu system based on current state."""
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Calculate required height for menu content
        title_height = 60

        # Use smaller line height for controls menu
        if menu_state == "controls":
            options_height = len(options) * 35
        else:
            options_height = len(options) * 50

        instructions = self._get_menu_instructions(menu_state)
        instructions_height = 40 if instructions else 20  # Single line for horizontal instructions

        # Calculate total menu height with proper padding
        menu_width = 600
        menu_height = title_height + options_height + instructions_height + 40  # 40px total padding
        menu_height = min(menu_height, self.height - 40)  # Leave some margin from screen edges

        menu_x = (self.width - menu_width) // 2
        menu_y = (self.height - menu_height) // 2

        # Draw menu background
        pygame.draw.rect(self.screen, (20, 20, 40), (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(self.screen, (255, 255, 255), (menu_x, menu_y, menu_width, menu_height), 3)

        # Draw title
        title_text = self._get_menu_title(menu_state)
        title_font = self.custom_fonts.get('red_alert_title', self.fallback_font)
        title_surface = title_font.render(title_text, True, (255, 255, 255))
        title_x = menu_x + (menu_width - title_surface.get_width()) // 2
        title_y = menu_y + 20
        self.screen.blit(title_surface, (title_x, title_y))

        # Draw options
        start_y = title_y + 60
        for i, option in enumerate(options):
            # Determine color based on selection
            if i == menu_selection:
                color = (255, 255, 0)  # Yellow for selected
                # Draw selection highlight with appropriate height
                if menu_state == "controls":
                    highlight_height = 30
                    line_height = 35
                else:
                    highlight_height = 40
                    line_height = 50
                highlight_rect = pygame.Rect(menu_x + 20, start_y + i * line_height - 5, menu_width - 40, highlight_height)
                pygame.draw.rect(self.screen, (60, 60, 100), highlight_rect)
            else:
                color = (255, 255, 255)  # White for unselected
                # Set line height for positioning
                if menu_state == "controls":
                    line_height = 35
                else:
                    line_height = 50

            # Render option text with value if applicable
            option_text = self._get_option_display_text(menu_state, option, settings_manager, audio_manager)

            # Use smaller font for controls menu to look more like plain text
            if menu_state == "controls":
                font = self.custom_fonts.get('red_alert_medium', self.fallback_font)
                line_height = 35  # Smaller line height for controls
            else:
                font = self.custom_fonts.get('red_alert_large', self.fallback_font)
                line_height = 50  # Normal line height

            text_surface = font.render(option_text, True, color)
            text_x = menu_x + 40
            text_y = start_y + i * line_height
            self.screen.blit(text_surface, (text_x, text_y))

        # Draw instructions at the bottom with proper spacing (horizontal layout)
        if instructions:
            # Join all instructions with separator for horizontal display
            instruction_text = "  •  ".join(instructions)
            instruction_start_y = menu_y + menu_height - 30  # Single line height
            medium_font = self.custom_fonts.get('red_alert_medium', self.fallback_font)
            instruction_surface = medium_font.render(instruction_text, True, (200, 200, 200))
            # Center the instruction text horizontally
            instruction_x = menu_x + (menu_width - instruction_surface.get_width()) // 2
            self.screen.blit(instruction_surface, (instruction_x, instruction_start_y))

    def _get_menu_title(self, menu_state: str) -> str:
        """Get the title for the current menu state."""
        titles = {
            "main": "SPACELAB MENU",
            "scenario": "SELECT SCENARIO",
            "settings": "SETTINGS",
            "controls": "CONTROLS",
            "audio": "AUDIO SETTINGS",
            "graphics": "GRAPHICS SETTINGS",
            "gameplay": "GAMEPLAY SETTINGS"
        }
        return titles.get(menu_state, "MENU")

    def _get_option_display_text(self, menu_state: str, option: str, settings_manager, audio_manager) -> str:
        """Get the display text for a menu option, including current values."""
        if menu_state == "audio":
            if option == "Music Volume":
                volume = settings_manager.get("music_volume")
                return f"Music Volume: {int(volume * 100)}%"
            elif option == "Sound Effects Volume":
                volume = settings_manager.get("sound_effects_volume")
                return f"Sound Effects Volume: {int(volume * 100)}%"
            elif option == "Audio Enabled":
                enabled = settings_manager.get("audio_enabled")
                return f"Audio Enabled: {'ON' if enabled else 'OFF'}"
        elif menu_state == "graphics":
            if option == "Show Labels":
                enabled = settings_manager.get("show_labels")
                return f"Show Labels: {'ON' if enabled else 'OFF'}"
            elif option == "Show Trails":
                enabled = settings_manager.get("show_trails")
                return f"Show Trails: {'ON' if enabled else 'OFF'}"
            elif option == "Show FPS":
                enabled = settings_manager.get("show_fps")
                return f"Show FPS: {'ON' if enabled else 'OFF'}"
            elif option == "Fullscreen":
                return f"Fullscreen: {'ON' if self.is_fullscreen else 'OFF'}"
        elif menu_state == "gameplay":
            if option == "Trail Length":
                length = settings_manager.get("trail_length")
                return f"Trail Length: {length}"
            elif option == "Max Time Scale":
                scale = settings_manager.get("max_time_scale")
                return f"Max Time Scale: {scale}x"
            elif option == "Physics Method":
                method = settings_manager.get("physics_method")
                return f"Physics Method: {method.replace('_', ' ').title()}"

        return option

    def _get_menu_instructions(self, menu_state: str) -> List[str]:
        """Get instruction text for the current menu state."""
        if menu_state in ["audio", "graphics", "gameplay"]:
            return ["↑↓ Navigate", "←→ Adjust", "ENTER Select", "ESC Back"]
        elif menu_state == "controls":
            return ["↑↓ Navigate", "ESC Back"]
        else:
            return ["↑↓ Navigate", "ENTER Select", "ESC Back"]

    def present(self) -> None:
        """Present the rendered frame to screen."""
        pygame.display.flip()
        self.clock.tick(FPS)

    def quit(self) -> None:
        """Clean up pygame resources."""
        pygame.quit()
