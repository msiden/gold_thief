import pygame
import os
import json

# Define Screen and sprite sizes
SCREEN_SIZE = (750, 500)
SPRITE_SIZE = (50, 50)


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


def load_images(animation, sprite_name):
    folder = {
        Animation.WALKING: Folder.WALKING_IMGS.format(sprite_name),
        Animation.STANDING: Folder.STANDING_IMGS.format(sprite_name)}[animation]
    if not os.path.exists(folder):
        return
    return [pygame.transform.scale(pygame.image.load(folder + i), SPRITE_SIZE) for i in os.listdir(folder)]


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
        self.layout_sprite = Sprite(SpriteName.LAYOUT, image=self.layout)
        self.layout_sprite.rect.x = self.layout_sprite.rect.y = 0
        self.layout_group = pygame.sprite.Group()
        self.layout_group.add(self.layout_sprite)


class Sprite(pygame.sprite.Sprite):

    def __init__(self, name, activity="standing", image=None, position=(0, 0)):

        pygame.sprite.Sprite.__init__(self)

        self.activity = None
        self.is_walking = self.activity == Activity.WALKING
        self.is_climbing = self.activity == Activity.CLIMBING
        self.is_passed_out = self.activity == Activity.PASSED_OUT
        self.is_pulling_up = self.activity == Activity.PULLING_UP
        self.is_carrying_bag = False
        self.is_standing_still = self.activity == Activity.STANDING
        self.animation = None
        self.direction = Direction.RIGHT
        self.name = name
        if image:
            self.animations = None
            self.image = pygame.image.load(image)
            self.image.set_colorkey(Color.WHITE)
            self.mask = pygame.mask.from_surface(self.image)
        else:
            self.animations = SPRITE_ANIMATIONS[name]
            self.update(activity)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position

    def update(self, activity):
        if activity != self.activity:
            self.animation = animation_loop(self.animations[activity])
        self.activity = activity
        self.image = next(self.animation)
        self.image.set_colorkey(Color.WHITE)
        self.mask = pygame.mask.from_surface(self.image)


# Enums
class Activity(object):
    WALKING = "walking"
    STANDING = "standing"
    CLIMBING = "climbing"
    PULLING_UP = "pulling_up"
    PASSED_OUT = "passed_out"


class Animation(Activity):
    pass


class Color(object):
    BLACK = (0, 0, 0)
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)
    WHITE = (255, 255, 255)


class Direction(object):
    RIGHT = "right"
    LEFT = "left"
    UP = "up"
    DOWN = "down"


class Folder(object):
    IMAGES = "images" + os.sep
    LAYOUTS = IMAGES + "layouts" + os.sep
    SPRITES = IMAGES + "sprites" + os.sep
    TEXTURES = IMAGES + "textures" + os.sep
    LEVELS = "levels" + os.sep
    WALKING_IMGS = SPRITES + "{}" + os.sep + "walking" + os.sep
    STANDING_IMGS = SPRITES + "{}" + os.sep + "standing" + os.sep


class FileName(object):
    LEVEL_DB = Folder.LEVELS + "level{}.json"


class SpriteName(object):
    PLAYER = "player"
    LAYOUT = "layout"
    ROBOT = "robot"


# Load sprite animation images and store in a dict
SPRITE_ANIMATIONS = {
    SpriteName.PLAYER: {
        Animation.WALKING: load_images(Animation.WALKING, SpriteName.PLAYER),
        Animation.STANDING: load_images(Animation.STANDING, SpriteName.PLAYER)},
    SpriteName.ROBOT: {
        Animation.STANDING: load_images(Animation.STANDING, SpriteName.ROBOT)}}

# Variables and objects
screen = pygame.display.set_mode(SCREEN_SIZE)
game_is_running = True
room = Rooms()
player = Sprite(name=SpriteName.PLAYER, position=(100, 150))
robot = Sprite(name=SpriteName.ROBOT, position=(400, 200))
robots = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
robots.add(robot)
for s in (player, robot):
    all_sprites.add(s)

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
    if not any(key_press):
        player.update(Activity.STANDING)
    if key_press[pygame.K_DOWN]:
        player.rect.y += 1
        player.update(Activity.WALKING)
    elif key_press[pygame.K_UP]:
        player.rect.y -= 1
        player.update(Activity.WALKING)
    if key_press[pygame.K_RIGHT]:
        player.rect.x += 1
        player.update(Activity.WALKING)
    elif key_press[pygame.K_LEFT]:
        player.rect.x -= 1
        player.update(Activity.WALKING)

    if pygame.sprite.spritecollide(player, robots, False, pygame.sprite.collide_mask):
        print("sprites have collided!")
    if pygame.sprite.spritecollide(player, room.layout_group, False, pygame.sprite.collide_mask):
        print("Player hit a wall")

    screen.blit(room.background_img, (0, 0))
    screen.blit(room.texture_img, (0, 0))
    all_sprites.draw(screen)
    pygame.display.flip()
