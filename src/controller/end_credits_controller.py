import pygame
from src.utils.settings import GameState


class EndCreditsController:
    def __init__(self, end_credits_view):
        self.view = end_credits_view

    def __handle_event(self, events, mouse_pos):
        next_state = None

        for event in events:
            if event.type == pygame.QUIT:
                return GameState.QUIT

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    for key, btn in self.view.buttons.items():
                        if btn["rect"].collidepoint(mouse_pos):
                            if key == "main_menu":
                                return GameState.MAIN_MENU

        return next_state

    def update(self, events):
        mouse_pos = pygame.mouse.get_pos()

        next_state = self.__handle_event(events, mouse_pos)
        self.view.update(mouse_pos)

        return next_state

    def draw(self):
        self.view.draw()