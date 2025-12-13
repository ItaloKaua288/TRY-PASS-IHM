import pygame
from os import path, listdir

from src.utils import settings


class AssetsManager:
    def __init__(self):
        self.assets_path = path.join(settings.BASE_PATH, 'assets')
        self.images = {}
        self.fonts = {}
        self.tilesets = {}
        self.frames = {}
        self.level_data = {}

    def get_font(self, name, size, bold=True):
        key = f"{name}_{size}_{bold}"
        if key not in self.fonts:
            try:
                # self.fonts[key] = pygame.font.SysFont("none", size, bold=bold)
                self.fonts[key] = pygame.font.Font("src/assets/fonts/SpaceMono-Bold.ttf", size)
            except pygame.error:
                self.fonts[key] = pygame.font.SysFont(None, size)
                pass
        return self.fonts[key]

    def get_image(self, relative_path):
        if relative_path not in self.images:
            full_path = path.join(self.assets_path, relative_path)
            self.images[relative_path] = pygame.image.load(full_path).convert_alpha()
        return self.images[relative_path]

    def get_tileset(self, relative_path):
        if relative_path not in self.tilesets:
            self.tilesets[relative_path] = {}
            folder_path = path.join(self.assets_path, relative_path)

            for filename in listdir(folder_path):
                tile_id = int(filename.split('_')[1].split('.')[0])
                surface = self.get_image(path.join(relative_path, filename))
                self.tilesets[relative_path][tile_id] = pygame.transform.smoothscale(surface, (settings.TILE_SIZE, settings.TILE_SIZE))
        return self.tilesets[relative_path]
