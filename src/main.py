import pygame

from src import assets_manager
from view import game_view, main_menu_view
from model import  game_model
from controller import game_controller, main_menu_controller
import config

class GameState:
    MAIN_MENU = "MAIN_MENU"
    IN_GAME = "IN_GAME"
    LEVEL_SELECT = "LEVEL_SELECT"
    QUIT = "QUIT"

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.assets = assets_manager.AssetsManager()

        pygame.display.set_caption("TRY:PASS")
        pygame.display.set_icon(self.assets.get_image(r"icons/logo.png"))

        self.game_model = game_model.GameModel()
        self.game_model.load_level("src/level_data/level_data_2.json", self.assets)

        self.main_menu_view = main_menu_view.MainMenuView(self.screen, self.assets)
        self.game_view = game_view.GameView(self.screen, self.assets, self.game_model)

        self.main_menu_controller = main_menu_controller.MainMenuController(self.main_menu_view)
        self.game_controller = game_controller.GameController(self.game_model, self.game_view)

        self.current_game_state = GameState.MAIN_MENU

    def run(self):
        while self.current_game_state != GameState.QUIT:
            events = pygame.event.get()
            mouse_pos = pygame.mouse.get_pos()

            if self.current_game_state == GameState.MAIN_MENU:
                self.main_menu_controller.handle_events(events, self)

                self.main_menu_view.update(mouse_pos)
                self.main_menu_view.draw()
            elif self.current_game_state == GameState.IN_GAME:
                self.game_controller.handle_events(events, self.game_model)
                self.game_controller.run_game(mouse_pos)
                self.game_view.draw(self.game_model, self.assets)

            pygame.display.flip()
            self.clock.tick(config.FPS)
            for event in events:
                if event.type == pygame.QUIT:
                    self.current_game_state = GameState.QUIT

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()