import pygame
from .ui_elements import IconButton, TextButton
from . import  camera

from src.config import TILE_SIZE, BLACK_COLOR, WHITE_COLOR, GRAY_COLOR, LIGHT_GREEN_COLOR, DARK_GRAY_COLOR, TRANSPARENT_COLOR


class BasePanel:
    def __init__(self, size, topleft_pos, title_text=None, font=None, bg_color=WHITE_COLOR, title_color=BLACK_COLOR,
                 border_radius=10, is_visible=True):
        self.width, self.height = size
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=topleft_pos)
        self.is_visible = is_visible

        self._draw_static_content(font, title_text, bg_color, title_color, border_radius)

    def _draw_static_content(self, font, title_text, bg_color, title_color, border_radius):
        pygame.draw.rect(self.image, bg_color, self.image.get_rect(), border_radius=border_radius)
        if title_text and font:
            title_surface = font.render(title_text, True, title_color)
            title_rect = title_surface.get_rect(center=(self.width // 2, 15))
            self.image.blit(title_surface, title_rect)

    def draw(self, screen, model, assets=None):
        if self.is_visible:
            screen.blit(self.image, self.rect)


class MapPanel:
    def __init__(self, size, pos, tile_map_data, assets):
        self.width, self.height = size
        self.tile_size = (TILE_SIZE, TILE_SIZE)
        self.tile_set = assets.get_tileset("sprites/tiles_map", self.tile_size)
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=pos)

        self.static_map_image = self._pre_render_map(tile_map_data)
        self.static_map_image_rect = self.static_map_image.get_rect()

        self.camera = camera.Camera((self.width, self.height), self.static_map_image.get_size())

    def _pre_render_map(self, tile_map_data):
        tile_size_x, tile_size_y = self.tile_size

        surface = pygame.Surface((len(tile_map_data[0]) * tile_size_x, len(tile_map_data) * tile_size_y))
        for i, row in enumerate(tile_map_data):
            for j, tile_id in enumerate(row):
                pos = (tile_size_x * j, tile_size_y * i)
                surface.blit(self.tile_set[tile_id], pos)
        return surface

    def draw(self, screen, model, assets):
        self.image.fill((0, 0, 0))
        self.camera.update(model.player.rect)

        self.image.blit(self.static_map_image, self.camera.apply_offset(self.static_map_image_rect))

        player_rect_in_world = pygame.Rect(model.player.rect.x, model.player.rect.y, self.tile_size[0], self.tile_size[1])
        self.image.blit(model.player.image, self.camera.apply_offset(player_rect_in_world))

        screen.blit(self.image, self.rect)


class TopBarPanel:
    def __init__(self, size, pos, font, objective_text, assets):
        self.width, self.height = size
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=pos)
        self.font = font
        self.objective_text = objective_text

        self._load_assets(assets)

    def _load_assets(self, assets):
        center_y = self.height // 2
        self.buttons = {
            "options": IconButton(assets.get_image("icons/options.png"), (30, center_y), (40, 40), WHITE_COLOR, GRAY_COLOR, 100),
            "idea": IconButton(assets.get_image("icons/idea.png"), (self.width - 80, center_y), (40, 40), WHITE_COLOR, GRAY_COLOR, 100),
            "music_note": IconButton(assets.get_image("icons/music_note.png"), (self.width - 30, center_y), (40, 40), WHITE_COLOR, GRAY_COLOR, 100)
        }

    def update(self, mouse_pos):
        local_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
        for button in self.buttons.values():
            button.update(local_pos)

    def draw(self, screen, model, assets):
        self.image.fill((0, 0, 0, 0))

        bg_objective = pygame.Rect(0, 0, 550, self.height - 10)
        bg_objective.center = (self.width // 2, self.height // 2)
        pygame.draw.rect(self.image, WHITE_COLOR, bg_objective, border_radius=10)

        objective_text_surface = self.font.render(self.objective_text, True, (0, 0, 0))
        self.image.blit(objective_text_surface, objective_text_surface.get_rect(center=bg_objective.center))

        for button in self.buttons.values():
            button.draw(self.image)

        screen.blit(self.image, self.rect)


class InventoryPanel(BasePanel):
    def __init__(self, size, pos, font):
        super().__init__(size, pos, "INVENTÁRIO", font, is_visible=False)

    def draw(self, screen, model, assets=None):
        if self.is_visible:
            screen.fill((0, 0, 0, 180))
        super().draw(screen, model, assets)

class ToolsPanel(BasePanel):
    def __init__(self, size, pos, font, assets):
        super().__init__(size, pos, "CAIXA DE FERRAMENTAS", font)

        self._create_elements(assets)
        self.draw_elements()

    def _create_elements(self, assets):
        button_font = assets.get_font("Monospace", 10)
        self.buttons = {
            "walk": IconButton(assets.get_image(r"icons/walk.png"), (30, 55), (50, 50), DARK_GRAY_COLOR, GRAY_COLOR, border_radius=10),
            "turn_right": IconButton(assets.get_image(r"icons/turn_right.png"), (85, 55), (50, 50), DARK_GRAY_COLOR, GRAY_COLOR, border_radius=10),
            "turn_left": IconButton(assets.get_image(r"icons/turn_left.png"), (140, 55), (50, 50), DARK_GRAY_COLOR, GRAY_COLOR, border_radius=10),
            "repeat": IconButton(assets.get_image(r"icons/repeat.png"), (30, 110), (50, 50), DARK_GRAY_COLOR, GRAY_COLOR, border_radius=10),
            "end_repeat": IconButton(assets.get_image(r"icons/end_repeat.png"), (85, 110), (50, 50), DARK_GRAY_COLOR, GRAY_COLOR, border_radius=10)
        }

    def draw_elements(self):
        for button in self.buttons.values():
            button.draw(self.image)

    def update(self, mouse_pos):
        mouse_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
        for button in self.buttons.values():
            button.update(mouse_pos)
        self.draw_elements()

class ExecutionPanel(BasePanel):
    def __init__(self, size, pos, font, assets):
        super().__init__(size, pos, "SEQUÊNCIA DE EXECUÇÃO", font)
        self.assets = assets
        self._create_elements(assets)
        self._draw_static_elements(self.assets)
        self.buttons_sequence = []

        self.default_bg = self.image.copy()

        self.slot_rects = self._calculate_slot_rects()

    def _create_elements(self, assets):
        self.buttons = {
            "execute": IconButton(assets.get_image("icons/play.png"), (self.width - 30, self.height // 2), (40, self.height - 10), LIGHT_GREEN_COLOR, GRAY_COLOR, 100),
        }

    def _calculate_slot_rects(self):
        rects = []

        size_frame_x = (self.width - 60) // 14
        size_frame_y = (self.height - 90)

        for i in range(2):
            if i == 0:
                y_pos = size_frame_y * i + 30
            else:
                y_pos = size_frame_x * i + 12
            for j in range(13):
                x_pos = size_frame_x * j + 10
                rects.append(pygame.Rect(x_pos, y_pos, size_frame_x, size_frame_y))
        return rects

    def pos_slot_collide(self, mouse_pos):
        for i, slot_rect in enumerate(self.slot_rects):
            if slot_rect.collidepoint(mouse_pos):
                row_index = i if i <= 12 else i - 13
                col_index = i // 12
                return (row_index, col_index), i
        return None, None

    def update(self, mouse_pos):
        mouse_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
        self.buttons["execute"].update(mouse_pos)

        for buttons in self.buttons_sequence:
            for button in buttons:
                button.update(mouse_pos)

    def _draw_static_elements(self, assets):
        size_frame_x = (self.width - 60) // 14
        size_frame_y = (self.height - 40) // 2

        black_frame_relative_path = "black_frame.png"
        frame_surface = pygame.transform.smoothscale(assets.get_image(black_frame_relative_path),(size_frame_x, size_frame_y))

        for i in range(2):
            for j in range(13):
                self.image.blit(frame_surface, (size_frame_x * j + 10, size_frame_y * i + 30))

    def is_actions_sequence_updated(self, model):
        new_command_sequence = [action.action_name for action in model.actions_sequence]
        current_command_sequence = [action[0].name for action in self.buttons_sequence]

        return new_command_sequence == current_command_sequence

    def get_size_frame_command(self):
        size_frame_x = (self.width - 60) // 14
        size_frame_y = (self.height - 110)

        return size_frame_x, size_frame_y

    def calculate_pos_command_buttons(self):
        positions = []
        size_frame_x, size_frame_y = self.get_size_frame_command()
        for i in range(25):
            if 26 / (i + 1) >= 2:
                x_pos, y_pos = (size_frame_x * i + 10, size_frame_y)
            else:
                x_pos, y_pos = (size_frame_x * (i - 13) + 10, size_frame_y + 50)
            command_pos = (x_pos, y_pos)
            change_pos = command_pos
            cancel_pos = (x_pos + 49, y_pos)
            positions.append((command_pos, change_pos, cancel_pos))
        return positions

    def draw(self, screen, model, assets=None, is_dragging=False, dragged_command_index=-1):
        super().draw(screen, model)
        self.image.blit(self.default_bg, (0, 0))
        self.buttons["execute"].draw(self.image)

        if not self.is_actions_sequence_updated(model):
            self._draw_static_elements(self.assets)

            size_frame_x, size_frame_y = self.get_size_frame_command()

            self.buttons_sequence.clear()

            for i, action in enumerate(model.actions_sequence):
                if is_dragging and i == dragged_command_index:
                    continue

                command_button_icon = assets.get_image(f"icons/{action.action_name.lower()}.png")
                change_button_icon = assets.get_image(f"icons/change.png")
                cancel_button_icon = assets.get_image(f"icons/cancel.png")

                if 26 / (i+1) >= 2:
                    x_pos, y_pos = (size_frame_x * i + 10, size_frame_y)
                else:
                    x_pos, y_pos = (size_frame_x * (i-13) + 10, size_frame_y + 50)

                command_button_pos = (x_pos, y_pos)
                change_button_pos = (x_pos, y_pos)
                cancel_button_pos = (x_pos + 49, y_pos)

                command_button = IconButton(command_button_icon, command_button_pos, (69, 50), TRANSPARENT_COLOR, TRANSPARENT_COLOR,
                                            name=action.action_name)
                change_button = IconButton(change_button_icon, change_button_pos, (20, 20), GRAY_COLOR, GRAY_COLOR,
                                           name="change_button")
                cancel_button = IconButton(cancel_button_icon, cancel_button_pos, (20, 20), GRAY_COLOR, GRAY_COLOR,
                                           name="cancel_button")

                command_button.rect.topleft = command_button_pos
                change_button.rect.topleft = change_button_pos
                cancel_button.rect.topleft = cancel_button_pos

                self.buttons_sequence.append([command_button, change_button, cancel_button])

        for buttons in self.buttons_sequence:
            for button in buttons:
                if button.is_visible:
                    self.image.blit(button.image, button.rect)

        # for k, action in enumerate(model.actions_sequence):
        #     # if is_dragging and k == dragged_command_index:
        #     #     continue
        #
        #     icon_path = f"icons/{action.action_name.lower()}.png"
        #     button = IconButton(assets.get_image(icon_path), (size_frame_x * k + 20, size_frame_y), (69, 50), TRANSPARENT_COLOR, TRANSPARENT_COLOR, name=action.action_name)
        #     button.rect.topleft = (size_frame_x * k + 20, size_frame_y + 20)
        #
        #     if 26 / (k+1) >= 2:
        #         pos = (size_frame_x * k + 10, size_frame_y)
        #         self.image.blit(button.image, pos)
        #     else:
        #         pos = (size_frame_x * (k-13) + 10, size_frame_y+50)
        #         self.image.blit(button.image, pos)
        #
        #     button.rect.topleft = pos
        #     self.buttons_sequence.append(button)