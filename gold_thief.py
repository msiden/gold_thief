import pygame
import os
import json


# Functions
def animation_loop(imgs):
    i = 0
    while True:
        yield imgs[i]
        i = i + 1 if i + 1 < len(imgs) else 0


def load_db(database):
    with open(database, "r") as f:
        db = json.loads(f.read())
    return db


# Classes
class Levels(object):

    def __init__(self):
        self.level = 1
        self.room = 1
        self.theme = None
        self.layout = None
        self.database = None
        self.theme_img = None
        self.layout_img = None
        self.background_img = None
        self.layout_sprite = None

    def load(self):
        dark_overlay = pygame.Surface(SCREEN_SIZE, flags=pygame.SRCALPHA)
        dark_overlay.fill((100, 100, 100, 0))
        self.database = load_db(LEVEL_DB.format(self.level))
        self.theme = THEMES_FOLDER + self.database[str(self.room)]["theme"]
        self.layout = LAYOUTS_FOLDER + self.database[str(self.room)]["layout"]
        self.theme_img = self.background_img = pygame.image.load(self.theme)
        self.theme_img = self.background_img = pygame.transform.scale(self.theme_img, SCREEN_SIZE)
        self.background_img.blit(dark_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        self.layout_img = pygame.image.load(self.layout)
        self.layout_img.set_colorkey(Color.BLACK)
        self.theme_img.blit(self.layout_img, (0, 0))
        self.theme_img.set_colorkey(Color.WHITE)
        self.layout_sprite = Sprite(self.theme)
        self.layout_sprite.rect.x = self.layout_sprite.rect.y = 0


class Sprite(pygame.sprite.Sprite):

    def __init__(self, image):

        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load(image)
        self.image.set_colorkey(Color.WHITE)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()


# Enums
class Color(object):
    BLACK = (0, 0, 0)
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)
    WHITE = (255, 255, 255)


# Constants
SCREEN_SIZE = (750, 500)
IMAGES_FOLDER = "images" + os.sep
LAYOUTS_FOLDER = IMAGES_FOLDER + "layouts" + os.sep
SPRITES_FOLDER = IMAGES_FOLDER + "sprites" + os.sep
THEMES_FOLDER = IMAGES_FOLDER + "themes" + os.sep
LEVELS_FOLDER = "levels" + os.sep
LEVEL_DB = LEVELS_FOLDER + "level{}.json"

# Variables and objects
screen = pygame.display.set_mode(SCREEN_SIZE)
game_is_running = True
level = Levels()
level.load()
background_img = pygame.image.load(THEMES_FOLDER + "granite.jpg")
background_img = pygame.transform.scale(background_img, SCREEN_SIZE)
dark = pygame.Surface(SCREEN_SIZE, flags=pygame.SRCALPHA)
dark.fill((100, 100, 100, 0))
background_img.blit(dark, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
walls_img = pygame.image.load(LAYOUTS_FOLDER + "room1_1.png")
walls_img.set_colorkey(Color.BLACK)
pattern = pygame.image.load(THEMES_FOLDER + "granite.jpg")
pattern = pygame.transform.scale(pattern, SCREEN_SIZE)
pattern.blit(walls_img, (0, 0))
pattern.set_colorkey(Color.WHITE)
walls = Sprite(LAYOUTS_FOLDER + "room1_1.png")
walls.rect.x = walls.rect.y = 0
player = Sprite(SPRITES_FOLDER + "player" + os.sep + "robot1.png")
player.rect.x = 100
player.rect.y = 150
block = Sprite(SPRITES_FOLDER + "robot" + os.sep + "robot2.png")
block.rect.x = 400
block.rect.y = 200
blocks = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
blocks.add(block)
walls_group = pygame.sprite.Group()
#walls_group.add(level.layout_sprite)
walls_group.add(walls)
for s in (player, block):
    all_sprites.add(s)
animate = False
player_imgs = animation_loop(
    [SPRITES_FOLDER + "player" + os.sep + "robot1.png", SPRITES_FOLDER + "player" + os.sep + "robot1b.png"])

# Initialize PyGame
pygame.init()

########################################################################################################################
# MAIN LOOP
########################################################################################################################
while game_is_running:
    for event in pygame.event.get():
        game_is_running = \
            not (event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE))
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_DOWN, pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT):
            animate = True
        elif event.type == pygame.KEYUP and event.key in (pygame.K_DOWN, pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT):
            animate = False

    key_press = pygame.key.get_pressed()
    if key_press[pygame.K_DOWN]:
        player.rect.y += 1
    elif key_press[pygame.K_UP]:
        player.rect.y -= 1
    if key_press[pygame.K_RIGHT]:
        player.rect.x += 1
    elif key_press[pygame.K_LEFT]:
        player.rect.x -= 1

    if animate:
        player.image = pygame.image.load(next(player_imgs)).convert()
    else:
        player.image = pygame.image.load(SPRITES_FOLDER + "player" + os.sep + "robot1.png")
    player.image.set_colorkey(Color.WHITE)

    if pygame.sprite.spritecollide(player, blocks, False, pygame.sprite.collide_mask):
        print("sprites have collided!")
    if pygame.sprite.spritecollide(player, walls_group, False, pygame.sprite.collide_mask):
        print("Player hit a wall")

    #screen.blit(level.background_img, (0, 0))
    #screen.blit(level.theme_img, (0, 0))

    screen.blit(background_img, (0, 0))
    screen.blit(pattern, (0, 0))
    all_sprites.draw(screen)
    pygame.display.flip()
