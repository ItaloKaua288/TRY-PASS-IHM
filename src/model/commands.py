from abc import abstractmethod, ABC

class Command(ABC):
    is_finished = False
    is_executing = False
    @abstractmethod
    def execute(self, model):
        pass


class WalkCommand(Command):
    action_name = "WALK"
    def execute(self, game_model):
        next_tile_pos_x, next_tile_pos_y = game_model.player.get_next_tile_pos()

        if game_model.is_valid_move((next_tile_pos_x, next_tile_pos_y)):
            game_model.player.set_next_move()
        self.is_finished = True


class TurnLeftCommand(Command):
    action_name = "TURN_LEFT"
    def execute(self, game_model):
        player = game_model.player
        if player.is_rotating:
            player.update()
        elif not player.is_moving:
            player.direction_index = (player.direction_index - 1) % len(player.directions)
            player.is_rotating = True
            player.direction_rotate = -1
            self.is_finished = True


class TurnRightCommand(Command):
    action_name = "TURN_RIGHT"
    def execute(self, game_model):
        player = game_model.player
        if player.is_rotating:
            player.update()
        elif not player.is_moving:
            player.direction_index = (player.direction_index + 1) % len(player.directions)
            player.is_rotating = True
            player.direction_rotate = 1
            self.is_finished = True

class RepeatCommand(Command):
    def __init__(self, repeat_num=1):
        self.action_name = "REPEAT"
        self.repeat_num = repeat_num
        self.command_list = []

        self._command_index = 0
        self._current_repeat = 0
        self._is_finished = False

    def execute(self, game_model):
        if self._is_finished or not self.command_list:
            return

        current_command = self.command_list[self._command_index]
        current_command.execute(self, game_model)

        if current_command.is_finished:
            self._command_index += 1

            if self._command_index >= len(self.command_list):
                self._current_repeat += 1
                self._command_index = 0

            if self._current_repeat >= self.repeat_num:
                self._is_finished = True

    def is_finished(self):
        return self._is_finished

class EndRepeatCommand(Command):
    action_name = "END_REPEAT"

    def execute(self, game_model):
        ...