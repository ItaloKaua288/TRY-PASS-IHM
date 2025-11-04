import pygame
from .ui_elements import IconButton
from . import  camera

from src.config import Colors, TILE_SIZE


class BasePanel:
    def __init__(self, size, topleft_pos, title_text=None, font=None, bg_color=Colors.WHITE_COLOR, title_color=Colors.BLACK_COLOR,
                 border_radius=10, is_visible=True):
        self.width, self.height = size
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=topleft_pos)
        self.is_visible = is_visible

        self._pre_render_static_content(font, title_text, bg_color, title_color, border_radius)

    def _pre_render_static_content(self, font, title_text, bg_color, title_color, border_radius):
        pygame.draw.rect(self.image, bg_color, self.image.get_rect(), border_radius=border_radius)
        if title_text and font:
            title_surface = font.render(title_text, True, title_color)
            title_rect = title_surface.get_rect(center=(self.width // 2, 20))
            self.image.blit(title_surface, title_rect)

    def draw(self, screen, model, assets=None):
        if self.is_visible:
            screen.blit(self.image, self.rect)


class MapPanel:
    def __init__(self, size, pos, assets, game_manager):
        self.width, self.height = size
        self.assets = assets
        self.game_manager = game_manager
        self.tile_size = (TILE_SIZE, TILE_SIZE)
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=pos)

        self.static_map_image = self.pre_render_map()

        self.camera = camera.Camera((self.width, self.height), self.static_map_image.get_size(), pos)

    def update_new_map(self):
        self.static_map_image = self.pre_render_map()
        self.camera = camera.Camera((self.width, self.height), self.static_map_image.get_size(), self.rect.topleft)

    def pre_render_map(self):
        game_model = self.game_manager.game_model
        tile_set = self.assets.get_tileset("sprites/tiles_map", self.tile_size)
        tile_map_data = game_model.tile_map
        interactable_objects = game_model.interactable_objects

        map_width = len(tile_map_data[0]) * self.tile_size[0]
        map_height = len(tile_map_data) * self.tile_size[1]
        map_surface = pygame.Surface((map_width, map_height))

        for i, row in enumerate(tile_map_data):
            for j, tile_id in enumerate(row):
                pos = (self.tile_size[0] * j, self.tile_size[1] * i)
                if tile_id in tile_set:
                    map_surface.blit(tile_set[tile_id], pos)

        for key, item_list in interactable_objects.items():
            for item in item_list:
                map_surface.blit(item.image, item.rect)
        return map_surface

    def update(self):
        self.camera.update(self.game_manager.game_model.player.rect)

    def get_player_rect_updated(self, player_rect):
        return self.camera.apply_offset(player_rect)

    def get_interactable_rect_list_updated(self):
        rects = {}
        for key, items in self.game_manager.game_model.interactable_objects.items():
            rects[key] = []
            for item in items:
                rects[key].append(self.camera.apply_offset(item.rect))
        return rects

    def draw(self, screen, model, assets):
        self.image.fill(Colors.BLACK_COLOR)
        self.image.blit(self.static_map_image, self.camera.apply_offset(self.static_map_image.get_rect()))

        self.image.blit(model.player.image, self.camera.apply_offset(model.player.rect))

        screen.blit(self.image, self.rect)


class TopBarPanel(BasePanel):
    def __init__(self, size, pos, font, assets, game_manager):
        super().__init__(size, pos, bg_color=Colors.TRANSPARENT_COLOR)
        self.font = font
        self.objective_text = game_manager.game_model.objective_text
        self.game_manager = game_manager

        self._create_buttons(assets)
        self._draw_static_elements()

    def _create_buttons(self, assets):
        center_y = self.height // 2
        self.buttons = {
            "options": IconButton(assets.get_image("icons/options.png"), (30, center_y), (40, 40), Colors.GRAY_COLOR, Colors.DARK_GRAY_COLOR, border_radius=10),
            "idea": IconButton(assets.get_image("icons/idea.png"), (self.width - 130, center_y), (40, 40), Colors.GRAY_COLOR, Colors.DARK_GRAY_COLOR, border_radius=10),
            "music": IconButton(assets.get_image("icons/music_note.png"), (self.width - 80, center_y), (40, 40), Colors.GRAY_COLOR, Colors.DARK_GRAY_COLOR, border_radius=10),
            "inventory": IconButton(assets.get_image("icons/bag.png"), (self.width - 30, center_y), (40, 40), Colors.GRAY_COLOR, Colors.DARK_GRAY_COLOR,10)
        }

    def _draw_static_elements(self):
        bg_objective_rect = pygame.Rect(0, 0, 400, self.height - 10)
        bg_objective_rect.center = (self.width // 2, self.height // 2)
        pygame.draw.rect(self.image, Colors.WHITE_COLOR, bg_objective_rect, border_radius=10)

        text_surface = self.font.render(self.objective_text, True, Colors.BLACK_COLOR)
        self.image.blit(text_surface, text_surface.get_rect(center=bg_objective_rect.center))

        for button in self.buttons.values():
            button.draw(self.image)

    def update(self, mouse_pos):
        local_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
        for button in self.buttons.values():
            button.update(local_pos)

    def update_elements(self):
        self.objective_text = self.game_manager.game_model.objective_text
        self._draw_static_elements()

    def draw(self, screen: pygame.Surface, model, assets=None):
        if self.is_visible:
            for button in self.buttons.values():
                button.draw(self.image)
            screen.blit(self.image, self.rect)


class InventoryPanel(BasePanel):
    def __init__(self, size, pos, font, assets, game_manager):
        super().__init__(size, pos, "INVENTÁRIO", font, is_visible=False)
        self.game_manager = game_manager
        self.inventory_items = []
        self.overlay = pygame.Surface(pygame.display.get_surface().get_size(), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 240))

        self.slot_rects = []
        self.slot_width = 64
        self.slot_height = 64
        self.max_slot_row = (self.height - 60) // self.slot_height
        self.max_slot_col = (self.width - 10) // self.slot_width

        self.__create_slot_rects(assets)

    def __create_slot_rects(self, assets):
        slot_surf = pygame.transform.smoothscale(assets.get_image("black_frame.png"), (self.slot_width, self.slot_height))

        for i in range(self.max_slot_row):
            row_rects = []
            for j in range(self.max_slot_col):
                row_rects.append(slot_surf.get_rect(topleft=(5 + slot_surf.get_width() * j, 60)))
                self.image.blit(slot_surf, row_rects[j])
            self.slot_rects.append(row_rects)

    def get_slot_rect_hovered(self, mouse_pos):
        local_mouse_pos = mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y

        for i, rect_row in enumerate(self.slot_rects):
            for j, rect in enumerate(rect_row):
                if rect.collidepoint(local_mouse_pos):
                    return (i * self.max_slot_col) + j
        return None

    def update(self, assets):
        self.__create_slot_rects(assets)

    def draw(self, screen, model=None, assets=None):
        if self.is_visible:
            image_surf = self.image.copy()
            screen.blit(self.overlay, (0, 0))
            player_inventory_items = self.game_manager.game_model.player.inventory.items
            for i, item in enumerate(player_inventory_items):
                pos_row = i // self.max_slot_row
                pos_col = i % self.max_slot_col
                image_surf.blit(pygame.transform.smoothscale(item.image, (self.slot_width, self.slot_height)), self.slot_rects[pos_row][pos_col])
            screen.blit(image_surf, self.rect)


class ToolsPanel(BasePanel):
    def __init__(self, size, pos, font, assets, game_manager):
        super().__init__(size, pos, "FERRAMENTAS", font)
        self.game_manager = game_manager
        self.assets = assets

        self.base_image = self.image.copy()

        self._create_buttons()
        self._draw_buttons_on_panel()

    def _create_buttons(self):
        row_buttons_count = (self.width - 5) // 55
        self.buttons = {}
        for i, type_button in enumerate(self.game_manager.game_model.available_actions):
            center_pos = (30 + 55 * (i % row_buttons_count), 55 + 55 * (i // row_buttons_count))
            self.buttons[type_button] = IconButton(self.assets.get_image(f"icons/{type_button.lower()}.png"), center_pos, (50, 50), Colors.GRAY_COLOR, Colors.DARK_GRAY_COLOR, border_radius=10)

    def _draw_buttons_on_panel(self):
        for button in self.buttons.values():
            button.draw(self.image)

    def update(self, mouse_pos):
        local_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
        for button in self.buttons.values():
            button.update(local_pos)

    def update_elements(self):
        self.image = self.base_image.copy()
        self._create_buttons()

    def draw(self, screen: pygame.Surface, model=None, assets=None):
        super().draw(screen, self.game_manager.game_model)
        if self.is_visible:
            for button in self.buttons.values():
                button.draw(self.image)
            screen.blit(self.image, self.rect)


class ExecutionPanel(BasePanel):
    def __init__(self, size, pos, font, assets, game_manager):
        super().__init__(size, pos, "SEQUÊNCIA DE EXECUÇÃO", font)
        self.assets = assets
        self.game_manager = game_manager
        self.EXECUTION_ROWS_NUM = 2
        self.EXECUTION_COLS_NUM = 13

        self.slot_width = 40
        self.slot_height = 40

        self.slot_rects = self._calculate_slot_rects()
        self.static_background = self._create_static_background()
        self.image.blit(self.static_background, (0, 0))

        self._create_buttons(assets)

        self.dragged_info = {"index": None, "pos": (0, 0)}

        self.command_buttons = []
        self._current_command_signature = ""

        self.default_bg = self.image.copy()

    def _calculate_slot_rects(self):
        rects = []
        for i in range(self.EXECUTION_ROWS_NUM * self.EXECUTION_COLS_NUM):
            row = i // self.EXECUTION_COLS_NUM
            col = i % self.EXECUTION_COLS_NUM

            x = 10 + col * self.slot_width
            y = 30 + row * self.slot_height

            rects.append(pygame.Rect(x, y, self.slot_width, self.slot_height))
        return rects

    def _create_buttons(self, assets):
        self.buttons = {
            "execute": IconButton(assets.get_image("icons/play.png"), (self.width - 30, 30), (50, 50), Colors.LIGHT_GREEN_COLOR, Colors.GRAY_COLOR, 10),
            "clear": IconButton(assets.get_image("icons/trash.png"), (self.width - 30, 90), (50, 50), Colors.RED_COLOR, Colors.GRAY_COLOR, 10)
        }

    def _create_static_background(self):
        background = self.image.copy()
        frame_img = self.assets.get_image("black_frame.png")
        scaled_frame = pygame.transform.smoothscale(frame_img, (self.slot_width, self.slot_height))

        for slot_rect in self.slot_rects:
            background.blit(scaled_frame, slot_rect)
        return background

    def _sync_buttons_with_model(self):
        self.command_buttons.clear()
        model_actions = self.game_manager.game_model.actions_sequence

        for i, action in enumerate(model_actions):
            command_button_icon = self.assets.get_image(f"icons/{action.action_name.lower()}.png")
            cancel_button_icon = self.assets.get_image(f"icons/cancel.png")
            command_pos = self.slot_rects[i].topleft
            cancel_pos = (command_pos[0] + 25, command_pos[1])
            size = (self.slot_width, self.slot_height)

            if i < len(self.command_buttons):
                self.command_buttons[i][0].rect.topleft = command_pos
                self.command_buttons[i][1].rect.topleft = cancel_pos
                pass
            else:
                command_button = IconButton(command_button_icon, command_pos, size, Colors.TRANSPARENT_COLOR, Colors.TRANSPARENT_COLOR, name=action.action_name)
                cancel_button = IconButton(cancel_button_icon, cancel_pos, (15, 15), Colors.GRAY_COLOR, Colors.GRAY_COLOR,
                                           name="cancel_button")
                command_button.rect.topleft = command_pos
                cancel_button.rect.topleft = cancel_pos
                self.command_buttons.append((command_button, cancel_button))

        self._current_command_signature = "".join([a.action_name for a in model_actions])

    def get_clicked_command_info(self, mouse_pos):
        local_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
        for key, buttons in enumerate(self.command_buttons):
            button_info = {"index": key}
            if buttons[0].rect.collidepoint(local_pos):
                if buttons[1].rect.collidepoint(local_pos):
                    button_info["action"] = buttons[1].name
                else:
                    button_info["action"] = buttons[0].name
                return button_info
        return None

    def start_drag(self, index, pos):
        if not (0 <= index < len(self.game_manager.game_model.actions_sequence)):
            return
        self.dragged_info["index"] = index
        self.dragged_info["pos"] = pos

    def update_drag(self, pos):
        local_pos = (pos[0] - self.rect.x, pos[1] - self.rect.y)
        if self.dragged_info["index"] is not None:
            for button in self.command_buttons[self.dragged_info["index"]]:
                button.rect.topleft = local_pos

    def stop_drag(self, mouse_pos):
        slot_index = self.get_slot_index(mouse_pos)

        if slot_index is not None:
            self._sync_buttons_with_model()

        self.dragged_info["index"] = None

    def get_slot_index(self, mouse_pos):
        local_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
        for key, slot_rect in enumerate(self.slot_rects):
            if slot_rect.collidepoint(local_pos):
                return key
        return None

    def update(self, mouse_pos):
        local_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
        for button in self.buttons.values():
            button.update(local_pos)

        model_signature = "".join([a.action_name for a in self.game_manager.game_model.actions_sequence])
        if model_signature != self._current_command_signature:
            self._sync_buttons_with_model()

        for buttons in self.command_buttons:
            for button in buttons:
                button.update(local_pos)

    def draw(self, screen: pygame.Surface, model, assets=None, is_dragging=False, dragged_command_index=-1):
        if not self.is_visible:
            return
        self.image.blit(self.static_background, (0, 0))
        for i, buttons in enumerate(self.command_buttons):
            for button in buttons:
                if i == self.game_manager.game_model.current_action_index:
                    pygame.draw.rect(self.image, Colors.LIGHT_GREEN_COLOR, pygame.Rect(button.rect.x, button.rect.y, button.rect.width, button.rect.height))
                button.draw(self.image)


        for button in self.buttons.values():
            button.draw(self.image)

        screen.blit(self.image, self.rect)

    def pos_slot_collide(self, mouse_pos):
        for i, slot_rect in enumerate(self.slot_rects):
            if slot_rect.collidepoint(mouse_pos):
                row_index = i if i <= 12 else i - 13
                col_index = i // 12
                return (row_index, col_index), i
        return None, None


class OptionsPanel(BasePanel):
    def __init__(self, size, pos, font, assets):
        super().__init__(size, pos, "Opções", font, is_visible=False)

        self.rect.x -= self.width // 2
        self.rect.y -= self.height // 2

        self.buttons = {}
        self._create_buttons(assets)

    def _create_buttons(self, assets):
        self.buttons = {
            "close": IconButton(assets.get_image("icons/cancel.png"), (self.width - 15, 15), (20, 20), Colors.GRAY_COLOR, Colors.DARK_GRAY_COLOR, border_radius=5)
        }

    def update(self, mouse_pos):
        local_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)

        for button in self.buttons.values():
            button.update(local_pos)

    def draw(self, screen, model, assets=None):
        if self.is_visible:
            for button in self.buttons.values():
                button.draw(self.image)

            screen.blit(self.image, self.rect)


class InfoPanel(BasePanel):
    def __init__(self, size, pos, font, assets, game_manager):
        super().__init__(size, pos, "", font, is_visible=True)
        self.game_manager = game_manager

        self.text_font = pygame.font.SysFont("monospace", 15)

        self.__create_elements(assets)

    def __create_elements(self, assets):
        item_hand_text = self.text_font.render("Item segurado:", True, True)
        self.image.blit(item_hand_text, (10, 10))
        self.item_map_count_text = self.text_font.render("Coletaveis: 0", True, True)
        self.image.blit(self.item_map_count_text, (10, 40))
        self.item_hand_slot_surf = pygame.transform.smoothscale(assets.get_image("black_frame.png"), (32, 32))

    def update(self):
        self.item_map_count_text = self.text_font.render(f"Coletaveis: {self.game_manager.game_model.get_count_collectibles_available()}", True, True)

    def draw(self, screen, model=None, assets=None):
        if self.is_visible:
            player_item_hand = self.game_manager.game_model.player.item_hand

            pygame.draw.rect(self.image, Colors.WHITE_COLOR, self.item_hand_slot_surf.get_rect(topleft=(150, 5)))
            self.image.blit(self.item_hand_slot_surf, (150, 5))
            if player_item_hand is not None:
                self.image.blit(player_item_hand.image, (150, 5))

            pygame.draw.rect(self.image, Colors.WHITE_COLOR, self.item_map_count_text.get_rect(topleft=(10, 40)))
            self.image.blit(self.item_map_count_text, (10, 40))
            screen.blit(self.image, self.rect)


class RepeatConfigPanel(BasePanel):
    """
    Um painel pop-up para configurar o número de repetições de um RepeatCommand.
    """

    def __init__(self, size, pos, font, assets):
        # Centraliza o painel na tela
        centered_pos = (pos[0] - size[0] // 2, pos[1] - size[1] // 2)
        super().__init__(size, centered_pos, "CONFIGURAR REPETIÇÃO", font, is_visible=True)

        self.assets = assets
        self.font = font

        # Armazena o índice do comando que está sendo editado
        self.target_command_index = None
        self.current_count = 1

        # Superfície de overlay para escurecer o fundo
        self.overlay = pygame.Surface(pygame.display.get_surface().get_size(), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 200))  # Fundo escuro semitransparente

        self._create_elements()

    def _create_elements(self):
        """Cria os botões internos do painel."""
        self.buttons = {
            "minus": IconButton(self.assets.get_image("icons/back.png"), (self.width // 2 - 60, self.height // 2),
                                (40, 40), Colors.GRAY_COLOR, Colors.DARK_GRAY_COLOR, 10),
            "plus": IconButton(self.assets.get_image("icons/forward.png"), (self.width // 2 + 60, self.height // 2),
                               (40, 40), Colors.GRAY_COLOR, Colors.DARK_GRAY_COLOR, 10),
            "ok": IconButton(self.assets.get_image("icons/back.png"), (self.width // 2, self.height - 40), (40, 40),
                             Colors.LIGHT_GREEN_COLOR, Colors.DARK_GRAY_COLOR, 10),
        }

    def open_for_command(self, command_index: int, current_repeat_count: int):
        """Abre o painel para um comando específico."""
        self.target_command_index = command_index
        # Garante que o contador comece em pelo menos 1
        self.current_count = max(1, current_repeat_count)
        self.is_visible = True

    def close_panel(self):
        """Fecha o painel e reseta seu estado."""
        self.is_visible = False
        self.target_command_index = None
        self.current_count = 1

    def get_clicked_button(self, mouse_pos) -> str | None:
        """Verifica qual botão interno foi clicado."""
        local_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
        for name, button in self.buttons.items():
            if button.rect.collidepoint(local_pos):
                return name
        return None

    def update(self, mouse_pos):
        """Atualiza o estado de hover dos botões internos."""
        if not self.is_visible:
            return

        local_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
        for button in self.buttons.values():
            button.update(local_pos)

    def draw(self, screen, model, assets=None):
        """Desenha o painel, o overlay e o contador numérico."""
        if not self.is_visible:
            return

        # 1. Desenha o overlay escuro
        screen.blit(self.overlay, (0, 0))

        # 2. Desenha o painel base (chama o draw da BasePanel)
        super().draw(screen, model, assets)

        # 3. Desenha os botões
        for button in self.buttons.values():
            button.draw(self.image)

        # 4. Desenha o texto do contador
        count_font = self.assets.get_font("Monospace", 30)  # Fonte maior para o número
        count_surf = count_font.render(str(self.current_count), True, Colors.BLACK_COLOR)
        count_rect = count_surf.get_rect(center=(self.width // 2, self.height // 2))
        self.image.blit(count_surf, count_rect)

        # 5. Blita a imagem final do painel (que agora contém os botões e texto)
        screen.blit(self.image, self.rect)