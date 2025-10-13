from . import player
from src.config import TILE_SIZE


class GameState:
    CODING = "CODING"
    EXECUTING = "EXECUTING"


class GameModel:
    def __init__(self):
        self.objective_text = None
        self.player = None
        self.tile_map = []
        self.walkable_tiles = {9, 10}

        self.running = True

        self.available_actions = ["RIGHT", "LEFT", "WALK"]
        self.actions_sequence = []

        self.game_state = GameState.CODING

    def load_level(self, level_filepath, assets):
        level_data = assets.get_level_data(level_filepath)
        if not level_data:
            return False

        self.tile_map = level_data["tile_map"]
        self.objective_text = level_data["objective_text"]
        self.player = player.Player(level_data["player_start_pos"], assets)
        return True

    def add_action_to_sequence(self, action, pos=-1):
        if len(self.actions_sequence) >= 26:
            return

        if self.game_state == GameState.CODING:
            if pos >= 0:
                self.actions_sequence.insert(pos, action)
            else:
                self.actions_sequence.append(action)

    def change_command_slot(self, command_index, new_index):
        command = self.actions_sequence.pop(command_index)
        self.actions_sequence.insert(new_index, command)

    def remove_action_from_sequence(self, index):
        if self.game_state == GameState.CODING and 0 <= index < len(self.actions_sequence):
            self.actions_sequence.pop(index)

    def start_execution(self):
        if self.game_state == GameState.CODING and self.actions_sequence:
            self.game_state = GameState.EXECUTING

    def reset_sequence(self):
        self.actions_sequence.clear()
        self.game_state = GameState.CODING

    def update(self):
        self.player.update_movement()
        self.player.update()

    def is_valid_move(self, pos_pixels):
        pos_pixels_x, pos_pixels_y = pos_pixels
        pos_x = pos_pixels_x // TILE_SIZE
        pos_y = pos_pixels_y // TILE_SIZE

        if not (0 <= pos_y < len(self.tile_map) and 0 <= pos_x < len(self.tile_map[0])):
            return False

        tile_id = self.tile_map[pos_y][pos_x]
        return tile_id in self.walkable_tiles
