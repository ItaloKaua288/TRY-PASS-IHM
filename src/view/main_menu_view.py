import pygame
from src.utils.settings import Colors


class MenuView:
    def __init__(self, screen, assets):
        self.screen = screen
        self.assets = assets

        self.font = self.assets.get_font("Monospace", 35)
        self.title_font = self.assets.get_font("Monospace", 80)

        self.options = ["Continuar", "Novo Jogo", "Opções", "Sair"]
        self.option_selected = None

        self._continue_button_is_visible = False

        self.options_surfaces = {}
        self.options_rects = []

        self.panels = {
            "options_menu": self.__create_menu_options()
        }

        self.background = self.__create_background()

        self.__update_layout()

    @property
    def continue_button_is_visible(self):
        return self._continue_button_is_visible

    @continue_button_is_visible.setter
    def continue_button_is_visible(self, value):
        """
        Setter Mágico: Quando o controller muda essa variável,
        o layout visual e as hitboxes (rects) se reorganizam automaticamente.
        """
        if self._continue_button_is_visible != value:
            self._continue_button_is_visible = value
            self.__update_layout()

    def __create_menu_options(self):
        surface = pygame.Surface((250, 150), pygame.SRCALPHA)
        pygame.draw.rect(surface, Colors.GRAY.value, surface.get_rect(), border_radius=10)

        buttons = {}
        buttons_name = {"mute": "Desativar Musica", "unmute": "Ativar Musica"}
        # btn_pos = (5, 5 + (btn_surface.height + 5) * btn_index)
        font = self.assets.get_font("Monospace", 15)
        for key, btn_name in buttons_name.items():
            text_surface = font.render(btn_name, True, Colors.BLACK.value)
            text_hover_surface = font.render(btn_name, True, Colors.WHITE.value)
            btn_surface = pygame.Surface((surface.get_width() - 10, 30), pygame.SRCALPHA)
            btn_surface_hover = btn_surface.copy()

            btn_surface.fill(Colors.GRAY.value)
            pygame.draw.rect(btn_surface, Colors.BLACK.value, btn_surface.get_rect(), width=1)
            btn_surface_hover.fill(Colors.DARK_GRAY.value)

            text_pos = (btn_surface.get_width() // 2 - text_surface.get_width() // 2, btn_surface.get_height() // 2 - text_surface.get_height() // 2)
            btn_surface.blit(text_surface, text_pos)
            btn_surface_hover.blit(text_hover_surface, text_pos)

            buttons[key] = {"surface": btn_surface, "hover_surface": btn_surface_hover, "rect": btn_surface.get_rect(topleft=(5, 5)), "is_hovered": False, "is_visible": False}

        buttons_name = {"music_volume": "Volume da música:", "effect_volume": "Volume dos efeitos"}

        btn_down_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
        btn_down_hover_surface = btn_down_surface.copy()
        pygame.draw.rect(btn_down_surface, Colors.GRAY.value, btn_down_surface.get_rect(), border_radius=10)
        pygame.draw.rect(btn_down_hover_surface, Colors.DARK_GRAY.value, btn_down_surface.get_rect(), border_radius=10)

        btn_icon_surface = pygame.transform.smoothscale(self.assets.get_image("images/icons/back.png"), (30, 30))
        btn_down_surface.blit(btn_icon_surface, (0, 0))
        btn_down_hover_surface.blit(btn_icon_surface, (0, 0))

        btn_up_surface = btn_down_surface.copy()
        btn_up_hover_surface = btn_up_surface.copy()
        pygame.draw.rect(btn_up_surface, Colors.GRAY.value, btn_up_surface.get_rect(), border_radius=10)
        pygame.draw.rect(btn_up_hover_surface, Colors.DARK_GRAY.value, btn_up_surface.get_rect(), border_radius=10)

        btn_icon_surface = pygame.transform.smoothscale(self.assets.get_image("images/icons/forward.png"), (30, 30))
        btn_up_surface.blit(btn_icon_surface, (0, 0))
        btn_up_hover_surface.blit(btn_icon_surface, (0, 0))

        for key, btn_name in buttons_name.items():
            btn_surface = pygame.Surface((surface.get_width() - 10, 30), pygame.SRCALPHA)
            btn_surface.blit(btn_down_surface, (0, 0))
            btn_surface.blit(btn_up_surface, (btn_surface.get_width() - 30, 0))
            btn_pos = (5, 55 + (50 * list(buttons_name.keys()).index(key)))

            text_surface = font.render(btn_name, True, Colors.BLACK.value)
            surface.blit(text_surface, (btn_pos[0], btn_pos[1] - 20))

            buttons[key] = {"surface": btn_surface, "hover_surface": btn_surface.copy(),
                                 "rect": btn_surface.get_rect(topleft=btn_pos),
                                 "down_btn": {"surface": btn_down_surface, "hover_surface": btn_down_hover_surface, "rect": btn_down_surface.get_rect(topleft=(0, 0)), "is_hovered": False},
                                 "up_btn": {"surface": btn_up_surface, "hover_surface": btn_up_hover_surface, "rect": btn_up_surface.get_rect(topleft=(btn_surface.get_width() - 30, 0)), "is_hovered": False},
                                 "value": 0,
                                 "is_hovered": False, "is_visible": True}

        return {"surface": surface, "rect": surface.get_rect(topleft=(750, 400)), "buttons": buttons, "is_visible": False}

    def __create_background(self):
        """Cria o background estático apenas uma vez na inicialização."""
        background_surf = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        background_surf.fill((0, 0, 0))

        title_surf = self.title_font.render("TRY:PASS", True, Colors.WHITE.value)
        title_rect = title_surf.get_rect(center=(self.screen.get_width() // 2, 80))
        background_surf.blit(title_surf, title_rect)

        logo_surf = self.assets.get_image("images/icons/logo.png").copy()
        logo_surf.set_alpha(20)
        logo_resized = pygame.transform.scale(logo_surf, (600, 600))
        logo_rect = logo_resized.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        background_surf.blit(logo_resized, logo_rect)

        return background_surf

    def __update_menu_options(self):
        panel = self.panels["options_menu"]
        buttons = panel["buttons"]

        mouse_pos = pygame.mouse.get_pos()
        local_mouse_pos = (mouse_pos[0] - panel["rect"].x, mouse_pos[1] - panel["rect"].y)

        for key, button in buttons.items():
            if button["is_visible"]:
                if button["rect"].collidepoint(local_mouse_pos):
                    if key in ["music_volume", "effect_volume"]:
                        local_btn_mouse_pos = pygame.math.Vector2(local_mouse_pos) - pygame.math.Vector2(button["rect"].topleft)
                        if button["down_btn"]["rect"].collidepoint(local_btn_mouse_pos):
                            button["down_btn"]["is_hovered"] = True
                            button["up_btn"]["is_hovered"] = False
                            button["hover_surface"].blit(button["down_btn"]["hover_surface"], button["down_btn"]["rect"])
                            button["hover_surface"].blit(button["up_btn"]["surface"], button["up_btn"]["rect"])
                        else:
                            button["hover_surface"].blit(button["down_btn"]["surface"], button["down_btn"]["rect"])

                        if button["up_btn"]["rect"].collidepoint(local_btn_mouse_pos):
                            button["up_btn"]["is_hovered"] = True
                            button["down_btn"]["is_hovered"] = False
                            button["hover_surface"].blit(button["up_btn"]["hover_surface"], button["up_btn"]["rect"])
                            button["hover_surface"].blit(button["down_btn"]["surface"], button["down_btn"]["rect"])
                        else:
                            button["hover_surface"].blit(button["up_btn"]["surface"], button["up_btn"]["rect"])
                    button["is_hovered"] = True
                    panel["surface"].blit(button["hover_surface"], button["rect"])
                else:
                    button["is_hovered"] = False
                    panel["surface"].blit(button["surface"], button["rect"])

        buttons_name = ["music_volume", "effect_volume"]
        bar_rect = pygame.Rect(32, 0, (buttons["music_volume"]["rect"].width - 85) // 5, buttons["music_volume"]["rect"].height)

        for btn_name in buttons_name:
            pygame.draw.rect(buttons[btn_name]["surface"], Colors.GRAY.value, (30, 0, buttons[btn_name]["rect"].width - 60, buttons[btn_name]["rect"].height))
            pygame.draw.rect(buttons[btn_name]["hover_surface"], Colors.GRAY.value, (30, 0, buttons[btn_name]["rect"].width - 60, buttons[btn_name]["rect"].height))
            for i in range(5):
                bar_rect.topleft = (32 + (bar_rect.width + 5) * i, 0)
                if i < buttons[btn_name]["value"]:
                    pygame.draw.rect(buttons[btn_name]["surface"], Colors.DARK_GRAY.value, bar_rect)
                    pygame.draw.rect(buttons[btn_name]["hover_surface"], Colors.DARK_GRAY.value, bar_rect)
                else:
                    pygame.draw.rect(buttons[btn_name]["surface"], Colors.DARK_GRAY.value, bar_rect, width=1)
                    pygame.draw.rect(buttons[btn_name]["hover_surface"], Colors.DARK_GRAY.value, bar_rect, width=1)
        return

    def __update_layout(self):
        """
        Recalcula posições e superfícies de texto.
        Chamado apenas na inicialização ou quando a visibilidade muda.
        """
        self.options_rects = []
        self.options_surfaces = {}

        screen_center_x = self.screen.get_width() // 2
        start_y = self.screen.get_height() // 2 - 50

        spacing = 60
        current_y_offset = 0

        for i, option in enumerate(self.options):
            surf_normal = self.font.render(option, True, Colors.WHITE.value)
            surf_selected = self.font.render(option, True, Colors.GRAY.value)

            rect = surf_normal.get_rect()

            if option == "Continuar" and not self._continue_button_is_visible:
                rect.topleft = (-1000, -1000)
            else:
                rect.center = (screen_center_x, start_y + current_y_offset)
                current_y_offset += spacing

            self.options_rects.append(rect)
            self.options_surfaces[i] = {"normal": surf_normal, "selected": surf_selected}

    def update(self):
        self.__update_menu_options()

    def draw(self):
        """Desenha o menu usando os assets pré-calculados."""
        self.screen.blit(self.background, (0, 0))

        for i, option in enumerate(self.options):
            if option == "Continuar" and not self._continue_button_is_visible:
                continue

            rect = self.options_rects[i]

            if self.option_selected == i:
                surf = self.options_surfaces[i]["selected"]
            else:
                surf = self.options_surfaces[i]["normal"]

            self.screen.blit(surf, rect)

        for panel in self.panels.values():
            if panel["is_visible"]:
                self.screen.blit(panel["surface"], panel["rect"])

