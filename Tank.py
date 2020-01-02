import math
import pygame
from pygame.math import Vector2


TANK_WIDTH = 40
TANK_LENGTH = 60


class Tank(pygame.sprite.Sprite):

    def __init__(self, xpos, ypos, color):
        pygame.sprite.Sprite.__init__(self)
        self.pos = Vector2(xpos, ypos)
        self.cannon = Cannon(self.pos, color)
        self.color_light = color["light"]
        self.color_dark = color["dark"]
        self.image = pygame.Surface((TANK_LENGTH, TANK_WIDTH), pygame.SRCALPHA)
        pygame.draw.rect(self.image, self.color_light, (0, 0, TANK_LENGTH, TANK_WIDTH))
        pygame.draw.rect(self.image, self.color_dark, (0, 0, TANK_LENGTH, TANK_WIDTH), 1)
        pygame.draw.rect(self.image, self.color_dark, (TANK_LENGTH - 5, 10, 5, TANK_WIDTH - 20), 1)
        pygame.draw.polygon(self.image, self.color_dark,
                            [(0, 8),
                             (0, TANK_WIDTH - 8),
                             (20, TANK_WIDTH // 2 + 8),
                             (20, TANK_WIDTH // 2 - 8)], 1)
        for i in range(-1, (TANK_LENGTH // 5 + 1)):
            pygame.draw.rect(self.image, self.color_dark, (i * 5, 0, 5, 8), 1)
            pygame.draw.rect(self.image, self.color_dark, (i * 5, TANK_WIDTH - 8, 5, 8), 1)
        self.orig_image = self.image
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        self.direction = 0
        self.speed = 0
        self.track = 0
        self.aim = self.cannon.angle

    def update(self, *args):
        if self.speed != 0:
            self._move_tracks()
        self._rotate()
        self._move()
        self.cannon.update(self.pos)
        self.aim = self.cannon.angle

    def _rotate(self):
        self.image = pygame.transform.rotozoom(self.orig_image, -self.direction, 1)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def _move(self):
        self.pos.x += self.speed * 10 * math.cos(math.radians(self.direction))
        self.pos.y += self.speed * 10 * math.sin(math.radians(self.direction))
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def _move_tracks(self):
        self.track = (self.track + self.speed * 10) % 5
        pygame.draw.rect(self.orig_image, self.color_light, (0, 0, TANK_LENGTH, 8))
        pygame.draw.rect(self.orig_image, self.color_light, (0, TANK_WIDTH - 8, TANK_LENGTH, 8))
        for i in range(-1, (TANK_LENGTH // 5) + 1):
            pygame.draw.rect(self.orig_image, self.color_dark, (int((i * 5) + self.track), 0, 5, 8), 1)
            pygame.draw.rect(self.orig_image, self.color_dark, (int((i * 5) + self.track), TANK_WIDTH - 8, 5, 8), 1)

    def turn(self, a):
        self.direction = (self.direction + a) % 360

    def aim_cannon(self, target):
        self.cannon.aim(target)


class Cannon(pygame.sprite.Sprite):

    def __init__(self, tank_pos, color):
        self.color_medium = color["medium"]
        self.color_dark = color["dark"]
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((80, 20), pygame.SRCALPHA)
        pygame.draw.rect(self.image, self.color_medium, (30, 7, 50, 6))
        pygame.draw.rect(self.image, self.color_dark, (30, 7, 50, 6), 1)
        pygame.draw.rect(self.image, self.color_medium, (20, 0, 30, 20))
        pygame.draw.rect(self.image, self.color_dark, (20, 0, 30, 20), 1)
        pygame.draw.rect(self.image, self.color_medium, (70, 5, 10, 10))
        pygame.draw.rect(self.image, self.color_dark, (70, 5, 10, 10), 1)
        pygame.draw.circle(self.image, self.color_dark, (40, 10), 7, 1)
        self.orig_image = self.image
        self.rect = self.image.get_rect(center=(int(tank_pos.x), int(tank_pos.y)))
        self.pos = tank_pos
        self.offset = Vector2(0, 0)
        self.angle = 0
        self.x = 0
        self.y = 0

    def update(self, *args):
        if len(args) != 0:
            self.pos = args[0]
        self._rotate()

    def _rotate(self):
        self.image = pygame.transform.rotozoom(self.orig_image, self.angle, 1)
        offset_rotated = self.offset.rotate(math.radians(self.angle)) + self.pos
        self.rect = self.image.get_rect(center=(int(offset_rotated.x), int(offset_rotated.y)))

    def aim(self, target):
        self.x, self.y = target
        self.x -= self.pos.x
        self.y -= self.pos.y
        angle = Vector2(0, 0).angle_to(Vector2(self.x, self.y))
        if angle == 0:
            pass
        elif angle < 0:
            angle *= -1
        else:
            angle = 360 - angle
        self.angle = int(angle)
