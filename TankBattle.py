import random
import sys
import pygame
import math
import time
from pygame.math import Vector2
import pickle

# GET SYSTEM ARGUMENTS #
if len(sys.argv) > 1:
    # sys.argv[1]...
    pass

# GLOBAL CONSTANTS #
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 760
FRAME_RATE = 60

TANK_WIDTH = 40
SHOT_SPEED = 10
TANK_LENGTH = 60
TURN_SPEED = 4
ACCELERATION = .005
MAX_SPEED = 0.3
FRICTION = 0.002

COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_RED_DARK = (100, 0, 0)
COLOR_RED_MEDIUM = (200, 70, 70)
COLOR_RED_LIGHT = (220, 100, 100)
COLOR_RED_ULTRALIGHT = (255, 180, 180)
COLOR_BLUE = (0, 0, 255)
COLOR_BLUE_DARK = (0, 0, 100)
COLOR_BLUE_MEDIUM = (70, 70, 200)
COLOR_BLUE_LIGHT = (100, 100, 220)
COLOR_BLUE_ULTRALIGHT = (180, 180, 255)
COLORS_DIRT = [(77, 48, 25), (58, 36, 19), (19, 12, 6)]
RED_PROFILE = {"light": COLOR_RED_LIGHT,
               "ultralight": COLOR_RED_ULTRALIGHT,
               "medium": COLOR_RED_MEDIUM,
               "dark": COLOR_RED_DARK,
               "full": COLOR_RED}
BLUE_PROFILE = {"light": COLOR_BLUE_LIGHT,
                "ultralight": COLOR_BLUE_ULTRALIGHT,
                "medium": COLOR_BLUE_MEDIUM,
                "dark": COLOR_BLUE_DARK,
                "full": COLOR_BLUE}

# CUSTOM EVENTS #
MY_EVENT = pygame.USEREVENT + 0

# PYGAME INIT #
pygame.init()
clock = pygame.time.Clock()
main_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
TIME_START = pygame.time.get_ticks()

""" SPRITE TEMPLATE
class MySprite(pygame.sprite.Sprite):

    def __init__(self, *args):
        pygame.sprite.Sprite.__init__(self)

    def update(self, *args):
        pass
"""


