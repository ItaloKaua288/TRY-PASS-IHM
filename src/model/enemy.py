import pygame
from src.config import TILE_SIZE


class DefaultEnemy(pygame.sprite.Sprite):
    def __init__(self, life, pos, assets):
        pygame.sprite.Sprite.__init__(self)
        self.life = life
        self.target_pos = pos
        self.assets = assets

        self.image = None

        self.is_moving = False
        self.is_rotating = False
        self.current_sprite = 0
        self.animation_speed = 0.01
        self.velocity = 2

        self.directions = [(0, 1, "down"), (-1, 0, "left"), (0, -1, "up"), (1, 0, "right")]
        self.direction_index = 0

        self.__load_sprites()

    def __load_sprites(self):
        self.__sprites = {}

        idle_imgs = [self.assets.get_image(f"sprites/main_character/idle_{i}.png") for i in range(2)]
        rotate_img = [self.assets.get_image(f"sprites/main_character/rotate_{i}.png") for i in range(2)]
        moving_imgs = [self.assets.get_image(f"sprites/main_character/moving_{i}.png") for i in range(2)]

        for idle_img in idle_imgs:
            idle_img.set_alpha(128)

        self.__sprites["idle"] = {
            "down": [pygame.transform.smoothscale(img, (TILE_SIZE, TILE_SIZE)) for img in idle_imgs],
            "left": [pygame.transform.rotate(img, 270) for img in idle_imgs],
            "up": [pygame.transform.rotate(img, 180) for img in idle_imgs],
            "right": [pygame.transform.rotate(img, 90) for img in idle_imgs]
        }

        self.__sprites["moving"] = {
            "down": [pygame.transform.smoothscale(img, (TILE_SIZE, TILE_SIZE)) for img in moving_imgs],
            "left": [pygame.transform.rotate(img, 270) for img in moving_imgs],
            "up": [pygame.transform.rotate(img, 180) for img in moving_imgs],
            "right": [pygame.transform.rotate(img, 90) for img in moving_imgs]
        }

        right_up = [pygame.transform.rotate(img, 90) for img in rotate_img]
        up_left = [pygame.transform.rotate(img, 180) for img in rotate_img]
        left_down = [pygame.transform.rotate(img, 270) for img in rotate_img]

        self.__sprites["rotate"] = {
            "clockwise": {
                "up": up_left[::-1],
                "right": right_up[::-1],
                "down": rotate_img[::-1],
                "left": left_down[::-1],
            },
            "counterclockwise": {
                "up": right_up,
                "left": up_left,
                "down": left_down,
                "right": rotate_img,
            },
        }
        self.transform_size((TILE_SIZE, TILE_SIZE))
        current_state = "moving" if self.is_moving else "idle"

        self.image = self.__sprites[current_state][self.directions[self.direction_index][2]][self.current_sprite]

        self.rect = self.image.get_rect(topleft=self.target_pos)

    def transform_size(self, size):
        for i, state_character in self.__sprites.items():
            for j, direction in state_character.items():
                if type(direction) is list:
                    for k, img in enumerate(direction):
                        self.__sprites[i][j][k] = pygame.transform.smoothscale(img, size)
                else:
                    for k, clock_directions in direction.items():
                        for y, clock_direction in enumerate(clock_directions):
                            self.__sprites[i][j][k][y] = pygame.transform.smoothscale(clock_direction, size)