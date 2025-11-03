import pygame
from src.view.ui_elements import TextButton
from src.view.game_menu_panels import OptionsPanel
from src.config import Colors

class MainMenuView:
    def __init__(self, screen, assets):
        self.screen = screen
        self.width, self.height = screen.get_size()

        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.panels = {}
        self.buttons = {}
        self._create_buttons(assets)
        self._create_panels(assets)
        self._create_static_elements(assets)

    def _create_buttons(self, assets):
        menu_font = assets.get_font("Monospace", 30)
        center_x = self.width // 2
        center_y = self.height // 2

        self.buttons = {
            "new_game": TextButton("Novo Jogo", menu_font, (center_x, center_y), Colors.TRANSPARENT_COLOR, Colors.TRANSPARENT_COLOR, text_color=Colors.WHITE_COLOR, text_color_hover=Colors.GRAY_COLOR),
            "options": TextButton("Opções", menu_font, (center_x, center_y + 35), Colors.TRANSPARENT_COLOR, Colors.TRANSPARENT_COLOR, text_color=Colors.WHITE_COLOR, text_color_hover=Colors.GRAY_COLOR),
            "quit": TextButton("Sair", menu_font, (center_x, center_y + 75), Colors.TRANSPARENT_COLOR, Colors.TRANSPARENT_COLOR, text_color=Colors.WHITE_COLOR, text_color_hover=Colors.GRAY_COLOR)
        }

    def _create_panels(self, assets):
        self.panels = {
            "options": OptionsPanel((400, 200), (self.width // 2, self.height // 2), assets.get_font("Monospace", 20), assets),
        }

    def _create_static_elements(self, assets):
        self.sprite_character = assets.get_image("sprites/main_character/idle_0.png").copy()
        self.sprite_character.set_alpha(40)

        title_font = assets.get_font("Monospace", 80)
        self.title_surf = title_font.render("TRY:PASS", True, Colors.WHITE_COLOR)

    def update(self, mouse_pos):
        for button in self.buttons.values():
            button.update(mouse_pos)

        for panel in self.panels.values():
            panel.update(mouse_pos)

    def draw(self):
        self.image.fill(Colors.BLACK_COLOR)

        center_x = self.width // 2
        center_y = self.height // 2
        self.image.blit(self.sprite_character, self.sprite_character.get_rect(center=(center_x, center_y)))
        self.image.blit(self.title_surf, self.title_surf.get_rect(center=(center_x, 80)))

        for button in self.buttons.values():
            button.draw(self.image)

        for panel in self.panels.values():
            panel.draw(self.image, None)

        self.screen.blit(self.image, (0, 0))