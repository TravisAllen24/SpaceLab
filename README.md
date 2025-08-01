# Space Lab

A comprehensive physics-based solar system simulation built with Python and pygame, featuring realistic gravitational interactions, multiple scenario systems, and interactive celestial body creation.

## Features

### Core Simulation
- Real-time Newtonian gravitational physics simulation
- Accurate orbital mechanics with configurable time steps
- Multiple predefined solar system scenarios
- Interactive pygame visualization with zoom and pan capabilities
- Collision detection and impact markers
- Orbital trails with configurable length and visibility

### Interactive Controls
- **Scenario Selection**: Choose from 5 different astronomical systems at startup
- **Dynamic Body Creation**:
  - Left-click drag: Create custom celestial bodies with user-defined properties
  - Right-click drag: Create satellites with velocity visualization
- **Time Control**: Variable time scaling (0.1x to 8192x speed)
- **Zoom System**: Mouse wheel and keyboard zoom (extensive range for solar system viewing)
- **Fullscreen Support**: Toggle between windowed and fullscreen modes
- **Visual Toggles**: Show/hide labels, trails, and impact markers

### Multiple Scenarios
1. **Earth-Moon System**: Earth, Moon, and ISS satellite
2. **Complete Solar System**: Sun with all 8 planets in realistic orbits
3. **Jupiter System**: Jupiter with its 4 major moons (Io, Europa, Ganymede, Callisto)
4. **Proxima Centauri System**: Red dwarf star with 3 known exoplanets
5. **Empty Space**: Blank canvas for creating custom systems

### Advanced Features
- **Collision System**: Realistic collision detection with impact site markers
- **Mass-based Survival**: Bodies survive collisions based on relative mass
- **Velocity Arrows**: Visual feedback when creating bodies with initial velocity
- **Starfield Background**: Procedurally generated star field with multiple star types
- **Responsive UI**: Resizable window with automatic scaling
- **Information Display**: Real-time position data and system status

## Installation
Open VSCode, open the terminal, and enter the following commands:
1. Clone repository
```bash
git clone https://github.com/TravisAllen24/SpaceLab.git
```
2. Create a virtual environment
```bash
python -m venv .venv
```
3. Activate the virtual environment
```bash
.venv\Scripts\activate.bat
```
4. Install Poetry
```bash
pip install poetry
```
5. Install dependencies using Poetry:
```bash
poetry install
```

## Usage


### Console commands
```bash
# Running with run_simulation.py
python run_simulation.py

# Direct module execution
python -m src.spacelab.main

# Using Poetry with module execution
poetry run python -m src.spacelab.main
```

### First Run
1. A startup menu will appear with scenario options
2. Use ↑/↓ arrow keys to navigate
3. Press ENTER to select a scenario
4. Press ESC to quit

## Scenarios

### 1. Earth-Moon System
- **Bodies**: Earth, Moon, International Space Station (ISS)
- **Scale**: Perfect for observing satellite orbits and lunar motion
- **Features**: Realistic Earth-Moon distance and orbital parameters
- **Best for**: Learning orbital mechanics, satellite deployment

### 2. Complete Solar System
- **Bodies**: Sun and all 8 planets with realistic masses and orbital velocities
- **Scale**: Requires significant zoom-out to view entire system
- **Features**: Planets start in varied orbital positions for dynamic viewing
- **Best for**: Understanding planetary motion, long-term orbital evolution

### 3. Jupiter System
- **Bodies**: Jupiter with its 4 major moons (Io, Europa, Ganymede, Callisto)
- **Scale**: Mid-range scale showing rapid moon orbits
- **Features**: Fast orbital periods demonstrate gravitational relationships
- **Best for**: Studying moon systems, rapid orbital dynamics

### 4. Proxima Centauri System
- **Bodies**: Red dwarf star with 3 known exoplanets (Proxima b, c, d)
- **Scale**: Very compact system with close planetary orbits
- **Features**: Based on real astronomical data from nearest star system
- **Best for**: Exploring exoplanet systems, tight orbital configurations

