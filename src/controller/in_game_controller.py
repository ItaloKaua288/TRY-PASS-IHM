import pygame

from src.utils.settings import GameState
from src.controller.entities_controller import DefaultEntityController

HOLD_THRESHOLD_MS = 200


class GameController:
    def __init__(self, in_game_view, game_model):
        self.view = in_game_view
        self.game_model = game_model

        self.game_is_paused = False
        self.is_executing = False

        self.player_controller = DefaultEntityController(self.game_model.player, self.game_model)
        self.enemies = [DefaultEntityController(enemy, self.game_model) for enemy in self.game_model.enemies]

        self.mouse_down_time = 0
        self.mouse_down_pos = (0, 0)
        self.hold_action_triggered = False
        self.is_dragging = False
        self.dragged_command_index = None

        self.command_execution_index = 0
        self.command_interpreter = CommandInterpreter()
        self.execution_interpreted_queue = []

    def update(self, events):
        """
        Atualiza a lógica do jogo a cada frame.
        Retorna: O próximo GameState (ou None se não mudar).
        """
        next_state = None

        state_from_events = self.__handle_events(events)

        self.view.update(self.game_is_paused)

        if self.game_is_paused:
            return state_from_events

        if state_from_events:
            next_state = state_from_events

        if self.is_executing:
            execution_state = self.__update_execution()
            if execution_state:
                next_state = execution_state

        self.player_controller.update()
        self.__enemies_update()

        death_state = self.__interact_enemy_map()
        if death_state:
            next_state = death_state

        return next_state

    def draw(self):
        self.view.draw()

    def __handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            if event.type == pygame.QUIT:
                return GameState.QUIT

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.is_dragging:
                    self.__stop_dragging(mouse_pos)
                else:
                    self.mouse_down_time = pygame.time.get_ticks()
                    self.mouse_down_pos = mouse_pos
                    self.hold_action_triggered = False

                    if not self.view.panels["execution_bar"]["config_repeat"]["rect"].collidepoint(mouse_pos):
                        self.view.panels["execution_bar"]["config_repeat"]["is_visible"] = False

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.__update_hold_state()

                if self.view.panels["pause_menu"]["is_visible"] and self.view.panels["pause_menu"]["menu_rect"].collidepoint(mouse_pos):
                    return self.__handle_pause_menu(mouse_pos)
                elif self.view.panels["top_bar"]["rect"].collidepoint(mouse_pos):
                    local_pos = (mouse_pos[0] - self.view.panels["top_bar"]["rect"].x, mouse_pos[1] - self.view.panels["top_bar"]["rect"].y)
                    return self.__handle_top_bar(local_pos)
                elif self.game_is_paused:
                    return None
                elif self.view.panels["inventory_bar"]["is_visible"]:
                    local_pos = (mouse_pos[0] - self.view.panels["inventory_bar"]["rect"].x, mouse_pos[1] - self.view.panels["inventory_bar"]["rect"].y)
                    self.__handle_inventory_bar(local_pos)
                else:
                    for key, panel in self.view.panels.items():
                        if panel["rect"].collidepoint(mouse_pos):
                            local_pos = (mouse_pos[0] - panel["rect"].x, mouse_pos[1] - panel["rect"].y)
                            if key == "tools_bar":
                                self.__handle_tools_bar(local_pos)
                            elif key == "execution_bar":
                                self.__handle_execution_bar(local_pos)
                            elif key == "status_bar":
                                self.__handle_status_bar(local_pos)
                            break
        return None

    def __update_hold_state(self):
        if self.mouse_down_time == 0 or self.hold_action_triggered or self.is_dragging:
            return

        duration = pygame.time.get_ticks() - self.mouse_down_time

        if duration > HOLD_THRESHOLD_MS:
            self.hold_action_triggered = True
            panel = self.view.panels["execution_bar"]
            if panel["rect"].collidepoint(self.mouse_down_pos):
                clicked_command = self.view.get_clicked_command_info(self.mouse_down_pos)

                if clicked_command is not None:
                    index, command = clicked_command.values()
                    if command is not None and not command["buttons"]["remove"]["is_hovered"]:
                        self.is_dragging = True
                        self.dragged_command_index = index

                        if 0 <= index < len(self.game_model.execution_queue):
                            self.is_dragging = True
                            cmd_type = self.game_model.remove_execution_command(index)[0]
                            self.view.dragged_command = {"index": index, "type": cmd_type, "command": command}

        self.mouse_down_time = 0
        self.hold_action_triggered = False

    def __stop_dragging(self, mouse_pos):
        target_new_slot_index = self.view.get_execution_command_slot_index_hovered(mouse_pos)
        self.game_model.add_execution_command(self.view.dragged_command["type"], index=target_new_slot_index)
        self.view.dragged_command = {"type": None, "index": None, "command": None}
        self.is_dragging = False

    def __handle_top_bar(self, mouse_pos):
        for key, button in self.view.panels["top_bar"]["buttons"].items():
            if button["rect"].collidepoint(mouse_pos):
                if not self.view.panels["pause_menu"]["is_visible"]:
                    if key == "options":
                        pause_menu = self.view.panels["pause_menu"]
                        pause_menu["is_visible"] = not pause_menu["is_visible"]
                        self.game_is_paused = pause_menu["is_visible"]
                    elif key == "idea":
                        help_menu = self.view.panels["help_menu"]
                        help_menu["is_visible"] = not help_menu["is_visible"]
                    elif key == "inventory" and not self.view.panels["pause_menu"]["is_visible"]:
                        self.view.panels["inventory_bar"]["is_visible"] = not self.view.panels["inventory_bar"]["is_visible"]
                        self.game_is_paused = self.view.panels["inventory_bar"]["is_visible"]
                return None
        return None

    def __handle_pause_menu(self, mouse_pos):
        pause_menu = self.view.panels["pause_menu"]

        for key, button in pause_menu["buttons"].items():
            if button["rect"].collidepoint(mouse_pos):
                if key == "Continuar":
                    pause_menu["is_visible"] = False
                    self.game_is_paused = False
                elif key == "Novo Jogo":
                    return GameState.NEW_GAME
                elif key == "Selecionar Fase":
                    return GameState.LEVEL_SELECT
                elif key == "Voltar ao Inicio":
                    return GameState.MAIN_MENU
                elif key == "Sair":
                    return GameState.QUIT
                return None
        return None

    def __handle_inventory_bar(self, mouse_pos):
        panel = self.view.panels["inventory_bar"]
        player_inventory = self.game_model.player.inventory

        if panel["rect"].collidepoint(mouse_pos):
            for i, slot_rect in enumerate(panel["slot_rects"]):
                if slot_rect.collidepoint(mouse_pos):
                    try:
                        key = panel["inventory_items"][i]
                        if player_inventory.handing_item is not None:
                            current_key = list(player_inventory.handing_item.keys())[0]
                            player_inventory.add_item(current_key)

                        player_inventory.handing_item = {key: 1}
                        player_inventory.remove_item(key)
                    except IndexError:
                        pass
                    return

    def __handle_execution_bar(self, mouse_pos):
        if self.is_executing: return

        panel = self.view.panels["execution_bar"]

        if panel["config_repeat"]["is_visible"]:
            for key, button in panel["config_repeat"]["buttons"].items():
                if button["is_hovered"]:
                    if key == "back":
                        if panel["config_repeat"]["repeat_num"] > 1:
                            panel["config_repeat"]["repeat_num"] -= 1
                    elif key == "forward":
                        panel["config_repeat"]["repeat_num"] += 1
                    else:
                        cmd_idx = panel["config_repeat"]["command_index"]
                        self.game_model.execution_queue[cmd_idx][1] = panel["config_repeat"]["repeat_num"]
                        panel["config_repeat"]["is_visible"] = False
                        panel["config_repeat"]["command_index"] = None
                    return
            return

        for i, slot_rect in enumerate(panel["slot_rects"]):
            if slot_rect.collidepoint(mouse_pos):
                try:
                    button = self.view.execution_commands_queue[i]
                    if button["buttons"]["remove"]["rect"].collidepoint(mouse_pos):
                        self.game_model.remove_execution_command(i)
                    else:
                        if self.game_model.execution_queue[i][0] == "repeat":
                            panel["config_repeat"]["is_visible"] = True
                            panel["config_repeat"]["repeat_num"] = self.game_model.execution_queue[i][1]

                            global_mouse = pygame.mouse.get_pos()
                            panel["config_repeat"]["rect"].topleft = (global_mouse[0], global_mouse[1] - panel["config_repeat"]["rect"].height // 2)
                            panel["config_repeat"]["command_index"] = i
                except IndexError:
                    pass
                return

        for key, button in self.view.panels["execution_bar"]["buttons"].items():
            if button["rect"].collidepoint(mouse_pos):
                if key == "play":
                    self.execution_interpreted_queue = self.command_interpreter.create_sequence_execution(self.game_model.execution_queue)
                    self.is_executing = True
                elif key == "clear":
                    self.execution_interpreted_queue.clear()
                    self.game_model.clear_execution_commands()
                return

    def __handle_tools_bar(self, mouse_pos):
        panel = self.view.panels["tools_bar"]
        for key, button in panel["buttons"].items():
            if button["rect"].collidepoint(mouse_pos):
                if key == "repeat":
                    self.game_model.add_execution_command(key, 2)
                else:
                    self.game_model.add_execution_command(key)
                return

    def __handle_status_bar(self, mouse_pos):
        if pygame.Rect(120, 5, 40, 40).collidepoint(mouse_pos):
            player_inv = self.game_model.player.inventory
            if player_inv.handing_item:
                item_name, amount = tuple(player_inv.handing_item.items())[0]
                player_inv.add_item(item_name, amount)
                player_inv.handing_item = None

    def __update_execution(self):
        if self.player_controller.entity.state != "idle":
            return None

        self.__interact_item_map()

        if self.command_execution_index >= len(self.execution_interpreted_queue):
            self.is_executing = False
            self.command_execution_index = 0
            self.view.current_command_executing = None

            return self.__check_victory()

        command_data = self.execution_interpreted_queue[self.command_execution_index]
        cmd_str = command_data["command"]

        if cmd_str == "walk":
            self.player_controller.last_pos = self.player_controller.entity.rect.topleft
            self.player_controller.move()
        elif cmd_str == "turn_left":
            self.player_controller.turn_left()
        elif cmd_str == "turn_right":
            self.player_controller.turn_right()

        self.view.current_command_executing = command_data["index"]
        self.command_execution_index += 1
        return None

    def __check_victory(self):
        final_pos = self.game_model.final_objective_pos
        if self.game_model.player.rect.collidepoint(final_pos):
            self.game_model.current_level += 1
            if self.game_model.current_level >= self.game_model.current_level_unlocked:
                self.game_model.current_level_unlocked += 1
                self.game_model.save_game()
            return GameState.IN_GAME
        return None

    def __interact_item_map(self):
        map_panel = self.view.panels["map_bar"]
        player = self.game_model.player
        entities_data = self.game_model.entities

        for key, entities in map_panel["entities"].items():
            for i, entity in enumerate(entities):
                if entity["rect"].colliderect(player.rect):
                    if "is_opened" in entities_data[key][i]["properties"].keys() and not entities_data[key][i]["properties"]["is_opened"]:
                        if key == "padlock_wall":
                            if player.inventory.handing_item and list(player.inventory.handing_item.keys())[0] == "key":
                                player.inventory.handing_item = None
                                entities_data[key][i]["properties"]["is_opened"] = True
                            else:
                                self.player_controller.move_back(self.player_controller.last_pos)
                                self.player_controller.last_pos = None
                        else:
                            for item in entities_data[key][i]["properties"]["items"]:
                                player.inventory.add_item(item["id"], item["qty"])
                                entities_data[key][i]["properties"]["is_opened"] = True
                    return

    def __interact_enemy_map(self):
        player = self.game_model.player
        for enemy in self.game_model.enemies:
            if enemy.rect.contains(player.rect):
                print("VOCE MORREU!")
                return GameState.MAIN_MENU
        return None

    def __enemies_update(self):
        for enemy_ctrl in self.enemies:
            enemy_ctrl.update()
            if enemy_ctrl.entity.state == "moving": continue

            enemy_ctrl.entity.direction = enemy_ctrl.entity.movements[enemy_ctrl.entity.current_movement]
            enemy_ctrl.move()

            if enemy_ctrl.entity.state == "idle":
                enemy_ctrl.entity.current_movement = (enemy_ctrl.entity.current_movement + 1) % len(
                    enemy_ctrl.entity.movements)


class CommandInterpreter:
    def __init__(self):
        pass

    def create_sequence_execution(self, commands):
        execution_queue = []
        loop_stack = []

        if not self.__check_structure(commands):
            return []

        i = 0

        max_steps = 1000
        steps = 0

        while i < len(commands) and steps < max_steps:
            cmd, val = commands[i]

            if cmd == "repeat":
                loop_stack.append({'count': val, 'start_index': i + 1})
                i += 1
            elif cmd == "end_repeat":
                if loop_stack:
                    loop_stack[-1]['count'] -= 1
                    if loop_stack[-1]['count'] > 0:
                        i = loop_stack[-1]['start_index']
                    else:
                        loop_stack.pop()
                        i += 1
                else:
                    i += 1
            else:
                execution_queue.append({"index": i, "command": cmd, "value": val})
                i += 1
            steps += 1

        return execution_queue

    def __check_structure(self, commands):
        balance = 0
        for cmd in commands:
            if cmd[0] == "repeat":
                balance += 1
            elif cmd[0] == "end_repeat":
                balance -= 1
            if balance < 0: return False
        return balance == 0
