import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, assets):
        pygame.sprite.Sprite.__init__(self)
        self.image = None
        self.current_sprite = 0

        self.is_moving = False
        self.velocity = 1
        self.target_pos = pos

        self.directions = [(0, 1, "down"), (-1, 0, "left"), (0, -1, "up"), (1, 0, "right")]
        self.direction_index = 0

        self.change_direction = False
        self._load_sprites(assets)

    def _load_sprites(self, assets):
        self.__sprites = {}

        idle_imgs = [assets.get_image(f"sprites/main_character/idle_{i}.png") for i in range(2)]
        moving_imgs = [assets.get_image(f"sprites/main_character/moving_{i}.png") for i in range(2)]

        self.__sprites["idle"] = {
            "down": idle_imgs,
            "left": [pygame.transform.rotate(img, 270) for img in idle_imgs],
            "up": [pygame.transform.rotate(img, 180) for img in idle_imgs],
            "right": [pygame.transform.rotate(img, 90) for img in idle_imgs]
        }

        self.__sprites["moving"] = {
            "down": moving_imgs,
            "left": [pygame.transform.rotate(img, 270) for img in moving_imgs],
            "up": [pygame.transform.rotate(img, 180) for img in moving_imgs],
            "right": [pygame.transform.rotate(img, 90) for img in moving_imgs]
        }

        current_state = "moving" if self.is_moving else "idle"

        self.image = self.__sprites[current_state][self.directions[self.direction_index][2]][self.current_sprite]
        self.rect = self.image.get_rect(topleft=self.target_pos)

    def turn_left(self):
        if not self.is_moving:
            self.direction_index = (self.direction_index + 1) % len(self.directions)

    def turn_right(self):
        if not self.is_moving:
            self.direction_index = (self.direction_index - 1 + len(self.directions)) % len(self.directions)

    def set_next_move(self, tile_size):
        if not self.is_moving:
            dx, dy = self.get_direction_vector()
            self.target_pos = (self.rect.x + dx * tile_size[0], self.rect.y + dy * tile_size[1])
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

    def transform_size(self, size):
        for i, state_character in self.__sprites.items():
            for j, direction in state_character.items():
                for k, img in enumerate(direction):
                    self.__sprites[i][j][k] = pygame.transform.smoothscale(img, size)

    def update(self):
        if self.change_direction:
            self.current_sprite = 0
            self.change_direction = False

        current_state = self.__sprites["moving"] if self.is_moving else self.__sprites["idle"]
        current_sprites = current_state[self.directions[self.direction_index][2]]

        self.image = current_sprites[int(self.current_sprite)]

        self.current_sprite += 0.025
        if self.current_sprite >= len(current_sprites):
            self.current_sprite = 0
