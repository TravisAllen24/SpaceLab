"""Startup menu for selecting simulation scenarios."""

import pygame
import os
from typing import Optional


class StartupMenu:
    """Menu for selecting simulation scenarios at startup."""

    def __init__(self, screen):
        self.screen = screen

        # Initialize pygame mixer for startup music
        try:
            pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
        except Exception as e:
            print(f"Warning: Could not initialize audio for startup menu: {e}")

        # Load startup music
        self._load_startup_music()

        # Load custom fonts
        self._load_custom_fonts()

        # Load background image
        self.background_image = None
        try:
            # Get the path to the background image in media folder
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level to spacelab, then into media/images
            spacelab_dir = os.path.dirname(current_dir)
            image_path = os.path.join(spacelab_dir, "media", "images", "8bit-space.jpg")
            self.background_image = pygame.image.load(image_path)
            # Scale the background to fit the screen
            self.background_image = pygame.transform.scale(self.background_image, screen.get_size())
        except Exception as e:
            print(f"Warning: Could not load background image: {e}")
            self.background_image = None

        self.selected_option = 0
        self.options = [
            {
                "name": "Earth-Moon System",
                "description": "Earth, Moon, and ISS satellite",
                "key": "earth_moon"
            },
            {
                "name": "Solar System",
                "description": "Sun, planets, and major moons",
                "key": "solar_system"
            },
            {
                "name": "Jupiter System",
                "description": "Jupiter and its major moons",
                "key": "jupiter_system"
            },
            {
                "name": "Proxima Centauri",
                "description": "Red dwarf star with 3 exoplanets",
                "key": "proxima_centauri"
            },
            {
                "name": "Empty Space",
                "description": "Start with empty space to create your own",
                "key": "empty"
            }
        ]

        # Colors (with some transparency for overlay effect)
        self.bg_color = (20, 20, 40, 180)  # Semi-transparent dark blue
        self.title_color = (255, 255, 255)
        self.selected_color = (100, 200, 255)
        self.normal_color = (200, 200, 200)
        self.description_color = (150, 150, 150)

        # Menu dimensions (adjusted for 5 options)
        self.menu_width = 400
        self.menu_height = 360  # Increased height for 5 options
        self.menu_x = (screen.get_width() - self.menu_width) // 2
        self.menu_y = (screen.get_height() - self.menu_height) // 2

    def _load_custom_fonts(self) -> None:
        """Load custom fonts from the fonts directory."""
        # Get the path to the fonts directory in media folder
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to spacelab, then into media/fonts
        spacelab_dir = os.path.dirname(current_dir)
        fonts_dir = os.path.join(spacelab_dir, "media", "fonts")

        try:
            # Look for Red Alert font files
            red_alert_inet_path = os.path.join(fonts_dir, "C&C Red Alert [INET].ttf")
            red_alert_lan_path = os.path.join(fonts_dir, "C&C Red Alert [LAN].ttf")

            # Load the INET version as primary, LAN as backup
            if os.path.exists(red_alert_inet_path):
                self.font_large = pygame.font.Font(red_alert_inet_path, 32)
                self.font_medium = pygame.font.Font(red_alert_inet_path, 24)
                self.font_small = pygame.font.Font(red_alert_inet_path, 16)
                print(f"Loaded custom fonts for menu: C&C Red Alert [INET]")
            elif os.path.exists(red_alert_lan_path):
                self.font_large = pygame.font.Font(red_alert_lan_path, 32)
                self.font_medium = pygame.font.Font(red_alert_lan_path, 24)
                self.font_small = pygame.font.Font(red_alert_lan_path, 16)
                print(f"Loaded custom fonts for menu: C&C Red Alert [LAN]")
            else:
                # Fallback to system fonts
                self.font_large = pygame.font.Font(None, 32)
                self.font_medium = pygame.font.Font(None, 24)
                self.font_small = pygame.font.Font(None, 16)
                print("Using system fonts for menu")

        except Exception as e:
            print(f"Error loading custom fonts for menu: {e}")
            # Fallback to system fonts
            self.font_large = pygame.font.Font(None, 32)
            self.font_medium = pygame.font.Font(None, 24)
            self.font_small = pygame.font.Font(None, 16)

    def _load_startup_music(self) -> None:
        """Load startup menu background music."""
        self.startup_music_path = None
        self.music_playing = False

        try:
            # Get the path to the music directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level to spacelab, then into media/music
            spacelab_dir = os.path.dirname(current_dir)
            music_dir = os.path.join(spacelab_dir, "media", "music")

            # Look for the startup music file
            startup_music_file = "663230_Spaze---Light-Years-Away.mp3"
            music_path = os.path.join(music_dir, startup_music_file)

            if os.path.exists(music_path):
                self.startup_music_path = music_path
                print(f"Loaded startup music: {startup_music_file}")
            else:
                print(f"Startup music file not found: {startup_music_file}")

        except Exception as e:
            print(f"Error loading startup music: {e}")

    def start_music(self) -> None:
        """Start playing the startup menu music."""
        if self.startup_music_path and not self.music_playing:
            try:
                pygame.mixer.music.load(self.startup_music_path)
                pygame.mixer.music.set_volume(0.3)  # Lower volume for background
                pygame.mixer.music.play(-1)  # Loop forever
                self.music_playing = True
                print("Started startup menu music")
            except Exception as e:
                print(f"Error playing startup music: {e}")

    def stop_music(self) -> None:
        """Stop the startup menu music."""
        if self.music_playing:
            try:
                pygame.mixer.music.stop()
                self.music_playing = False
                print("Stopped startup menu music")
            except Exception as e:
                print(f"Error stopping startup music: {e}")

    def handle_event(self, event) -> Optional[str]:
        """Handle menu events. Returns selected scenario key or None."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return self.options[self.selected_option]["key"]
            elif event.key == pygame.K_ESCAPE:
                return "quit"

        return None

    def draw(self):
        """Draw the startup menu."""
        # Draw background image if available, otherwise use solid color
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill((20, 20, 40))

        # Create a semi-transparent overlay for the menu area
        menu_surface = pygame.Surface((self.menu_width, self.menu_height))
        menu_surface.set_alpha(200)  # Semi-transparent
        menu_surface.fill((20, 20, 40))  # Dark blue background

        # Draw border around menu
        pygame.draw.rect(menu_surface, (100, 100, 150), menu_surface.get_rect(), 2)

        # Blit the menu surface to the screen
        self.screen.blit(menu_surface, (self.menu_x, self.menu_y))

        # Draw title (positioned relative to menu)
        title_text = "Space Lab Menu"
        title_surface = self.font_large.render(title_text, True, self.title_color)
        title_x = self.menu_x + (self.menu_width - title_surface.get_width()) // 2
        self.screen.blit(title_surface, (title_x, self.menu_y + 20))

        # Draw subtitle
        subtitle_text = "Choose a scenario:"
        subtitle_surface = self.font_medium.render(subtitle_text, True, self.title_color)
        subtitle_x = self.menu_x + (self.menu_width - subtitle_surface.get_width()) // 2
        self.screen.blit(subtitle_surface, (subtitle_x, self.menu_y + 60))

        # Draw options (compact spacing for 5 options)
        start_y = self.menu_y + 90
        for i, option in enumerate(self.options):
            color = self.selected_color if i == self.selected_option else self.normal_color

            # Draw option name
            name_surface = self.font_medium.render(option["name"], True, color)
            name_x = self.menu_x + (self.menu_width - name_surface.get_width()) // 2
            y_pos = start_y + i * 45  # Even more compact spacing
            self.screen.blit(name_surface, (name_x, y_pos))

            # Draw description (smaller font)
            desc_surface = self.font_small.render(option["description"], True, self.description_color)
            desc_x = self.menu_x + (self.menu_width - desc_surface.get_width()) // 2
            self.screen.blit(desc_surface, (desc_x, y_pos + 20))  # Closer description

            # Draw selection indicator
            if i == self.selected_option:
                indicator = ">"
                indicator_surface = self.font_medium.render(indicator, True, self.selected_color)
                indicator_x = name_x - 25  # Closer to text
                self.screen.blit(indicator_surface, (indicator_x, y_pos))

        # Draw instructions at bottom of menu
        instructions = [
            "upArrow/downArrow: Navigate    ENTER: Select    ESC: Quit"
        ]

        inst_y = self.menu_y + self.menu_height - 30
        for instruction in instructions:
            inst_surface = self.font_small.render(instruction, True, self.description_color)
            inst_x = self.menu_x + (self.menu_width - inst_surface.get_width()) // 2
            self.screen.blit(inst_surface, (inst_x, inst_y))


def show_startup_menu(screen) -> Optional[str]:
    """Show the startup menu and return the selected scenario."""
    menu = StartupMenu(screen)
    clock = pygame.time.Clock()

    # Start the startup menu music
    menu.start_music()

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    menu.stop_music()
                    return "quit"

                result = menu.handle_event(event)
                if result is not None:
                    menu.stop_music()
                    return result

            menu.draw()
            pygame.display.flip()
            clock.tick(60)
    except Exception as e:
        print(f"Error in startup menu: {e}")
        menu.stop_music()
        return "quit"
