"""Entry point for the Solar System simulation."""

import pygame
from .simulation import SolarSystemSimulation
from .graphics.startup_menu import show_startup_menu


def main():
    """Main entry point for the application."""
    try:
        print("Initializing Solar System Simulation...")
        print("Make sure you have pygame installed: poetry install")
        print()

        # Initialize pygame for the menu
        pygame.init()
        screen = pygame.display.set_mode((800, 600))  # Smaller window for startup menu
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
        print(f"Error: {e}")
        print("Please install pygame with: pip install pygame")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
