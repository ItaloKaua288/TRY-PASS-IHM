import pygame

from src.config import TILE_SIZE
from src.model.commands import WalkCommand, TurnLeftCommand, TurnRightCommand, RepeatCommand, EndRepeatCommand
from src.model.game_model import GameState
from src.config import GameStateMap
from src.model.items import Chest

COMMAND_MAP = {
    "walk": WalkCommand,
    "turn_left": TurnLeftCommand,
    "turn_right": TurnRightCommand,
    "repeat": RepeatCommand,
    "end_repeat": EndRepeatCommand,
}

class GameController:
    def __init__(self, model, view, game_manager):
        self.model = model
        self.view = view
        self.game_manager = game_manager

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
                    map_panel = self.view.panels["map"]
                    player_rect = map_panel.get_player_rect_updated(self.model.player.rect)
                    for key, map_items_rect in map_panel.get_interactable_rect_list_updated().items():
                        for j, map_item_rect in enumerate(map_items_rect):
                            if player_rect.colliderect(map_item_rect):
                                self._handle_map_item_interacted(key, j)
                else:
                    self.model.current_action_index = i
                    action.execute(self.model)
                    return

            self.model.reset_sequence()
            self.model.game_state = GameState.CODING

        self.model.update()

        self.view.update(mouse_pos)

    def _handle_map_item_interacted(self, key, item_list_pos):
        if self.model.is_victory():
            self.game_manager.current_game_state = GameStateMap.MAIN_MENU
            return

        map_item = self.model.interactable_objects[key][item_list_pos]
        if map_item.is_interacted:
            return
        player_inventory = self.model.player.inventory

        if isinstance(map_item, Chest):
            for item in map_item.internal_items:
                player_inventory.add_item(item)
        map_item.is_interacted = True

    def collect_map_item(self, key, map_item_rect):
        pass

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
                if key == "top_bar":
                    self._handle_top_bar_panel_click(game_state_manager)
                elif self.view.panels["inventory"].is_visible:
                    self._handle_inventory_panel(mouse_pos)
                else:
                    if key == "tools":
                        self._handle_tools_panel_click()
                    elif key == "execution":
                        self._handle_execution_panel_click(mouse_pos, game_model)
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

    def _handle_inventory_panel(self, mouse_pos):
        player_inventory = self.model.player.inventory
        inventory_panel = self.view.panels["inventory"]

        for i, item in enumerate(player_inventory.items):
            if inventory_panel.get_slot_rect_hovered(mouse_pos) == i:
                if self.model.player.item_hand == item:
                    self.model.player.item_hand = None
                else:
                    self.model.player.item_hand = item
            if item.is_used:
                player_inventory.remove_item(item)