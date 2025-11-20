import pygame

from src.utils.settings import GameState

class MenuController:
    def __init__(self, menu_view, game_model):
        self.view = menu_view
        self.game_model = game_model

        self.__check_continue_availability()

    def update(self, events):
        """
        Processa a lógica do menu.
        Retorna: O novo GameState se houver mudança, ou None se continuar no Menu.
        """
        next_state = None

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

    def __check_continue_availability(self):
        """Verifica no Model se existe progresso para habilitar o botão Continuar."""
        if self.game_model.get_current_level_unlocked() > 1:
            self.view.continue_button_is_visible = True
        else:
            self.view.continue_button_is_visible = False

    def __handle_mouse_hover(self):
        mouse_pos = pygame.mouse.get_pos()
        self.view.option_selected = None

        for i, rect in enumerate(self.view.options_rects):
            if rect.collidepoint(mouse_pos):
                self.view.option_selected = i
                return

    def __handle_mouse_click(self):
        if self.view.option_selected is None:
            return None

        selected_option = self.view.options[self.view.option_selected]

        # Lógica de Transição de Estados
        if selected_option == "Continuar" and self.view.continue_button_is_visible:
            return GameState.CONTINUE_GAME

        elif selected_option == "Novo Jogo":
            return GameState.NEW_GAME  # Isso vai para o NEW_GAME no GameController

        elif selected_option == "Opções":
            print("Ainda não implementado")
            return None

        elif selected_option == "Sair":
            return GameState.QUIT

        return None
