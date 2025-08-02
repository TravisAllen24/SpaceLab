"""Settings manager for saving and loading user preferences."""

import json
import os
from typing import Dict, Any, Optional


class SettingsManager:
    """Manages user settings with save/load functionality."""

    def __init__(self):
        """Initialize the settings manager."""
        # Get the path to save settings
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.settings_file = os.path.join(current_dir, "user_settings.json")

        # Default settings
        self.default_settings = {
            # Audio settings
            "audio_enabled": True,
            "music_volume": 0.3,
            "sound_effects_volume": 0.5,

            # Graphics settings
            "fullscreen": False,
            "window_width": 1200,
            "window_height": 800,
            "show_fps": False,
            "show_labels": True,
            "show_trails": True,

            # Gameplay settings
            "trail_length": 100,
            "max_time_scale": 8192,
            "physics_method": "multi_step",  # Options: "single_step", "multi_step", "patched_conic"
            "max_physics_steps": 10,

            # UI settings
            "show_instructions": True,
            "show_coordinates": True,

            # Performance settings
            "star_count": 200,
            "collision_detection": True
        }

        # Current settings (loaded from file or defaults)
        self.settings = self.default_settings.copy()
        self.load_settings()

    def load_settings(self) -> None:
        """Load settings from file."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Only update settings that exist in defaults (for safety)
                    for key, value in loaded_settings.items():
                        if key in self.default_settings:
                            self.settings[key] = value
                print(f"Settings loaded from {self.settings_file}")
            else:
                print("No settings file found, using defaults")
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.settings = self.default_settings.copy()

    def save_settings(self) -> None:
        """Save current settings to file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            print(f"Settings saved to {self.settings_file}")
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self.settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a setting value."""
        if key in self.default_settings:
            self.settings[key] = value
        else:
            print(f"Warning: Unknown setting key '{key}'")

    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        self.settings = self.default_settings.copy()
        print("Settings reset to defaults")

    def get_all_settings(self) -> Dict[str, Any]:
        """Get all current settings."""
        return self.settings.copy()
