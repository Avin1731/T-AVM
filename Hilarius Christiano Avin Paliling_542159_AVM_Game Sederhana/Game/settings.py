from pathlib import Path

# Display
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TITLE = "Survival Hardcore Matrix Edition"
FPS = 60

# Paths
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
SPRITES_DIR = ASSETS_DIR / "sprites"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Physics
GRAVITY = 0.5

# Debug
DEBUG_MODE = True

# Spawn
MOB_SPAWN_COOLDOWN = 5000  # dalam milidetik (5 detik)
MAX_MOBS = 5  # jumlah maksimum mob yang bisa ada di layar
MOB_SPAWN_INCREASE_RATE = 0.05  # Peningkatan kesulitan per spawn