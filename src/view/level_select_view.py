import pygame
from src.utils.settings import Colors


class LevelSelectView:
    def __init__(self, screen, assets):
        self.screen = screen
        self.assets = assets

        self.buttons = {}

        self.current_selected_level = 0
        self.current_level_unlocked = 1
        self.level_slots_rects = []
        self.button_selected = None

        self.level_map_surface = pygame.transform.smoothscale(
            self.assets.get_image("images/images/level_map.png"),
            (self.screen.get_width() - 50, self.screen.get_height() - 100)
        )
        self.select_indicator_surface = pygame.transform.smoothscale(
            assets.get_image("images/icons/logo.png"), (80, 80)
        )
        self.padlock_surface = pygame.transform.smoothscale(
            assets.get_image("images/icons/padlock.png"), (80, 80)
        )

        self.__create_elements()

    def __create_elements(self):
        rects_pos = [(216, 418), (323, 540), (448, 378), (600, 447), (504, 566), (797, 557), (1024, 518), (909, 449),
                     (1060, 384), (732, 315), (1000, 260), (1056, 171), (804, 197), (509, 192), (229, 221)]

        for rect_pos in rects_pos:
            rect = pygame.Rect(0, 0, 100, 80)
            rect.center = rect_pos
            self.level_slots_rects.append(rect)

        main_menu_icon_surface = pygame.transform.smoothscale(self.assets.get_image("images/icons/back.png"), (40, 40))

        main_menu_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.rect(main_menu_surface, Colors.LIGHT_GRAY.value, main_menu_surface.get_rect(), border_radius=10)
        main_menu_rect = main_menu_surface.get_rect(topleft=(5, 5))
        main_menu_surface.blit(main_menu_icon_surface, (5, 5))

        main_menu_hover_surface = main_menu_surface.copy()
        pygame.draw.rect(main_menu_hover_surface, Colors.DARK_GRAY.value, main_menu_surface.get_rect(),
                         border_radius=10)
        main_menu_hover_surface.blit(main_menu_icon_surface, (5, 5))

        text_font = self.assets.get_font("Monospace", 40)
        text_surface = text_font.render("Selecionar", True, Colors.BLACK.value)
        select_surface = pygame.Surface((text_surface.get_width() + 20, text_surface.get_height() + 10),
                                        pygame.SRCALPHA)
        select_rect = select_surface.get_rect(
            topleft=(self.screen.get_width() // 2 - select_surface.get_width() // 2, self.screen.get_height() - 100))
        pygame.draw.rect(select_surface, Colors.LIGHT_GRAY.value, select_surface.get_rect(), border_radius=10)
        select_surface.blit(text_surface, (10, 5))

        text_surface = text_font.render("Selecionar", True, Colors.WHITE.value)
        select_hover_surface = select_surface.copy()
        pygame.draw.rect(select_hover_surface, Colors.DARK_GRAY.value, select_surface.get_rect(), border_radius=10)
        select_hover_surface.blit(text_surface, (10, 5))

        self.buttons = {
            "main_menu": {"surface": main_menu_surface, "hover_surface": main_menu_hover_surface,
                          "rect": main_menu_rect},
            "select": {"surface": select_surface, "hover_surface": select_hover_surface, "rect": select_rect},
        }

    def update(self):
        """
        Atualiza apenas o estado VISUAL da View (animações, hovers).
        A lógica de jogo/clique fica no Controller.
        """
        mouse_pos = pygame.mouse.get_pos()
        self.button_selected = None

        for key, button in self.buttons.items():
            if button["rect"].collidepoint(mouse_pos):
                self.button_selected = key
                return

    def draw(self):
        self.screen.fill(Colors.BLACK.value)

        self.screen.blit(self.level_map_surface, self.level_map_surface.get_rect(center=self.screen.get_rect().center))

        if 0 <= self.current_selected_level < len(self.level_slots_rects):
            self.screen.blit(self.select_indicator_surface, self.select_indicator_surface.get_rect(
                center=self.level_slots_rects[self.current_selected_level].center))

        for slot_rect in self.level_slots_rects[self.current_level_unlocked:]:
            self.screen.blit(self.padlock_surface, self.padlock_surface.get_rect(center=slot_rect.center))


        for key, button in self.buttons.items():
            if key == self.button_selected:
                self.screen.blit(button["hover_surface"], button["rect"])
            else:
                self.screen.blit(button["surface"], button["rect"])
