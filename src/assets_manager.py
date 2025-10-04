import json

import pygame
from os import path, listdir


class AssetsManager:
    def __init__(self):
        self.base_path = path.dirname(path.dirname(__file__))
        self.assets_path = path.join(self.base_path, 'src', 'assets')
        self.images = {}
        self.fonts = {}
        self.tilesets = {}
        self.frames = {}
        self.level_data = {}

    def get_font(self, name, size):
        key = f"{name}_{size}"
        if key not in self.fonts:
            self.fonts[key] = pygame.font.SysFont(name, size, True)
        return self.fonts[key]

    def get_image(self, relative_path):
        if relative_path not in self.images:
            full_path = path.join(self.assets_path, relative_path)
            self.images[relative_path] = pygame.image.load(full_path).convert_alpha()
        return self.images[relative_path]

    def get_tileset(self, relative_path, tile_size):
        if relative_path not in self.tilesets:
            self.tilesets[relative_path] = {}
            folder_path = path.join(self.assets_path, relative_path)
            for filename in listdir(folder_path):
                tile_id = int(filename.split('_')[1].split('.')[0])
                surface = self.get_image(path.join(relative_path, filename))
                self.tilesets[relative_path][tile_id] = pygame.transform.smoothscale(surface, tile_size)
        return self.tilesets[relative_path]

    def get_frames(self, relative_path):
        if relative_path not in self.frames:
            full_path = path.join(self.assets_path, relative_path)
            self.frames[relative_path] = pygame.image.load(full_path).convert_alpha()
        return self.frames[relative_path]

    def get_level_data(self, relative_path):
        if relative_path not in self.level_data:
            full_path = path.join(self.base_path, relative_path)
            try:
                with open(full_path) as file:
                    level_data = json.load(file)

                    self.level_data[relative_path] = {
                        "objective_text": level_data["objective"],
                        "tile_map": level_data["tile_map"],
                        "player_start_pos": level_data["player_start_pos"]
                    }
            except (FileNotFoundError, KeyError) as e:
                return None
        return self.level_data[relative_path]
