import pygame

from src.config import TILE_SIZE
from src.model.commands import WalkCommand, TurnLeftCommand, TurnRightCommand, RepeatCommand, EndRepeatCommand
from src.model.game_model import GameState


class GameController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.tile_size = (TILE_SIZE, TILE_SIZE)

        start_tile_pos = model.player.target_pos
        start_pixel_pos = (start_tile_pos[0] * self.tile_size[0], start_tile_pos[1] * self.tile_size[1])
        self.model.player.rect.topleft = start_pixel_pos

        self._setup_init()

    def _setup_init(self):
        self.model.player.transform_size(self.tile_size)

    def update_elements(self, mouse_pos):
        self.model.update()
        self.view.update(mouse_pos)

    def handle_events(self, events, mouse_pos):
        if self.model.game_state == GameState.EXECUTING and not self.model.player.is_moving:
            self.model.actions_sequence.pop(0).execute(self.model)

            if len(self.model.actions_sequence) == 0:
                self.model.game_state = GameState.CODING
        else:
            for event in events:
                if event.type == pygame.KEYDOWN and not self.model.player.is_moving:
                    if event.key == pygame.K_a:
                        turnrightcommand = TurnRightCommand()
                        turnrightcommand.execute(self.model)
                    elif event.key == pygame.K_d:
                        turnleftcommand = TurnLeftCommand()
                        turnleftcommand.execute(self.model)
                    elif event.key == pygame.K_w:
                        walkcommand = WalkCommand()
                        walkcommand.execute(self.model)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.view.buttons["inventory"].rect.collidepoint(mouse_pos):
                        self._view_button_handler()
                    elif self.view.panels["top_bar"].rect.collidepoint(mouse_pos):
                        self._top_bar_handler()
                    elif self.view.panels["tools"].rect.collidepoint(mouse_pos):
                        self._tools_handler()
                    elif self.view.panels["execution"].rect.collidepoint(mouse_pos):
                        self._execute_handler(mouse_pos)

    def _view_button_handler(self):
        button = self.view.buttons["inventory"]
        if button.is_hovered:
            inventory_panel = self.view.panels["inventory"]
            if inventory_panel.is_visible:
                inventory_panel.is_visible = False
            else:
                inventory_panel.is_visible = True

    def _top_bar_handler(self):
        buttons = self.view.panels["top_bar"].buttons

        for key, button in buttons.items():
            if button.is_hovered:
                match key:
                    case "options":
                        print("Options")
                    case "idea":
                        print("Idea")
                    case "music_note":
                        print("Music note")

    def _tools_handler(self):
        buttons = self.view.panels["tools"].buttons

        for key, button in buttons.items():
            if button.is_hovered:
                match key:
                    case "walk":
                        self.model.add_action_to_sequence(WalkCommand())
                    case "turn_left":
                        self.model.add_action_to_sequence(TurnLeftCommand())
                    case "turn_right":
                        self.model.add_action_to_sequence(TurnRightCommand())
                    case "repeat":
                        self.model.add_action_to_sequence(RepeatCommand())
                        self.model.add_action_to_sequence(EndRepeatCommand())

    def _execute_handler(self, mouse_pos):
        buttons = self.view.panels["execution"].buttons
        actions_buttons = self.view.panels["execution"].buttons_sequence

        mouse_pos = (mouse_pos[0] - self.view.panels["execution"].rect.x + 10, mouse_pos[1] - self.view.panels["execution"].rect.y)

        for i, button in enumerate(actions_buttons):
            button.update(mouse_pos)
            if button.is_hovered:
                self.model.remove_action_from_sequence(i)

                if button.name.lower() == "repeat":
                    self.model.remove_action_from_sequence(i)
                elif button.name.lower() == "end_repeat":
                    self.model.remove_action_from_sequence(i - 1)

        for key, button in buttons.items():
            if button.is_hovered:
                match key:
                    case "execute":
                        self.model.start_execution()
