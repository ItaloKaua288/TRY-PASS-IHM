import asyncio
import sys
import pygame

from src.controller.sound_controller import SoundController
from src.utils.settings import SCREEN_WIDTH, SCREEN_HEIGHT, GameState
from src.utils.assets_manager import AssetsManager
from src.model.game_model import GameModel

from src.view.level_select_view import LevelSelectView
from src.controller.level_select_controller import LevelSelectController
from src.view.main_menu_view import MenuView
from src.controller.main_menu_controller import MenuController
from src.view.in_game_view import GameView
from src.controller.in_game_controller import GameController

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("TRY:PASS")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.assets = AssetsManager()
        pygame.display.set_icon(self.assets.get_image("images/icons/logo.png"))

        self.game_model = GameModel(1)

        self.state = GameState.MAIN_MENU
        self.current_controller = None

        self.sound_controller = SoundController(1, 0.2, 2)

        self._switch_state(GameState.MAIN_MENU)

    def _switch_state(self, new_state):
        """Gerencia a troca de controladores e views centralizada."""
        self.state = new_state

        if self.state == GameState.MAIN_MENU:
            view = MenuView(self.screen, self.assets)
            self.current_controller = MenuController(view, self.game_model, self.sound_controller)
        elif self.state == GameState.LEVEL_SELECT:
            view = LevelSelectView(self.screen, self.assets)
            self.current_controller = LevelSelectController(view, self.assets, self.game_model, self.sound_controller)
        elif self.state == GameState.IN_GAME:
            if self.game_model.current_level >= 5:
                self._switch_state(GameState.MAIN_MENU)
            else:
                self.game_model.load_level(self.assets)
                view = GameView(self.screen, self.assets, self.game_model)
                self.current_controller = GameController(view, self.game_model, self.sound_controller)
        elif self.state == GameState.CONTINUE_GAME:
            level = self.game_model.get_current_level_unlocked()
            self.game_model.current_level = level
            self._switch_state(GameState.IN_GAME)
        elif self.state == GameState.NEW_GAME:
            self.game_model.current_level = 1
            self.game_model.reset_save_game()
            self.game_model.save_game()
            self._switch_state(GameState.LEVEL_SELECT)
        elif self.state == GameState.QUIT:
            pygame.quit()
            sys.exit()

    async def run(self):
        """Loop Principal Único (Single Loop Pattern)"""
        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False

            if self.current_controller:
                next_state = self.current_controller.update(events)
                if next_state:
                    self._switch_state(next_state)

            self.screen.fill((0, 0, 0))

            if self.current_controller:
                self.current_controller.draw()

            pygame.display.flip()
            self.clock.tick(60)

            # await asyncio.sleep(0)
