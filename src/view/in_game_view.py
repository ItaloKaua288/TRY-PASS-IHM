import pygame
from src.utils.settings import Colors, TOTAL_SLOTS_EXECUTION, TILE_SIZE


class GameView:
    def __init__(self, screen, assets, game_model):
        self.screen = screen
        self.assets = assets
        self.model = game_model

        self.buttons = {}

        self.panels = {
            "execution_bar": self.__create_execution_bar(),
            "status_bar": self.__create_status_bar(),
            "map_bar": self.__create_map_bar(),
            "tools_bar": self.__create_tools_bar(),
            "inventory_bar": self.__create_inventory_bar(),
            "help_menu": self.__create_help_menu(),
            "top_bar": self.__create_top_bar(),
            "pause_menu": self.__create_pause_menu()
        }

        self._current_command_signature = ""
        self.execution_commands_queue = []
        self.current_command_executing = None
        self.camera_offset = [0, 0]

        self.items_floating_to_inventory = []

        self.dragged_command = {"index": None, "command": None}

    def __create_top_bar(self):
        surface = pygame.Surface((1000, 60), pygame.SRCALPHA)

        buttons_name = ["options", "idea", "inventory"]
        buttons_pos = [(30, 30), (910, 30), (970, 30)]

        buttons = {}
        for i, name in enumerate(buttons_name):
            img_name = "bag" if name == "inventory" else name
            btn_icon = pygame.transform.smoothscale(self.assets.get_image(f"images/icons/{img_name}.png").convert_alpha(), (40, 40))

            btn_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
            btn_surface_hover = btn_surface.copy()
            rect = btn_surface.get_rect(center=buttons_pos[i])

            pygame.draw.rect(btn_surface, Colors.LIGHT_GRAY.value, btn_surface.get_rect(topleft=(0, 0)), border_radius=10)
            pygame.draw.rect(btn_surface_hover, Colors.GRAY.value, btn_surface.get_rect(topleft=(0, 0)),border_radius=10)
            btn_surface.blit(btn_icon, btn_surface.get_rect(topleft=(5, 5)))
            btn_surface_hover.blit(btn_icon, btn_surface.get_rect(topleft=(5, 5)))

            buttons[name] = {"surface": btn_surface, "hover_surface": btn_surface_hover, "rect": rect, "is_hovered": False}
            surface.blit(btn_surface, rect)

        objective_surface = pygame.Surface((500, 50), pygame.SRCALPHA)
        objective_rect = objective_surface.get_rect(center=(500, 30))
        pygame.draw.rect(objective_surface, Colors.LIGHT_GRAY.value, objective_surface.get_rect(), border_radius=10)
        surface.blit(objective_surface, objective_rect)
        title_font = pygame.font.SysFont("monospace", 17)

        title_surface = title_font.render(self.model.meta["description"], True, Colors.BLACK.value)

        surface.blit(title_surface, title_surface.get_rect(center=objective_rect.center))

        return {"surface": surface, "rect": surface.get_rect(topleft=(5, 5)), "buttons": buttons, "objective_bar": None, "is_visible": True}

    def __create_tools_bar(self):
        surface = pygame.Surface((265, 500), pygame.SRCALPHA)
        pygame.draw.rect(surface, Colors.LIGHT_GRAY.value, surface.get_rect(topleft=(0, 0)), border_radius=10)

        font = self.assets.get_font("Monospace", 15)
        title_surf = font.render("FERRAMENTAS", True, Colors.BLACK.value)
        surface.blit(title_surf, title_surf.get_rect(center=(surface.get_rect().centerx, 10)))

        buttons = {}
        for i, command in enumerate(self.model.constraints["available_commands"]):
            icon_surf = pygame.transform.smoothscale(
                self.assets.get_image(f"images/icons/{command}.png").convert_alpha(), (50, 50))
            btn_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
            btn_surface_hover = btn_surface.copy()
            btn_rect = btn_surface.get_rect(topleft=(5 + 65 * (i % 4), 40 + 65 * (i // 4)))
            pygame.draw.rect(btn_surface, Colors.GRAY.value, btn_surface.get_rect(), border_radius=10)
            pygame.draw.rect(btn_surface_hover, Colors.DARK_GRAY.value, btn_surface.get_rect(), border_radius=10)
            btn_surface.blit(icon_surf, icon_surf.get_rect(center=btn_surface.get_rect().center))
            btn_surface_hover.blit(icon_surf, icon_surf.get_rect(center=btn_surface.get_rect().center))
            surface.blit(btn_surface, btn_rect.topleft)
            buttons[command] = {"surface": btn_surface, "hover_surface": btn_surface_hover, "rect": btn_rect,
                                "is_hovered": False}

        return {"surface": surface, "rect": surface.get_rect(topleft=(1010, 5)), "buttons": buttons, "is_visible": True}

    def __create_execution_bar(self):
        surface = pygame.Surface((750, 150), pygame.SRCALPHA)
        pygame.draw.rect(surface, Colors.LIGHT_GRAY.value, surface.get_rect(topleft=(0, 0)), border_radius=10)

        font = self.assets.get_font("Monospace", 15)
        title_surf = font.render("ÁREA DE EXECUÇÃO", True, Colors.BLACK.value)
        surface.blit(title_surf, title_surf.get_rect(center=(surface.get_rect().centerx, 10)))

        buttons_name = ["play", "clear"]
        buttons_pos = [(715, 50), (715, 115)]
        buttons_color = ((Colors.GREEN.value, Colors.DARK_GREEN.value), (Colors.RED.value, Colors.DARK_RED.value))

        buttons = {}
        for i, name in enumerate(buttons_name):
            img_name = "trash" if name == "clear" else name
            btn_icon = pygame.transform.smoothscale(self.assets.get_image(f"images/icons/{img_name}.png").convert_alpha(), (40, 40))
            btn_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
            btn_surface_hover = btn_surface.copy()
            rect = btn_surface.get_rect(center=buttons_pos[i])

            pygame.draw.rect(btn_surface, buttons_color[i][0], btn_surface.get_rect(), border_radius=10)
            pygame.draw.rect(btn_surface_hover, buttons_color[i][1], btn_surface.get_rect(), border_radius=10)
            btn_surface.blit(btn_icon, btn_surface.get_rect(topleft=(10, 10)))
            btn_surface_hover.blit(btn_icon, btn_surface.get_rect(topleft=(10, 10)))
            buttons[name] = {"surface": btn_surface, "hover_surface": btn_surface_hover, "rect": rect, "is_hovered": False}
            surface.blit(btn_surface, rect)

        slot_rects = []
        for i in range(TOTAL_SLOTS_EXECUTION):
            rect = pygame.Rect(5 + 64 * (i % 10), 20 + 64 * (i // 10), 64, 64)
            pygame.draw.rect(surface, Colors.BLACK.value, rect, width=1)
            slot_rects.append(rect)

        config_repeat_surface = pygame.Surface((150, 100), pygame.SRCALPHA)
        pygame.draw.rect(config_repeat_surface, Colors.WHITE.value, config_repeat_surface.get_rect(), border_radius=10)

        text = font.render("Repetições", True, Colors.BLACK.value)
        config_repeat_surface.blit(text, (config_repeat_surface.get_rect().centerx - text.get_width() // 2, 1))

        buttons_name = ["back", "forward", "check"]
        buttons_pos = ((25, 40), (125, 40), (config_repeat_surface.get_rect().centerx, 80))
        config_repeat_buttons = {}
        for i, name in enumerate(buttons_name):
            button_surface = pygame.Surface((35, 35), pygame.SRCALPHA)
            button_hover_surface = button_surface.copy()
            icon_surface = pygame.transform.smoothscale(
                self.assets.get_image(f"images/icons/{name}.png").convert_alpha(), (30, 30))
            button_rect = button_surface.get_rect()

            pygame.draw.rect(button_surface, Colors.LIGHT_GRAY.value, button_rect, border_radius=10)
            pygame.draw.rect(button_hover_surface, Colors.DARK_GRAY.value, button_rect, border_radius=10)

            button_surface.blit(icon_surface, icon_surface.get_rect(center=button_rect.center))
            button_hover_surface.blit(icon_surface, icon_surface.get_rect(center=button_rect.center))
            button_rect = button_surface.get_rect(center=buttons_pos[i])
            config_repeat_surface.blit(button_surface, button_rect)

            config_repeat_buttons[name] = {"surface": button_surface, "hover_surface": button_hover_surface, "rect": button_rect, "is_hovered": False}

        return {"surface": surface, "default_background": surface, "rect": surface.get_rect(topleft=(5, 565)),
                "buttons": buttons, "slot_rects": slot_rects, "is_visible": True,
                "config_repeat": {
                    "surface": config_repeat_surface,
                    "default_background": config_repeat_surface.copy(),
                    "rect": config_repeat_surface.get_rect(),
                    "buttons": config_repeat_buttons,
                    "repeat_num": 0,
                    "command_index": None,
                    "is_visible": False
                },
        }

    def __create_map_bar(self):
        surface = pygame.Surface((1000, 490), pygame.SRCALPHA)
        surface_rect = surface.get_rect(topleft=(5, 70))
        pygame.draw.rect(surface, Colors.BLACK.value, surface.get_rect(topleft=(0, 0)), border_radius=10)

        map = self.model.map
        map_surface = pygame.Surface((map["width"] * TILE_SIZE, map["height"] * TILE_SIZE), pygame.SRCALPHA)

        for row_index, tile_row in enumerate(map["tiles"]):
            for col_index, tile_index in enumerate(tile_row):
                map_surface.blit(self.model.tile_map_surf[tile_index], (col_index * TILE_SIZE, row_index * TILE_SIZE))

        map_entities = {}
        for key, items in self.model.entities.items():
            if key == "enemy":
                continue

            entities = []
            for item in items:

                # item_surface = pygame.transform.smoothscale(self.assets.get_image(f"images/sprites/items/{item["type"]}.png").convert_alpha(), (TILE_SIZE, TILE_SIZE))
                item_surface = pygame.transform.smoothscale(self.assets.get_image(f"images/sprites/items/{key}.png").convert_alpha(), (TILE_SIZE, TILE_SIZE))
                # item_rect = item_surface.get_rect(topleft=item["pos"])
                item_rect = item_surface.get_rect(topleft=item.pos)

                # if item["type"] != "padlock_wall":
                # if key != "padlock_wall":
                #     map_surface.blit(item_surface, item_rect)

                entities.append({"surface": item_surface, "rect": item_rect})

            map_entities[key] = entities

        surface.blit(map_surface, (0, 0))

        return {"surface": surface, "rect": surface_rect, "buttons": {}, "map_surface": map_surface,
                "entities": map_entities, "is_visible": True}

    def __create_inventory_bar(self):
        surface = pygame.Surface((600, 400), pygame.SRCALPHA)
        surface_rect = surface.get_rect(center=self.screen.get_rect().center)
        pygame.draw.rect(surface, Colors.LIGHT_GRAY.value, surface.get_rect(topleft=(0, 0)), border_radius=10)

        font = self.assets.get_font("Monospace", 25)
        text_surface = font.render("INVENTÁRIO", True, Colors.BLACK.value)
        surface.blit(text_surface, text_surface.get_rect(center=(surface_rect.width // 2, 25)))

        overlay_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(overlay_surface, Colors.BLACK.value + (200,), overlay_surface.get_rect(topleft=(0, 0)))

        overlay_surface.blit(surface, surface_rect)

        slot_rects = []
        slot_size = 64
        total_slots_col = (surface_rect.width - 10) // slot_size
        total_slots_row = (surface_rect.height - 40) // slot_size
        for i in range(total_slots_row):
            for j in range(total_slots_col):
                slot_rect = pygame.Rect(j * slot_size + 10 + surface_rect.x, i * slot_size + 50 + surface_rect.y,
                                        slot_size, slot_size)
                pygame.draw.rect(overlay_surface, Colors.BLACK.value, slot_rect, width=1)
                slot_rects.append(slot_rect)

        return {"surface": overlay_surface, "rect": overlay_surface.get_rect(), "default_background": overlay_surface,
                "buttons": {}, "inventory_rect": surface_rect, "slot_rects": slot_rects, "is_visible": False}

    def __create_status_bar(self):
        surface = pygame.Surface((245, 150), pygame.SRCALPHA)
        pygame.draw.rect(surface, Colors.LIGHT_GRAY.value, surface.get_rect(topleft=(0, 0)), border_radius=10)

        text_font = self.assets.get_font("Monospace", 15)
        hand_item_surface = text_font.render("Item na mão:", True, Colors.BLACK.value)
        surface.blit(hand_item_surface, hand_item_surface.get_rect(topleft=(5, 15)))

        return {"surface": surface, "background": surface, "rect": surface.get_rect(topleft=(760, 565)), "buttons": {},
                "is_visible": True}

    def __create_help_menu(self):
        text_font = self.assets.get_font("Monospace", 12, False)
        help_text_surface = text_font.render(self.model.help, True, Colors.BLACK.value, wraplength=390)

        surface = pygame.Surface((400, help_text_surface.height + 30), pygame.SRCALPHA)
        pygame.draw.rect(surface, Colors.LIGHT_GRAY.value, surface.get_rect(topleft=(0, 0)), border_radius=10)
        pygame.draw.rect(surface, Colors.BLACK.value, surface.get_rect(), width=2, border_radius=10)
        surface_rect = surface.get_rect()

        surface.blit(help_text_surface, (5, 25))

        text_font = self.assets.get_font("Monospace", 15)
        title_surface = text_font.render("Ajuda", True, Colors.BLACK.value)
        surface.blit(title_surface, title_surface.get_rect(center=(surface_rect.centerx, 15)))

        return {"surface": surface, "background": surface, "rect": surface.get_rect(center=(900, 60 + surface.height // 2)), "buttons": {}, "is_visible": True}

    def __create_pause_menu(self):
        surface = pygame.Surface((300, 230), pygame.SRCALPHA)
        surface_rect = surface.get_rect(center=self.screen.get_rect().center)
        pygame.draw.rect(surface, Colors.LIGHT_GRAY.value, surface.get_rect(topleft=(0, 0)), border_radius=10)
        pygame.draw.rect(surface, Colors.WHITE.value, surface.get_rect(topleft=(0, 0)), border_radius=10, width=2)
        pygame.draw.rect(surface, Colors.BLACK.value, pygame.Rect(5, 40, surface_rect.width - 19, 2))

        font = self.assets.get_font("Monospace", 25)
        text_surface = font.render("Menu do Jogo", True, Colors.BLACK.value)
        surface.blit(text_surface, text_surface.get_rect(center=(surface_rect.width // 2, 25)))

        overlay_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(overlay_surface, Colors.BLACK.value + (200,), overlay_surface.get_rect(topleft=(0, 0)))

        overlay_surface.blit(surface, surface_rect)

        buttons_name = ("Continuar", "Novo Jogo", "Selecionar Fase", "Voltar ao Inicio", "Sair")
        buttons = {}
        for i, name in enumerate(buttons_name):
            text_surface = font.render(name, True, Colors.BLACK.value)
            btn_surface = pygame.Surface((surface.width - 10, text_surface.height + 2), pygame.SRCALPHA)
            btn_hover_surface = btn_surface.copy()
            btn_rect = btn_surface.get_rect()

            pygame.draw.rect(btn_surface, Colors.GRAY.value, btn_rect, border_radius=10)
            pygame.draw.rect(btn_hover_surface, Colors.DARK_GRAY.value, btn_rect, border_radius=10)

            text_pos = btn_rect.width // 2 - text_surface.width // 2, 2
            btn_surface.blit(text_surface, btn_surface.get_rect(topleft=text_pos))
            btn_hover_surface.blit(text_surface, btn_surface.get_rect(topleft=text_pos))

            btn_pos = surface_rect.width // 2 - btn_rect.width // 2 + surface_rect.x, 50 + i * 35 + surface_rect.y
            buttons[name] = {"surface": btn_surface, "hover_surface": btn_hover_surface, "rect": btn_surface.get_rect(topleft=btn_pos), "is_hovered": False}

        return {"surface": overlay_surface, "rect": overlay_surface.get_rect(), "default_background": overlay_surface,
                "buttons": buttons, "menu_rect": surface_rect, "is_visible": False}

    def calculate_camera_offset(self):
        player = self.model.player

        map_panel = self.panels["map_bar"]
        camera_size = map_panel["surface"].get_size()
        map_size = map_panel["map_surface"].get_size()
        half_camera_width = camera_size[0] // 2
        half_camera_height = camera_size[1] // 2

        offset_x = player.rect.centerx - half_camera_width
        offset_y = player.rect.centery - half_camera_height

        offset_x = max(0, min(offset_x, camera_size[0] - map_size[0]))
        offset_y = max(0, min(offset_y, camera_size[1] - map_size[1]))

        self.camera_offset = [offset_x, offset_y]

    def update(self, game_paused=False):
        self.calculate_camera_offset()
        mouse_pos = pygame.mouse.get_pos()

        for key, panel_items in self.panels.items():
            if game_paused and key not in  ("pause_menu", "inventory_bar"):
                continue

            panel_topleft = panel_items["rect"].topleft
            local_mouse_pos = mouse_pos[0] - panel_topleft[0], mouse_pos[1] - panel_topleft[1]
            for button in panel_items["buttons"].values():
                if button["rect"].collidepoint(local_mouse_pos):
                    panel_items["surface"].blit(button["hover_surface"], button["rect"])
                    button["is_hovered"] = True
                else:
                    panel_items["surface"].blit(button["surface"], button["rect"])
                    button["is_hovered"] = False

        self.__update_items_floating_to_inventory()
        self.__update_map_bar()
        self.__update_execution_bar()
        self.__update_status_bar()
        self.__update_inventory_bar()

    def __update_status_bar(self):
        status_panel = self.panels["status_bar"]
        handing_rect = pygame.Rect(120, 5, 40, 40)
        pygame.draw.rect(status_panel["surface"], Colors.BLACK.value, handing_rect, 1)
        status_panel["surface"] = status_panel["background"].copy()

        text_font = self.assets.get_font("Monospace", 15)

        counter_colectables_surface = text_font.render(
            f"Coletaveis restantes: {self.model.get_remaining_collectibles_count()}", True, Colors.BLACK.value)

        status_panel["surface"].blit(counter_colectables_surface, counter_colectables_surface.get_rect(topleft=(5, 55)))

        handing_item = self.model.player.inventory.handing_item
        if handing_item is not None:
            handing_item_surface = pygame.transform.smoothscale(
                self.assets.get_image(f"images/sprites/items/{tuple(handing_item.keys())[0]}.png"), handing_rect.size)
            status_panel["surface"].blit(handing_item_surface, handing_rect)

    def __update_map_bar(self):
        map_panel = self.panels["map_bar"]

        player = self.model.player

        map_rect = map_panel["map_surface"].get_rect()
        map_panel["surface"].blit(map_panel["map_surface"], (map_rect.x - self.camera_offset[0], map_rect.y - self.camera_offset[1]))

        for key, entities in self.model.entities.items():
            for i, entity in enumerate(entities):
                if key == "chest":
                    if not entity.is_opened:
                        item_surface = pygame.transform.smoothscale(self.assets.get_image(f"images/sprites/items/{key}.png").convert_alpha(), (TILE_SIZE, TILE_SIZE))
                    else:
                        item_surface = pygame.transform.smoothscale(self.assets.get_image(f"images/sprites/items/{key}_opened.png").convert_alpha(), (TILE_SIZE, TILE_SIZE))
                    map_panel["entities"][key][i]["surface"] = item_surface
                if key == "padlock_wall":
                    if entity.is_opened:
                        continue
                map_panel["surface"].blit(map_panel["entities"][key][i]["surface"], (entity.pos[0] - self.camera_offset[0], entity.pos[1] - self.camera_offset[1]))

        player_sprites = player.sprites[player.state]
        if player.direction_rotate < 0 and player.state == "rotating":
            player_sprites = [x for x in player_sprites[player.direction_list[
                (player.direction_list.index(player.direction) - 1) % len(player.direction_list)]]]
            player_sprites.reverse()
        else:
            player_sprites = player_sprites[player.direction]
        map_panel["surface"].blit(player_sprites[player.current_sprite],
                                  (self.model.player.rect.topleft[0] - self.camera_offset[0],
                                   self.model.player.rect.topleft[1] - self.camera_offset[1]))

        for enemy in self.model.enemies:
            enemy_sprites = enemy.sprites[enemy.state]
            if enemy.direction_rotate < 0 and enemy.state == "rotating":
                enemy_sprites = [x for x in enemy_sprites[enemy.direction_list[
                    (enemy.direction_list.index(enemy.direction) - 1) % len(enemy.direction_list)]]]
                enemy_sprites.reverse()
            else:
                enemy_sprites = enemy_sprites[enemy.direction]
            map_panel["surface"].blit(enemy_sprites[enemy.current_sprite],
                                      (enemy.rect.topleft[0] - self.camera_offset[0],
                                       enemy.rect.topleft[1] - self.camera_offset[1]))

    def __update_inventory_bar(self):
        panel = self.panels["inventory_bar"]

        player_inventory = self.model.player.inventory.inventory

        panel["surface"] = panel["default_background"].copy()

        count = 0
        amount_font = self.assets.get_font("Monospace", 20)
        inventory_items = []
        for key, amount in player_inventory.items():
            icon_surface = pygame.transform.scale(self.assets.get_image(f"images/sprites/items/{key}.png").convert_alpha(),
                                                  panel["slot_rects"][0].size)
            icon_rect = icon_surface.get_rect(topleft=panel["slot_rects"][count].topleft)

            amount_text_surface = amount_font.render(str(amount), True, Colors.BLACK.value)
            amount_bg_surface = pygame.Surface(amount_text_surface.get_size())
            amount_bg_rect = amount_bg_surface.get_rect(
                topleft=(icon_rect.x - amount_bg_surface.get_width() + icon_rect.width - 1, icon_rect.topleft[1] + 1))
            amount_bg_surface.fill(Colors.WHITE.value)
            amount_text_rect = amount_text_surface.get_rect()
            amount_bg_surface.blit(amount_text_surface, amount_text_rect)

            panel["surface"].blit(icon_surface, icon_rect)
            panel["surface"].blit(amount_bg_surface, amount_bg_rect)

            inventory_items.append(key)
            count += 1
        panel["inventory_items"] = inventory_items

    def __update_execution_bar(self):
        panel = self.panels["execution_bar"]

        execution_queue = self.model.execution_queue

        panel["surface"] = panel["default_background"].copy()

        mouse_pos = pygame.mouse.get_pos()
        local_mouse_pos = mouse_pos[0] - panel["rect"].topleft[0], mouse_pos[1] - panel["rect"].topleft[1]

        for button in panel["buttons"].values():
            if button["is_hovered"]:
                panel["surface"].blit(button["hover_surface"], button["rect"])
            else:
                panel["surface"].blit(button["surface"], button["rect"])

        repeat_local_mouse_pos = mouse_pos[0] - panel["config_repeat"]["rect"].topleft[0], mouse_pos[1] - panel["config_repeat"]["rect"].topleft[1]
        for button in panel["config_repeat"]["buttons"].values():
            button["is_hovered"] = button["rect"].collidepoint(repeat_local_mouse_pos)

        for execution_command in self.execution_commands_queue:
            execution_command["buttons"]["remove"]["is_hovered"] = execution_command["buttons"]["remove"]["rect"].collidepoint(local_mouse_pos)

            if execution_command["buttons"]["remove"]["rect"].collidepoint(local_mouse_pos):
                panel["surface"].blit(execution_command["buttons"]["remove"]["hover_surface"], execution_command["buttons"]["remove"]["rect"])
            else:
                panel["surface"].blit(execution_command["buttons"]["remove"]["surface"], execution_command["buttons"]["remove"]["rect"])

        if self.current_command_executing is not None:
            pygame.draw.rect(panel["surface"], Colors.GREEN.value, panel["slot_rects"][self.current_command_executing])

        current_command_signature = "".join([command[0] for command in execution_queue])

        if self._current_command_signature != current_command_signature:
            self._current_command_signature = current_command_signature
            self.execution_commands_queue.clear()
            command_buttons = []
            remove_surface = pygame.Surface((16, 16))
            remove_hover_surface = remove_surface.copy()
            remove_surface.fill(Colors.GRAY.value)
            remove_hover_surface.fill(Colors.DARK_GRAY.value)
            remove_icon = pygame.transform.smoothscale(self.assets.get_image(f"images/icons/cancel.png").convert_alpha(), (10, 10))
            remove_surface.blit(remove_icon, (3, 3))
            remove_hover_surface.blit(remove_icon, (3, 3))

            for i, command in enumerate(execution_queue):
                remove_rect = remove_surface.get_rect(topleft=(i % 10 * panel["slot_rects"][i].width + panel["slot_rects"][i].width - 11, panel["slot_rects"][i].topleft[1]))
                icon_surf = pygame.transform.smoothscale(self.assets.get_image(f"images/icons/{command[0]}.png").convert_alpha(), (55, 55))
                icon_rect = icon_surf.get_rect(center=panel["slot_rects"][i].center)
                panel["surface"].blit(icon_surf, icon_rect)
                panel["surface"].blit(remove_surface, remove_rect)

                command_buttons.append({"type": command[0], "surface": icon_surf, "rect": icon_rect, "buttons": {"remove": {"surface": remove_surface, "hover_surface": remove_hover_surface, "rect": remove_rect, "is_hovered": False}}})
                self.execution_commands_queue = command_buttons
        else:
            for i, command in enumerate(self.execution_commands_queue):
                panel["surface"].blit(command["surface"], command["rect"])

                if command["type"] == "repeat":
                    count_surface = self.assets.get_font("Monospace", 17).render(str(execution_queue[i][1]), True, Colors.WHITE.value, Colors.GRAY.value)
                    panel["surface"].blit(count_surface,
                                          (command["rect"].x + command["rect"].width - count_surface.width + 3,
                                                 command["rect"].y + command["rect"].height - count_surface.height + 3)
                    )

        if self.dragged_command["command"] is not None:
            panel["surface"].blit(self.dragged_command["command"]["surface"], local_mouse_pos)

        panel["config_repeat"]["surface"] = panel["config_repeat"]["default_background"].copy()

        text = self.assets.get_font("Monospace", 25).render(str(panel["config_repeat"]["repeat_num"]), True,
                                                            Colors.BLACK.value)
        panel["config_repeat"]["surface"].blit(text, text.get_rect(topleft=(70, 25)))

        for i, button in enumerate(panel["config_repeat"]["buttons"].values()):
            if button["is_hovered"]:
                panel["config_repeat"]["surface"].blit(button["hover_surface"], button["rect"])
            else:
                panel["config_repeat"]["surface"].blit(button["surface"], button["rect"])

    def __update_items_floating_to_inventory(self):
        if not self.items_floating_to_inventory:
            return

        SPEED = 15

        inventory_btn_pos = self.panels["top_bar"]["buttons"]["inventory"]["rect"].center
        for item in self.items_floating_to_inventory:
            if item["surface"] is None:
                item["surface"] = pygame.transform.smoothscale(self.assets.get_image(f"images/sprites/items/{item["key"]}.png").convert_alpha(), (TILE_SIZE, TILE_SIZE))

            item["pos"] = pygame.math.Vector2(item["pos"][0], item["pos"][1])
            target = pygame.math.Vector2(inventory_btn_pos[0], inventory_btn_pos[1])
            distance = item["pos"].distance_to(target)

            if distance <= SPEED:
                self.items_floating_to_inventory.remove(item)
                return

            direction_vector = target - item["pos"]
            direction_vector = direction_vector.normalize()
            new_pos = item["pos"] + direction_vector * SPEED

            item["pos"] = new_pos

    def get_clicked_command_info(self, mouse_pos):
        panel = self.panels["execution_bar"]
        local_mouse_pos = mouse_pos[0] - panel["rect"].topleft[0], mouse_pos[1] - panel["rect"].topleft[1]

        for i, slot_rect in enumerate(panel["slot_rects"]):
            if slot_rect.collidepoint(local_mouse_pos) and i < len(self.execution_commands_queue):
                return {"index": i, "command": self.execution_commands_queue[i]}
        return None

    def get_execution_command_slot_index_hovered(self, mouse_pos):
        panel = self.panels["execution_bar"]
        local_mouse_pos = mouse_pos[0] - panel["rect"].topleft[0], mouse_pos[1] - panel["rect"].topleft[1]

        for i, slot_rect in enumerate(panel["slot_rects"]):
            if slot_rect.collidepoint(local_mouse_pos):
                return i
        return None

    def draw(self):
        self.screen.fill(Colors.DARK_GRAY.value)

        for panel in self.panels.values():
            if panel["is_visible"]:
                self.screen.blit(panel["surface"], panel["rect"])

        if self.panels["execution_bar"]["config_repeat"]["is_visible"]:
            self.screen.blit(self.panels["execution_bar"]["config_repeat"]["surface"], self.panels["execution_bar"]["config_repeat"]["rect"])

        for item in self.items_floating_to_inventory:
            if item["surface"] is None:
                continue
            self.screen.blit(item["surface"], item["pos"])

