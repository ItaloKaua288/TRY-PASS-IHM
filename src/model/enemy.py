import pygame
from src.utils.settings import TILE_SIZE


class DefaultEnemy(pygame.sprite.Sprite):
    def __init__(self, life, pos, movements_list, assets, image_path="images/sprites/main_character.png", opacity=128):
        super().__init__()

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

        self.opacity = opacity
        self.__load_sprites(image_path)

        self.rect = self.image.get_rect(topleft=self.pos)

    def __load_sprites(self, image_path):
        spritesheet = self.assets.get_image(image_path).copy()

        if self.opacity < 255:
            spritesheet.set_alpha(self.opacity)

        states = ["idle", "moving", "rotating"]
        directions = ["down", "right", "up", "left"]

        self.sprites = {}

        original_frame_size = 1000

        for i, state in enumerate(states):
            self.sprites[state] = {}
            for j, direction in enumerate(directions):
                self.sprites[state][direction] = []

                sheet_y = i * 3000 + (j + (i % 3)) * original_frame_size

                for x in range(4):
                    sheet_x = x * original_frame_size

                    rect_clip = pygame.Rect(sheet_x, sheet_y, original_frame_size, original_frame_size)
                    subsurface = spritesheet.subsurface(rect_clip)

                    scaled_surface = pygame.transform.smoothscale(subsurface, (TILE_SIZE, TILE_SIZE))

                    self.sprites[state][direction].append(scaled_surface)

        self.image = self.sprites[self.state][self.direction][0]

    def update_rect_position(self):
        """
        Sincroniza o rect do Pygame com a posição lógica (self.pos).
        Deve ser chamado pelo Controller sempre que self.pos mudar.
        """
        self.rect.topleft = self.pos
