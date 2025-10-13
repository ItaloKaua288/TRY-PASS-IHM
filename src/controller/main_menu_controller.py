import pygame
from src.config import GameStateMap

class MainMenuController:
    def __init__(self, view):
        self.view = view

    def handle_events(self, events, game_state_manager):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for key, button in self.view.buttons.items():
                    if button.is_hovered:
                        match key:
                            case "new_game":
                                game_state_manager.current_game_state = GameStateMap.IN_GAME
                            case "options":
                                print("options")
                            case "quit":
                                game_state_manager.current_game_state = GameStateMap.QUIT
