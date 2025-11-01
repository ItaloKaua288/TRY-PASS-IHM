import pygame

from src.config import GameStateMap
from src.view import game_view
from src.model import game_model


class LevelSelectController:
    def __init__(self, view, game_model, assets, game_manager):
        self.view = view
        self.game_model = game_model
        self.game_manager = game_manager
        self.assets = assets

    def run(self, events, mouse_pos):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.__handle_click(mouse_pos)
            elif event.type == pygame.KEYDOWN:
                self.__handle_key_pressed()

    def __handle_click(self, mouse_pos):
        for key, button in self.view.buttons.items():
            if button.is_hovered:
                if key == "main_menu":
                    self.game_manager.current_game_state = GameStateMap.MAIN_MENU
                elif key == "select":
                    self.game_manager.game_model = game_model.GameModel()
                    # self.game_view = game_view.GameView(self.view, self.assets, self.game_model)
                    self.game_manager.game_model.load_level(f"src/level_data/level_data_{self.view.level_selected}.json", self.assets)
                    self.game_manager.game_view.model = self.game_manager.game_model
                    self.game_manager.game_controller.model = self.game_manager.game_model
                    self.game_manager.game_view.panels["map"].game_model = self.game_manager.game_model
                    self.game_manager.game_view.panels["map"].update_new_map()
                    self.game_manager.game_view.panels["execution"].game_model = self.game_manager.game_model
                    self.game_manager.current_game_state = GameStateMap.IN_GAME
                return

        for i, level_slot_rect in enumerate(self.view.level_slot_rects):
            if level_slot_rect.collidepoint(mouse_pos):
                self.view.level_selected = i

    def __handle_key_pressed(self):
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_d]:
            if self.view.level_selected < len(self.view.level_slot_rects) - 1:
                self.view.level_selected += 1
        elif keys_pressed[pygame.K_a]:
            if not self.view.level_selected <= 0:
                self.view.level_selected -= 1

