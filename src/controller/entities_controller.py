from src.utils.settings import TILE_SIZE

class DefaultEntityController:
    def __init__(self, entity, game_model):
        self.entity = entity
        self.game_model = game_model
        self.last_pos = entity.rect.topleft

    def update(self):
        if tuple(self.entity.pos) != self.entity.rect.topleft:
            self.entity.state = "moving"
            self.__update_movement()
        elif self.entity.state == "rotating":
            self.__update_rotating()
        elif self.entity.state == "idle":
            self.__update_idle()
        else:
            self.entity.state = "idle"

    def __update_idle(self):
        if self.entity.last_tick_sprite_update >= 25:
            if self.entity.current_sprite >= 3:
                self.entity.current_sprite = 0
            else:
                self.entity.current_sprite += 1
            self.entity.last_tick_sprite_update = 0
        self.entity.last_tick_sprite_update += 1

    def __update_movement(self):
        if self.entity.last_tick_sprite_update >= 3:
            if self.entity.current_sprite >= 3:
                self.entity.current_sprite = 0
            else:
                self.entity.current_sprite += 1
            self.entity.last_tick_sprite_update = 0
        self.entity.last_tick_sprite_update += 1

        if self.entity.pos == self.entity.rect.topleft:
            self.entity.state = "idle"
            self.entity.update_rect_position()
            return

        target_x, target_y = self.entity.pos

        if self.entity.rect.x < target_x:
            self.entity.rect.x = min(self.entity.rect.x + self.entity.velocity, target_x)
        else:
            self.entity.rect.x = max(self.entity.rect.x - self.entity.velocity, target_x)

        if self.entity.rect.y < target_y:
            self.entity.rect.y = min(self.entity.rect.y + self.entity.velocity, target_y)
        else:
            self.entity.rect.y = max(self.entity.rect.y - self.entity.velocity, target_y)

    def __update_rotating(self):
        if self.entity.last_tick_sprite_update >= 5:
            if self.entity.current_sprite >= 3:
                self.entity.current_sprite = 0
            else:
                self.entity.current_sprite += 1
            self.entity.last_tick_sprite_update = 0
        else:
            self.entity.last_tick_sprite_update += 1

        if self.entity.current_sprite >= 3:
            self.entity.state = "idle"

            current_direction_index = self.entity.direction_list.index(self.entity.direction)
            if self.entity.direction_rotate == 1:
                self.entity.direction = self.entity.direction_list[
                    (current_direction_index + 1) % len(self.entity.direction_list)]
            elif self.entity.direction_rotate == -1:
                self.entity.direction = self.entity.direction_list[
                    (current_direction_index - 1) % len(self.entity.direction_list)]
            return

    def move(self):
        if not self.__next_move_is_valid():
            return

        self.entity.state = "moving"
        self.entity.pos = self.__get_next_player_pos()

    def move_back(self, pos):
        if pos is None:
            return
        self.entity.pos = pos

    def turn_left(self):
        self.entity.state = "rotating"
        self.entity.current_sprite = 0
        self.entity.direction_rotate = 1

    def turn_right(self):
        self.entity.state = "rotating"
        self.entity.current_sprite = 0
        self.entity.direction_rotate = -1

    def __get_next_player_pos(self):
        if self.entity.direction == "down":
            target_pos = (self.entity.rect.x, self.entity.rect.y + TILE_SIZE)
        elif self.entity.direction == "right":
            target_pos = (self.entity.rect.x + TILE_SIZE, self.entity.rect.y)
        elif self.entity.direction == "left":
            target_pos = (self.entity.rect.x - TILE_SIZE, self.entity.rect.y)
        else:
            target_pos = (self.entity.rect.x, self.entity.rect.y - TILE_SIZE)
        return target_pos

    def __next_move_is_valid(self):
        next_player_pixel_pos = self.__get_next_player_pos()
        next_player_tile_pos_x = next_player_pixel_pos[0] // TILE_SIZE
        next_player_tile_pos_y = next_player_pixel_pos[1] // TILE_SIZE

        map = self.game_model.map

        if not (0 <= next_player_tile_pos_y < map["height"]) or not (0 <= next_player_tile_pos_x < map["width"]):
            return False

        tile_index = map["tiles"][next_player_tile_pos_y][next_player_tile_pos_x]

        if tile_index in [9, 10, 11]:
            return True
        return False
