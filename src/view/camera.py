import pygame


class Camera:
    def __init__(self, size, map_size, pos):
        self.width, self.height = size
        self.map_width, self.map_height = map_size
        self.rect = pygame.Rect(pos[0], pos[1], self.width, self.height)

    def apply_offset(self, entity_rect):
        return entity_rect.move(self.rect.topleft)

    def update(self, target_entity):
        x = max(-(self.map_width - self.width), min(0, -target_entity.x + int(self.width / 2)))
        y = max(-(self.map_height - self.height), min(0, -target_entity.y + int(self.height / 2)))

        self.rect.x = x
        self.rect.y = y
