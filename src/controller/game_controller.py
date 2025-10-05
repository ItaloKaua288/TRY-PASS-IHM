import pygame

from src.config import TILE_SIZE

class GameController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.tile_size = (TILE_SIZE, TILE_SIZE)

        start_tile_pos = model.player.target_pos
        start_pixel_pos = (start_tile_pos[0] * self.tile_size[0], start_tile_pos[1] * self.tile_size[1])
        self.model.player.rect.topleft = start_pixel_pos

        self._setup_init()

    def _setup_init(self):
        self.model.player.transform_size(self.tile_size)

    def update_elements(self, mouse_pos):
        self.model.update()
        self.view.update(mouse_pos)

    def handle_events(self, events, mouse_pos):
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._button_handler(mouse_pos)

    def _button_handler(self, mouse_pos):
        for k, button in self.view.buttons.items():
            if button.is_hovered:
                if k == "inventory":
                    inventory_panel = self.view.panels["inventory"]
                    if inventory_panel.is_visible:
                        inventory_panel.is_visible = False
                    else:
                        inventory_panel.is_visible = True
                return

        for k, button in self.view.panels["top_bar"].buttons.items():
            if button.is_hovered:
                match k:
                    case "options":
                        print("Options")
                    case "idea":
                        print("Idea")
                    case "music_note":
                        print("Music note")


