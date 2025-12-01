from src.controller.game_controller import Game
# import os, sys

# dirpath = os.getcwd()
# sys.path.append(dirpath)
# if getattr(sys, "frozen", False):
#     os.chdir(sys._MEIPASS)

def main():
    game = Game()
    game.run()

if __name__ == '__main__':
    main()
