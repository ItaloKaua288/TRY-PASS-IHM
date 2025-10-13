import pygame
from .ui_panels import MapPanel, TopBarPanel, InventoryPanel, ExecutionPanel, ToolsPanel
from .ui_elements import TextButton

from src.config import WHITE_COLOR, GRAY_COLOR, BLACK_COLOR_2


class GameView:
    def __init__(self, screen, assets, model):
        self.screen = screen
        self.assets = assets
        self.width, self.height = screen.get_size()
        self.dragged_info = {}

        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.panels = {}
        self.buttons = {}
        self._create_ui_elements(model)

    def _create_ui_elements(self, model):
        title_font = self.assets.get_font("Monospace", 15)

        self.panels = {
            "map": MapPanel((self.width - 220, self.height - 210), (5, 60), model.tile_map, self.assets),
            "execution": ExecutionPanel((self.width - 10, 140), (5, self.height - 145), title_font, self.assets, model),
            "inventory": InventoryPanel((400, 366), ((self.width // 2) - 200, (self.height // 2) - 183), title_font),
            "tools": ToolsPanel((200, 366), (self.width - 205, 60), title_font, self.assets),
            "top_bar": TopBarPanel((self.width - 215, 50), (5, 5), title_font, model.objective_text, self.assets)
        }

        self.buttons = {
            "inventory": TextButton("Inventário", title_font, (self.width - 105, 30), WHITE_COLOR, GRAY_COLOR,(195, 50))
        }

    def update(self, mouse_pos):
        self.panels["top_bar"].update(mouse_pos)
        self.panels["tools"].update(mouse_pos)
        self.panels["execution"].update(mouse_pos)
        self.buttons["inventory"].update(mouse_pos)

    def draw(self, model, assets):
        self.image.fill(BLACK_COLOR_2)

        for panel in self.panels.values():
            panel.draw(self.image, model, assets)

        for button in self.buttons.values():
            button.draw(self.image)

        self.screen.blit(self.image, (0, 0))
        pygame.display.flip()