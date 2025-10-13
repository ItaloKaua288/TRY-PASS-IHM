import pygame

from src import assets_manager
from view import game_view
from model import  game_model
from controller import game_controller
import config

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
        self.view = game_view.GameView(self.screen, self.assets, self.game_model)

        self.controller = game_controller.GameController(self.game_model, self.view)

    def run(self):
        while self.game_model.running:
            events = pygame.event.get()
            self.controller.handle_events(events, self.game_model)

            mouse_pos = pygame.mouse.get_pos()
            self.controller.run_game(mouse_pos)
            self.view.draw(self.game_model, self.assets)

            pygame.display.flip()
            self.clock.tick(config.FPS)

            for event in events:
                if event.type == pygame.QUIT:
                    self.game_model.running = False

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()