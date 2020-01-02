import os
import random
import sys
import pygame
import math
import time
from pygame.math import Vector2
import pickle
from Tank import Tank

# GET SYSTEM ARGUMENTS #
if len(sys.argv) > 1:
    # sys.argv[1]...
    pass

# FILE SETTINGS #
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")

# DISPLAY SETTINGS #
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 760
FRAME_RATE = 60

# GAME ELEMENT SETTINGS #
TURN_SPEED = 4
MAX_HEALTH = 1000
MAX_SPEED = 0.3
FRICTION = 0.002
ACCELERATION = .005
BIG_SHOT_SIZE = 10
BIG_SHOT_MAX = 5
BIG_SHOT_SPEED = 10
SMALL_SHOT_SIZE = 4
SMALL_SHOT_MAX = 100
SMALL_SHOT_SPEED = 15

# COLOR SETTINGS #
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_GREEN = (255, 0, 0)
PIXEL_COLORS = [(255, 0, 0), (255, 255, 0), (255, 153, 51)]
DIRT_COLORS = [(77, 48, 25), (58, 36, 19), (19, 12, 6)]
ROCK_COLORS = [(128, 128, 128), (77, 77, 77), (51, 51, 51)]
RED_PROFILE = {"light": (220, 100, 100),
               "ultralight": (255, 180, 180),
               "medium": (200, 70, 70),
               "dark": (100, 0, 0),
               "full": COLOR_RED}
BLUE_PROFILE = {"light": (100, 100, 220),
                "ultralight": (180, 180, 255),
                "medium": (70, 70, 200),
                "dark": (0, 0, 100),
                "full": COLOR_BLUE}


def make_background_tile(colors, width=10, height=10):
    width = width
    height = height
    surf = pygame.Surface((width, height))
    surf.fill(COLOR_BLACK)
    pArr = pygame.PixelArray(surf)
    for i in range(width):
        for j in range(height):
            pArr[i][j] = random.choice(colors)

    surf.set_colorkey(COLOR_BLACK)
    return surf


