from . import player


class GameState:
    CODING = "CODING"
    EXECUTING = "EXECUTING"


class GameModel:
    def __init__(self):
        self.objective_text = None
        self.player = None
        self.tile_map = []
        self.walkable_tiles = {9, 10}

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

    def add_action_to_sequence(self, action):
        if self.game_state == GameState.CODING and action in self.available_actions:
            self.actions_sequence.append(action)

    def remove_action_from_sequence(self, index):
        if self.game_state == GameState.CODING and 0 <= index < len(self.actions_sequence):
            self.actions_sequence.pop(index)

    def start_execution(self):
        if self.game_state == GameState.CODING and self.actions_sequence:
            self.game_state = GameState.EXECUTING

    def reset_sequence(self):
        self.actions_sequence.clear()
        self.game_state = GameState.CODING

    def process_next_action(self):
        if self.game_state != GameState.EXECUTING or not self.actions_sequence:
            self.game_state = GameState.CODING
            return

        action = self.actions_sequence.pop(0)

        if action == "WALK":
            next_pos = self.player.get_next_pos()
            if self.is_valid_move(next_pos):
                self.player.move()
        elif action == "LEFT":
            self.player.turn_left()
        elif action == "RIGHT":
            self.player.turn_right()

    def update(self):
        self.player.update_movement()
        self.player.update()

    def is_valid_move(self, pos):
        pos_x, pos_y = pos

        if not (0 <= pos_y < len(self.tile_map) and 0 <= pos_x < len(self.tile_map[0])):
            return False

        tile_id = self.tile_map[pos_y][pos_x]
        return tile_id in self.walkable_tiles
