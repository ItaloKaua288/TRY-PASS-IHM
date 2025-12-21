import pygame

from src.utils.settings import GameState

class MenuController:
    def __init__(self, menu_view, game_model, sound_controller):
        self.view = menu_view
        self.game_model = game_model
        self.sound_controller = sound_controller

        self.hover_sound = pygame.mixer.Sound('src/assets/sounds/hit_1.wav')
        self.click_sound = pygame.mixer.Sound('src/assets/sounds/blop_1.wav')

        self.__check_continue_availability()

    def update(self, events):
        """
        Processa a lógica do menu.
        Retorna: O novo GameState se houver mudança, ou None se continuar no Menu.
        """
        next_state = None

        self.view.update()
        self.__update_sounds()
        self.__update_options_menu()

        for event in events:
            if event.type == pygame.MOUSEMOTION:
                self.__handle_mouse_hover()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    next_state = self.__handle_mouse_click()

        return next_state

    def draw(self):
        """Apenas delega o desenho para a View."""
        self.view.draw()

    def __update_sounds(self):
        self.hover_sound.set_volume(self.sound_controller.get_effects_volume())
        self.click_sound.set_volume(self.sound_controller.get_effects_volume())

    def __update_options_menu(self):
        panel = self.view.panels["options_menu"]

        for k, btn in panel["buttons"].items():
            if k == "mute":
                btn["is_visible"] = self.sound_controller.music_enabled
            elif k == "unmute":
                btn["is_visible"] = not self.sound_controller.music_enabled
            elif k == "music_volume":
                btn["value"] = int(self.sound_controller.music_volume * 5)
            else:
                btn["value"] = int(self.sound_controller.effects_volume * 5)

    def __check_continue_availability(self):
        """Verifica no Model se existe progresso para habilitar o botão Continuar."""
        if self.game_model.get_current_level_unlocked() > 1:
            self.view.continue_button_is_visible = True
        else:
            self.view.continue_button_is_visible = False

    def __handle_mouse_hover(self):
        mouse_pos = pygame.mouse.get_pos()

        for i, rect in enumerate(self.view.options_rects):
            if rect.collidepoint(mouse_pos):
                if self.view.option_selected == i:
                    return
                self.hover_sound.play()
                self.view.option_selected = i
                return
        self.view.option_selected = None

    def __handle_mouse_click(self):
        options_menu = self.view.panels["options_menu"]
        if options_menu["is_visible"]:
            for k, btn in options_menu["buttons"].items():
                if btn["is_visible"] and btn["is_hovered"]:
                    if k == "mute":
                        self.sound_controller.disable_music()
                        btn["is_visible"] = not btn["is_visible"]
                    elif k == "unmute":
                        self.sound_controller.enable_music()
                        btn["is_visible"] = not btn["is_visible"]
                    elif k in ["music_volume", "effect_volume"]:
                        if btn["down_btn"]["is_hovered"]:
                            btn["value"] = max(0, btn["value"] - 1)

                            if k == "music_volume":
                                self.sound_controller.music_down()
                            else:
                                self.sound_controller.effects_down()
                        elif btn["up_btn"]["is_hovered"]:
                            btn["value"] = min(5, btn["value"] + 1)

                            if k == "music_volume":
                                self.sound_controller.music_up()
                            else:
                                self.sound_controller.effects_up()
                    return None

        if self.view.option_selected is None:
            return None

        selected_option = self.view.options[self.view.option_selected]
        self.click_sound.play()

        if selected_option == "Continuar" and self.view.continue_button_is_visible:
            return GameState.CONTINUE_GAME
        elif selected_option == "Novo Jogo":
            return GameState.NEW_GAME
        elif selected_option == "Opções":
            self.view.panels["options_menu"]["is_visible"] = not self.view.panels["options_menu"]["is_visible"]
            return None
        elif selected_option == "Sair":
            return GameState.QUIT

        return None