class Shot(pygame.sprite.Sprite):

    def __init__(self, size, p):
        self.color_ultralight = p.color["ultralight"]
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((size, size))
        self.image.fill(COLOR_WHITE)
        self.image.set_colorkey(COLOR_WHITE)
        pygame.draw.circle(self.image, self.color_ultralight, (size // 2, size // 2), size // 2)
        self.rect = self.image.get_rect()
        self.aim = -math.radians(p.tank.cannon.angle)
        self.rect.centerx = int(p.tank.cannon.pos.x + math.cos(self.aim) * 30)
        self.rect.centery = int(p.tank.cannon.pos.y + math.sin(self.aim) * 30)
        self.size = size
        if self.size == BIG_SHOT_SIZE:
            self.speed = BIG_SHOT_SPEED
        elif self.size == SMALL_SHOT_SIZE:
            self.speed = SMALL_SHOT_SPEED
        self.tank_aim = p.tank.direction
        self.tank_speed = p.tank.speed
        self.pos = Vector2(p.tank.cannon.pos)

    def update(self, *args):
        if 0 < self.rect.centerx < SCREEN_WIDTH and 0 < self.rect.centery < SCREEN_HEIGHT:
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
        self.shots = pygame.sprite.RenderPlain(())
        self.parts = pygame.sprite.RenderPlain(self.tank)
        self.target = (0, 0)
        self.last_shot = 0
        self.health = 1000
        self.big_shots = BIG_SHOT_MAX
        self.small_shots = SMALL_SHOT_MAX

    def update(self, target=None):

        if game_timer % 60 == 0:
            self.big_shots = min(self.big_shots + 1, BIG_SHOT_MAX)
        if game_timer % 20 == 0:
            self.small_shots = min(self.small_shots + 1, SMALL_SHOT_MAX)

        if target:
            self.target = target

        if self.tank.speed <= 0:
            self.tank.speed = 0
        else:
            self.tank.speed -= FRICTION

        self.tank.aim_cannon(self.target)
        self.parts.update()
        self.shots.update()

        element = pygame.sprite.spritecollideany(self.tank, obstructions)
        if element and element != self.tank:
            angle = Vector2(0, 0).angle_to(self.tank.pos - element.pos)
            if abs(angle) > 135:       # RIGHT SIDE
                self.tank.rect.right = element.rect.left
            elif 0 < abs(angle) < 45:  # LEFT SIDE
                self.tank.rect.left = element.rect.right
            elif 45 < angle < 135:     # TOP SIDE
                self.tank.rect.top = element.rect.bottom
            else:                      # BOTTOM SIDE
                self.tank.rect.bottom = element.rect.top
            self.tank.pos = Vector2(self.tank.rect.center)
            self.tank.speed = max(0, self.tank.speed - ACCELERATION)

        if not main_screen.get_rect().contains(self.tank):
            rect = self.tank.rect
            if rect.top <= 0:
                rect.top = 0
            if rect.bottom >= SCREEN_HEIGHT:
                rect.rect.bottom = SCREEN_HEIGHT
            if rect.left <= 0:
                rect.left = 0
            if rect.right >= SCREEN_WIDTH:
                rect.right = SCREEN_WIDTH
            self.tank.pos = Vector2(rect.center)
            self.tank.speed = max(0, self.tank.speed - ACCELERATION)

    def turn_right(self):
        self.tank.turn(TURN_SPEED)

    def turn_left(self):
        self.tank.turn(-TURN_SPEED)

    def go(self):
        if self.tank.speed < MAX_SPEED:
            self.tank.speed += ACCELERATION

    def stop(self):
        if self.tank.speed > 0:
            self.tank.speed -= ACCELERATION

    def shoot(self, size):
        log_shot = False
        if size == BIG_SHOT_SIZE:
            if self.big_shots > 0:
                self.big_shots -= 1
                log_shot = True
        elif size == SMALL_SHOT_SIZE:
            if self.small_shots > 0:
                self.small_shots -= 1
                log_shot = True
        if log_shot:
            shot = Shot(size, self)
            self.shots.add(shot)
            self.last_shot = shot.size

    def take_damage(self, size):
        if size == BIG_SHOT_SIZE:
            self.health = max(0, self.health - 10)
        if size == SMALL_SHOT_SIZE:
            self.health = max(0, self.health - 1)

    def get_pos(self):
        return self.tank.pos

    def get_sprites(self):
        return self.tank, self.tank.cannon

    def get_data(self):
        data = {"pos": self.tank.pos,
                "direction": self.tank.direction,
                "speed": self.tank.speed,
                "target": self.target,
                "last_shot": self.last_shot,
                "health": self.health,
                "big_shots": self.big_shots,
                "small_shots": self.small_shots}
        self.last_shot = 0
        return pickle.dumps(data, -1)

    def set_data(self, data):
        data = pickle.loads(data)
        self.tank.pos = data["pos"]
        self.tank.pos.x += 500  ########################################
        self.tank.direction = data["direction"]
        self.tank.speed = data["speed"]
        self.target = data["target"]
        if data["last_shot"]:
            shot = Shot(data["last_shot"], self)
            self.shots.add(shot)
        self.health = data["health"]
        self.big_shots = data["big_shots"]
        self.small_shots = data["small_shots"]


class HitPixel(pygame.sprite.Sprite):

    def __init__(self, xy=(0, 0), size=5):
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


def draw_text(text, surface, font, x, y, color, bg, pos='left'):
    text_image = font.render(text, 1, color, bg)
    text_image.set_colorkey(bg)
    text_rect = text_image.get_rect()

    if pos == 'left':
        text_rect.topleft = (int(x), int(y))
    elif pos == 'center':
        text_rect.midtop = (int(x), int(y))
    elif pos == 'right':
        text_rect.topright = (int(x), int(y))

    surface.blit(text_image, text_rect)
    return text_rect


def draw_info_banner():
    global player, enemy
    h = MAX_HEALTH // 200

    # PLAYER INFO
    temp = draw_text("PLAYER", main_screen, TEXT_FONT_SMALL, 20, 20, COLOR_WHITE, COLOR_BLACK)
    pygame.draw.rect(main_screen, player.color["dark"], (20, temp.bottom + 10, MAX_HEALTH // h, 20))
    pygame.draw.rect(main_screen, player.color["medium"], (20, temp.bottom + 10, player.health // h, 20))
    bar = pygame.draw.rect(main_screen, player.color["light"], (20, temp.bottom + 10, MAX_HEALTH // h, 20), 1)
    for i in range(BIG_SHOT_MAX):
        shots = pygame.draw.rect(main_screen, player.color["dark"], (20 + i * 10, bar.bottom + 10, 5, 10))
        if i <= player.big_shots:
            pygame.draw.rect(main_screen, player.color["light"], (20 + i * 10, bar.bottom + 10, 5, 10))
    for i in range(SMALL_SHOT_MAX):
        pygame.draw.rect(main_screen, player.color["dark"], (20 + i * 2, shots.bottom + 10, 1, 10), 1)
        if i <= player.small_shots:
            pygame.draw.rect(main_screen, player.color["light"], (20 + i * 2, shots.bottom + 10, 1, 10))
    # ENEMY INFO #
    temp = draw_text("ENEMY", main_screen, TEXT_FONT_SMALL, SCREEN_WIDTH - 20, 20, COLOR_WHITE, COLOR_BLACK, "right")
    pygame.draw.rect(main_screen, enemy.color["dark"],
                     (SCREEN_WIDTH - 20 - MAX_HEALTH // h, temp.bottom + 10, MAX_HEALTH // h, 20))
    pygame.draw.rect(main_screen, enemy.color["medium"],
                     (SCREEN_WIDTH - 20 - enemy.health // h, temp.bottom + 10, enemy.health // h, 20))
    bar = pygame.draw.rect(main_screen, enemy.color["light"],
                           (SCREEN_WIDTH - 20 - MAX_HEALTH // h, temp.bottom + 10, MAX_HEALTH // h, 20), 1)
    for i in range(BIG_SHOT_MAX):
        shots = pygame.draw.rect(main_screen, enemy.color["dark"],
                                 (SCREEN_WIDTH - 20 + i * 10 - BIG_SHOT_MAX * 10 + 5, bar.bottom + 10, 5, 10))
        if BIG_SHOT_MAX - i <= enemy.big_shots:
            pygame.draw.rect(main_screen, enemy.color["light"],
                             (SCREEN_WIDTH - 20 + i * 10 - BIG_SHOT_MAX * 10 + 5, bar.bottom + 10, 5, 10))
    for i in range(SMALL_SHOT_MAX):
        pygame.draw.rect(main_screen, enemy.color["dark"],
                         (SCREEN_WIDTH - 20 + i * 2 - SMALL_SHOT_MAX * 2 + 1, shots.bottom + 10, 1, 10), 1)
        if SMALL_SHOT_MAX - i <= enemy.small_shots:
            pygame.draw.rect(main_screen, enemy.color["light"],
                             (SCREEN_WIDTH - 20 + i * 2 - SMALL_SHOT_MAX * 2 + 1, shots.bottom + 10, 1, 10))


# GAME INITIALIZATION #
pygame.init()
clock = pygame.time.Clock()
TIME_START = pygame.time.get_ticks()
game_timer = 0

# FONT SETTINGS #
TITLE_FONT = pygame.font.Font(os.path.join(data_dir, "freesansbold.ttf"), 160)
BANNER_FONT = pygame.font.Font(os.path.join(data_dir, "freesansbold.ttf"), 52)
TEXT_FONT_BIG = pygame.font.Font(os.path.join(data_dir, "freesansbold.ttf"), 30)
TEXT_FONT_MED = pygame.font.Font(os.path.join(data_dir, "freesansbold.ttf"), 20)
TEXT_FONT_SMALL = pygame.font.Font(os.path.join(data_dir, "freesansbold.ttf"), 16)
TEXT_FONT_TINY = pygame.font.Font(os.path.join(data_dir, "freesansbold.ttf"), 12)

# AREA ELEMENTS #
main_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
DIRT_BG = make_background_tile(DIRT_COLORS, 200, 200)
ROCK_BG = make_background_tile(ROCK_COLORS, 50, 50)
# GRASS_BG
# WATER_BG

# PLAYER ELEMENTS #
player = Player(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2, RED_PROFILE)
enemy = Player(SCREEN_WIDTH // 4 * 3, SCREEN_HEIGHT // 2, BLUE_PROFILE)

# SPRITE CONTAINER INITIALIZATION #
tanks = pygame.sprite.RenderPlain((enemy.get_sprites(), player.get_sprites()))
obstructions = pygame.sprite.RenderPlain((enemy.tank))
map_elements = pygame.sprite.RenderPlain(())
pixels = pygame.sprite.RenderPlain(())


def main():
    global main_screen, player, enemy, game_timer

    for i in range(math.ceil(SCREEN_WIDTH // DIRT_BG.get_width()) + 1):
        for j in range(math.ceil(SCREEN_HEIGHT // DIRT_BG.get_width()) + 1):
            background.blit(DIRT_BG, (i * DIRT_BG.get_width(), j * DIRT_BG.get_width()))

    done = False
    while not done:
        # GAME CLOCK #
        clock.tick(FRAME_RATE)
        game_timer += 1

        # EVENT HANDLER #
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                done = True
                break

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                pass

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left-click
                    player.shoot(BIG_SHOT_SIZE)
                if event.button == 2:  # right-click
                    pass
                if event.button == 3:  # middle-click
                    pass

        # PLAYER MOVEMENT #
        " TANK MOVEMENT "
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:  # right key pressed
            player.turn_right()
        if keys[pygame.K_a]:  # left key pressed
            player.turn_left()
        if keys[pygame.K_w]:  # up key pressed
            player.go()
        if keys[pygame.K_s]:  # up key pressed
            player.stop()
        " RAPID FIRE "
        buttons = pygame.mouse.get_pressed()
        if buttons[2] == 1:
            player.shoot(SMALL_SHOT_SIZE)

        # SCREEN UPDATES #
        main_screen.fill(COLOR_BLACK)
        main_screen.blit(background, (0, 0))
        draw_info_banner()

        # PLAYER UPDATE #
        player.update(pygame.mouse.get_pos())
        #temp = player.get_data()
        #enemy.set_data(temp)
        enemy.update()

        # HIT DETECTION #
        enemy_shot = pygame.sprite.spritecollide(enemy.tank, player.shots, True)
        if enemy_shot:
            # enemy.take_damage(enemy_shot[0].size)
            for i in range(5):
                pixels.add(HitPixel(enemy_shot[0].pos, enemy_shot[0].size))

        player_shot = pygame.sprite.spritecollide(player.tank, enemy.shots, True)
        if player_shot:
            player.take_damage(player_shot[0].size)
            for i in range(5):
                pixels.add(HitPixel(player_shot[0].pos, player_shot[0].size))

        # PROCESS ALL UPDATES #
        pixels.update()
        player.shots.draw(main_screen)
        enemy.shots.draw(main_screen)
        tanks.draw(main_screen)
        pixels.draw(main_screen)

        pygame.display.update()

    # CLEAN UP & QUIT #

    pygame.quit()


# START #
if __name__ == "__main__":
    main()