class Tank(pygame.sprite.Sprite):

    def __init__(self, xpos, ypos, color):
        pygame.sprite.Sprite.__init__(self)
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
        self.pos = Vector2((xpos, ypos))
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        self.direction = 0
        self.speed = 0
        self.track = 0

    def update(self, *args):
        if self.speed != 0:
            self.move_tracks()
        self.rotate()
        self.move()
        # Slow down tank if not accelerating
        if self.speed > 0:
            self.speed = max(0, self.speed - FRICTION)

    def rotate(self):
        self.image = pygame.transform.rotozoom(self.orig_image, -self.direction, 1)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def move(self):
        self.pos.x += self.speed * 10 * math.cos(math.radians(self.direction))
        self.pos.x = min(self.pos.x, SCREEN_WIDTH - TANK_WIDTH // 2)
        self.pos.x = max(TANK_WIDTH // 2, self.pos.x)
        self.pos.y += self.speed * 10 * math.sin(math.radians(self.direction))
        self.pos.y = min(self.pos.y, SCREEN_HEIGHT - TANK_WIDTH // 2)
        self.pos.y = max(TANK_WIDTH // 2, self.pos.y)
        if (self.pos.x == 0 + TANK_WIDTH // 2 or self.pos.x == SCREEN_WIDTH - TANK_WIDTH // 2) \
                or (self.pos.y == 0 + TANK_WIDTH // 2 or self.pos.y == SCREEN_HEIGHT - TANK_WIDTH // 2):
            self.speed = max(0, self.speed - ACCELERATION)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def move_tracks(self):
        self.track = (self.track + self.speed * 10) % 5
        pygame.draw.rect(self.orig_image, self.color_light, (0, 0, TANK_LENGTH, 8))
        pygame.draw.rect(self.orig_image, self.color_light, (0, TANK_WIDTH - 8, TANK_LENGTH, 8))
        for i in range(-1, (TANK_LENGTH // 5) + 1):
            pygame.draw.rect(self.orig_image, self.color_dark, (int((i * 5) + self.track), 0, 5, 8), 1)
            pygame.draw.rect(self.orig_image, self.color_dark, (int((i * 5) + self.track), TANK_WIDTH - 8, 5, 8), 1)

    def turn(self, a):
        self.direction = (self.direction + a) % 360

    def accelerate(self, t):
        self.speed += t
        self.speed = min(self.speed, MAX_SPEED)
        self.speed = max(0, self.speed)


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
        self.rotate()

    def rotate(self):
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


class Shot(pygame.sprite.Sprite):

    def __init__(self, size, start_pos, aim, tank_aim, tank_speed, color):
        self.color_ultralight = color["ultralight"]
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((size, size))
        self.image.fill(COLOR_WHITE)
        self.image.set_colorkey(COLOR_WHITE)
        pygame.draw.circle(self.image, self.color_ultralight, (size // 2, size // 2), size // 2)
        self.rect = self.image.get_rect()
        self.rect.centerx = int(start_pos.x + math.cos(-math.radians(aim)) * 30)
        self.rect.centery = int(start_pos.y + math.sin(-math.radians(aim)) * 30)
        self.aim = -math.radians(aim)
        self.size = size
        if self.size > 4:
            self.speed = SHOT_SPEED
        else:
            self.speed = SHOT_SPEED * 1.5
        self.tank_aim = tank_aim
        self.tank_speed = tank_speed
        self.pos = Vector2(start_pos)

    def update(self, *args):
        if -100 < self.rect.centerx < SCREEN_WIDTH + 100 and -100 < self.rect.centery < SCREEN_HEIGHT + 100:
            self.rect.centerx += int(self.speed * math.cos(self.aim))
            self.rect.centery += int(self.speed * math.sin(self.aim))
            self.rect.centerx += int(self.tank_speed * math.cos(self.tank_aim))
            self.rect.centery += int(self.tank_speed * math.sin(self.tank_aim))
            self.pos = Vector2(self.rect.center)
        else:
            self.kill()
            del self


class Player:

    def __init__(self, xpos, ypos, color):
        self.color = color
        self.tank = Tank(xpos, ypos, self.color)
        self.cannon = Cannon(self.tank.pos, self.color)
        self.shots = pygame.sprite.RenderPlain(())
        self.parts = pygame.sprite.RenderPlain(())
        self.parts.add(self.tank, self.cannon)
        self.last_shot = 0

    def update(self):
        self.parts.update(self.tank.pos)
        self.shots.update()

    def turn_right(self):
        self.tank.turn(TURN_SPEED)

    def turn_left(self):
        self.tank.turn(-TURN_SPEED)

    def go(self):
        self.tank.accelerate(ACCELERATION)

    def stop(self):
        self.tank.accelerate(-ACCELERATION)

    def shoot(self, size):
        if size > 0:
            shot = Shot(size, self.cannon.pos, self.cannon.angle, self.tank.direction,
                        self.tank.speed, self.color)
            self.shots.add(shot)
            self.last_shot = shot.size
            return shot

    def aim(self, target):
        self.cannon.aim(target)

    def get_pos(self):
        return self.tank.pos

    def get_sprites(self):
        return self.tank, self.cannon

    def get_data(self):
        data = {"pos": self.tank.pos,
                "direction": self.tank.direction,
                "speed": self.tank.speed,
                "angle": self.cannon.angle,
                "last_shot": self.last_shot}
        self.last_shot = 0
        return pickle.dumps(data, -1)

    def set_data(self, data):
        data = pickle.loads(data)
        self.tank.pos = data["pos"]
        self.tank.pos.x += 500 ########################################
        self.tank.direction = data["direction"]
        self.tank.speed = data["speed"]
        self.cannon.angle = data["angle"]
        if data["last_shot"] != 0:
            shot = Shot(data["last_shot"], self.cannon.pos, self.cannon.angle, self.tank.direction,
                        self.tank.speed, self.color)
            self.shots.add(shot)


class HitPixel(pygame.sprite.Sprite):

    def __init__(self, xy=(0, 0), size=5):
        PIXEL_COLORS = [(255, 0, 0), (255, 255, 0), (255, 153, 51)]

        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((random.randrange(2, size), random.randrange(2, size)))
        self.image.fill(random.choice(PIXEL_COLORS))
        self.rect = self.image.get_rect()
        self.angle = random.random() * (2 * math.pi)
        self.rect.center = (int(xy[0]), int(xy[1]))
        self.speed = random.random() * 20
        self.image.set_alpha(255)

    def update(self, *args):
        self.rect.centerx += int(self.speed * math.cos(self.angle))
        self.rect.centery += int(self.speed * math.sin(self.angle))
        self.image.set_alpha(self.image.get_alpha() - 20)
        if self.image.get_alpha() <= 0:
            self.kill()
            del self


def make_background_tile(colors):
    width = 100
    height = 100
    surf = pygame.Surface((width, height))
    surf.fill(COLOR_BLACK)
    pArr = pygame.PixelArray(surf)
    for i in range(height):
        for j in range(width):
            pArr[i][j] = random.choice(colors)

    surf.set_colorkey(COLOR_BLACK)
    return surf


DIRT_BG = make_background_tile(COLORS_DIRT)


def main():
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    for i in range(SCREEN_WIDTH // DIRT_BG.get_width() + 1):
        for j in range(SCREEN_HEIGHT // DIRT_BG.get_width() + 1):
            background.blit(DIRT_BG, (i * DIRT_BG.get_width(), j * DIRT_BG.get_width()))

    player = Player(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2, RED_PROFILE)
    enemy = Player(SCREEN_WIDTH // 4 * 3, SCREEN_HEIGHT // 2, BLUE_PROFILE)

    elements = pygame.sprite.RenderPlain(())
    elements.add(player.get_sprites(), enemy.get_sprites())

    pixels = pygame.sprite.RenderPlain(())

    done = False
    while not done:
        # GAME CLOCK #
        clock.tick(FRAME_RATE)

        # EVENT HANDLER #
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                done = True
                break

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                pass

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left-click
                    player.shoot(10)
                if event.button == 2:  # right-click
                    pass
                if event.button == 3:  # middle-click
                    pass

        # PLAYER MOVEMENT #
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:  # right key pressed
            player.turn_right()
        if keys[pygame.K_a]:  # left key pressed
            player.turn_left()
        if keys[pygame.K_w]:  # up key pressed
            player.go()
        if keys[pygame.K_s]:  # up key pressed
            player.stop()

        buttons = pygame.mouse.get_pressed()
        if buttons[2] == 1:
            player.shoot(4)

        player.aim(pygame.mouse.get_pos())
        # enemy.aim(player.get_pos())

        # SCREEN UPDATES #
        main_screen.fill(COLOR_BLACK)
        main_screen.blit(background, (0, 0))

        player.update()
        enemy.update()

        player_hit = pygame.sprite.spritecollide(enemy.tank, player.shots, True)
        if player_hit:
            for i in range(5):
                pixels.add(HitPixel(player_hit[0].pos, player_hit[0].size))
        enemy_hit = pygame.sprite.spritecollide(player.tank, enemy.shots, True)
        if enemy_hit:
            for i in range(5):
                pixels.add(HitPixel(enemy_hit[0].pos, enemy_hit[0].size))

        temp = player.get_data()
        enemy.set_data(temp)

        pixels.update()
        player.shots.draw(main_screen)
        enemy.shots.draw(main_screen)
        elements.draw(main_screen)
        pixels.draw(main_screen)

        pygame.display.update()

    # CLEAN UP & QUIT #

    pygame.quit()


# START #
if __name__ == "__main__":
    main()
