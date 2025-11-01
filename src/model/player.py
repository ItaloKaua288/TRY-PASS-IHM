import pygame

from src.config import TILE_SIZE
from src.model.inventory import Inventory


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, assets):
        pygame.sprite.Sprite.__init__(self)
        self.image = None

        self.inventory = Inventory()
        self.item_hand = None

        self.is_moving = False
        self.is_rotating = False
        self.current_sprite = 0
        self.animation_speed = 0.025
        self.velocity = 2

        self.target_pos = pos

        self.directions = [(0, 1, "down"), (-1, 0, "left"), (0, -1, "up"), (1, 0, "right")]
        self.direction_index = 0

        self.direction_rotate = 1
        self.rotation_count = 0
        self.rotation_speed = 0.2

        self.change_direction = False
        self._load_sprites(assets)

    def _load_sprites(self, assets):
        self.__sprites = {}

        idle_imgs = [assets.get_image(f"sprites/main_character/idle_{i}.png") for i in range(2)]
        rotate_img = [assets.get_image(f"sprites/main_character/rotate_{i}.png") for i in range(2)]
        moving_imgs = [assets.get_image(f"sprites/main_character/moving_{i}.png") for i in range(2)]

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

    def get_next_tile_pos(self):
        dx, dy = self.get_direction_vector()
        return self.rect.x + dx * TILE_SIZE, self.rect.y + dy * TILE_SIZE

    def set_next_move(self):
        if not self.is_moving:
            dx, dy = self.get_direction_vector()
            self.target_pos = (self.rect.x + dx * TILE_SIZE, self.rect.y + dy * TILE_SIZE)
            self.is_moving = True

    def get_direction_vector(self):
        return self.directions[self.direction_index][:2]

    def _update_rotation(self):
        if self.rotation_count >= 2:
            self.rotation_count = 0
            self.is_rotating = False
            return

        sprites = self.__sprites["rotate"]
        if self.direction_rotate > 0:
            sprites = sprites["clockwise"]
        elif self.direction_rotate < 0:
            sprites = self.__sprites["rotate"]["counterclockwise"]
        self.image = sprites[self.directions[self.direction_index][2]][int(self.rotation_count)]
        self.rotation_count += self.rotation_speed

    def _update_movement(self):
        if self.rect.topleft == self.target_pos:
            self.is_moving = False
            return

        target_x, target_y = self.target_pos

        if self.rect.x < target_x:
            self.rect.x = min(self.rect.x + self.velocity, target_x)
        elif self.rect.x > target_x:
            self.rect.x = max(self.rect.x - self.velocity, target_x)

        if self.rect.y < target_y:
            self.rect.y = min(self.rect.y + self.velocity, target_y)
        elif self.rect.y > target_y:
            self.rect.y = max(self.rect.y - self.velocity, target_y)

    def _animate_sprites(self, state: str):
        current_sprites = self.__sprites[state][self.directions[self.direction_index][2]]
        self.current_sprite = (self.current_sprite + self.animation_speed) % len(current_sprites)
        self.image = current_sprites[int(self.current_sprite)]

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

    def update(self):
        if self.is_rotating:
            self._update_rotation()
        elif self.is_moving:
            self._update_movement()
            self._animate_sprites("moving")
        else:
            self._animate_sprites("idle")