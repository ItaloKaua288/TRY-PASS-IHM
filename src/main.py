import pygame

from src import assets_manager
from view import game_view
from model import  game_model
from controller import game_controller
import config

pygame.init()
screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

assets = assets_manager.AssetsManager()

pygame.display.set_icon(assets.get_image(r"icons\logo.png"))
pygame.display.set_caption("TRY:PASS")
clock = pygame.time.Clock()

game_model = game_model.GameModel()
game_model.load_level("src/level_data/level_data_2.json", assets)

game_view = game_view.GameView(screen, assets, game_model)
game_controller = game_controller.GameController(game_model, game_view)

running = True
while running:
    clock.tick(config.FPS)

    events = pygame.event.get()
    mouse_pos = pygame.mouse.get_pos()

    game_view.draw(game_model)
    game_controller.update_elements(mouse_pos)
    game_controller.handle_events(events, mouse_pos)

    for event in events:
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()

pygame.quit()

