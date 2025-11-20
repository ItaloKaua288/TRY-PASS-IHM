import json

import pygame
from os import path, listdir

from src import config


class AssetsManager:
    def __init__(self):
        self.assets_path = path.join(config.BASE_PATH, 'src', 'assets')
        self.images = {}
        self.fonts = {}
        self.tilesets = {}
        self.frames = {}
        self.level_data = {}

    def get_font(self, name, size):
        key = f"{name}_{size}"
        if key not in self.fonts:
            try:
                self.fonts[key] = pygame.font.SysFont(name, size, True)
            except pygame.error:
                self.fonts[key] = pygame.font.SysFont(None, size)
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
                self.tilesets[relative_path][tile_id] = pygame.transform.smoothscale(surface, (config.TILE_SIZE, config.TILE_SIZE))
        return self.tilesets[relative_path]

    def get_level_data(self, relative_path):
        if relative_path not in self.level_data:
            full_path = path.join(config.BASE_PATH, relative_path)
            try:
                with open(full_path, 'r', encoding='utf-8') as file:
                    level_data = json.load(file)

                    self.level_data[relative_path] = {
                        "objective_text": level_data["objective_text"],
                        "tile_map": level_data["tile_map"],
                        "player_start_pos": level_data["player_start_pos"],
                        "final_objective_pos": level_data["final_objective_pos"],
                        "interactable_objects": level_data["interactable_objects"],
                        "available_actions": level_data["available_actions"],
                        "enemies": level_data["enemies"]
                    }
                    file.close()
            except (FileNotFoundError, KeyError):
                return None
        return self.level_data[relative_path]
