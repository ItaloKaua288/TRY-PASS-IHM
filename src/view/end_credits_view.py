import pygame
from src.utils.settings import Colors

class EndCreditsView:
    def __init__(self, screen, assets):
        self.screen = screen
        self.assets = assets

        self.__create_elements()

    def __create_elements(self):
        self.background = pygame.Surface(self.screen.get_size())

        self.background.fill(Colors.BLACK.value)

        character_surface = pygame.transform.smoothscale(self.assets.get_image("images/icons/logo.png").copy(), (600, 600))
        character_surface.set_alpha(20)
        self.background.blit(character_surface, (
            self.background.get_width() // 2 - character_surface.get_width() // 2,
            self.background.get_height() // 2 - character_surface.get_height() // 2)
        )

        title_font = self.assets.get_font("Monospace", 80)

        title_surf = title_font.render("TRY:PASS", True, Colors.WHITE.value)
        title_rect = title_surf.get_rect(center=(self.screen.get_width() // 2, 80))
        self.background.blit(title_surf, title_rect)

        font = self.assets.get_font("Monospace", 20)
        text_list = ["Fim do conteúdo atual!",
                "Você completou todas as fases disponíveis do jogo.",
                "Mas a jornada ainda não acabou!",
                "Novas fases, desafios e surpresas estão sendo desenvolvidos e chegarão em breve.",
                "Obrigado por jogar, apoiar e fazer parte dessa aventura.",
                "Nos vemos na próxima atualização!"]

        for i, text in enumerate(text_list):
            text_surface = font.render(text, True, Colors.WHITE.value)
            self.background.blit(text_surface, (
                self.background.get_width() // 2 - text_surface.get_width() // 2,
                self.background.get_height() // 2 - text_surface.get_height() // 2 - 100 + i * 30
            ))

        main_menu_icon_surface = pygame.transform.smoothscale(self.assets.get_image("images/icons/back.png"), (40, 40))
        main_menu_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.rect(main_menu_surface, Colors.LIGHT_GRAY.value, main_menu_surface.get_rect(), border_radius=10)
        main_menu_rect = main_menu_surface.get_rect(topleft=(5, 5))
        main_menu_surface.blit(main_menu_icon_surface, (5, 5))

        main_menu_hover_surface = main_menu_surface.copy()
        pygame.draw.rect(main_menu_hover_surface, Colors.DARK_GRAY.value, main_menu_surface.get_rect(), border_radius=10)
        main_menu_hover_surface.blit(main_menu_icon_surface, (5, 5))

        self.buttons = {
            "main_menu": {
                "surface": main_menu_surface,
                 "hover_surface": main_menu_hover_surface,
                 "rect": main_menu_rect,
                 "is_hovered": False
            }
        }

    def update(self, mouse_pos):
        for btn in self.buttons.values():
            if btn["rect"].collidepoint(mouse_pos):
                btn["is_hovered"] = True
                self.background.blit(btn["hover_surface"], btn["rect"])
            else:
                btn["is_hovered"] = False
                self.background.blit(btn["surface"], btn["rect"])

    def draw(self):
        self.screen.blit(self.background, (0, 0))