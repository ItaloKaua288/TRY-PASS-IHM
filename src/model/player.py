import pygame

from src.config import TILE_SIZE

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, assets):
        pygame.sprite.Sprite.__init__(self)
        self.image = None

        self.is_moving = False
        self.is_rotating = False
        self.current_sprite = 0
        self.animation_speed = 0.025
        self.velocity = 2

        self.target_pos = pos

        self.directions = [(0, 1, "down"), (-1, 0, "left"), (0, -1, "up"), (1, 0, "right")]
        self.direction_index = 0


        self.target_angles = [0, 270, 180, 90]
        self.current_angle = self.target_angles[self.direction_index]
        self.target_angle = self.target_angles[self.direction_index]
        self.rotation_speed = 10

        self.change_direction = False
        self._load_sprites(assets)

    def _load_sprites(self, assets):
        self.__sprites = {}

        idle_imgs = [assets.get_image(f"sprites/main_character/idle_{i}.png") for i in range(2)]
        moving_imgs = [assets.get_image(f"sprites/main_character/moving_{i}.png") for i in range(2)]

        self.__sprites["idle"] = {
            "down": [pygame.transform.smoothscale(img, (TILE_SIZE, TILE_SIZE)) for img in moving_imgs],
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

    def update_movement(self):
        if not self.is_moving:
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

        if self.rect.topleft == self.target_pos:
            self.is_moving = False

    def _rotate_image(self):
        self.image = pygame.transform.rotate(self.image, self.current_angle)
        self.transform_size((TILE_SIZE, TILE_SIZE))

        # print(self.image.get_rect().center)
        # self.rect = self.image.get_rect(center=self.rect_center)

    def _update_rotation(self):
        if self.current_angle == self.target_angle:
            self.is_rotating = False
            return

        diff = (self.target_angle - self.current_angle + 180) % 360 - 180

        if abs(diff) < self.rotation_speed:
            self.current_angle = self.target_angle
        elif diff > 0:
            self.current_angle = (self.current_angle + self.rotation_speed) % 360
        else:
            self.current_angle = (self.current_angle - self.rotation_speed + 360) % 360

        self.image = self.image.copy()
        self._rotate_image()

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

        # self.rect_center = self.rect.center

    def _animate_sprites(self, state: str):
        current_sprites = self.__sprites[state][self.directions[self.direction_index][2]]
        self.current_sprite = (self.current_sprite + self.animation_speed) % len(current_sprites)
        self.image = current_sprites[int(self.current_sprite)]
        # self._rotate_image()

    def transform_size(self, size):
        for i, state_character in self.__sprites.items():
            for j, direction in state_character.items():
                for k, img in enumerate(direction):
                    self.__sprites[i][j][k] = pygame.transform.smoothscale(img, size)

    def update(self):
        if self.is_rotating:
            self._update_rotation()
        elif self.is_moving:
            self._update_movement()
            self._animate_sprites("moving")
        else:
            self._animate_sprites("idle")

        # if self.change_direction:
        #     self.current_sprite = 0
        #     self.change_direction = False
        #
        # current_state = self.__sprites["moving"] if self.is_moving else self.__sprites["idle"]
        # current_sprites = current_state[self.directions[self.direction_index][2]]
        #
        # self.image = current_sprites[int(self.current_sprite)]
        #
        # self.current_sprite += self.animation_speed
        # if self.current_sprite >= len(current_sprites):
        #     self.current_sprite = 0

        # if self.change_direction:
        #     self.current_sprite = 0
        #     self.change_direction = False
        #
        # current_state = self.__sprites["moving"] if self.is_moving else self.__sprites["idle"]
        # current_sprites = current_state[self.directions[self.direction_index][2]]
        #
        # self.image = current_sprites[int(self.current_sprite)]
        #
        # self.current_sprite += self.animation_speed
        # if self.current_sprite >= len(current_sprites):
        #     self.current_sprite = 0
