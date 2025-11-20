from . import player, enemy
from src.model.items import Chest, Door, Item
from src.config import TILE_SIZE, BASE_PATH
from os import path
import json


class GameState:
    CODING = "CODING"
    EXECUTING = "EXECUTING"


class GameModel:
    def __init__(self):
        self.final_objective_pos = None
        self.objective_text = None
        self.player = None
        self.enemy_list = []
        self.tile_map = []
        self.walkable_tiles = {9, 10}
        self.interactable_objects = {}
        self.available_actions = []

        self.last_level_played = 0

        self.running = True

        self.actions_sequence = []
        self.current_action_index = -1
        self.last_action_index = -1

        self.game_state = GameState.CODING

    def load_level(self, level_filepath, assets):
        level_data = assets.get_level_data(level_filepath)
        if not level_data:
            return False

        self.tile_map = level_data["tile_map"]
        self.objective_text = level_data["objective_text"]

        player_pos_pixel = level_data["player_start_pos"][0] * TILE_SIZE, level_data["player_start_pos"][1] * TILE_SIZE
        self.player = player.Player(player_pos_pixel, assets)
        self.available_actions = level_data["available_actions"]
        self.final_objective_pos = level_data["final_objective_pos"][0] * TILE_SIZE, level_data["final_objective_pos"][1] * TILE_SIZE

        for key, item_list in level_data["interactable_objects"].items():
            item_class_list = []
            if key == "chest.png":
                for item in item_list:
                    item_pos = (item[0][0] * TILE_SIZE, item[0][1] * TILE_SIZE)
                    internal_items = [Item(item_name.split(".")[0], assets) for item_name in item[1:]]
                    chest = Chest(item_pos, assets, internal_items)
                    item_class_list.append(chest)
            elif key == "door.png":
                for item in item_list:
                    item_pos = (item[0][0] * TILE_SIZE, item[0][1] * TILE_SIZE)
                    door = Door(item_pos, assets)
                    item_class_list.append(door)
            self.interactable_objects[key] = item_class_list

        for key, enemy_pos_list in level_data["enemies"].items():
            for pos in enemy_pos_list:
                pixel_pos = (pos[0] * TILE_SIZE, pos[1] * TILE_SIZE)
                self.enemy_list.append(enemy.DefaultEnemy(1, pixel_pos, assets))

        with open(path.join(BASE_PATH, "src", "level_data", "game_save.json"), 'r', encoding='utf-8') as file:
            game_save = json.load(file)
            self.last_level_played = game_save["last_level_played"]
            file.close()
        return True

    def get_count_collectibles_available(self):
        count = 0
        for item in self.interactable_objects["chest.png"]:
            if not item.is_interacted:
                count += 1
        return count

    def add_action_to_sequence(self, action, pos=-1):
        if len(self.actions_sequence) >= 26:
            return

        if self.game_state == GameState.CODING:
            if pos >= 0:
                self.actions_sequence.insert(pos, action)
            else:
                self.actions_sequence.append(action)

    def change_command_slot(self, command_index, new_index):
        command = self.actions_sequence.pop(command_index)
        self.actions_sequence.insert(new_index, command)

    def remove_action_from_sequence(self, index):
        if self.game_state == GameState.CODING and 0 <= index < len(self.actions_sequence):
            self.actions_sequence.pop(index)

    def start_execution(self):
        if self.game_state == GameState.CODING and len(self.actions_sequence) > 0:
            self.game_state = GameState.EXECUTING

    def reset_sequence(self):
        for action in self.actions_sequence:
            action.is_finished = False
            self.current_action_index = -1
        self.last_action_index = -1

    def clear_sequence(self):
        self.actions_sequence.clear()
        self.game_state = GameState.CODING

    def update(self):
        self.player.update()

    def is_valid_move(self, pos_pixels):
        pos_pixels_x, pos_pixels_y = pos_pixels
        pos_x = pos_pixels_x // TILE_SIZE
        pos_y = pos_pixels_y // TILE_SIZE

        if not (0 <= pos_y < len(self.tile_map) and 0 <= pos_x < len(self.tile_map[0])):
            return False

        tile_id = self.tile_map[pos_y][pos_x]
        return tile_id in self.walkable_tiles

    def is_victory(self):
        return self.final_objective_pos == self.player.target_pos

    def unlock_next_level(self):
        file_src = path.join(BASE_PATH, "src", "level_data", "game_save.json")
        game_save = {}
        with open(file_src, 'r', encoding='utf-8') as file:
            game_save = json.load(file)
            game_save["current_level_unlocked"] += 1
            file.close()

        with open(file_src, 'w', encoding='utf-8') as file:
            file.write(json.dumps(game_save))
            file.close()

    def get_current_level_unlocked(self):
        file_src = path.join(BASE_PATH, "src", "level_data", "game_save.json")
        with open(file_src, 'r', encoding='utf-8') as file:
            game_save = json.load(file)
            current_level_unlocked = game_save["current_level_unlocked"]
            file.close()
            return current_level_unlocked