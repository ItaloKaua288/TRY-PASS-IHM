from src.controller.game_controller import Game
import asyncio
import os, sys

dirpath = os.getcwd()
sys.path.append(dirpath)
if getattr(sys, "frozen", False):
    os.chdir(sys._MEIPASS)

async def main():
    game = Game()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())
