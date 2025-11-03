import pygame
from src.config import GameStateMap

class MainMenuController:
    def __init__(self, view, game_manager):
        self.view = view
        self.game_manager = game_manager

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for key, button in self.view.buttons.items():
                    if button.is_hovered:
                        match key:
                            case "new_game":
                                self.game_manager.current_game_state = GameStateMap.LEVEL_SELECT
                            case "options":
                                self._toggle_visibility_options()
                            case "quit":
                                self.game_manager.current_game_state = GameStateMap.QUIT
                    else:
                        if self.view.panels["options"].is_visible:
                            self._handle_options()

    def _toggle_visibility_options(self):
        self.view.panels["options"].is_visible = not self.view.panels["options"].is_visible

    def _handle_options(self):
        buttons = self.view.panels["options"].buttons

        for key, button in buttons.items():
            if button.is_hovered:
                match key:
                    case "close":
                        self.view.panels["options"].is_visible = False
