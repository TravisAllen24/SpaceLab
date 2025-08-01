"""Entry point for the Solar System simulation."""

from .simulation import SolarSystemSimulation


def main():
    """Main entry point for the application."""
    try:
        simulation = SolarSystemSimulation()
        simulation.run()
    except ImportError as e:
        print(f"Error: {e}")
        print("Please install pygame with: pip install pygame")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
