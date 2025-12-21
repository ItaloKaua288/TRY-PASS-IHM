import pygame

class SoundController:
    def __init__(self, volume=1, music=1, effects=1):
        self.volume = max(0, min(volume, 1))
        self.music_volume = max(0, min(music, 1)) * self.volume
        self.effects_volume = max(0, min(effects, 1)) * self.volume

        self.music_enabled = True

        pygame.mixer.music.load("src/assets/sounds/background.ogg")
        pygame.mixer.music.set_volume(self.music_volume)
        pygame.mixer.music.play(-1)

    def volume_up(self):
        if self.volume <= 0.8:
            self.volume = round(self.volume + 0.2, 1)

    def volume_down(self):
        if self.volume >= 0.2:
            self.volume = round(self.volume - 0.2, 1)

    def music_up(self):
        if self.music_volume <= 0.8:
            self.music_volume = round(self.music_volume + 0.2, 1)
            if self.music_enabled:
                pygame.mixer.music.set_volume(self.music_volume)
            else:
                pygame.mixer.music.set_volume(0)

    def music_down(self):
        if self.music_volume >= 0.2:
            self.music_volume = round(self.music_volume - 0.2, 1)
            if self.music_enabled:
                pygame.mixer.music.set_volume(self.music_volume)
            else:
                pygame.mixer.music.set_volume(0)

    def get_music_volume(self):
        return self.music_volume * self.volume

    def effects_up(self):
        if self.effects_volume <= 0.8:
            self.effects_volume = round(self.effects_volume + 0.2, 1)

    def effects_down(self):
        if self.effects_volume >= 0.2:
            self.effects_volume = round(self.effects_volume - 0.2, 1)

    def get_effects_volume(self):
        return self.effects_volume * self.volume

    def disable_music(self):
        self.music_enabled = False
        pygame.mixer.music.set_volume(0)

    def enable_music(self):
        self.music_enabled = True
        pygame.mixer.music.set_volume(self.music_volume)