import pygame
from .main_menu_panels import MapPanel, TopBarPanel, InventoryPanel, ExecutionPanel, ToolsPanel, InfoPanel

from src.config import Colors


class GameView:
    def __init__(self, screen, assets, model):
        self.screen = screen
        self.assets = assets
        self.model = model
        self.width, self.height = screen.get_size()
        self.dragged_info = {}

        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.panels = {}
        self._create_ui_elements()

    def _create_ui_elements(self):
        title_font = self.assets.get_font("Monospace", 15)

        self.panels = {
            "map": MapPanel((self.width - 185, self.height - 190), (5, 60), self.model, self.assets),
            "execution": ExecutionPanel((600, 120), (5, self.height - 125), title_font, self.assets, self.model),
            "tools": ToolsPanel((170, 366), (self.width - 175, 5), title_font, self.model, self.assets),
            "info": InfoPanel((235, 120), (610, self.height - 125), title_font, self.model, self.assets),
            "inventory": InventoryPanel((400, 366), ((self.width // 2) - 200, (self.height // 2) - 183), title_font, self.assets),
            "top_bar": TopBarPanel((self.width - 185, 50), (5, 5), title_font, self.model.objective_text, self.assets)
        }

    def update(self, mouse_pos):
        self.width, self.height = self.screen.get_size()
        self.panels["top_bar"].update(mouse_pos)
        self.panels["tools"].update(mouse_pos)
        self.panels["execution"].update(mouse_pos)
        self.panels["map"].update()
        self.panels["info"].update()

    def draw(self, *args, **kwargs):
        self.image.fill(Colors.BLACK_COLOR_2)

        for panel in self.panels.values():
            panel.draw(self.image, self.model, self.assets)

        self.screen.blit(self.image, (0, 0))
        pygame.display.flip()