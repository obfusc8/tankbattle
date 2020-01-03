import codecs
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
SCREEN_WIDTH = 1250
SCREEN_HEIGHT = 750
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
BIG_SHOT_DAMAGE = 10
SMALL_SHOT_SIZE = 4
SMALL_SHOT_MAX = 100
SMALL_SHOT_SPEED = 15
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


class Shot(pygame.sprite.Sprite):

    def __init__(self, size, p):
        self.color_ultralight = p.color["ultralight"]
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((size, size))
        self.image.fill(COLOR_WHITE)
        self.image.set_colorkey(COLOR_WHITE)
        pygame.draw.circle(self.image, self.color_ultralight, (size // 2, size // 2), size // 2)
        self.rect = self.image.get_rect()
        self.pos = p.tank.pos
        self.size = size  ################### DELETE
        if size == BIG_SHOT_SIZE:
            speed = BIG_SHOT_SPEED
        elif size == SMALL_SHOT_SIZE:
            speed = SMALL_SHOT_SPEED
        aim = -math.radians(p.tank.cannon.angle)
        self.rect.centerx = int(p.tank.cannon.pos.x + math.cos(aim) * 30)
        self.rect.centery = int(p.tank.cannon.pos.y + math.sin(aim) * 30)
        self.xv = int(speed * math.cos(aim) + p.tank.speed * math.cos(p.tank.direction))
        self.yv = int(speed * math.sin(aim) + p.tank.speed * math.sin(p.tank.direction))

    def update(self, *args):
        if main_screen.get_rect().contains(self):
            self.rect.centerx += self.xv
            self.rect.centery += self.yv
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
        self.health = 50
        self.big_shots = BIG_SHOT_MAX
        self.small_shots = SMALL_SHOT_MAX
        self.friction = FRICTION

    def update(self, target=None):
        self.shots.update()
        if self.health > 0:
            if game_timer % 60 == 0:
                self.big_shots = min(self.big_shots + 1, BIG_SHOT_MAX)
            if game_timer % 20 == 0:
                self.small_shots = min(self.small_shots + 1, SMALL_SHOT_MAX)
            if target:
                self.target = target

            if self.tank.speed <= 0:
                self.tank.speed = 0
            else:
                self.tank.speed -= self.friction
            self.tank.aim_cannon(self.target)
            self.parts.update()

            element = pygame.sprite.spritecollide(self.tank, obstructions, False)
            if element:
                for e in element:
                    if e != self.tank:
                        rect = self.tank.rect
                        angle = Vector2(0, 0).angle_to(self.tank.pos - e.pos)
                        if abs(angle) > 135:  # RIGHT SIDE
                            rect.right = e.rect.left
                        if 0 < abs(angle) < 45:  # LEFT SIDE
                            rect.left = e.rect.right
                        if 45 < angle < 135:  # TOP SIDE
                            rect.top = e.rect.bottom
                        if -135 < angle < -45:  # BOTTOM SIDE
                            rect.bottom = e.rect.top
                        self.tank.pos = Vector2(rect.center)
                        # self.tank.speed = max(0, self.tank.speed - ACCELERATION)

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
                self.friction = FRICTION * 2
                self.tank.speed = min(self.tank.speed, MAX_SPEED / 2)
            else:
                self.friction = FRICTION

            shot = pygame.sprite.spritecollide(self.tank, shots, False)
            if shot and shot[0] not in self.shots:
                for i in range(5):
                    pixels.add(HitPixel(shot[0].pos, shot[0].size))
                if shot[0] in enemy.shots:
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
            elif size == SMALL_SHOT_SIZE:
                if self.small_shots > 0:
                    self.small_shots -= 1
                    log_shot = True
            if log_shot:
                shot = Shot(size, self)
                self.shots.add(shot)
                shots.add(shot)
                self.last_shot = shot.size

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
                "last_shot": self.last_shot,
                "health": self.health,
                "big_shots": self.big_shots,
                "small_shots": self.small_shots}
        self.last_shot = 0
        #pickle.dump(data, f)
        return pickle.dumps(data, -1)

    def receive_data(self, data):
        #data = pickle.loads(data)
        self.tank.pos = data["pos"]
        #self.tank.pos.x += 500  ########################################
        self.tank.direction = data["direction"]
        self.tank.speed = data["speed"]
        self.target = data["target"]
        if data["last_shot"]:
            shot = Shot(data["last_shot"], self)
            self.shots.add(shot)
            shots.add(shot)
        self.health = data["health"]
        self.big_shots = data["big_shots"]
        self.small_shots = data["small_shots"]


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
ROCK_BG = make_background_tile(ROCK_COLORS, 50, 50, 1)
SAND_BG = make_background_tile(SAND_COLORS, 50, 50)
GRASS_BG = make_background_tile(GRASS_COLORS, 50, 50)
WATER_BG = make_background_tile(WATER_COLORS, 50, 50)
element_key = {"R": ROCK_BG, "S": SAND_BG, "G": GRASS_BG, "W": WATER_BG}

# PLAYER ELEMENTS #
player = Player(main_screen.get_rect().left + 375, SCREEN_HEIGHT // 3*2, RED_PROFILE)
enemy = Player(main_screen.get_rect().right - 375, SCREEN_HEIGHT // 3*2, BLUE_PROFILE)

# SPRITE CONTAINER INITIALIZATION #
tanks = pygame.sprite.RenderPlain((enemy.get_sprites(), player.get_sprites()))
shots = pygame.sprite.RenderPlain(())
obstructions = pygame.sprite.RenderPlain(enemy.tank)
obstacles = pygame.sprite.RenderPlain()
map_elements = pygame.sprite.RenderPlain(())
ether = pygame.sprite.RenderPlain(())
pixels = pygame.sprite.RenderPlain(())


class Element(pygame.sprite.Sprite):

    def __init__(self, image, xy):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
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


def place_elements(element_map):
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
                if element_map[n] == "W":
                    obstacles.add(element)


def final_screen(win):
    if win:
        temp = pygame.draw.rect(main_screen, (0, 200, 0), (0, SCREEN_HEIGHT//2-100, SCREEN_WIDTH, 200))
        temp = pygame.draw.rect(main_screen, (0, 100, 0), (0, temp.top + 25, SCREEN_WIDTH, 150))
        temp = draw_text("WINNER", main_screen, TITLE_FONT, SCREEN_WIDTH//2, temp.top - 25, COLOR_WHITE, COLOR_BLACK, "center")
    else:
        temp = pygame.draw.rect(main_screen, (200, 0, 0), (0, SCREEN_HEIGHT//2-100, SCREEN_WIDTH, 200))
        temp = pygame.draw.rect(main_screen, (100, 0, 0), (0, temp.top + 25, SCREEN_WIDTH, 150))
        temp = draw_text("LOSER", main_screen, TITLE_FONT, SCREEN_WIDTH//2, temp.top - 25, COLOR_WHITE, COLOR_BLACK, "center")
    temp = draw_text("Press 'Esc' to quit", main_screen, TEXT_FONT_MED, SCREEN_WIDTH // 2, temp.bottom + 25, COLOR_WHITE, COLOR_BLACK, "center")


#f = open("tankdata", "wb")


def main():
    global main_screen, player, enemy, game_timer

    for i in range(math.ceil(SCREEN_WIDTH // DIRT_BG.get_width()) + 1):
        for j in range(math.ceil(SCREEN_HEIGHT // DIRT_BG.get_width()) + 1):
            background.blit(DIRT_BG, (i * DIRT_BG.get_width(), j * DIRT_BG.get_width()))

    pregame = True
    game_on = True
    show_controls = False
    while pregame:
        clock.tick(FRAME_RATE)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                game_on = False
                pregame = False
                break

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                pregame = False
                break

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left-click
                    x, y = pygame.mouse.get_pos()
                    if box.collidepoint(x, y):
                        show_controls = not show_controls
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

        if not show_controls:
            image = pygame.Surface((240, 50))
            image.fill((0, 0, 0))
            image.set_alpha(80)
            box = main_screen.blit(image, (25, SCREEN_HEIGHT-image.get_height()-25))
            temp = draw_text("CONTROLS", main_screen, TEXT_FONT_MED, box.centerx, box.top+10, (150, 150, 150), COLOR_BLACK, "center")
        else:
            image = pygame.Surface((240, 300))
            image.fill((0, 0, 0))
            image.set_alpha(80)
            box = main_screen.blit(image, (25, SCREEN_HEIGHT-image.get_height()-25))
            temp = draw_text("CONTROLS", main_screen, TEXT_FONT_MED, box.centerx, box.top+10, (150, 150, 150), COLOR_BLACK, "center")
            temp = draw_text("___________________", main_screen, TEXT_FONT_MED, box.centerx, temp.top+10, (125, 125, 125), COLOR_BLACK, "center")
            temp = draw_text("FORWARD", main_screen, TEXT_FONT_SMALL, box.centerx, temp.bottom+15, (220, 220, 220), COLOR_BLACK, "center")
            temp = draw_text("W", main_screen, TEXT_FONT_SMALL, box.centerx, temp.bottom + 5, (220, 220, 220), COLOR_BLACK, "center")
            temp = draw_text("   LEFT    A        D    RIGHT", main_screen, TEXT_FONT_SMALL, box.centerx, temp.bottom + 5, (220, 220, 220), COLOR_BLACK, "center")
            temp = draw_text("S", main_screen, TEXT_FONT_SMALL, box.centerx, temp.bottom + 5, (220, 220, 220), COLOR_BLACK, "center")
            temp = draw_text("STOP", main_screen, TEXT_FONT_SMALL, box.centerx, temp.bottom + 5, (220, 220, 220), COLOR_BLACK, "center")
            temp = draw_text("AIM - Mouse", main_screen, TEXT_FONT_SMALL, box.centerx, temp.bottom + 25, (220, 220, 220), COLOR_BLACK, "center")
            temp = draw_text("FIRE - Left Click", main_screen, TEXT_FONT_SMALL, box.centerx, temp.bottom + 5, (220, 220, 220), COLOR_BLACK, "center")
            temp = draw_text("RAPID FIRE - Right Click", main_screen, TEXT_FONT_SMALL, box.centerx, temp.bottom + 5, (220, 220, 220), COLOR_BLACK, "center")

        player.update(pygame.mouse.get_pos())
        enemy.update(player.tank.pos)

        pixels.update()

        shots.draw(main_screen)
        tanks.draw(main_screen)
        pixels.draw(main_screen)

        pygame.display.update()

    # START GAME #
    tanks.empty()
    obstructions.empty()
    del player, enemy
    player = Player(main_screen.get_rect().left + 375, SCREEN_HEIGHT // 2, RED_PROFILE)
    enemy = Player(main_screen.get_rect().right - 375, SCREEN_HEIGHT // 2, BLUE_PROFILE)
    obstructions.add(enemy.tank)
    tanks.add(enemy.get_sprites(), player.get_sprites())
    place_elements(GAME_MAP2)

    #### FOR TESTING ONLY #####################################################################
    contents = list()
    f = open("tankdata", "rb")
    while True:
        try:
            contents.append(pickle.load(f))
            contents[-1]["pos"].x += 500
        except EOFError:
            f.close()
            break
    move_counter = 0
    move_size = len(contents)
    ###########################################################################################

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

        # ELEMENT UPDATES #
        map_elements.update()
        player.update(pygame.mouse.get_pos())
        #temp = player.send_data()
        temp = contents[move_counter] ###################################
        move_counter = (move_counter + 1) % move_size ###################
        enemy.receive_data(temp)
        enemy.update()
        map_elements.update()
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
    try:
        f.close() ###########################################
    except:
        pass
    pygame.quit()


# START #
if __name__ == "__main__":
    main()
    try:
        f.close() ###########################################
    except:
        pass
    print("GAME OVER")
