import pygame

from src.config import TILE_SIZE
from src.model.commands import WalkCommand, TurnLeftCommand, TurnRightCommand, RepeatCommand, EndRepeatCommand
from src.model.game_model import GameState
from src.config import GameStateMap

COMMAND_MAP = {
    "walk": WalkCommand,
    "turn_left": TurnLeftCommand,
    "turn_right": TurnRightCommand,
    "repeat": RepeatCommand,
    "end_repeat": EndRepeatCommand,
}

class GameController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.is_dragging = False
        self.dragged_command_index = None

        self._initialize_player_position()

    def _initialize_player_position(self):
        start_tile_pos = self.model.player.target_pos
        pixel_pos = (start_tile_pos[0] * TILE_SIZE, start_tile_pos[1] * TILE_SIZE)
        self.model.player.rect.topleft = pixel_pos

    def run_game(self, mouse_pos):
        if self.model.game_state == GameState.EXECUTING and not self.model.player.is_moving:

            for i, action in enumerate(self.model.actions_sequence):
                if action.is_finished:
                    continue
                else:
                    self.model.current_action_index = i
                    action.execute(self.model)
                    return

            self.model.reset_sequence()
            self.model.game_state = GameState.CODING

        self.model.update()

        self.view.update(mouse_pos)

    def handle_events(self, events, game_model, game_state_manager):
        mouse_pos = pygame.mouse.get_pos()

        if self.model.game_state == GameState.EXECUTING:
            return

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_mouse_down(mouse_pos, game_model, game_state_manager)

            if event.type == pygame.MOUSEMOTION and self.is_dragging:
                self.view.panels["execution"].update_drag(mouse_pos)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self._handle_mouse_up(mouse_pos, game_model)

    def _handle_mouse_down(self, mouse_pos, game_model, game_state_manager):
        for key, panel in self.view.panels.items():
            if panel.rect.collidepoint(mouse_pos):
                if key == "tools":
                    self._handle_tools_panel_click()
                elif key == "execution":
                    self._handle_execution_panel_click(mouse_pos, game_model)
                elif key == "top_bar":
                    self._handle_top_bar_panel_click(game_state_manager)
                return

    def _handle_mouse_up(self, mouse_pos, game_model):
        if self.is_dragging:
            execution_panel = self.view.panels["execution"]
            target_slot_index = execution_panel.get_slot_index(mouse_pos)

            if target_slot_index is not None and self.dragged_command_index is not None:
                self.model.change_command_slot(self.dragged_command_index, target_slot_index)

            self.is_dragging = False
            self.dragged_command_index = None
            execution_panel.stop_drag(mouse_pos, game_model)

    def _toggle_inventory_visibility(self):
        inventory_panel = self.view.panels["inventory"]
        inventory_panel.is_visible = not inventory_panel.is_visible

    def _handle_top_bar_panel_click(self, game_state_manager):
        topbar_panel = self.view.panels["top_bar"]

        for key, button in topbar_panel.buttons.items():
            if button.is_hovered:
                if key == "options":
                    game_state_manager.current_game_state = GameStateMap.MAIN_MENU
                elif key == "inventory":
                    self._toggle_inventory_visibility()
                else:
                    print(key)

    def _handle_tools_panel_click(self):
        tools_panel = self.view.panels["tools"]

        for key, button in tools_panel.buttons.items():
            if button.is_hovered:
                if command_class := COMMAND_MAP.get(key):
                    self.model.add_action_to_sequence(command_class())
                    return

    def _handle_execution_panel_click(self, mouse_pos, game_model):
        execution_panel = self.view.panels["execution"]

        if execution_panel.buttons["execute"].is_hovered:
            self.model.start_execution()
            return
        if execution_panel.buttons["clear"].is_hovered:
            self.model.clear_sequence()
            return

        clicked_info = execution_panel.get_clicked_command_info(mouse_pos)
        if clicked_info:
            index, action_type = clicked_info["index"], clicked_info["action"]
            if action_type == "cancel_button":
                self.model.remove_action_from_sequence(index)
            else:
                self.is_dragging = True
                self.dragged_command_index = index
                execution_panel.start_drag(index, mouse_pos, game_model)
