from abc import abstractmethod, ABC

from src.config import TILE_SIZE


class Command(ABC):
    @abstractmethod
    def execute(self, model):
        pass

class WalkCommand(Command):
    action_name = "ANDAR"
    def execute(self, game_model):
        next_tile_pos_x, next_tile_pos_y = game_model.player.get_next_tile_pos()

        if game_model.is_valid_move((next_tile_pos_x, next_tile_pos_y)):
            game_model.player.set_next_move()
            game_model.remove_action_from_sequence(0)

class TurnLeftCommand(Command):
    action_name = "VIRAR_ESQUERDA"
    def execute(self, game_model):
        player = game_model.player
        if not player.is_moving:
            player.direction_index = (player.direction_index + 1) % len(player.directions)
            game_model.remove_action_from_sequence(0)

class TurnRightCommand(Command):
    action_name = "VIRAR_DIREITA"
    def execute(self, game_model):
        player = game_model.player
        if not player.is_moving:
            player.direction_index = (player.direction_index - 1 + len(player.directions)) % len(player.directions)
            game_model.remove_action_from_sequence(0)