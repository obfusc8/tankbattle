import os
import random
import socket
import sys
import threading
import time
from tkinter import Tk, messagebox
import pygame
import math
from pygame.compat import geterror
from pygame.math import Vector2
import pickle

# GET SYSTEM ARGUMENTS #
if len(sys.argv) > 1:
    # sys.argv[1]...
    pass

# FILE SETTINGS #
"""
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)
"""
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")

# DISPLAY SETTINGS #
SCREEN_WIDTH = 1250
SCREEN_HEIGHT = 750
FRAME_RATE = 30

# GAME ELEMENT SETTINGS #
TANK_WIDTH = 40
TANK_LENGTH = 60
TURN_SPEED = 8
MAX_HEALTH = 750
MAX_SPEED = .6
FRICTION = 0.01
ACCELERATION = .02
BIG_SHOT_SIZE = 10
BIG_SHOT_MAX = 5
BIG_SHOT_SPEED = 20
BIG_SHOT_DAMAGE = 10
SMALL_SHOT_SIZE = 4
SMALL_SHOT_MAX = 100
SMALL_SHOT_SPEED = 30
SMALL_SHOT_DAMAGE = 1

# COLOR SETTINGS #
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_GREEN = (255, 0, 0)
PIXEL_COLORS = [(255, 0, 0), (255, 255, 0), (255, 153, 51)]
DIRT_COLORS = [(77, 48, 25), (58, 36, 19), (19, 12, 6)]
SAND_COLORS = [(212, 186, 119), (194, 156, 61), (136, 109, 43)]
ROCK_COLORS = [(110, 110, 110), (77, 77, 77), (51, 51, 51)]
GRASS_COLORS = [(96, 70, 0), (57, 70, 0)]
WATER_COLORS = [(0, 80, 150), (0, 50, 70)]
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

# 1150 x 850 = 23 x 17 @ 50px Cells
GAME_MAP1 = "" \
            "........................." \
            "........................." \
            ".......RRRRRRRRRRR......." \
            "............R............" \
            "............R............" \
            "...R.................R..." \
            "...R.....R.....R.....R..." \
            "...R.....RRRRRRR.....R..." \
            "...R.....R.....R.....R..." \
            "...R.................R..." \
            "............R............" \
            "............R............" \
            ".......RRRRRRRRRRR......." \
            "........................." \
            "........................."

GAME_MAP2 = "" \
            "GGGGGGGGGGWWWWWGGGGGGGGGG" \
            "GGGGGGGGGGWWWWWGGGGGGGGGG" \
            "GGGGGGGRRRRRRRRRRRGGGGGGG" \
            "GGGG........R........GGGG" \
            "GGGG........R........GGGG" \
            "GGGR.................RGGG" \
            "GGGR.....R.....R.....RGGG" \
            "GGGR.....RRRRRRR.....RGGG" \
            "GGGR.....R.....R.....RGGG" \
            "GGGR.................RGGG" \
            "GGGG........R........GGGG" \
            "GGGG........R........GGGG" \
            "GGGGGGGRRRRRRRRRRRGGGGGGG" \
            "GGGGGGGGGGWWWWWGGGGGGGGGG" \
            "GGGGGGGGGGWWWWWGGGGGGGGGG"


