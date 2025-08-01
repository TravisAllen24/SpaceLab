"""Configuration settings for the solar system simulation."""

# Window settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_TITLE = "Solar System Simulation"
FPS = 60

# Simulation settings
TIME_SCALE = 10.0  # Speed up simulation (10x real time)
PHYSICS_DT = 1.0  # Physics time step in seconds

# Physics Integration Method
# Choose between two integration methods:
# "single_step" - Fast, uses large time steps (can be unstable at high time warps)
# "multi_step" - Stable, uses multiple small time steps (better for high time warps)
# "patched_conic" - Uses a simple patched conic approximation for orbits
# Note: "patched_conic" is not yet implemented, so it will raise NotImplemented
PHYSICS_INTEGRATION_METHOD = "multi_step"  # Options: "single_step" or "multi_step"
MAX_PHYSICS_STEPS_PER_FRAME = 100  # Maximum physics steps per frame (for multi_step method)

# Rendering settings
SCALE_FACTOR = .001  # Scale factor for converting km to pixels
CENTER_X = WINDOW_WIDTH // 2
CENTER_Y = WINDOW_HEIGHT // 2

# Zoom settings
ZOOM_FACTOR = 1.0  # Current zoom level
MIN_ZOOM = 0.00001  # Minimum zoom (extremely zoomed out for solar system)
MAX_ZOOM = 10.0  # Maximum zoom (zoomed in)
ZOOM_SPEED = 0.1  # How much zoom changes per scroll

# Colors (RGB)
BACKGROUND_COLOR = (0, 0, 0)  # Black
EARTH_COLOR = (0, 100, 255)   # Blue
MOON_COLOR = (200, 200, 200)  # Gray
SATELLITE_COLOR = (255, 255, 0)  # Yellow
TRAIL_COLOR = (100, 100, 100)   # Dark gray

# Visualization
SHOW_TRAILS = True
TRAIL_LENGTH = 10000  # Number of points in trail (0 = unlimited)
MIN_RENDER_RADIUS = 2  # Minimum pixel radius for bodies

# Starfield
STAR_COUNT = 200  # Number of background stars
STAR_COLORS = [
    (255, 255, 255),  # White
    (255, 255, 200),  # Warm white
    (200, 200, 255),  # Cool white/blue
    (255, 200, 200),  # Warm/red
]

# Labels
SHOW_LABELS = True  # Show labels next to celestial bodies
LABEL_FONT_SIZE = 16  # Font size for body labels
LABEL_COLOR = (255, 255, 255)  # White text
LABEL_OFFSET = 5  # Pixels between body and label
LABEL_BACKGROUND_COLOR = (0, 0, 0)  # Black background
LABEL_BACKGROUND_ALPHA = 128  # Semi-transparent background
