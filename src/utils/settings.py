from enum import Enum, auto
from pathlib import Path

FPS = 60
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BASE_PATH = Path(__file__).parent.parent
TOTAL_SLOTS_EXECUTION = 20
TILE_SIZE = 32

class Colors(Enum):
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    DARK_RED = (150, 0, 0)
    GREEN = (0, 255, 0)
    DARK_GREEN = (0, 150, 0)
    BLUE = (0, 0, 255),
    DARK_BLUE = (0, 0, 150),
    LIGHT_GRAY = (200, 200, 200)
    DARK_GRAY = (30, 30, 30)
    GRAY = (128, 128, 128)

class ActionsCommands(Enum):
    WALK = "walk"
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    REPEAT = "repeat"
    END_REPEAT = "end_repeat"

COMMANDS_TRANSLATED = {
    "walk": "andar",
    "turn_left": "girar para a esquerda",
    "turn_right": "girar para a direita",
    "repeat": "repetir",
    "end_repeat": "fim repetir"
}


class GameState(Enum):
    MAIN_MENU = auto()
    NEW_GAME = auto()
    CONTINUE_GAME = auto()
    IN_GAME = auto()
    LEVEL_SELECT = auto()
    QUIT = auto()
    END_CREDITS = auto()