from abc import ABC
import pygame
from src.utils.settings import TILE_SIZE

class BaseEntity(ABC):
    def __init__(self, pos):
        self.pos = pos

class Item:
    def __init__(self, name, quantity=1):
        self.name = name
        self.quantity = quantity

class Chest(BaseEntity):
    def __init__(self, pos, items=None):
        super().__init__(pos)
        self.is_opened = False

        if items is not None:
            self.items = items
        else:
            self.items = []

    def add_item(self, item: Item):
        for x in self.items:
            if x.name == item.name:
                x.quantity += 1
                return
        self.items.append(item)

    def remove_item(self, item: Item):
        for x in self.items:
            if x.name == item.name:
                if x.quantity > 1:
                    x.quantity -= 1
                else:
                    self.items.remove(item)
                return

class Door(BaseEntity):
    def __init__(self, pos, state, required_item=None):
        super().__init__(pos)
        self.state = state
        self.required_item = required_item


# class Enemy(BaseEntity):
#     def __init__(self, pos, subtype, life, direction, pattern, speed=1):
#         super().__init__(pos)
#         self.subtype = subtype
#         self.life = life
#         self.direction = direction
#         self.pattern = pattern
#         self.speed = speed

class PadlockWall(BaseEntity):
    def __init__(self, pos, required_item):
        super().__init__(pos)
        self.is_opened = False
        self.required_item = required_item

class DefaultEnemy(pygame.sprite.Sprite):
    def __init__(self, life, pos, movements_list, assets, subtype, image_path="images/sprites/goblin.png"):
        super().__init__()
        self.subtype = subtype
        self.assets = assets

        self.life = life
        self.movements = movements_list
        self.current_movement = 0
        self.velocity = 2

        self.pos = list(pos)
        self.direction_list = ["down", "right", "up", "left"]
        self.direction = "down"
        self.state = "idle"

        self.current_sprite = 0
        self.last_tick_sprite_update = 0
        self.rotation_count = 0
        self.direction_rotate = 1

        self.__load_sprites(image_path)

        self.rect = self.image.get_rect(topleft=self.pos)

    def __load_sprites(self, image_path):
        spritesheet = self.assets.get_image(image_path)

        states = ["idle", "moving", "rotating"]
        directions = ["down", "right", "up", "left"]

        FRAME_SIZE = 1000

        self.sprites = {}
        for i, state in enumerate(states):
            self.sprites[state] = {}
            for j, direction in enumerate(directions):
                sheet_y = i * 3000 + (j + (i % 3)) * FRAME_SIZE

                frames = []
                for x in range(4):
                    sheet_x = x * FRAME_SIZE

                    rect_clip = pygame.Rect(sheet_x, sheet_y, FRAME_SIZE, FRAME_SIZE)
                    subsurface = spritesheet.subsurface(rect_clip)

                    scaled_frame = pygame.transform.smoothscale(subsurface, (TILE_SIZE, TILE_SIZE))
                    frames.append(scaled_frame)

                self.sprites[state][direction] = frames
        # self.sprites = {}
        #
        # original_frame_size = 1000
        #
        # for i, state in enumerate(states):
        #     self.sprites[state] = {}
        #     for j, direction in enumerate(directions):
        #         self.sprites[state][direction] = []
        #
        #         sheet_y = i * 3000 + (j + (i % 3)) * original_frame_size
        #
        #         for x in range(4):
        #             sheet_x = x * original_frame_size
        #
        #             rect_clip = pygame.Rect(sheet_x, sheet_y, original_frame_size, original_frame_size)
        #             subsurface = spritesheet.subsurface(rect_clip)
        #
        #             scaled_surface = pygame.transform.smoothscale(subsurface, (TILE_SIZE, TILE_SIZE))
        #
        #             self.sprites[state][direction].append(scaled_surface)

        self.image = self.sprites[self.state][self.direction][0]

    def update_rect_position(self):
        """
        Sincroniza o rect do Pygame com a posição lógica (self.pos).
        Deve ser chamado pelo Controller sempre que self.pos mudar.
        """
        self.rect.topleft = self.pos
