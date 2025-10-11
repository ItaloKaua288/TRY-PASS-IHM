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
            "repeat": IconButton(assets.get_image(r"icons/repeat_icon.png"), (30, 110), (50, 50), DARK_GRAY_COLOR, GRAY_COLOR, border_radius=10),
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

    def _create_elements(self, assets):
        self.buttons = {
            "execute": IconButton(assets.get_image("icons/play.png"), (self.width - 30, self.height // 2), (40, self.height - 10), LIGHT_GREEN_COLOR, GRAY_COLOR, 100),
        }

    def update(self, mouse_pos):
        mouse_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
        self.buttons["execute"].update(mouse_pos)

    def _draw_static_elements(self, assets):
        size_frame_x = (self.width - 60) // 14
        size_frame_y = (self.height - 40) // 2

        black_frame_relative_path = "black_frame.png"
        frame_surface = pygame.transform.smoothscale(assets.get_image(black_frame_relative_path),(size_frame_x, size_frame_y))

        for i in range(2):
            for j in range(13):
                self.image.blit(frame_surface, (size_frame_x * j + 10, size_frame_y * i + 30))

    def draw(self, screen, model, assets=None):
        super().draw(screen, model)
        self.image.fill(WHITE_COLOR)

        self._draw_static_elements(self.assets)
        self.buttons["execute"].draw(self.image)

        size_frame_x = (self.width - 60) // 14
        size_frame_y = (self.height - 110)
        button_font = self.assets.get_font("Monospace", 8)

        self.buttons_sequence.clear()
        for k, action in enumerate(model.actions_sequence):
            icon_path = f"icons/{action.action_name.lower()}.png"
            button = IconButton(assets.get_image(icon_path), (size_frame_x * k + 20, size_frame_y), (69, 50), TRANSPARENT_COLOR, TRANSPARENT_COLOR, name=action.action_name)
            button.rect.topleft = (size_frame_x * k + 20, size_frame_y + 20)

            if 26 / (k+1) >= 2:
                pos = (size_frame_x * k + 10, size_frame_y)
                self.image.blit(button.image, pos)

            else:
                pos = (size_frame_x * (k-13) + 10, size_frame_y+50)
                self.image.blit(button.image, pos)

            button.rect.topleft = pos
            self.buttons_sequence.append(button)