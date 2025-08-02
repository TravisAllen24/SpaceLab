"""Audio manager for background music and sound effects."""

import pygame
import os
import random
from typing import Dict, Optional


class AudioManager:
    """Manages background music and sound effects for the simulation."""

    def __init__(self):
        """Initialize the audio manager."""
        # Initialize pygame mixer for audio
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.init()

        # Audio state
        self.is_muted = False
        self.current_track = None
        self.music_volume = 0.3  # Lower volume for background music

        # Load music tracks for different scenarios
        self.scenario_music = self._load_scenario_music()

    def _load_scenario_music(self) -> Dict[str, str]:
        """Load and map music tracks to different scenarios."""
        # Get the path to the music directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        music_dir = os.path.join(current_dir, "..", "media", "music")

        # Map scenarios to music files
        scenario_music = {}

        try:
            # Look for music files
            music_files = [
                "505813_The-Maze-Of-Mayonnaise.mp3",
                "623104_Bossfight---Milky-Ways.mp3",
                "503544_Starship-Showdown.mp3",
                "485978_Partyt-Aumlr-Igaringng.mp3",
                "383158_Bossfight___Dr._Finkelfrac.mp3"
            ]

            # Map specific tracks to scenarios
            track_mapping = {
                "earth_moon": "505813_The-Maze-Of-Mayonnaise.mp3",  # Calm track for Earth-Moon
                "solar_system": "623104_Bossfight---Milky-Ways.mp3",  # Epic track for solar system
                "jupiter_system": "503544_Starship-Showdown.mp3",  # Action track for Jupiter
                "proxima_centauri": "485978_Partyt-Aumlr-Igaringng.mp3",  # Alien track for exoplanets
                "empty": "383158_Bossfight___Dr._Finkelfrac.mp3"  # Mysterious track for empty space
            }

            # Check which files exist and build the mapping
            for scenario, filename in track_mapping.items():
                file_path = os.path.join(music_dir, filename)
                if os.path.exists(file_path):
                    scenario_music[scenario] = file_path
                    print(f"Loaded music for {scenario}: {filename}")
                else:
                    print(f"Music file not found for {scenario}: {filename}")

        except Exception as e:
            print(f"Error loading music files: {e}")

        return scenario_music

    def play_scenario_music(self, scenario: str) -> None:
        """Play background music for a specific scenario."""
        if self.is_muted:
            return

        # Stop current music
        pygame.mixer.music.stop()

        # Get the music file for this scenario
        music_file = self.scenario_music.get(scenario)
        if music_file and os.path.exists(music_file):
            try:
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)  # -1 means loop forever
                self.current_track = scenario
                print(f"Playing background music for {scenario}")
            except Exception as e:
                print(f"Error playing music for {scenario}: {e}")
        else:
            print(f"No music available for scenario: {scenario}")

    def toggle_mute(self) -> None:
        """Toggle mute on/off."""
        self.is_muted = not self.is_muted

        if self.is_muted:
            pygame.mixer.music.set_volume(0)
            print("Audio muted")
        else:
            pygame.mixer.music.set_volume(self.music_volume)
            print("Audio unmuted")

    def stop_music(self) -> None:
        """Stop all music."""
        pygame.mixer.music.stop()
        self.current_track = None

    def set_volume(self, volume: float) -> None:
        """Set the music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        if not self.is_muted:
            pygame.mixer.music.set_volume(self.music_volume)

    def cleanup(self) -> None:
        """Clean up audio resources."""
        pygame.mixer.music.stop()
        pygame.mixer.quit()
