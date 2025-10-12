import pygame


class BaseButton:
    def __init__(self):
        self.image = None
        self.is_hovered = False
        self.normal_surface = None
        self.hover_surface = None
        self.is_visible = True

    def _setup_rect(self, center_pos):
        self.image = self.normal_surface
        self.rect = self.image.get_rect(center=center_pos)

    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.is_hovered = True
            self.image = self.hover_surface
        else:
            self.is_hovered = False
            self.image = self.normal_surface

    def is_clicked(self, event):
        return self.is_hovered and event.type == pygame.MOUSEBUTTONDOWN

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class TextButton(BaseButton):
    def __init__(self, text, font, center_pos, color, color_hover, size=None, border_radius=10):
        super().__init__()
        self.text = text

        self._create_elements(color, color_hover, font, size, border_radius)
        self._setup_rect(center_pos)

    def _create_elements(self, color, color_hover, font, size, border_radius):
        normal_text = font.render(self.text, True, (0, 0, 0))
        hover_text = font.render(self.text, True, (0, 0, 0))

        width, height = size

        if width and height:
            rect = pygame.Rect(0, 0, width, height)

            self.normal_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(self.normal_surface, color, rect, border_radius=border_radius)
            self.normal_surface.blit(normal_text, normal_text.get_rect(center=(width // 2, height // 2)))

            self.hover_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(self.hover_surface, color_hover, rect, border_radius=border_radius)
            self.hover_surface.blit(hover_text, hover_text.get_rect(center=(width // 2, height // 2)))
        else:
            self.normal_surface = normal_text
            self.hover_surface = hover_text


class IconButton(BaseButton):
    def __init__(self, icon, center_pos, size, color, color_hover, border_radius=0, name=None):
        super().__init__()

        self.icon = icon
        self.name = name

        self._resize_icon(size)
        self._create_surfaces(size, color, color_hover, border_radius)
        self._setup_rect(center_pos)

    def _resize_icon(self, size):
        self.icon = pygame.transform.smoothscale(self.icon, (size[0] - 10, size[1] - 10))

    def _create_surfaces(self, size, color, color_hover, border_radius):
        self.normal_surface = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(self.normal_surface, color, self.normal_surface.get_rect(), border_radius=border_radius)
        icon_rect = self.icon.get_rect(center=self.normal_surface.get_rect().center)
        self.normal_surface.blit(self.icon, icon_rect)

        self.hover_surface = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(self.hover_surface, color_hover, self.hover_surface.get_rect(), border_radius=border_radius)
        self.hover_surface.blit(self.icon, icon_rect)