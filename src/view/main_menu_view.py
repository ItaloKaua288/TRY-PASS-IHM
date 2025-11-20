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

    def __update_layout(self):
        """
        Recalcula posições e superfícies de texto.
        Chamado apenas na inicialização ou quando a visibilidade muda.
        """
        self.options_rects = []
        self.options_surfaces = {}

        screen_center_x = self.screen.get_width() // 2
        start_y = self.screen.get_height() // 2 - 50

        spacing = 50
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
        """Se houver animações de fundo ou partículas, atualize aqui."""
        pass

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

