import pygame


class GameController:
    def __init__(self, model):
        self.model = model
        self.tile_size = (42, 33)

        start_tile_pos = (7, 5)
        start_pixel_pos = (start_tile_pos[0] * self.tile_size[0], start_tile_pos[1] * self.tile_size[1])
        self.model.player.rect.topleft = start_pixel_pos
        self.model.player.target_pos = start_pixel_pos

        self._setup_init()

    def _setup_init(self):
        self.model.player.transform_size(self.tile_size)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and not self.model.player.is_moving:
                if event.key == pygame.K_a:
                    self.model.player.turn_left()
                elif event.key == pygame.K_d:
                    self.model.player.turn_right()
                elif event.key == pygame.K_w:
                    dx, dy = self.model.player.get_direction_vector()
                    current_tile_x = self.model.player.rect.x // self.tile_size[0]
                    current_tile_y = self.model.player.rect.y // self.tile_size[1]

                    next_tile = (current_tile_x + dx, current_tile_y + dy)

                    if self.model.is_valid_move(next_tile):
                        self.model.player.set_next_move(self.tile_size)
