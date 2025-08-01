#!/usr/bin/env python3
"""
Root-level script to run the Solar System simulation.
This script handles the import paths correctly and provides an easy entry point.
"""

import sys
import os

# Add the src directory to Python path so we can import solar_system modules
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

try:
    import pygame
    from spacelab.simulation import SolarSystemSimulation
    from spacelab.graphics.startup_menu import show_startup_menu

    def main():
        """Main entry point for the Solar System simulation."""
        print("Initializing Solar System Simulation...")
        print()

        try:
            # Initialize pygame for the menu
            pygame.init()
            screen = pygame.display.set_mode((1200, 800))
            pygame.display.set_caption("Solar System Simulation - Startup")

            # Show startup menu
            selected_scenario = show_startup_menu(screen)

            if selected_scenario == "quit" or selected_scenario is None:
                print("Exiting...")
                pygame.quit()
                return

            # Create and run simulation with selected scenario
            simulation = SolarSystemSimulation(selected_scenario)
            simulation.run()

        except ImportError as e:
            print(f"Import Error: {e}")
            print("Please install pygame with one of the following commands:")
            print("  poetry install")
            print("  pip install pygame numpy")
            return 1
        except Exception as e:
            print(f"An error occurred: {e}")
            return 1

        return 0

    if __name__ == "__main__":
        exit_code = main()
        sys.exit(exit_code)

except ImportError as e:
    print(f"Failed to import simulation modules: {e}")
    print("Make sure you're running this script from the Solar-System root directory.")
    sys.exit(1)
