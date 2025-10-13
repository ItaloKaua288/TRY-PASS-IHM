import pygame
from .ui_elements import IconButton
from . import  camera

from src.config import TILE_SIZE, BLACK_COLOR, WHITE_COLOR, GRAY_COLOR, LIGHT_GREEN_COLOR, DARK_GRAY_COLOR, TRANSPARENT_COLOR


class BasePanel:
    def __init__(self, size, topleft_pos, title_text=None, font=None, bg_color=WHITE_COLOR, title_color=BLACK_COLOR,
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
    def __init__(self, size, pos, tile_map_data, assets):
        self.width, self.height = size
        self.tile_size = (TILE_SIZE, TILE_SIZE)
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=pos)

        tile_set = assets.get_tileset("sprites/tiles_map", self.tile_size)
        self.static_map_image = self._pre_render_map(tile_map_data, tile_set)

        self.camera = camera.Camera((self.width, self.height), self.static_map_image.get_size())

    def _pre_render_map(self, tile_map_data, tile_set):
        map_width = len(tile_map_data[0]) * self.tile_size[0]
        map_height = len(tile_map_data) * self.tile_size[1]
        map_surface = pygame.Surface((map_width, map_height))

        for i, row in enumerate(tile_map_data):
            for j, tile_id in enumerate(row):
                pos = (self.tile_size[0] * j, self.tile_size[1] * i)
                if tile_id in tile_set:
                    map_surface.blit(tile_set[tile_id], pos)
        return map_surface

    def draw(self, screen, model, assets):
        self.image.fill(BLACK_COLOR)
        self.camera.update(model.player.rect)

        self.image.blit(self.static_map_image, self.camera.apply_offset(self.static_map_image.get_rect()))

        self.image.blit(model.player.image, self.camera.apply_offset(model.player.rect))

        screen.blit(self.image, self.rect)


class TopBarPanel(BasePanel):
    def __init__(self, size, pos, font, objective_text, assets):
        super().__init__(size, pos, bg_color=TRANSPARENT_COLOR)
        self.font = font
        self.objective_text = objective_text

        self._create_buttons(assets)
        self._draw_static_elements()

    def _create_buttons(self, assets):
        center_y = self.height // 2
        self.buttons = {
            "options": IconButton(assets.get_image("icons/options.png"), (30, center_y), (40, 40), GRAY_COLOR, DARK_GRAY_COLOR, border_radius=50),
            "idea": IconButton(assets.get_image("icons/idea.png"), (self.width - 80, center_y), (40, 40), GRAY_COLOR, DARK_GRAY_COLOR, border_radius=50),
            "music": IconButton(assets.get_image("icons/music_note.png"), (self.width - 30, center_y), (40, 40), GRAY_COLOR, DARK_GRAY_COLOR, border_radius=50)
        }

    def _draw_static_elements(self):
        bg_objective_rect = pygame.Rect(0, 0, 550, self.height - 10)
        bg_objective_rect.center = (self.width // 2, self.height // 2)
        pygame.draw.rect(self.image, WHITE_COLOR, bg_objective_rect, border_radius=10)

        text_surface = self.font.render(self.objective_text, True, BLACK_COLOR)
        self.image.blit(text_surface, text_surface.get_rect(center=bg_objective_rect.center))

        for button in self.buttons.values():
            button.draw(self.image)

    def update(self, mouse_pos):
        local_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
        for button in self.buttons.values():
            button.update(local_pos)

    def draw(self, screen: pygame.Surface, model, assets=None):
        super().draw(screen, model)
        if self.is_visible:
            for button in self.buttons.values():
                button.draw(self.image)
            screen.blit(self.image, self.rect)


class InventoryPanel(BasePanel):
    def __init__(self, size, pos, font):
        super().__init__(size, pos, "INVENTÁRIO", font, is_visible=False)

        self.overlay = pygame.Surface(pygame.display.get_surface().get_size(), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 240))

    def draw(self, screen, model, assets=None):
        if self.is_visible:
            screen.blit(self.overlay, (0, 0))
        super().draw(screen, model, assets)

class ToolsPanel(BasePanel):
    def __init__(self, size, pos, font, assets):
        super().__init__(size, pos, "CAIXA DE FERRAMENTAS", font)

        self._create_buttons(assets)
        self._draw_buttons_on_panel()

    def _create_buttons(self, assets):
        self.buttons = {
            "walk": IconButton(assets.get_image("icons/walk.png"), (30, 55), (50, 50), GRAY_COLOR, DARK_GRAY_COLOR, border_radius=10),
            "turn_right": IconButton(assets.get_image("icons/turn_right.png"), (85, 55), (50, 50), GRAY_COLOR, DARK_GRAY_COLOR, border_radius=10),
            "turn_left": IconButton(assets.get_image("icons/turn_left.png"), (140, 55), (50, 50), GRAY_COLOR, DARK_GRAY_COLOR, border_radius=10),
            "repeat": IconButton(assets.get_image("icons/repeat.png"), (30, 110), (50, 50), GRAY_COLOR, DARK_GRAY_COLOR, border_radius=10),
            "end_repeat": IconButton(assets.get_image("icons/end_repeat.png"), (85, 110), (50, 50), GRAY_COLOR, DARK_GRAY_COLOR, border_radius=10)
        }

    def _draw_buttons_on_panel(self):
        for button in self.buttons.values():
            button.draw(self.image)

    def update(self, mouse_pos):
        local_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
        for button in self.buttons.values():
            button.update(local_pos)

    def draw(self, screen: pygame.Surface, model, assets=None):
        super().draw(screen, model)
        if self.is_visible:
            for button in self.buttons.values():
                button.draw(self.image)
            screen.blit(self.image, self.rect)

