# Solar System Simulation

A physics-based solar system simulation built with Python and pygame, featuring gravitational interactions between Earth, Moon, and artificial satellites.

## Features

- Real-time gravitational physics simulation
- Interactive pygame visualization
- Earth, Moon, and satellite objects
- Orbital trails and information display
- Pause/resume and reset functionality

## Installation

1. Install dependencies using Poetry:
```bash
poetry install
```

2. Or install manually:
```bash
pip install pygame numpy
```

## Usage

### Option 1: Root-level script (Recommended)
```bash
python run_simulation.py
```

### Option 2: Using Poetry
```bash
poetry run python -m solar_system.main
```

### Option 3: Direct module execution
```bash
python -m src.solar_system.main
```

### Option 4: Windows batch file
```cmd
run_simulation.bat
```

## Controls

- **SPACE**: Pause/Resume simulation
- **R**: Reset simulation
- **ESC**: Exit

## Project Structure

```
Solar-System/
├── src/
│   └── solar_system/
│       ├── main.py              # Entry point
│       ├── simulation.py        # Main simulation loop
│       ├── bodies/              # Celestial body classes
│       ├── physics/             # Physics calculations
│       ├── graphics/            # Pygame rendering
│       ├── config/              # Configuration settings
│       └── utils/               # Utility functions
├── tests/                       # Unit tests
└── examples/                    # Example scripts
```

## Development

The simulation uses:
- **Physics**: Newtonian gravity with configurable time steps
- **Rendering**: Pygame for 2D visualization with trails
- **Architecture**: Modular design with separation of concerns

## License

MIT License
