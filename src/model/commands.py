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
    def __init__(self, repeat_count=1):
        self.action_name = "REPEAT"
        self.repeat_count = repeat_count
        self.command_list = []

        self._command_index = 0
        self._current_repeat = 0
        self._is_finished = False

    def execute(self, game_model):
        if self.is_finished:
            return

        if self.repeat_count <= 0:
            next_end_repeat_index = -1
            for i, command in enumerate(game_model.actions_sequence[game_model.current_action_index:]):
                if type(command) == EndRepeatCommand:
                    command.is_finished = False
                    next_end_repeat_index = i
                self.repeat_count -= 1
            game_model.current_action_index = 0

        self.is_finished = True

        # if self._is_finished or not self.command_list or self.repeat_count <= 0:
        #     return

        # current_command = self.command_list[self._command_index]
        # current_command.execute(self, game_model)
        #
        # if current_command.is_finished:
        #     self._command_index += 1
        #
        #     if self._command_index >= len(self.command_list):
        #         self._command_index = 0
        #
        #     if self.repeat_count <= 0:
        #         self._is_finished = True

    def is_finished(self):
        return self._is_finished

class EndRepeatCommand(Command):
    action_name = "END_REPEAT"

    def execute(self, game_model):
        actions_sequence = game_model.actions_sequence
        end_repeat_index = game_model.current_action_index
        for i in range(end_repeat_index, -1, -1):
            if type(actions_sequence[i]) == RepeatCommand:
                last_repeat_command = actions_sequence[i]
                if last_repeat_command.repeat_count > 0:
                    for command in actions_sequence[i:end_repeat_index]:
                        command.is_finished = False
                    game_model.current_action_index = i+1
                else:
                    game_model.current_action_index = end_repeat_index
        self.is_finished = True