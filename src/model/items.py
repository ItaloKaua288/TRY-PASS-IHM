import pygame
from src.config import TILE_SIZE

class Item:
    def __init__(self, name, assets):
        self.name = name
        self.is_used = False
        self.is_colected = False

        self.image = pygame.transform.smoothscale(assets.get_image(f"sprites/items/{name}.png"), (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect()


class Chest:
    def __init__(self, pos, assets, internal_items=None):
        self.is_interacted = False
        self.pos = pos
        self.internal_items = [] if internal_items is None else internal_items

        self.image = pygame.transform.smoothscale(assets.get_image("sprites/items/chest.png"), (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=pos)

class Door:
    def __init__(self, pos, assets):
        self.is_interacted = False
        self.pos = pos

        self.image = pygame.transform.smoothscale(assets.get_image("sprites/items/door.png"), (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=pos)

