import pygame
from .ui_panels import MapPanel, TopBarPanel, InventoryPanel, ExecutionPanel, ToolsPanel
from .ui_elements import TextButton

from src.config import WHITE_COLOR, GRAY_COLOR

class GameView:
    def __init__(self, screen, assets, model):
        self.screen = screen
        self.assets = assets
        self.width, self.height = screen.get_size()

        self._create_ui_elements(model)

    def _create_ui_elements(self, model):
        title_font = self.assets.get_font("Monospace", 15)

        self.panels = {
            "map": MapPanel((self.width - 220, self.height - 210), (5, 60), model.tile_map, self.assets),
            "inventory": InventoryPanel((300, 366), (self.width - 510, 60), title_font),
            "execution": ExecutionPanel((self.width - 10, 140), (5, self.height - 145), title_font, self.assets),
            "tools": ToolsPanel((200, 366), (self.width - 205, 60), title_font, self.assets),
            "top_bar": TopBarPanel((self.width - 215, 50), (5, 5), title_font, model.objective_text, self.assets),
        }

        self.buttons = {
            "inventory": TextButton("Inventário", title_font, (self.width - 105, 30), WHITE_COLOR, GRAY_COLOR,
                                     (195, 50))
        }

    def update(self, mouse_pos):
        self.panels["top_bar"].update(mouse_pos)
        self.panels["tools"].update(mouse_pos)
        self.panels["execution"].update(mouse_pos)
        self.buttons["inventory"].update(mouse_pos)

    def draw(self, model, assets):
        self.screen.fill((30, 30, 30))

        for panel in self.panels.values():
            panel.draw(self.screen, model, assets)

        for button in self.buttons.values():
            button.draw(self.screen)

        pygame.display.flip()