### 5. Empty Space
- **Bodies**: None (blank canvas)
- **Scale**: User-defined through body creation
- **Features**: Complete freedom to design custom systems
- **Best for**: Experimentation, education, creating unique scenarios

## Controls

### Basic Controls
- **SPACE**: Pause/Resume simulation
- **R**: Reset simulation to initial state
- **ESC**: Exit simulation

### View Controls
- **Mouse Wheel**: Zoom in/out
- **+/-**: Zoom with keyboard
- **F11**: Toggle fullscreen mode
- **L**: Toggle body labels on/off
- **T**: Toggle orbital trails on/off
- **C**: Clear all trails and impact markers

### Time Controls
- **,** (comma): Decrease time scale (slow down)
- **.** (period): Increase time scale (speed up)

### Interactive Creation
- **Left Mouse Drag**: Create custom celestial body
  - Drag to set initial velocity
  - Input dialog for mass, radius, and name
- **Right Mouse Drag**: Create satellite
  - Drag direction and length sets initial velocity
  - Automatic naming (Satellite-1, Satellite-2, etc.)

### Visual Feedback
- Yellow arrows show satellite velocity during creation
- Red arrows show custom body velocity during creation
- Speed values displayed during velocity setup

## Project Structure

```
SpaceLab/
├── src/
│   └── spacelab/
│       ├── main.py              # Entry point with startup menu
│       ├── simulation.py        # Main simulation loop and event handling
│       ├── bodies/              # Celestial body classes
│       │   ├── celestial_body.py   # Base celestial body class
│       │   ├── satellite.py        # Artificial satellite class
│       │   ├── custom_body.py       # User-created body class
│       │   └── impact_marker.py     # Collision impact markers
│       ├── physics/             # Physics calculations
│       │   ├── gravity.py           # Gravitational force calculations
│       │   └── collision.py         # Collision detection system
│       ├── graphics/            # Pygame rendering system
│       │   ├── renderer.py          # Main rendering engine
│       │   ├── startup_menu.py      # Scenario selection menu
│       │   └── input_dialog.py      # User input dialogs
│       ├── scenarios/           # Predefined system setups
│       │   └── predefined_systems.py # All scenario definitions
│       ├── config/              # Configuration settings
│       │   └── settings.py          # Simulation parameters
│       └── utils/               # Utility functions
│           └── math_helpers.py      # Mathematical utilities
├── run_simulation.py            # Root-level entry script
├── pyproject.toml              # Poetry configuration
└── README.md                   # This file
```

## Development

### Architecture
The simulation uses a modular design with clear separation of concerns:

- **Physics Engine**: Newtonian gravity with configurable time steps and collision detection
- **Rendering System**: Pygame-based 2D visualization with trails, zoom, and starfield
- **Scenario System**: Predefined astronomical systems with realistic parameters
- **Interactive Features**: Real-time body creation with input validation
- **UI/UX**: Responsive interface with keyboard and mouse controls

### Technical Details
- **Coordinate System**: Cartesian coordinates with origin at system center
- **Units**: Kilometers for distance, kg for mass, km/s for velocity
- **Time Scaling**: Adjustable simulation speed from 0.1x to 8192x real-time
- **Collision Model**: Radius-based collision with mass-dependent survival rules
- **Zoom Range**: Extreme zoom range suitable for viewing from satellite orbits to entire solar systems

### Customization
- All simulation parameters are configurable in `src/spacelab/config/settings.py`
- New scenarios can be added in `src/spacelab/scenarios/predefined_systems.py`
- Visual appearance can be modified in the renderer and settings files

### Performance
- Optimized physics calculations for real-time simulation
- Trail management to prevent memory issues
- Efficient rendering with off-screen culling
- Configurable trail lengths and update rates

## License

MIT License
