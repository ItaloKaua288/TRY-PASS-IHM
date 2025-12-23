import pygame

from src.utils.settings import GameState, COMMANDS_TRANSLATED
from src.controller.entities_controller import DefaultEntityController

HOLD_THRESHOLD_MS = 200

class GameController:
    def __init__(self, in_game_view, game_model, sound_controller):
        self.view = in_game_view
        self.game_model = game_model
        self.sound_controller = sound_controller

        self.game_is_paused = True
        self.is_executing = False
        self.game_over = False

        self.current_state = "coding"

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

        self.sounds = {
            "plim_1": pygame.mixer.Sound("src/assets/sounds/plim_1.wav"),
            "hit_2": pygame.mixer.Sound("src/assets/sounds/hit_2.wav"),
            "sucess": pygame.mixer.Sound("src/assets/sounds/sucess.wav"),
            "hit_1": pygame.mixer.Sound("src/assets/sounds/hint.wav"),
            "hit_3": pygame.mixer.Sound('src/assets/sounds/hit_3.wav'),
            "blop_2": pygame.mixer.Sound("src/assets/sounds/blop_2.wav"),
            "swoosh": pygame.mixer.Sound("src/assets/sounds/swoosh.wav"),
        }

    def update(self, events):
        next_state = None

        state_from_events = self.__handle_events(events)

        self.view.update(self.game_is_paused, self.is_executing)
        self.__update_sounds()

        if self.game_over and not self.view.level_chat.is_visible:
            return GameState.IN_GAME

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

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_is_paused = True
                    self.view.panels["pause_menu"]["is_visible"] = True
                return None

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.is_dragging:
                    self.__stop_dragging(mouse_pos)
                else:
                    self.mouse_down_time = pygame.time.get_ticks()
                    self.mouse_down_pos = mouse_pos
                    self.hold_action_triggered = False

                    if not self.view.panels["execution_bar"]["config_repeat"]["rect"].collidepoint(mouse_pos):
                        self.view.panels["execution_bar"]["config_repeat"]["is_visible"] = False
                return None

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.__update_hold_state()

                if self.view.panels["pause_menu"]["is_visible"]:
                    return self.__handle_pause_menu(mouse_pos)
                elif self.view.level_chat.is_visible:
                    self.__handle_level_chat(mouse_pos)
                elif self.view.tip_view.is_visible:
                    self.__handle_tips_view()
                elif self.view.panels["top_bar"]["rect"].collidepoint(mouse_pos):
                    local_pos = (mouse_pos[0] - self.view.panels["top_bar"]["rect"].x, mouse_pos[1] - self.view.panels["top_bar"]["rect"].y)
                    return self.__handle_top_bar(local_pos)
                elif self.view.panels["inventory_bar"]["is_visible"]:
                    local_pos = (mouse_pos[0] - self.view.panels["inventory_bar"]["rect"].x, mouse_pos[1] - self.view.panels["inventory_bar"]["rect"].y)
                    self.__handle_inventory_bar(local_pos)
                elif self.view.panels["popup_alert_menu"]["is_visible"]:
                    local_pos = (mouse_pos[0] - self.view.panels["popup_alert_menu"]["rect"].x, mouse_pos[1] - self.view.panels["popup_alert_menu"]["rect"].y)
                    self.__handle_popup_alert_menu(local_pos)
                elif self.game_is_paused:
                    return None
                elif self.view.panels["help_menu"]["is_visible"] and self.view.panels["help_menu"]["rect"].collidepoint(mouse_pos):
                    self.__handle_help_menu()
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
        if self.mouse_down_time == 0 or self.hold_action_triggered or self.is_dragging or self.is_executing:
            return

        duration = pygame.time.get_ticks() - self.mouse_down_time

        if duration > HOLD_THRESHOLD_MS:
            self.hold_action_triggered = True
            panel = self.view.panels["execution_bar"]
            if panel["config_repeat"]["is_visible"] and panel["config_repeat"]["rect"].collidepoint(self.mouse_down_pos):
                return
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

    def __handle_help_menu(self):
        return None

    def __handle_level_chat(self, mouse_pos):
        if not self.view.level_chat.rect.collidepoint(mouse_pos):
            return

        panel = self.view.level_chat

        if panel.current_text_line_panel == -1:
            panel.current_text_line_panel = 0
            return

        if panel.current_text_line_panel >= len(panel.text_lines_panels) - 1:
            panel.is_visible = False
            self.game_is_paused = False
            # self.view.panels["help_menu"]["is_visible"] = True
        else:
            panel.current_text_line_panel += 1

        self.sounds["hit_1"].play()

    def __handle_top_bar(self, mouse_pos):
        for key, button in self.view.panels["top_bar"]["buttons"].items():
            if button["rect"].collidepoint(mouse_pos):
                if not self.view.panels["pause_menu"]["is_visible"]:
                    if not button["is_visible"]:
                        continue

                    self.sounds["hit_1"].play()
                    if key == "options":
                        pause_menu = self.view.panels["pause_menu"]
                        pause_menu["is_visible"] = not pause_menu["is_visible"]
                        self.game_is_paused = pause_menu["is_visible"]
                    elif key == "restart_level":
                        return GameState.IN_GAME
                    elif key == "music_note":
                        self.sound_controller.disable_music()
                    elif key == "unmusic_note":
                        self.sound_controller.enable_music()
                    elif key == "idea":
                        help_menu = self.view.panels["help_menu"]
                        help_menu["is_visible"] = not help_menu["is_visible"]
                    elif key == "inventory" and not self.view.panels["pause_menu"]["is_visible"]:
                        self.view.panels["inventory_bar"]["is_visible"] = not self.view.panels["inventory_bar"]["is_visible"]
                        self.game_is_paused = self.view.panels["inventory_bar"]["is_visible"]
                return None
        return None

    def __handle_pause_menu(self, mouse_pos):
        if not self.view.panels["pause_menu"]["menu_rect"].collidepoint(mouse_pos):
            return None

        pause_menu = self.view.panels["pause_menu"]

        for key, button in pause_menu["buttons"].items():
            if button["rect"].collidepoint(mouse_pos):
                self.sounds["hit_1"].play()
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
                        self.sounds["hit_1"].play()
                        if player_inventory.handing_item is not None:
                            current_key = list(player_inventory.handing_item.keys())[0]
                            player_inventory.add_item(current_key)

                        player_inventory.handing_item = {key: 1}
                        player_inventory.remove_item(key)
                    except IndexError:
                        pass
                    return

    def __handle_execution_bar(self, mouse_pos):
        panel = self.view.panels["execution_bar"]

        for key, button in panel["buttons"].items():
            if button["rect"].collidepoint(mouse_pos):
                if button["is_visible"]:
                    self.sounds["hit_1"].play()
                    if key == "play":
                        if self.game_model.execution_queue:
                            self.execution_interpreted_queue = self.command_interpreter.create_sequence_execution(self.game_model.execution_queue)
                            if self.execution_interpreted_queue:
                                self.is_executing = True
                            else:
                                self.view.panels["popup_alert_menu"]["text"] = "ERRO: Quantidade de REPETIÇÃO e FIM DE REPETIÇÃO, na ÁREA DE EXECUÇÃO, são diferentes!"
                                self.view.panels["popup_alert_menu"]["is_visible"] = True
                    elif key == "clear":
                        self.execution_interpreted_queue.clear()
                        self.game_model.clear_execution_commands()
                    else:
                        self.is_executing = False
                    return

        if self.is_executing: return

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
                        self.sounds["swoosh"].play()
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

    def __handle_popup_alert_menu(self, mouse_pos):
        panel = self.view.panels["popup_alert_menu"]

        for k, btn in panel["buttons"].items():
            if btn["rect"].collidepoint(mouse_pos):
                if k == "ok":
                    panel["is_visible"] = False
                    return

    def __handle_tips_view(self):
        tip_view = self.view.tip_view
        if tip_view.tips_data[tip_view.current_tutorial]["close_btn"]["is_hovered"]:
            tip_view.is_visible = False
            tip_view.current_tutorial = None
            self.game_is_paused = False

    def __handle_tools_bar(self, mouse_pos):
        if self.is_executing:
            return

        panel = self.view.panels["tools_bar"]
        for key, button in panel["buttons"].items():
            if button["rect"].collidepoint(mouse_pos):
                self.sounds["hit_1"].play()
                if button["info_btn"]["is_hovered"]:
                    self.view.tip_view.is_visible = True
                    self.view.tip_view.show_tutorial(key)
                    self.game_is_paused = True
                    button["info_btn"]["is_hovered"] = False
                    return

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
        self.__interact_item_map()

        if "rules" in self.view.model.constraints.keys() and self.view.model.constraints["rules"]:
            for key, rules in self.view.model.constraints["rules"].items():
                if key == "commands":
                    for command_key, command_rules in rules.items():
                        for rule_key, rule in command_rules.items():
                            if rule_key == "min":
                                count = 0

                                if command_key == "repeat":
                                    for command in self.game_model.execution_queue:
                                        if command[0] == command_key:
                                            count += 1
                                else:
                                    for command in self.execution_interpreted_queue:
                                        if command["command"] == command_key:
                                            count += 1

                                if count < rule:
                                    self.view.panels["popup_alert_menu"]["text"] = f"Restrição: O numero de {COMMANDS_TRANSLATED[command_key]} precisa ser no mínimo {rule}"
                                    self.view.panels["popup_alert_menu"]["is_visible"] = True
                                    self.is_executing = False
                                    return None

        if self.player_controller.entity.state != "idle":
            return None

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

    def __update_sounds(self):
        for sound in self.sounds.values():
            sound.set_volume(self.sound_controller.get_effects_volume())

        if self.sound_controller.music_enabled:
            self.view.panels["top_bar"]["buttons"]["music_note"]["is_visible"] = True
            self.view.panels["top_bar"]["buttons"]["unmusic_note"]["is_visible"] = False
        else:
            self.view.panels["top_bar"]["buttons"]["music_note"]["is_visible"] = False
            self.view.panels["top_bar"]["buttons"]["unmusic_note"]["is_visible"] = True

    def __check_victory(self):
        final_pos = self.game_model.final_objective_pos
        if self.game_model.player.rect.collidepoint(final_pos):
            self.sounds["sucess"].play()
            self.game_model.current_level += 1
            if self.game_model.current_level >= self.game_model.current_level_unlocked:
                self.game_model.current_level_unlocked += 1
                self.game_model.save_game()
            return GameState.END_CREDITS
        return None

    def __interact_item_map(self):
        map_panel = self.view.panels["map_bar"]
        player = self.game_model.player
        entities_data = self.game_model.entities

        for key, entities in map_panel["entities"].items():
            for i, entity in enumerate(entities):
                if entity["rect"].colliderect(player.rect):
                    if hasattr(entities_data[key][i], "is_opened") and not entities_data[key][i].is_opened:
                        if key == "padlock_wall":
                            if player.inventory.handing_item and list(player.inventory.handing_item.keys())[0] == "key":
                                self.sounds["plim_1"].play()
                                player.inventory.handing_item = None
                                entities_data[key][i].is_opened = True
                            else:
                                self.sounds["hit_2"].play()
                                self.player_controller.move_back(self.player_controller.last_pos)
                                self.player_controller.last_pos = None
                        elif key == "chest":
                            self.sounds["plim_1"].play()
                            for item in entities_data[key][i].items:
                                player.inventory.add_item(item.name, item.quantity)
                                entities_data[key][i].is_opened = True
                                self.view.items_floating_to_inventory.append({"key": item.name, "pos": list(entity["rect"].center), "surface": None})
                    return

    def __interact_enemy_map(self):
        player = self.game_model.player
        for enemy in self.game_model.enemies:
            if enemy.rect.colliderect(player.rect):
                self.sounds["hit_3"].play()
                self.game_over = True
                self.game_is_paused = True
                self.view.level_chat.game_over = True
                self.view.level_chat.is_visible = True
                self.view.level_chat.current_text_line_panel = -1
        return None

    def __enemies_update(self):
        for enemy_ctrl in self.enemies:
            enemy_ctrl.update()
            if enemy_ctrl.entity.state != "idle": continue

            current_movement = enemy_ctrl.entity.movements[enemy_ctrl.entity.current_movement]
            if current_movement == "move":
                enemy_ctrl.last_pos = enemy_ctrl.entity.rect.topleft
                enemy_ctrl.move()
            elif current_movement == "turn_left":
                enemy_ctrl.turn_left()
            elif current_movement == "turn_right":
                enemy_ctrl.turn_right()
            enemy_ctrl.entity.current_movement = (enemy_ctrl.entity.current_movement + 1) % len(enemy_ctrl.entity.movements)


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
