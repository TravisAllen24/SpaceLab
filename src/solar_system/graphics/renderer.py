"""Pygame rendering system for the solar system simulation."""

import pygame
import random
from typing import List, Tuple
from ..bodies.celestial_body import CelestialBody
from ..config.settings import *


class Renderer:
    """Handles all pygame rendering operations."""

    def __init__(self, width: int = WINDOW_WIDTH, height: int = WINDOW_HEIGHT):
        """Initialize the renderer with pygame."""
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.width = width
        self.height = height

        # Trail system
        self.trails = {}  # Dictionary to store trails for each body

        # Zoom system
        self.zoom = ZOOM_FACTOR

        # Star field
        self.stars = self._generate_stars()

    def _generate_stars(self) -> List[Tuple[int, int, Tuple[int, int, int], int]]:
        """Generate random stars for the background."""
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

    def draw_starfield(self) -> None:
        """Draw the starry background."""
        for x, y, color, size in self.stars:
            pygame.draw.circle(self.screen, color, (x, y), size)

    def world_to_screen(self, x_km: float, y_km: float) -> Tuple[int, int]:
        """Convert world coordinates (km) to screen coordinates (pixels)."""
        screen_x = int(CENTER_X + x_km * SCALE_FACTOR * self.zoom)
        screen_y = int(CENTER_Y - y_km * SCALE_FACTOR * self.zoom)  # Flip Y axis
        return (screen_x, screen_y)

    def calculate_render_radius(self, body: CelestialBody) -> int:
        """Calculate the radius for rendering a celestial body."""
        # Scale the radius with zoom, but ensure it's visible
        scaled_radius = max(int(body.radius_km * SCALE_FACTOR * self.zoom), MIN_RENDER_RADIUS)
        return min(scaled_radius, 50)  # Cap at 50 pixels for very large bodies

    def zoom_in(self) -> None:
        """Zoom in by the zoom speed."""
        old_zoom = self.zoom
        self.zoom = min(self.zoom + ZOOM_SPEED, MAX_ZOOM)
        # Clear trails when zoom changes to prevent distortion
        if self.zoom != old_zoom:
            self.trails.clear()
    
    def zoom_out(self) -> None:
        """Zoom out by the zoom speed."""
        old_zoom = self.zoom
        self.zoom = max(self.zoom - ZOOM_SPEED, MIN_ZOOM)
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

    def draw_body(self, body: CelestialBody) -> None:
        """Draw a single celestial body with label."""
        screen_pos = self.world_to_screen(body.x_position, body.y_position)
        radius = self.calculate_render_radius(body)

        # Draw the body
        pygame.draw.circle(self.screen, body.color, screen_pos, radius)

        # Draw outline
        pygame.draw.circle(self.screen, (255, 255, 255), screen_pos, radius, 1)

        # Draw label if enabled
        if SHOW_LABELS:
            self._draw_body_label(body, screen_pos, radius)

        # Update trail
        if SHOW_TRAILS:
            self._update_trail(body, screen_pos)

    def _draw_body_label(self, body: CelestialBody, screen_pos: Tuple[int, int], radius: int) -> None:
        """Draw a label next to the celestial body."""
        font = pygame.font.Font(None, LABEL_FONT_SIZE)
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
        if body.name not in self.trails:
            self.trails[body.name] = []

        trail = self.trails[body.name]
        trail.append(screen_pos)

        # Limit trail length (0 means unlimited)
        if TRAIL_LENGTH > 0 and len(trail) > TRAIL_LENGTH:
            trail.pop(0)

        # Draw trail
        if len(trail) > 1:
            pygame.draw.lines(self.screen, TRAIL_COLOR, False, trail, 1)

    def draw_info(self, bodies: List[CelestialBody]) -> None:
        """Draw information text on screen."""
        font = pygame.font.Font(None, 24)
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

    def present(self) -> None:
        """Present the rendered frame to screen."""
        pygame.display.flip()
        self.clock.tick(FPS)

    def quit(self) -> None:
        """Clean up pygame resources."""
        pygame.quit()
