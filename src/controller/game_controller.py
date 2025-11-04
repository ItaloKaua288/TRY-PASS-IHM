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

HOLD_THRESHOLD_MS = 200

class GameController:
    def __init__(self, view, game_manager):
        self.view = view
        self.game_manager = game_manager

        self.is_dragging = False
        self.dragged_command_index = None

        self.mouse_down_time = 0
        self.mouse_down_pos = (0, 0)
        self.hold_action_triggered = False

        self._initialize_player_position()

    def _initialize_player_position(self):
        start_tile_pos = self.game_manager.game_model.player.target_pos
        pixel_pos = (start_tile_pos[0] * TILE_SIZE, start_tile_pos[1] * TILE_SIZE)
        self.game_manager.game_model.player.rect.topleft = pixel_pos

    def run_game(self, mouse_pos):
        game_model = self.game_manager.game_model

        self._update_hold_state()

        if game_model.game_state == GameState.EXECUTING and not game_model.player.is_moving:
            for i, action in enumerate(game_model.actions_sequence):
                if action.is_finished:
                    map_panel = self.view.panels["map"]
                    player_rect = map_panel.get_player_rect_updated(game_model.player.rect)
                    for key, map_items_rect in map_panel.get_interactable_rect_list_updated().items():
                        for j, map_item_rect in enumerate(map_items_rect):
                            if player_rect.colliderect(map_item_rect):
                                self._handle_map_item_interacted(key, j)
                else:
                    game_model.current_action_index = i
                    action.execute(game_model)
                    return

            game_model.reset_sequence()
            game_model.game_state = GameState.CODING

        game_model.update()

        self.view.update(mouse_pos)

    def _handle_map_item_interacted(self, key, item_list_pos):
        game_model = self.game_manager.game_model
        if game_model.is_victory():
            self.game_manager.current_game_state = GameStateMap.MAIN_MENU
            return

        map_item = game_model.interactable_objects[key][item_list_pos]
        if map_item.is_interacted:
            return
        player_inventory = game_model.player.inventory

        if isinstance(map_item, Chest):
            for item in map_item.internal_items:
                player_inventory.add_item(item)
        map_item.is_interacted = True

    def collect_map_item(self, key, map_item_rect):
        pass

    def handle_events(self, events, game_model):
        mouse_pos = pygame.mouse.get_pos()
        game_model = self.game_manager.game_model

        if game_model.game_state == GameState.EXECUTING:
            return

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.mouse_down_time = pygame.time.get_ticks()
                self.mouse_down_pos = mouse_pos
                self.hold_action_triggered = False

            if event.type == pygame.MOUSEMOTION and self.is_dragging:
                self.view.panels["execution"].update_drag(mouse_pos)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.is_dragging:
                    self._handle_drag_drop(mouse_pos)
                elif self.hold_action_triggered:
                    pass
                else:
                    self._handle_simple_click(mouse_pos)

                self.mouse_down_time = 0
                self.hold_action_triggered = False
                # self._handle_mouse_up(mouse_pos)

    def _handle_mouse_down(self, mouse_pos):
        for key, panel in self.view.panels.items():
            if panel.rect.collidepoint(mouse_pos):
                if key == "top_bar":
                    self._handle_top_bar_panel_click()
                elif self.view.panels["inventory"].is_visible:
                    self._handle_inventory_panel(mouse_pos)
                else:
                    if key == "tools":
                        self._handle_tools_panel_click()
                    elif key == "execution":
                        self._handle_execution_panel_click(mouse_pos)
                return

    def _handle_mouse_up(self, mouse_pos):
        if self.is_dragging:
            execution_panel = self.view.panels["execution"]
            target_slot_index = execution_panel.get_slot_index(mouse_pos)

            if target_slot_index is not None and self.dragged_command_index is not None:
                self.game_manager.game_model.change_command_slot(self.dragged_command_index, target_slot_index)

            self.is_dragging = False
            self.dragged_command_index = None
            execution_panel.stop_drag(mouse_pos)

    def _update_hold_state(self):
        if self.mouse_down_time == 0 or self.hold_action_triggered or self.is_dragging:
            return
        duration = pygame.time.get_ticks() - self.mouse_down_time
        if duration > HOLD_THRESHOLD_MS:
            self.hold_action_triggered = True
            self._handle_hold_action(self.mouse_down_pos)

    def _handle_hold_action(self, mouse_pos):
        execution_panel = self.view.panels["execution"]
        if execution_panel.rect.collidepoint(mouse_pos):
            clicked_info = execution_panel.get_clicked_command_info(mouse_pos)

            if clicked_info and clicked_info["action"] != "cancel_button":
                self.is_dragging = True
                self.dragged_command_index = clicked_info["index"]
                execution_panel.start_drag(clicked_info["index"], mouse_pos)

    def _handle_simple_click(self, mouse_pos):
        if self.view.panels["repeat_config"].is_visible:
            self._handle_repeat_config_click(mouse_pos)
            return
        elif self.view.panels["inventory"].is_visible:
            self._handle_inventory_panel(mouse_pos)
            # Verifica se o clique foi no painel de inventário
            if self.view.panels["inventory"].rect.collidepoint(mouse_pos):
                return  # Clique foi dentro do inventário, não faça mais nada
            # Se não, continua para checar outros botões (como o de fechar)

            # Lógica de clique normal
        for key, panel in self.view.panels.items():
            if panel.rect.collidepoint(mouse_pos):
                if key == "top_bar":
                    self._handle_top_bar_panel_click()
                elif key == "tools":
                    self._handle_tools_panel_click()
                elif key == "execution":
                    self._handle_execution_panel_click(mouse_pos)
                return
        # for key, panel in self.view.panels.items():
        #     if panel.rect.collidepoint(mouse_pos):
        #         if key == "top_bar":
        #             self._handle_top_bar_panel_click()
        #         elif self.view.panels["inventory"].is_visible:
        #             self._handle_inventory_panel(mouse_pos)
        #         else:
        #             if key == "tools":
        #                 self._handle_tools_panel_click()
        #             elif key == "execution":
        #                 self._handle_execution_panel_click(mouse_pos)
        #         return

    def _handle_repeat_config_click(self, mouse_pos):
        """Lida com cliques dentro do painel de configuração de repetição."""
        panel = self.view.panels["repeat_config"]
        clicked_button = panel.get_clicked_button(mouse_pos)
        print(clicked_button)

        if clicked_button == "plus":
            panel.current_count += 1
        elif clicked_button == "minus":
            panel.current_count = max(1, panel.current_count - 1)  # Não permite 0 ou negativo
        elif clicked_button == "ok":
            # Ação principal: Atualiza o Model
            command_index = panel.target_command_index
            new_count = panel.current_count

            if command_index is not None:
                command = self.game_manager.game_model.actions_sequence[command_index]
                # print(command)
                if isinstance(command, RepeatCommand):
                    command.repeat_count = new_count

            panel.close_panel()
        elif not panel.rect.collidepoint(mouse_pos):
            # Clicar fora do painel também o fecha (como um "cancelar")
            panel.close_panel()
            pass

    def _handle_drag_drop(self, mouse_pos):
        if self.is_dragging:
            execution_panel = self.view.panels["execution"]
            target_slot_index = execution_panel.get_slot_index(mouse_pos)

            if target_slot_index is not None and self.dragged_command_index is not None:
                self.game_manager.game_model.change_command_slot(self.dragged_command_index, target_slot_index)

            self.is_dragging = False
            self.dragged_command_index = None
            execution_panel.stop_drag(mouse_pos)

    def _toggle_inventory_visibility(self):
        inventory_panel = self.view.panels["inventory"]
        inventory_panel.is_visible = not inventory_panel.is_visible

    def _handle_top_bar_panel_click(self):
        topbar_panel = self.view.panels["top_bar"]
        for key, button in topbar_panel.buttons.items():
            if button.is_hovered:
                if key == "options":
                    self.game_manager.current_game_state = GameStateMap.MAIN_MENU
                elif key == "inventory":
                    self._toggle_inventory_visibility()
                else:
                    print(key)

    def _handle_tools_panel_click(self):
        tools_panel = self.view.panels["tools"]

        for key, button in tools_panel.buttons.items():
            if button.is_hovered:
                if command_class := COMMAND_MAP.get(key):
                    self.game_manager.game_model.add_action_to_sequence(command_class())
                    return

    def _handle_execution_panel_click(self, mouse_pos):
        execution_panel = self.view.panels["execution"]
        game_model = self.game_manager.game_model

        if execution_panel.buttons["execute"].is_hovered:
            game_model.start_execution()
            return
        if execution_panel.buttons["clear"].is_hovered:
            game_model.clear_sequence()
            return

        clicked_info = execution_panel.get_clicked_command_info(mouse_pos)
        if clicked_info:
            index, action_type = clicked_info["index"], clicked_info["action"]
            if action_type == "cancel_button":
                game_model.remove_action_from_sequence(index)
            elif action_type == "REPEAT":
                self.view.panels["repeat_config"].open_for_command(index, 1)

    def _handle_inventory_panel(self, mouse_pos):
        game_model = self.game_manager.game_model
        player_inventory = game_model.player.inventory
        inventory_panel = self.view.panels["inventory"]

        for i, item in enumerate(player_inventory.items):
            if inventory_panel.get_slot_rect_hovered(mouse_pos) == i:
                if game_model.player.item_hand == item:
                    game_model.player.item_hand = None
                else:
                    game_model.player.item_hand = item
            if item.is_used:
                player_inventory.remove_item(item)