def load_sound(name):
    class NoneSound:
        def play(self):
            pass

    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(data_dir, name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error:
        print("Cannot load sound: %s" % fullname)
        raise SystemExit(str(geterror()))
    return sound


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


def make_background_tile(colors, width=10, height=10, border=0):
    width = width
    height = height
    image = pygame.Surface((width, height))
    image.fill(COLOR_WHITE)
    image_pixels = pygame.PixelArray(image)
    for i in range(width):
        for j in range(height):
            image_pixels[i][j] = random.choice(colors)

    if border > 0:
        for i in range(width):
            image_pixels[i][0] = colors[-1]
            image_pixels[i][height - 1] = colors[-1]
        image_pixels[0] = colors[-1]
        image_pixels[width - 1] = colors[-1]

    image.set_colorkey(COLOR_WHITE)
    return image


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
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = 0
        self.speed = 0
        self.track = 0
        self.aim = self.cannon.angle
        self.dead = False

    def update(self, *args):
        if not self.dead:
            if self.speed != 0:
                self._move_tracks()
            self._rotate()
            self._move()
            self.cannon.update(self.pos)
            self.aim = self.cannon.angle

    def _rotate(self):
        self.image = pygame.transform.rotozoom(self.orig_image, -self.direction, 1)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        self.mask = pygame.mask.from_surface(self.image)

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

    def face_towards(self, target):
        x, y = target
        x -= self.pos.x
        y -= self.pos.y
        angle = Vector2(0, 0).angle_to(Vector2(x, y))
        if angle == 0:
            pass
        elif angle < 0:
            angle *= -1
        else:
            angle = 360 - angle
        self.direction = -int(angle)

    def destroy(self):
        self.dead = True
        pygame.draw.rect(self.orig_image, (0, 0, 0, 125), (0, 0, TANK_LENGTH, TANK_WIDTH))
        self._rotate()
        self.cannon.kill()


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


class Shot(pygame.sprite.Sprite):

    def __init__(self, size, p):
        self.color_ultralight = p.color["ultralight"]
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((size, size))
        self.image.fill(COLOR_WHITE)
        self.image.set_colorkey(COLOR_WHITE)
        pygame.draw.circle(self.image, self.color_ultralight, (size // 2, size // 2), size // 2)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.pos = p.tank.pos
        if size == BIG_SHOT_SIZE:
            speed = BIG_SHOT_SPEED
        elif size == SMALL_SHOT_SIZE:
            speed = SMALL_SHOT_SPEED
        aim = -math.radians(p.tank.cannon.angle)
        self.rect.centerx = int(p.tank.cannon.pos.x + math.cos(aim) * 30)
        self.rect.centery = int(p.tank.cannon.pos.y + math.sin(aim) * 30)
        self.xv = int(speed * math.cos(aim) + p.tank.speed * math.cos(p.tank.direction))
        self.yv = int(speed * math.sin(aim) + p.tank.speed * math.sin(p.tank.direction))
        self.size = size

    def update(self, *args):
        if main_screen.get_rect().contains(self):
            self.rect.centerx += self.xv
            self.rect.centery += self.yv
            self.pos = Vector2(self.rect.center)
        else:
            self.kill()
            del self


class HitPixel(pygame.sprite.Sprite):

    def __init__(self, xy=(0, 0), size=5, alpha_fade=25):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((random.randrange(2, size), random.randrange(2, size)))
        self.image.fill(random.choice(PIXEL_COLORS))
        self.rect = self.image.get_rect()
        self.angle = random.random() * (2 * math.pi)
        self.rect.center = (int(xy[0]), int(xy[1]))
        self.speed = random.random() * 40
        self.image.set_alpha(255)
        self.alpha_fade = alpha_fade

    def update(self, *args):
        if self.rect.x > SCREEN_WIDTH - self.image.get_width() or self.rect.x < 0:
            self.angle = math.pi - self.angle
        if self.rect.y > SCREEN_HEIGHT - self.image.get_height() or self.rect.y < 0:
            self.angle *= -1
        self.rect.centerx += int(self.speed * math.cos(self.angle))
        self.rect.centery += int(self.speed * math.sin(self.angle))
        self.image.set_alpha(self.image.get_alpha() - self.alpha_fade)
        if self.image.get_alpha() <= 0:
            self.kill()
            del self


class Element(pygame.sprite.Sprite):

    def __init__(self, image, xy):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = xy
        self.pos = Vector2(xy)
        self.health = 100
        self.alpha = 255

    def update(self, *args):
        if self in obstructions:
            shot = pygame.sprite.spritecollide(self, shots, False)
            if shot:
                for s in shot:
                    for i in range(5):
                        pixels.add(HitPixel(s.pos, s.size))
                    s.kill()
                    del s
                    """ WILL NEED TO COMMUNICATE GAME STATE BEFORE ADDING DESTRUCTION
                    self.health -= 1
                    self.alpha -= 2
                    self.image.set_alpha(self.alpha)
                    if self.health < 0:
                        for i in range(5):
                            pixels.add(HitPixel(self.pos, self.image.get_width()))
                        obstructions.remove(self)
    """


class LaserSight(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        epos = enemy.tank.pos
        ppos = player.tank.pos
        self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.line(self.image, (255, 0, 0), (int(epos.x), int(epos.y)), (int(ppos.x), int(ppos.y)))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.on_target = False

    def update(self, *args):
        self.image.fill((0, 0, 0, 0))
        epos = enemy.tank.pos
        ppos = player.tank.pos
        if pygame.sprite.spritecollideany(self, walls, pygame.sprite.collide_mask):
            pygame.draw.line(self.image, (255, 0, 0), (int(epos.x), int(epos.y)), (int(ppos.x), int(ppos.y)))
            self.on_target = False
        else:
            pygame.draw.line(self.image, (0, 255, 0), (int(epos.x), int(epos.y)), (int(ppos.x), int(ppos.y)))
            self.on_target = True
        self.mask = pygame.mask.from_surface(self.image)


class Player:

    def __init__(self, xpos, ypos, color, is_enemy=False):
        self.color = color
        self.tank = Tank(xpos, ypos, self.color)
        self.shots = pygame.sprite.RenderPlain(())
        self.parts = pygame.sprite.RenderPlain(self.tank)
        self.target = (0, 0)
        self.last_small_shot = 0
        self.last_big_shot = 0
        self.health = MAX_HEALTH
        self.big_shots = BIG_SHOT_MAX
        self.small_shots = SMALL_SHOT_MAX
        self.friction = FRICTION
        self.is_enemy = is_enemy

    def update(self, target=None):
        self.shots.update()
        if self.health > 0:
            if game_timer % FRAME_RATE == 0:
                self.big_shots = min(self.big_shots + 1, BIG_SHOT_MAX)
            if game_timer % FRAME_RATE//4 == 0:
                self.small_shots = min(self.small_shots + 1, SMALL_SHOT_MAX)
            if target:
                self.target = target

            if self.tank.speed <= 0:
                self.tank.speed = 0
            else:
                self.tank.speed -= self.friction
            self.tank.aim_cannon(self.target)
            self.parts.update()

            element = pygame.sprite.spritecollide(self.tank, obstructions, False, pygame.sprite.collide_mask)
            if element:
                for e in element:
                    if e != self.tank:
                        rect = self.tank.rect
                        angle = Vector2(0, 0).angle_to(self.tank.pos - e.pos)
                        if abs(angle) >= 135:  # RIGHT SIDE
                            rect.right = e.rect.left
                        if 0 <= abs(angle) <= 45:  # LEFT SIDE
                            rect.left = e.rect.right
                        if 45 < angle < 135:  # TOP SIDE
                            rect.top = e.rect.bottom
                        if -135 <= angle <= -45:  # BOTTOM SIDE
                            rect.bottom = e.rect.top
                        self.tank.pos = Vector2(rect.center)
                        self.tank.speed = max(0, self.tank.speed - ACCELERATION)

            if not main_screen.get_rect().contains(self.tank):
                rect = self.tank.rect
                if rect.top <= 0:
                    rect.top = 0
                if rect.bottom >= SCREEN_HEIGHT:
                    rect.bottom = SCREEN_HEIGHT
                if rect.left <= 0:
                    rect.left = 0
                if rect.right >= SCREEN_WIDTH:
                    rect.right = SCREEN_WIDTH
                self.tank.pos = Vector2(self.tank.rect.center)
                # self.tank.speed = max(0, self.tank.speed - ACCELERATION)

            if pygame.sprite.spritecollide(self.tank, obstacles, False):
                self.friction = FRICTION * 1.5
                self.tank.speed = min(self.tank.speed, MAX_SPEED / 2)
            else:
                self.friction = FRICTION

            shot = pygame.sprite.spritecollide(self.tank, shots, False, pygame.sprite.collide_mask)
            if shot and shot[0] not in self.shots:
                for i in range(5):
                    pixels.add(HitPixel(shot[0].pos, shot[0].size))
                if not (self.is_enemy and multi_player):
                    self.take_damage(shot[0].size)
                shot[0].kill()
                del shot[0]

        elif not self.tank.dead:
            self.tank.cannon.kill()
            self.tank.destroy()
            self.tank.kill()
            for i in range(500):
                pixels.add(HitPixel(self.tank.pos, 20, 2))
            ether.add(self.tank)

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
        if not self.tank.dead:
            log_shot = False
            if size == BIG_SHOT_SIZE:
                if self.big_shots > 0:
                    self.big_shots -= 1
                    log_shot = True
                    if sounds_on:
                        gun_sound.play()
                    self.last_big_shot = size
            elif size == SMALL_SHOT_SIZE:
                if self.small_shots > 0:
                    machine_gun_sound.stop()
                    if sounds_on:
                        machine_gun_sound.play()
                    self.small_shots -= 1
                    log_shot = True
                    self.last_small_shot = size
            if log_shot or (self.is_enemy and multi_player):
                shot = Shot(size, self)
                self.shots.add(shot)
                shots.add(shot)

    def take_damage(self, size):
        if size == BIG_SHOT_SIZE:
            self.health = max(0, self.health - BIG_SHOT_DAMAGE)
        if size == SMALL_SHOT_SIZE:
            self.health = max(0, self.health - SMALL_SHOT_DAMAGE)

    def get_pos(self):
        return self.tank.pos

    def is_dead(self):
        if self.tank.dead:
            return True
        else:
            return False

    def get_sprites(self):
        return self.tank, self.tank.cannon

    def send_data(self):
        data = {"pos": self.tank.pos,
                "direction": self.tank.direction,
                "speed": self.tank.speed,
                "target": self.target,
                "last_big_shot": self.last_big_shot,
                "last_small_shot": self.last_small_shot,
                "health": self.health}
        self.last_big_shot = 0
        self.last_small_shot = 0
        player_queue.insert(0, data)

    def receive_data(self, data):
        self.tank.pos = data["pos"]
        self.tank.direction = data["direction"]
        self.tank.speed = data["speed"]
        self.target = data["target"]
        self.health = data["health"]
        if data["last_big_shot"]:
            self.shoot(data["last_big_shot"])
        if data["last_small_shot"]:
            self.shoot(data["last_small_shot"])


# GAME INITIALIZATION #
pygame.init()
clock = pygame.time.Clock()
TIME_START = pygame.time.get_ticks()
recv_error_flag = False
send_error_flag = False
game_timer = 0

# NETWORKING SETUP #
if len(sys.argv) > 1:
    SERVER_IP = sys.argv[1]
else:
    # SERVER_IP = "192.168.86.38"
    SERVER_IP = "SAL-1908-KJ"
PORT = 9998
SEND_SERVER = None
RECV_SERVER = None
EVENT_CLOSE_SEND_SOCKET = pygame.USEREVENT + 0
EVENT_CLOSE_RECV_SOCKET = pygame.USEREVENT + 1

# FONT SETTINGS #
TITLE_FONT = pygame.font.Font(os.path.join(data_dir, "freesansbold.ttf"), 160)
BANNER_FONT = pygame.font.Font(os.path.join(data_dir, "freesansbold.ttf"), 52)
TEXT_FONT_BIG = pygame.font.Font(os.path.join(data_dir, "freesansbold.ttf"), 30)
TEXT_FONT_MED = pygame.font.Font(os.path.join(data_dir, "freesansbold.ttf"), 20)
TEXT_FONT_SMALL = pygame.font.Font(os.path.join(data_dir, "freesansbold.ttf"), 16)
TEXT_FONT_TINY = pygame.font.Font(os.path.join(data_dir, "freesansbold.ttf"), 12)

# LOAD SOUNDS #
gun_sound = load_sound("gun.wav")
machine_gun_sound = load_sound("machine_gun.wav")
explosion_sound = load_sound("explosion.wav")
idle_sound = load_sound("idle.wav")
win_sound = load_sound("win.wav")
lose_sound = load_sound("lose.wav")

# AREA ELEMENTS #
main_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
DIRT_BG = make_background_tile(DIRT_COLORS, 200, 200)
ROCK_BG = make_background_tile(ROCK_COLORS, 50, 50, 1)
SAND_BG = make_background_tile(SAND_COLORS, 50, 50)
GRASS_BG = make_background_tile(GRASS_COLORS, 50, 50)
WATER_BG = make_background_tile(WATER_COLORS, 50, 50)
element_key = {"R": ROCK_BG, "S": SAND_BG, "G": GRASS_BG, "W": WATER_BG}

# PLAYER ELEMENTS #
player = Player(main_screen.get_rect().left + 375, SCREEN_HEIGHT // 3*2, RED_PROFILE)
enemy = Player(main_screen.get_rect().right - 375, SCREEN_HEIGHT // 3*2, BLUE_PROFILE, True)
enemy_laser_sight = None
player_queue = list()
enemy_queue = list()
send_thread = None
recv_thread = None

# GAME SETTINGS #
sounds_on = False
auto_aim_on = False
final_sounds_played = False
multi_player = False
single_player = False
start_on_left = False
game_on = True

# SPRITE CONTAINER INITIALIZATION #
tanks = pygame.sprite.RenderPlain((enemy.get_sprites(), player.get_sprites()))
shots = pygame.sprite.RenderPlain(())
obstructions = pygame.sprite.RenderPlain(enemy.tank)
walls = pygame.sprite.RenderPlain(())
obstacles = pygame.sprite.RenderPlain()
map_elements = pygame.sprite.RenderPlain(())
ether = pygame.sprite.RenderPlain(())
pixels = pygame.sprite.RenderPlain(())


def make_server_connections():
    global SEND_SERVER, RECV_SERVER, recv_error_flag, start_on_left, send_thread, recv_thread

    send_server_connected = False
    recv_server_connected = False

    try:

        while not (send_server_connected and recv_server_connected):

            TEMP_SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            print(" Connecting to the TankBattle server... ")
            TEMP_SERVER.connect((SERVER_IP, PORT))
            greeting = TEMP_SERVER.recv(1024).decode('ascii')
            print(" " + greeting)

            print(" " + "Waiting for the other player to join...")
            greeting = TEMP_SERVER.recv(1024).decode('ascii')
            print(" " + greeting)

            if greeting.find("1") != -1:  # first to connect
                SEND_SERVER = TEMP_SERVER
                send_thread = threading.Thread(target=send_server_thread, daemon=True)
                send_thread.start()
                send_server_connected = True
                if send_server_connected and not recv_server_connected:
                    start_on_left = True
                    time.sleep(2)  # give server time to make other send connection
            else:
                RECV_SERVER = TEMP_SERVER
                recv_thread = threading.Thread(target=recv_server_thread, daemon=True)
                recv_thread.start()
                recv_server_connected = True

    except OSError:
        info = "OSError: [WinError 10038] Try restarting the game..."
        print(info)
        recv_error_flag = True
    except ConnectionResetError:
        info = "[Connection Reset Error] Try restarting the game..."
        print(info)
        recv_error_flag = True
    except ConnectionAbortedError:
        info = "[Connection Aborted Error] Try restarting the game..."
        print(info)
        recv_error_flag = True
    except ConnectionRefusedError:
        info = "[Connection Refused Error] Try restarting the game..."
        print(info)
        print(" If this continues to occur, restart the Battleship server")
        recv_error_flag = True
    except KeyboardInterrupt:
        info = "[Keyboard Interrupt] Restart the game..."
        print(info)
        recv_error_flag = True


def send_server_thread():
    global send_error_flag

    send_server_connected = True
    #print("Starting the send server...")
    while send_server_connected:

        try:
            if len(player_queue) > 0:

                # SEND DATA
                #print("sending", str(player_queue[-1]))
                data = pickle.dumps(player_queue.pop(-1), -1)
                SEND_SERVER.send(data)

                # WAIT FOR ACKNOWLEDGEMENT
                #print("waiting for ACK")
                ack = SEND_SERVER.recv(64).decode('ascii')
                if not ack:
                    info = "SORRY! Server connection lost..."
                    print(info)
                    send_error_flag = True
                    break
                if ack != "ACK":
                    print(ack)
                #print("ACK received")

        except OSError:
            break

        for event in pygame.event.get(EVENT_CLOSE_SEND_SOCKET):
            if event.type == EVENT_CLOSE_SEND_SOCKET:
                print("THREAD: EVENT CLOSE DETECTED")
                send_server_connected = False
                break

    SEND_SERVER.close()
    print("SEND_SERVER Thread FINISHED")
    return


def recv_server_thread():
    global recv_error_flag

    recv_server_connected = True
    print("Starting the receive server...")
    while recv_server_connected:

        try:

            # RECEIVE DATA
            #print("waiting for data")
            pickled_data = RECV_SERVER.recv(1024)
            #print("received data")

            if not pickled_data:
                info = "SORRY! Server connection lost..."
                print(info)
                recv_error_flag = True
                break

            try:
                data = pickle.loads(pickled_data)
                # SEND ACKNOWLEDGEMENT
                #print("sending ack")
                RECV_SERVER.send("ACK".encode('ascii'))
                enemy_queue.insert(0, data)
                if len(enemy_queue) > 5:
                    enemy_queue.pop(-1)

            except pickle.UnpicklingError as info:
                print("UnpicklingError:", info.args)
                RECV_SERVER.send("BAD: UnpicklingError".encode('ascii'))
                continue
            except KeyError as info:
                print("KeyError:", info.args)
                RECV_SERVER.send("BAD: KeyError".encode('ascii'))
                continue

        except OSError:
            break

        for event in pygame.event.get(EVENT_CLOSE_RECV_SOCKET):
            if event.type == EVENT_CLOSE_RECV_SOCKET:
                print("THREAD: EVENT CLOSE DETECTED")
                recv_server_connected = False
                break

    RECV_SERVER.close()
    print("RECV SERVER Thread FINISHED")
    return


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


def load_map(element_map):
    width = SCREEN_WIDTH // 50
    height = SCREEN_HEIGHT // 50
    for i in range(height):
        for j in range(width):
            n = i * width + j
            if element_map[n] != ".":
                k = element_map[n]
                element = Element(element_key[element_map[n]], (j * 50 + 25, i * 50 + 25))
                map_elements.add(element)
                if element_map[n] == "R":
                    obstructions.add(element)
                    walls.add(element)
                if element_map[n] == "W":
                    obstacles.add(element)


def final_screen(win):
    global final_sounds_played
    if not final_sounds_played:
        if sounds_on:
            explosion_sound.play()
    if win:
        if sounds_on and not final_sounds_played:
            win_sound.play()
        temp = pygame.draw.rect(main_screen, (0, 200, 0), (0, SCREEN_HEIGHT//2-100, SCREEN_WIDTH, 200))
        temp = pygame.draw.rect(main_screen, (0, 100, 0), (0, temp.top + 25, SCREEN_WIDTH, 150))
        temp = draw_text("WINNER", main_screen, TITLE_FONT, SCREEN_WIDTH//2, temp.top - 25, COLOR_WHITE, COLOR_BLACK, "center")
    else:
        if sounds_on and not final_sounds_played:
            lose_sound.play()
        temp = pygame.draw.rect(main_screen, (200, 0, 0), (0, SCREEN_HEIGHT//2-100, SCREEN_WIDTH, 200))
        temp = pygame.draw.rect(main_screen, (100, 0, 0), (0, temp.top + 25, SCREEN_WIDTH, 150))
        temp = draw_text("LOSER", main_screen, TITLE_FONT, SCREEN_WIDTH//2, temp.top - 25, COLOR_WHITE, COLOR_BLACK, "center")
    temp = draw_text("Press 'Esc' to quit", main_screen, TEXT_FONT_MED, SCREEN_WIDTH // 2, temp.bottom + 25, COLOR_WHITE, COLOR_BLACK, "center")
    final_sounds_played = True


def enemy_bot():
    tank = enemy.tank
    global enemy_laser_sight
    if enemy_laser_sight is None:
        enemy_laser_sight = LaserSight()
    enemy_laser_sight.update()
    # main_screen.blit(enemy_laser_sight.image, (0, 0))   # COMMENT TO REMOVE LINE FROM VIEW
    if enemy_laser_sight.on_target:
        tank.face_towards(player.tank.pos)
        if not player.is_dead():
            if game_timer % 10 == 0:
                enemy.shoot(BIG_SHOT_SIZE)
            else:
                enemy.shoot(SMALL_SHOT_SIZE)
    elif game_timer % FRAME_RATE == 0:
        direction = math.radians(tank.direction)
        NW = tank.pos + 55 * Vector2(math.cos(direction-math.pi/4), math.sin(direction-math.pi/4))
        NE = tank.pos + 55 * Vector2(math.cos(direction+math.pi/4), math.sin(direction+math.pi/4))
        SE = tank.pos + 55 * Vector2(math.cos(direction+3*math.pi/4), math.sin(direction+3*math.pi/4))
        SW = tank.pos + 55 * Vector2(math.cos(direction-3*math.pi/4), math.sin(direction-3*math.pi/4))
        adjacents = [NW, NE, SE, SW]
        for wall in walls:
            for a in adjacents:
                if wall.rect.collidepoint(int(a[0]), int(a[1])):
                    adjacents.remove(a)
                    break
            closest = adjacents[0]
        for a in adjacents:
            if a.distance_to(player.tank.pos) < closest.distance_to(player.tank.pos):
                closest = a
        tank.face_towards(closest)
    else:
        enemy.go()


def setup_game():
    global sounds_on, auto_aim_on, start_on_left, single_player, multi_player, game_on, player, enemy
    # PLAYER SETUP #
    pregame = True
    show_controls = False
    show_start = False
    hide_button = pygame.Rect((0, 0, 0, 0))
    count_down = 4 * FRAME_RATE - 1
    server_started = False
    while pregame:
        clock.tick(FRAME_RATE)

        if multi_player and not server_started:
            make_server_connections()
            server_started = True

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                game_on = False
                pregame = False
                break

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                pregame = False
                break

            if event.type == pygame.KEYDOWN and event.key == pygame.K_1:
                sounds_on = not sounds_on

            if event.type == pygame.KEYDOWN and event.key == pygame.K_2:
                auto_aim_on = not auto_aim_on

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left-click
                    x, y = pygame.mouse.get_pos()
                    if single_button.collidepoint(x, y):
                        if not (single_player or multi_player):
                            single_player = True
                            start_on_left = True
                    elif multi_button.collidepoint(x, y):
                        if not (single_player or multi_player):
                            multi_player = True
                    elif controls_box.collidepoint(x, y):
                        show_controls = not show_controls
                    elif start_box.collidepoint(x, y):
                        if not (single_player or multi_player):
                            show_start = not show_start
                    else:
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

        main_screen.fill(COLOR_BLACK)
        main_screen.blit(background, (0, 0))

        temp = draw_text("TANK BATTLE", main_screen, TITLE_FONT, SCREEN_WIDTH // 2, SCREEN_HEIGHT//6, COLOR_WHITE, COLOR_BLACK, "center")
        if single_player:
            temp = draw_text("Single player game starting...", main_screen, TEXT_FONT_BIG, SCREEN_WIDTH // 2, temp.bottom+25, COLOR_WHITE, COLOR_BLACK, "center")
            temp = draw_text(str(max(0, count_down//FRAME_RATE)), main_screen, TITLE_FONT, SCREEN_WIDTH // 2, temp.bottom, COLOR_WHITE, COLOR_BLACK, "center")
            count_down -= 1
        if multi_player:
            temp = draw_text("Multi-player game starting...", main_screen, TEXT_FONT_BIG, SCREEN_WIDTH // 2, temp.bottom+25, COLOR_WHITE, COLOR_BLACK, "center")
            if server_started:
                temp = draw_text(str(max(0, count_down//FRAME_RATE)), main_screen, TITLE_FONT, SCREEN_WIDTH // 2, temp.bottom, COLOR_WHITE, COLOR_BLACK, "center")
                count_down -= 1

        if count_down // FRAME_RATE == 0:
            pregame = False

        if not show_controls:
            image = pygame.Surface((240, 50))
            image.fill((0, 0, 0))
            image.set_alpha(80)
            controls_box = main_screen.blit(image, (25, SCREEN_HEIGHT-image.get_height()-25))
            temp = draw_text("CONTROLS", main_screen, TEXT_FONT_MED, controls_box.centerx, controls_box.top+10, (150, 150, 150), COLOR_BLACK, "center")
        else:
            image = pygame.Surface((240, 300))
            image.fill((0, 0, 0))
            image.set_alpha(80)
            controls_box = main_screen.blit(image, (25, SCREEN_HEIGHT-image.get_height()-25))
            temp = draw_text("CONTROLS", main_screen, TEXT_FONT_MED, controls_box.centerx, controls_box.top+10, (150, 150, 150), COLOR_BLACK, "center")
            temp = draw_text("___________________", main_screen, TEXT_FONT_MED, controls_box.centerx, temp.top+10, (125, 125, 125), COLOR_BLACK, "center")
            temp = draw_text("FORWARD", main_screen, TEXT_FONT_SMALL, controls_box.centerx, temp.bottom+15, (220, 220, 220), COLOR_BLACK, "center")
            temp = draw_text("W", main_screen, TEXT_FONT_SMALL, controls_box.centerx, temp.bottom + 5, (220, 220, 220), COLOR_BLACK, "center")
            temp = draw_text("   LEFT    A        D    RIGHT", main_screen, TEXT_FONT_SMALL, controls_box.centerx, temp.bottom + 5, (220, 220, 220), COLOR_BLACK, "center")
            temp = draw_text("S", main_screen, TEXT_FONT_SMALL, controls_box.centerx, temp.bottom + 5, (220, 220, 220), COLOR_BLACK, "center")
            temp = draw_text("STOP", main_screen, TEXT_FONT_SMALL, controls_box.centerx, temp.bottom + 5, (220, 220, 220), COLOR_BLACK, "center")
            temp = draw_text("AIM - Mouse", main_screen, TEXT_FONT_SMALL, controls_box.centerx, temp.bottom + 25, (220, 220, 220), COLOR_BLACK, "center")
            temp = draw_text("FIRE - Left Click", main_screen, TEXT_FONT_SMALL, controls_box.centerx, temp.bottom + 5, (220, 220, 220), COLOR_BLACK, "center")
            temp = draw_text("RAPID FIRE - Right Click", main_screen, TEXT_FONT_SMALL, controls_box.centerx, temp.bottom + 5, (220, 220, 220), COLOR_BLACK, "center")

        if not show_start:
            image = pygame.Surface((240, 50))
            image.fill((0, 0, 0))
            image.set_alpha(80)
            start_box = main_screen.blit(image, (SCREEN_WIDTH-image.get_width()-25, SCREEN_HEIGHT-image.get_height()-25))
            temp = draw_text("START", main_screen, TEXT_FONT_MED, start_box.centerx, start_box.top+10, (150, 150, 150), COLOR_BLACK, "center")
            single_button = hide_button
            multi_button = hide_button
        else:
            image = pygame.Surface((240, 240))
            image.fill((0, 0, 0))
            image.set_alpha(80)
            start_box = main_screen.blit(image, (SCREEN_WIDTH-image.get_width()-25, SCREEN_HEIGHT-image.get_height()-25))
            image = pygame.Surface((200, 50))
            if single_player:
                image.fill((100, 50, 50))
            else:
                image.fill((50, 50, 50))
            single_button = main_screen.blit(image, (start_box.centerx-image.get_width()//2, start_box.top+70))
            image = pygame.Surface((200, 50))
            if multi_player:
                image.fill((100, 50, 50))
            else:
                image.fill((50, 50, 50))
            multi_button = main_screen.blit(image, (start_box.centerx-image.get_width()//2, start_box.top+160))
            temp = draw_text("START", main_screen, TEXT_FONT_MED, start_box.centerx, start_box.top+10, (150, 150, 150), COLOR_BLACK, "center")
            temp = draw_text("___________________", main_screen, TEXT_FONT_MED, start_box.centerx, temp.top+10, (125, 125, 125), COLOR_BLACK, "center")
            temp = draw_text("SINGLE PLAYER", main_screen, TEXT_FONT_SMALL, start_box.centerx, temp.bottom+40, (220, 220, 220), COLOR_BLACK, "center")
            temp = draw_text("MULTI-PLAYER", main_screen, TEXT_FONT_SMALL, start_box.centerx, temp.bottom+65, (220, 220, 220), COLOR_BLACK, "center")

        player.update(pygame.mouse.get_pos())
        enemy.update(player.tank.pos)

        pixels.update()

        shots.draw(main_screen)
        tanks.draw(main_screen)
        pixels.draw(main_screen)

        pygame.display.update()

    ether.empty()
    shots.empty()
    tanks.empty()
    pixels.empty()
    obstructions.empty()
    del player, enemy


def main():
    global main_screen, player, enemy, game_timer, sounds_on, auto_aim_on, enemy_laser_sight
    global single_player, multi_player, send_error_flag, recv_error_flag, start_on_left
    global send_thread, recv_thread

    # GENERATE BACKGROUND #
    for i in range(math.ceil(SCREEN_WIDTH // DIRT_BG.get_width()) + 1):
        for j in range(math.ceil(SCREEN_HEIGHT // DIRT_BG.get_width()) + 1):
            background.blit(DIRT_BG, (i * DIRT_BG.get_width(), j * DIRT_BG.get_width()))

    # SETUP GAME: SINGLE or MULTI-PLAYER
    setup_game()

    # INITIALIZE GAME #
    player_side = left_side = main_screen.get_rect().left + 375
    enemy_side = right_side = main_screen.get_rect().right - 375
    if not start_on_left:
        player_side = right_side
        enemy_side = left_side
    player = Player(player_side, SCREEN_HEIGHT // 2, RED_PROFILE)
    enemy = Player(enemy_side, SCREEN_HEIGHT // 2, BLUE_PROFILE, True)

    obstructions.add(enemy.tank)
    tanks.add(enemy.get_sprites(), player.get_sprites())

    load_map(GAME_MAP2)

    done = False
    game_over = False
    while not done and game_on:
        # GAME CLOCK #
        clock.tick(FRAME_RATE)
        game_timer += 1

        # EVENT HANDLER #
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                done = True
                break

            if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                done = True
                break

            if event.type == pygame.KEYDOWN and event.key == pygame.K_1:
                sounds_on = not sounds_on

            if event.type == pygame.KEYDOWN and event.key == pygame.K_2:
                auto_aim_on = not auto_aim_on

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left-click
                    player.shoot(BIG_SHOT_SIZE)
                if event.button == 2:  # right-click
                    pass
                if event.button == 3:  # middle-click
                    pass

        # IF SOMETHING GOES WRONG WITH SERVER THREADS
        if not game_over and (send_error_flag or recv_error_flag):
            Tk().wm_withdraw()  # to hide the main window
            messagebox.showerror('Server Error', 'The enemy has left the game!')
            send_error_flag = False
            recv_error_flag = False

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

        # ELEMENT UPDATES #
        map_elements.update()
        if auto_aim_on:
            player.update(enemy.tank.pos)
        else:
            player.update(pygame.mouse.get_pos())
        # IF SINGLE PLAYER
        if single_player:
            enemy.update(player.tank.pos)
            enemy_bot()
        # IF MUTLIPLAYER
        if multi_player:
            player.send_data()
            for i in range(len(enemy_queue)):
                enemy.receive_data(enemy_queue.pop(-1))
                enemy.update()
        pixels.update()

        # DRAW EVERYTHING #
        map_elements.draw(main_screen)
        draw_info_banner()
        if player.is_dead() or enemy.is_dead():
            game_over = True
            obstructions.empty()
            final_screen(enemy.is_dead())
        ether.draw(main_screen)
        shots.draw(main_screen)
        tanks.draw(main_screen)
        pixels.draw(main_screen)

        # FLIP THE DISPLAY #
        pygame.display.update()

    # CLEAN UP & QUIT #
    if multi_player:
        print("Closing server sockets...")
        try:
            SEND_SERVER.shutdown(socket.SHUT_WR)
            SEND_SERVER.close()
        except OSError:
            pass
        try:
            RECV_SERVER.shutdown(socket.SHUT_WR)
            RECV_SERVER.close()
        except OSError:
            pass
        pygame.event.post(pygame.event.Event(EVENT_CLOSE_SEND_SOCKET))
        pygame.event.post(pygame.event.Event(EVENT_CLOSE_RECV_SOCKET))
        print("Killing SEND_SERVER thread...")
        send_thread.join()
        print("Killing RECV_SERVER thread...")
        recv_thread.join()

    pygame.quit()


# START #
if __name__ == "__main__":
    main()
    print("GAME OVER")
