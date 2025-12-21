import pygame

from src.utils.settings import GameState

class LevelSelectController:
    def __init__(self, level_select_view, assets, game_model, sound_controller):
        self.view = level_select_view
        self.assets = assets
        self.game_model = game_model

        self.change_level_sound = pygame.mixer.Sound('src/assets/sounds/hit_1.wav')
        self.change_level_sound.set_volume(sound_controller.get_effects_volume())
        self.click_sound = pygame.mixer.Sound('src/assets/sounds/blop_1.wav')
        self.click_sound.set_volume(sound_controller.get_effects_volume())
        self.wrong_sound = pygame.mixer.Sound('src/assets/sounds/hit_2.wav')
        self.wrong_sound.set_volume(sound_controller.get_effects_volume())

        self.view.current_level_unlocked = self.game_model.get_current_level_unlocked()

    def update(self, events):
        """
        Processa lógica da tela de seleção.
        Retorna: Novo GameState ou None.
        """
        next_state = None

        self.view.update()

        for event in events:
            if event.type == pygame.QUIT:
                return GameState.QUIT

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    next_state = self.__handle_click()

        return next_state

    def draw(self):
        """Delega o desenho para a View."""
        self.view.draw()

    def __handle_click(self):
        mouse_pos = pygame.mouse.get_pos()

        for i, level_slots_rect in enumerate(self.view.level_slots_rects):
            if level_slots_rect.collidepoint(mouse_pos):
                if i <= self.view.current_level_unlocked - 1:
                    self.view.current_selected_level = i
                    self.change_level_sound.play()
                else:
                    self.wrong_sound.play()

                return None

        if self.view.button_selected is not None:
            self.click_sound.play()

            if self.view.button_selected == "main_menu":
                return GameState.MAIN_MENU
            elif self.view.button_selected == "select":
                self.game_model.current_level = self.view.current_selected_level + 1
                return GameState.IN_GAME
        return None