# import pygame
#
# from src.config import TILE_SIZE
# from src.model.commands import WalkCommand, TurnLeftCommand, TurnRightCommand, RepeatCommand, EndRepeatCommand
# from src.model.game_model import GameState
# from src.config import GameStateMap
# from src.model.items import Chest
#
# COMMAND_MAP = {
#     "walk": WalkCommand,
#     "turn_left": TurnLeftCommand,
#     "turn_right": TurnRightCommand,
#     "repeat": RepeatCommand,
#     "end_repeat": EndRepeatCommand,
# }
#
# class GameController:
#     def __init__(self, view, game_manager):
#         self.view = view
#         self.game_manager = game_manager
#
#         self.is_dragging = False
#         self.dragged_command_index = None
#
#         self._initialize_player_position()
#
#     def _initialize_player_position(self):
#         start_tile_pos = self.game_manager.game_model.player.target_pos
#         pixel_pos = (start_tile_pos[0] * TILE_SIZE, start_tile_pos[1] * TILE_SIZE)
#         self.game_manager.game_model.player.rect.topleft = pixel_pos
#
#     def run_game(self, mouse_pos):
#         game_model = self.game_manager.game_model
#         if game_model.game_state == GameState.EXECUTING and not game_model.player.is_moving:
#             for i, action in enumerate(game_model.actions_sequence):
#                 if action.is_finished:
#                     map_panel = self.view.panels["map"]
#                     player_rect = map_panel.get_player_rect_updated(game_model.player.rect)
#                     for key, map_items_rect in map_panel.get_interactable_rect_list_updated().items():
#                         for j, map_item_rect in enumerate(map_items_rect):
#                             if player_rect.colliderect(map_item_rect):
#                                 self._handle_map_item_interacted(key, j)
#                 else:
#                     game_model.current_action_index = i
#                     action.execute(game_model)
#                     return
#
#             game_model.reset_sequence()
#             game_model.game_state = GameState.CODING
#
#         game_model.update()
#
#         self.view.update(mouse_pos)
#
#     def _handle_map_item_interacted(self, key, item_list_pos):
#         game_model = self.game_manager.game_model
#         if game_model.is_victory():
#             self.game_manager.current_game_state = GameStateMap.MAIN_MENU
#             return
#
#         map_item = game_model.interactable_objects[key][item_list_pos]
#         if map_item.is_interacted:
#             return
#         player_inventory = game_model.player.inventory
#
#         if isinstance(map_item, Chest):
#             for item in map_item.internal_items:
#                 player_inventory.add_item(item)
#         map_item.is_interacted = True
#
#     def collect_map_item(self, key, map_item_rect):
#         pass
#
#     def handle_events(self, events, game_model):
#         mouse_pos = pygame.mouse.get_pos()
#         game_model = self.game_manager.game_model
#
#         if game_model.game_state == GameState.EXECUTING:
#             return
#
#         for event in events:
#             if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
#                 self._handle_mouse_down(mouse_pos)
#
#             if event.type == pygame.MOUSEMOTION and self.is_dragging:
#                 self.view.panels["execution"].update_drag(mouse_pos)
#
#             if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
#                 self._handle_mouse_up(mouse_pos)
#
#     def _handle_mouse_down(self, mouse_pos):
#         for key, panel in self.view.panels.items():
#             if panel.rect.collidepoint(mouse_pos):
#                 if key == "top_bar":
#                     self._handle_top_bar_panel_click()
#                 elif self.view.panels["inventory"].is_visible:
#                     self._handle_inventory_panel(mouse_pos)
#                 else:
#                     if key == "tools":
#                         self._handle_tools_panel_click()
#                     elif key == "execution":
#                         self._handle_execution_panel_click(mouse_pos)
#                 return
#
#     def _handle_mouse_up(self, mouse_pos):
#         if self.is_dragging:
#             execution_panel = self.view.panels["execution"]
#             target_slot_index = execution_panel.get_slot_index(mouse_pos)
#
#             if target_slot_index is not None and self.dragged_command_index is not None:
#                 self.game_manager.game_model.change_command_slot(self.dragged_command_index, target_slot_index)
#
#             self.is_dragging = False
#             self.dragged_command_index = None
#             execution_panel.stop_drag(mouse_pos)
#
#     def _toggle_inventory_visibility(self):
#         inventory_panel = self.view.panels["inventory"]
#         inventory_panel.is_visible = not inventory_panel.is_visible
#
#     def _handle_top_bar_panel_click(self):
#         topbar_panel = self.view.panels["top_bar"]
#         for key, button in topbar_panel.buttons.items():
#             if button.is_hovered:
#                 if key == "options":
#                     self.game_manager.current_game_state = GameStateMap.MAIN_MENU
#                 elif key == "inventory":
#                     self._toggle_inventory_visibility()
#                 else:
#                     print(key)
#
#     def _handle_tools_panel_click(self):
#         tools_panel = self.view.panels["tools"]
#
#         for key, button in tools_panel.buttons.items():
#             if button.is_hovered:
#                 if command_class := COMMAND_MAP.get(key):
#                     self.game_manager.game_model.add_action_to_sequence(command_class())
#                     return
#
#     def _handle_execution_panel_click(self, mouse_pos):
#         execution_panel = self.view.panels["execution"]
#         game_model = self.game_manager.game_model
#
#         if execution_panel.buttons["execute"].is_hovered:
#             game_model.start_execution()
#             return
#         if execution_panel.buttons["clear"].is_hovered:
#             game_model.clear_sequence()
#             return
#
#         clicked_info = execution_panel.get_clicked_command_info(mouse_pos)
#         if clicked_info:
#             index, action_type = clicked_info["index"], clicked_info["action"]
#             if action_type == "cancel_button":
#                 game_model.remove_action_from_sequence(index)
#             else:
#                 self.is_dragging = True
#                 self.dragged_command_index = index
#                 execution_panel.start_drag(index, mouse_pos)
#
#     def _handle_inventory_panel(self, mouse_pos):
#         game_model = self.game_manager.game_model
#         player_inventory = game_model.player.inventory
#         inventory_panel = self.view.panels["inventory"]
#
#         for i, item in enumerate(player_inventory.items):
#             if inventory_panel.get_slot_rect_hovered(mouse_pos) == i:
#                 if game_model.player.item_hand == item:
#                     game_model.player.item_hand = None
#                 else:
#                     game_model.player.item_hand = item
#             if item.is_used:
#                 player_inventory.remove_item(item)