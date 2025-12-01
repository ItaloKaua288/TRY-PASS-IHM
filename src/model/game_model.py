import json
import re
from os import path, listdir
from pathlib import Path
from src.model import entities

from src.model.player import Player
from src.utils.settings import BASE_PATH, TILE_SIZE, TOTAL_SLOTS_EXECUTION


class GameModel:
    def __init__(self, current_level=1):
        self.help = None
        self.map = None
        self.constraints = None
        self.player_start = None
        self.config = None
        self.meta = None
        self.entities = {}
        self.current_level = current_level
        self.tile_map_surf = {}
        self.final_objective_pos = None

        self.enemies = []

        self.player = None

        self.execution_queue = []

        self.current_level_unlocked = self.__load_save_game()

    def load_level(self, assets):
        """Carrega os dados do JSON e inicializa as entidades."""
        self.execution_queue = []
        self.enemies = []

        self.tile_map_surf = assets.get_tileset("images/sprites/tiles_map")

        file_path = path.join(BASE_PATH, "level_data", f"level_data_{self.current_level}.json")

        try:
            with open(file_path, "r", encoding='utf-8') as file:
                level_data = json.load(file)

                self.meta = level_data["meta"]
                self.config = level_data["config"]
                self.player_start = [x * TILE_SIZE for x in level_data["player"]["player_start"].values()]
                self.final_objective_pos = [x * TILE_SIZE for x in level_data["final_objective"].values()]
                self.constraints = level_data["constraints"]
                self.map = level_data["map"]
                self.help = level_data["help"]

                self.entities = {}
                for entity in level_data["entities"]:
                    entity["pos"] = [x * TILE_SIZE for x in entity["pos"].values()]

                    if entity["type"] == "enemy":
                        entity_obj = entities.DefaultEnemy(1, entity["pos"], entity["behavior"]["pattern"], assets, entity["subtype"])
                        entity_obj.direction = entity["behavior"]["direction"]
                        self.enemies.append(entity_obj)
                        continue
                    elif entity["type"] == "chest":
                        items = [entities.Item(x["id"], x["qty"]) for x in entity["properties"]["items"]]
                        entity_obj = entities.Chest(entity["pos"], items)
                    elif entity["type"] == "door":
                        entity_obj = entities.Door(entity["pos"], entity["properties"]["state"], entity["properties"]["required_item"])
                    elif entity["type"] == "padlock_wall":
                        entity_obj = entities.PadlockWall(entity["pos"], entity["properties"]["required_item"])

                    if self.entities.keys().__contains__(entity["type"]):
                        self.entities[entity["type"]].append(entity_obj)
                    else:
                        self.entities[entity["type"]] = [entity_obj]

                # for entity in level_data["entities"]:
                #     entity["pos"] = [x * TILE_SIZE for x in entity["pos"].values()]
                #
                #     if entity["type"] == "enemy":
                #         enemy = DefaultEnemy(
                #             entity["properties"]["life"],
                #             entity["pos"],
                #             entity["behavior"]["pattern"],
                #             assets,
                #         )
                #         enemy.direction = entity["behavior"]["direction"]
                #         self.enemies.append(enemy)
                #
                #     if self.entities.keys().__contains__(entity["type"]):
                #         self.entities[entity["type"]].append(entity)
                #     else:
                #         self.entities[entity["type"]] = [entity]

                self.player = Player(self.player_start, assets)
                self.player.direction = level_data["player"]["direction"]
        except FileNotFoundError:
            print(f"ERRO: Level {self.current_level} não encontrado.")
            if self.current_level != 1:
                print("Tentando carregar o Nível 1 como fallback...")
                self.current_level = 1
                self.load_level(assets)
            else:
                print("CRÍTICO: Nível 1 também não existe. Verifique os arquivos.")

    def add_execution_command(self, command, value=1, index=None):
        if command is None or len(self.execution_queue) >= TOTAL_SLOTS_EXECUTION:
            return

        cmd_data = [command, value]

        if index is None:
            self.execution_queue.append(cmd_data)
        else:
            self.execution_queue.insert(index, cmd_data)

    def remove_execution_command(self, index=-1):
        if 0 <= index < len(self.execution_queue):
            return self.execution_queue.pop(index)
        return None

    def clear_execution_commands(self):
        self.execution_queue.clear()

    def switch_command_slot(self, command_index, target_index):
        if command_index < 0 or command_index >= len(self.execution_queue):
            return

        target_index = max(0, min(target_index, len(self.execution_queue) - 1))

        command = self.execution_queue.pop(command_index)
        self.execution_queue.insert(target_index, command)

    def get_remaining_collectibles_count(self):
        count = 0
        for key, entities in self.entities.items():
            if key != "door" and key != "padlock_wall":
                for entity in entities:
                    # if "is_opened" in entity["properties"].keys() and not entity["properties"]["is_opened"]:
                    if hasattr(entity, "is_opened") and not entity.is_opened:
                        count += 1
        return count

    def get_current_level_unlocked(self):
        return self.current_level_unlocked

    def save_game(self):
        """Salva o progresso se o jogador desbloqueou um nível novo."""
        max_available = self.__max_level_available()
        next_unlock = self.current_level

        self.current_level_unlocked = max(1, min(max_available, next_unlock))

        save_file_path = (Path.home() / "Documents" / "Try Pass" / "save_game.json").resolve()
        save_file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(path.join(save_file_path), "w") as file:
                json.dump({"current_level_unlocked": self.current_level_unlocked}, file, indent=4)
        except IOError as e:
            print(f"Erro ao salvar jogo: {e}")

    def reset_save_game(self):
        save_folder_path = (Path.home() / "Documents" / "Try Pass").resolve()
        save_folder_path.mkdir(parents=True, exist_ok=True)

        try:
            with open(path.join(save_folder_path, "save_game.json"), "w") as file:
                json.dump({"current_level_unlocked": 1}, file, indent=4)
        except IOError as e:
            print(f"Erro ao resetar o save game: {e}")

    def __load_save_game(self):
        save_file_path = (Path.home() / "Documents" / "Try Pass" / "save_game.json").resolve()
        save_file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(save_file_path, "r") as file:
                data = json.load(file)
                return data.get("current_level_unlocked", 1)
        except (FileNotFoundError, json.JSONDecodeError):
            return 1

    def __max_level_available(self):
        count = 0
        level_dir = path.join(BASE_PATH, "level_data")
        try:
            for file in listdir(level_dir):
                if re.match(r"^level_data_([1-9]\d*)\.json$", file):
                    count += 1
        except FileNotFoundError:
            return 0
        return count

    def is_available_level(self, level: int):
        max_level = self.__max_level_available()
        return 1 <= level <= max_level

