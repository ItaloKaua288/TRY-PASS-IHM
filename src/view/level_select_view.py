import pygame
from src.config import Colors
from src.view.ui_elements import IconButton, TextButton

class LevelSelectView:
    def __init__(self, screen, assets, game_manager):
        self.screen = screen
        self.assets = assets
        self.game_manager = game_manager

        self.buttons = {}

        self.image = pygame.Surface(screen.get_size())
        self.rect = self.image.get_rect()

        self.select_indicator_surf = pygame.transform.smoothscale(assets.get_image("icons/logo.png"), (50, 50))

        self.level_slot_rects = []
        self.level_selected = 0

        self.level_map_surf = pygame.transform.smoothscale(self.assets.get_image("images/level_map.png"), (self.screen.get_width() - 50, self.screen.get_height() - 100))

        self.__create_buttons()
        self.__create_level_slot_rects()

    def __create_level_slot_rects(self):
        rects_pos = [(180, 330), (260, 425), (361, 301), (477, 353), (402, 448), (635, 439), (817, 410), (727, 360),
                     (843, 305), (582, 253), (798, 210), (842, 142), (642, 162), (407, 157), (189, 181)]
        for rect_pos in rects_pos:
            rect = pygame.Rect(0, 0, 100, 80)
            rect.center = rect_pos
            self.level_slot_rects.append(rect)

    def __create_buttons(self):
        text_font = self.assets.get_font("Monospace", 15)
        self.buttons = {
            "main_menu": IconButton(self.assets.get_image("icons/back.png"), (30, 30), (50, 50), Colors.GRAY_COLOR, Colors.DARK_GRAY_COLOR, border_radius=10),
            "select": TextButton("Selecionar", text_font, (self.rect.centerx, 540), Colors.GRAY_COLOR, Colors.DARK_GRAY_COLOR, border_radius=10, size=(100, 40))
        }

    def update(self, mouse_pos):
        for button in self.buttons.values():
            button.update(mouse_pos)

    def draw(self):
        self.image.fill(Colors.BLACK_COLOR)
        self.image.blit(self.level_map_surf, self.level_map_surf.get_rect(centerx=self.rect.centerx, centery=self.rect.centery))
        self.image.blit(self.select_indicator_surf, self.select_indicator_surf.get_rect(center=self.level_slot_rects[self.level_selected].center))
        for button in self.buttons.values():
            button.draw(self.image)
        self.screen.blit(self.image, self.rect)
