import pygame
from src.utils.settings import TILE_SIZE


class Inventory:
    def __init__(self):
        self.inventory = {}
        self.handing_item = None

    def add_item(self, item, count=1):
        if item in self.inventory.keys():
            self.inventory[item] += count
        else:
            self.inventory[item] = count

    def remove_item(self, key):
        if key in self.inventory.keys():
            self.inventory[key] -= 1

            if self.inventory[key] <= 0:
                del self.inventory[key]


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, assets):
        super().__init__()

        self.pos = list(pos)
        self.assets = assets
        self.inventory = Inventory()

        self.direction_list = ["down", "right", "up", "left"]
        self.velocity = 2
        self.direction = "down"
        self.state = "idle"

        self.current_sprite = 0
        self.last_tick_sprite_update = 0
        self.rotation_count = 0
        self.direction_rotate = 1

        self.__load_sprites()

        self.rect = self.image.get_rect(topleft=self.pos)

    def __load_sprites(self):
        spritesheet = self.assets.get_image("images/sprites/main_character.png")

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

        self.image = self.sprites[self.state][self.direction][0]

    def update_rect_position(self):
        """
        Método auxiliar para sincronizar a posição lógica (self.pos)
        com a posição de renderização/colisão (self.rect).
        O Controller deve chamar isso após mover o player.
        """
        self.rect.topleft = self.pos
