import pygame
from .ui_elements import IconButton
from . import  camera

from src.config import TILE_SIZE, BLACK_COLOR, WHITE_COLOR, GRAY_COLOR


class BasePanel:
    def __init__(self, size, topleft_pos, title_text=None, font=None, bg_color=WHITE_COLOR, title_color=BLACK_COLOR,
                 border_radius=10):
        self.width, self.height = size
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=topleft_pos)

        self._draw_static_content(font, title_text, bg_color, title_color, border_radius)

    def _draw_static_content(self, font, title_text, bg_color, title_color, border_radius):
        pygame.draw.rect(self.image, bg_color, self.image.get_rect(), border_radius=border_radius)
        if title_text and font:
            title_surface = font.render(title_text, True, title_color)
            title_rect = title_surface.get_rect(center=(self.width // 2, 15))
            self.image.blit(title_surface, title_rect)

    def draw(self, screen, model):
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

    def draw(self, screen, model):
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
        self.buttons = []

        icons = [
            assets.get_image("icons/options.png"),
            assets.get_image("icons/idea.png"),
            assets.get_image("icons/music_note.png")
        ]

        buttons_x_pos = [30, self.width - 80, self.width - 30]
        for i, icon in enumerate(icons):
            center_pos = (buttons_x_pos[i], self.height // 2)
            self.buttons.append(IconButton(icon, center_pos, (40, 40), WHITE_COLOR, GRAY_COLOR, 100))

    def update(self, mouse_pos):
        local_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
        for button in self.buttons:
            button.update(local_pos)

    def draw(self, screen, model):
        self.image.fill((0, 0, 0, 0))

        bg_objective = pygame.Rect(0, 0, 550, self.height - 10)
        bg_objective.center = (self.width // 2, self.height // 2)
        pygame.draw.rect(self.image, WHITE_COLOR, bg_objective, border_radius=10)

        objective_text_surface = self.font.render(self.objective_text, True, (0, 0, 0))
        self.image.blit(objective_text_surface, objective_text_surface.get_rect(center=bg_objective.center))

        for button in self.buttons:
            button.draw(self.image)

        screen.blit(self.image, self.rect)


class InventoryPanel(BasePanel):
    def __init__(self, size, pos, font):
        super().__init__(size, pos, "INVENTÁRIO", font)


class ToolsPanel(BasePanel):
    def __init__(self, size, pos, font):
        super().__init__(size, pos, "CAIXA DE FERRAMENTAS", font)


class ExecutionPanel(BasePanel):
    def __init__(self, size, pos, font, assets):
        super().__init__(size, pos, "SEQUÊNCIA DE EXECUÇÃO", font)

        self._draw_elements(assets)

    def _draw_elements(self, assets):
        size_frame_x = (self.width - 20) // 15
        size_frame_y = (self.height - 40) // 2

        black_frame_relative_path = "black_frame.png"
        frame_surface = pygame.transform.smoothscale(assets.get_frames(black_frame_relative_path),
                                                     (size_frame_x, size_frame_y))

        for i in range(2):
            for j in range(15):
                self.image.blit(frame_surface, (size_frame_x * j + 10, size_frame_y * i + 30))