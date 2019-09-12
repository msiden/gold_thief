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
class Rooms(object):

    def __init__(self):
        self.level = 1
        self.room = 1
        self.texture = None
        self.layout = None
        self.database = None
        self.texture_img = None
        self.layout_img = None
        self.background_img = None
        self.layout_sprite = None
        self.layout_group = None
        self.load()

    def load(self):
        dark_overlay = pygame.Surface(SCREEN_SIZE, flags=pygame.SRCALPHA)
        dark_overlay.fill((100, 100, 100, 0))
        self.database = load_db(FileName.LEVEL_DB.format(self.level))
        self.texture = Folder.TEXTURES + self.database[str(self.room)]["texture"]
        self.layout = Folder.LAYOUTS + self.database[str(self.room)]["layout"]
        self.texture_img = pygame.image.load(self.texture)
        self.background_img = pygame.image.load(self.texture)
        self.texture_img = pygame.transform.scale(self.texture_img, SCREEN_SIZE)
        self.background_img = pygame.transform.scale(self.texture_img, SCREEN_SIZE)
        self.background_img.blit(dark_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        self.layout_img = pygame.image.load(self.layout)
        self.layout_img.set_colorkey(Color.BLACK)
        self.texture_img.blit(self.layout_img, (0, 0))
        self.texture_img.set_colorkey(Color.WHITE)
        self.layout_sprite = Sprite(self.layout)
        self.layout_sprite.rect.x = self.layout_sprite.rect.y = 0
        self.layout_group = pygame.sprite.Group()
        self.layout_group.add(self.layout_sprite)


class Sprite(pygame.sprite.Sprite):

    def __init__(self, image):

        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load(image)
        self.image.set_colorkey(Color.WHITE)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.is_walking = False
        self.is_climbing = False
        self.is_passed_out = False
        self.is_pulling_up = False
        self.is_carrying_bag = False
        self.is_standing_still = False
        self.animation = []
        self.direction = Direction.RIGHT
        self.update()

    def update(self):
        self.is_walking = False
        self.is_climbing = False
        self.is_passed_out = False
        self.is_pulling_up = False
        self.is_carrying_bag = False
        self.is_standing_still = not any([self.is_walking, self.is_climbing, self.is_passed_out, self.is_pulling_up])

    def get_images(self):
        walking = []
        for i in os.listdir(Folder.PLAYER_WALKING_IMGS):
            walking.append(pygame.image.load(Folder.PLAYER_WALKING_IMGS + i))
        print(walking)


# Enums
class Color(object):
    BLACK = (0, 0, 0)
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)
    WHITE = (255, 255, 255)


class Direction(object):
    RIGHT = "RIGHT"
    LEFT = "LEFT"
    UP = "UP"
    DOWN = "DOWN"


class Folder(object):
    IMAGES = "images" + os.sep
    LAYOUTS = IMAGES + "layouts" + os.sep
    SPRITES = IMAGES + "sprites" + os.sep
    TEXTURES = IMAGES + "textures" + os.sep
    LEVELS = "levels" + os.sep
    PLAYER_IMAGES = SPRITES + "player" + os.sep
    PLAYER_STANDING_IMGS = PLAYER_IMAGES + "standing" + os.sep
    PLAYER_WALKING_IMGS = PLAYER_IMAGES + "walking" + os.sep


class FileName(object):
    LEVEL_DB = Folder.LEVELS + "level{}.json"


# Constants
SCREEN_SIZE = (750, 500)

# Variables and objects
screen = pygame.display.set_mode(SCREEN_SIZE)
game_is_running = True
room = Rooms()
player = Sprite(Folder.SPRITES + "player" + os.sep + "robot1.png")
player.rect.x = 100
player.rect.y = 150
block = Sprite(Folder.SPRITES + "robot" + os.sep + "robot2.png")
block.rect.x = 400
block.rect.y = 200
blocks = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
blocks.add(block)
for s in (player, block):
    all_sprites.add(s)
animate = False
player_imgs = animation_loop([
    Folder.SPRITES + "player" + os.sep + "robot1.png",
    Folder.SPRITES + "player" + os.sep + "robot1b.png"])
print(player.get_images())
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
        player.image = pygame.image.load(Folder.SPRITES + "player" + os.sep + "robot1.png")
    player.image.set_colorkey(Color.WHITE)

    if pygame.sprite.spritecollide(player, blocks, False, pygame.sprite.collide_mask):
        print("sprites have collided!")
    if pygame.sprite.spritecollide(player, room.layout_group, False, pygame.sprite.collide_mask):
        print("Player hit a wall")

    screen.blit(room.background_img, (0, 0))
    screen.blit(room.texture_img, (0, 0))
    all_sprites.draw(screen)
    pygame.display.flip()