class ExecutionPanel(BasePanel):
    def __init__(self, size, pos, font, assets, game_model):
        super().__init__(size, pos, "SEQUÊNCIA DE EXECUÇÃO", font)
        self.assets = assets
        self.game_model = game_model
        self.EXECUTION_ROWS_NUM = 2
        self.EXECUTION_COLS_NUM = 13

        self.slot_width = (self.width - (self.EXECUTION_COLS_NUM + 1) * 10) // self.EXECUTION_COLS_NUM
        self.slot_height = (self.height - 10 - (self.EXECUTION_ROWS_NUM + 1) * 10) // self.EXECUTION_ROWS_NUM

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
            "execute": IconButton(assets.get_image("icons/play.png"), (self.width - 30, self.height // 2), (40, self.height - 10), LIGHT_GREEN_COLOR, GRAY_COLOR, 100),
        }

    def _create_static_background(self):
        background = self.image.copy()
        frame_img = self.assets.get_image("black_frame.png")
        scaled_frame = pygame.transform.smoothscale(frame_img, (self.slot_width, self.slot_height))

        for slot_rect in self.slot_rects:
            background.blit(scaled_frame, slot_rect)
        return background

    def _sync_buttons_with_model(self, model_actions):
        # while len(self.command_buttons) > len(model_actions):
        #     self.command_buttons.pop()
        self.command_buttons.clear()

        for i, action in enumerate(model_actions):
            command_button_icon = self.assets.get_image(f"icons/{action.action_name.lower()}.png")
            change_button_icon = self.assets.get_image(f"icons/change.png")
            cancel_button_icon = self.assets.get_image(f"icons/cancel.png")
            command_pos = self.slot_rects[i].topleft
            cancel_pos = (command_pos[0] + 48, command_pos[1])
            size = (self.slot_width, self.slot_height)

            if i < len(self.command_buttons):
                # self.command_buttons[i].update_icon(icon)
                self.command_buttons[i][0].rect.topleft = command_pos
                self.command_buttons[i][1].rect.topleft = command_pos
                self.command_buttons[i][2].rect.topleft = cancel_pos
                pass
            else:
                command_button = IconButton(command_button_icon, command_pos, size, TRANSPARENT_COLOR, TRANSPARENT_COLOR, name=action.action_name)
                change_button = IconButton(change_button_icon, command_pos, (20, 20), GRAY_COLOR, GRAY_COLOR,
                                           name="change_button")
                cancel_button = IconButton(cancel_button_icon, cancel_pos, (20, 20), GRAY_COLOR, GRAY_COLOR,
                                           name="cancel_button")
                command_button.rect.topleft = command_pos
                change_button.rect.topleft = command_pos
                cancel_button.rect.topleft = cancel_pos
                self.command_buttons.append((command_button, change_button, cancel_button))

        self._current_command_signature = "".join([a.action_name for a in model_actions])

    def get_clicked_command_info(self, mouse_pos):
        local_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
        for key, buttons in enumerate(self.command_buttons):
            button_info = {"index": key}
            if buttons[1].rect.collidepoint(local_pos):
                button_info["action"] = buttons[1].name
                return button_info
            elif buttons[2].rect.collidepoint(local_pos):
                button_info["action"] = buttons[2].name
                return button_info
        return None

    def start_drag(self, index, pos, game_model):
        if not (0 <= index < len(game_model.actions_sequence)):
            return
        self.dragged_info["index"] = index
        self.dragged_info["pos"] = pos

    def update_drag(self, pos):
        local_pos = (pos[0] - self.rect.x, pos[1] - self.rect.y)
        if self.dragged_info["index"] is not None:
            for button in self.command_buttons[self.dragged_info["index"]]:
                button.rect.topleft = local_pos

    def stop_drag(self, mouse_pos, game_model):
        slot_index = self.get_slot_index(mouse_pos)

        if slot_index is not None:
            self._sync_buttons_with_model(game_model.actions_sequence)

        self.dragged_info["index"] = None

    def get_slot_index(self, mouse_pos):
        local_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
        for key, slot_rect in enumerate(self.slot_rects):
            if slot_rect.collidepoint(local_pos):
                return key
        return None

    def update(self, mouse_pos):
        local_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
        self.buttons["execute"].update(local_pos)

        model_signature = "".join([a.action_name for a in self.game_model.actions_sequence])
        if model_signature != self._current_command_signature:
            self._sync_buttons_with_model(self.game_model.actions_sequence)

        for buttons in self.command_buttons:
            for button in buttons:
                button.update(local_pos)

    def draw(self, screen: pygame.Surface, model, assets=None, is_dragging=False, dragged_command_index=-1):
        if not self.is_visible:
            return

        self.image.blit(self.static_background, (0, 0))

        for i, buttons in enumerate(self.command_buttons):
            # if is_dragging and i == dragged_command_index:
            #     continue

            for button in buttons:
                button.draw(self.image)

        self.buttons["execute"].draw(self.image)

        screen.blit(self.image, self.rect)

    def pos_slot_collide(self, mouse_pos):
        for i, slot_rect in enumerate(self.slot_rects):
            if slot_rect.collidepoint(mouse_pos):
                row_index = i if i <= 12 else i - 13
                col_index = i // 12
                return (row_index, col_index), i
        return None, None