import pygame
import os
import json

# Define Screen and sprite sizes and game update frequency (FPS) etc
FPS = 25
GRAVITY = 5
SCREEN_SIZE = (750, 500)
SPRITE_SIZE = (50, 50)
SUPPORTED_KEY_PRESSES = (pygame.K_DOWN, pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT)

# Setup screen
screen = pygame.display.set_mode(SCREEN_SIZE)


# Functions
def animation_loop(imgs):
    """
    Generator function that will continuously loop through a list of pyGame images

    - imgs -- (List. Mandatory) A list of images

    Yields: image
    """
    i = 0
    while True:
        yield imgs[i]
        i = i + 1 if i + 1 < len(imgs) else 0


def generate_sprites(room_obj, name):
    """
    Generate a sprites group from room setup dictionary

    - room_obj -- (Object. Mandatory) An instance of Room class
    - name -- (String. Mandatory) The name of the sprite to generate. Use SpriteNames enum.

    returns: An instance of pygame.sprites.Group()
    """
    sprites_db = room_obj.database[str(room_obj.room)]["sprites"][name]
    sprites = []
    group = pygame.sprite.Group()
    for spr in sprites_db:
        activity = spr["activity"] if "activity" in spr else Activity.IDLE
        h_direction = spr["h_direction"] if "h_direction" in spr else Direction.RIGHT
        v_direction = spr["v_direction"] if "v_direction" in spr else Direction.NONE
        sprites.append(Sprite(
            name=name, position=spr["position"], activity=activity, h_direction=h_direction, v_direction=v_direction))
    for spr in sprites:
        group.add(spr)
    return group


def gravity():
    """Apply gravity effect to all sprites"""
    for sp in all_sprites:
        for spr in sp.sprites():
            spr.move(Direction.DOWN, GRAVITY, update_activity=False)


def key_presses():
    """Check key presses and control the player sprite"""
    key_press = pygame.key.get_pressed()
    if not any([key_press[k] for k in SUPPORTED_KEY_PRESSES]):
        player.update(Activity.IDLE)
    if key_press[pygame.K_DOWN]:
        # Only allowed when next to a ladder
        #player.move(Direction.DOWN)
        pass
    elif key_press[pygame.K_UP]:
        #player.move(Direction.UP)
        # Only allowed when next to a ladder
        pass
    if key_press[pygame.K_RIGHT]:
        player.move(Direction.RIGHT)
    elif key_press[pygame.K_LEFT]:
        player.move(Direction.LEFT)


def load_db(database):
    """
    Read a json file and return as dict

    - database -- (String. Mandatory) The json-file to read.

    Returns: Dict
    """
    with open(database, "r") as f:
        db = json.loads(f.read())
    return db


def load_images(animation, sprite_name):
    """
    Read all image files in a folder and return as a list of pyGame images

    - animation -- (String. Mandatory) The name of the requested animation. Use Animation enum
    - sprite_name -- (String. Optional) The name of the sprite. Use SpriteName enum.

    Returns: List
    """
    folder = {
        Animation.WALKING: Folder.WALKING_IMGS.format(sprite_name),
        Animation.IDLE: Folder.IDLE_IMGS.format(sprite_name)}[animation]
    if not os.path.exists(folder):
        return
    return [pygame.transform.scale(pygame.image.load(folder + i).convert(), SPRITE_SIZE) for i in os.listdir(folder)]


# Classes
class Rooms(object):
    """Class for loading a room layout from a level setup json-file"""

    def __init__(self):
        self.background_img = None
        self.database = None
        self.layout = None
        self.layouts = None
        self.layout_img = None
        self.layout_sprite = None
        self.level = 1
        self.room = 1
        self.texture = None
        self.texture_img = None

    def load(self, level, room_):
        """Load a new room"""
        dark_overlay = pygame.Surface(SCREEN_SIZE, flags=pygame.SRCALPHA)
        dark_overlay.fill((100, 100, 100, 0))
        self.level = level
        self.room = room_
        self.database = load_db(FileName.LEVEL_DB.format(self.level))
        self.texture = Folder.TEXTURES + self.database[str(self.room)]["texture"]
        self.texture_img = pygame.image.load(self.texture)
        self.layout = Folder.LAYOUTS + self.database[str(self.room)]["layout"]
        self.background_img = pygame.image.load(self.texture)
        self.background_img = pygame.transform.scale(self.texture_img, SCREEN_SIZE)
        self.background_img.blit(dark_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        self.layout_img = pygame.image.load(self.layout).convert()
        self.layout_img.set_colorkey(Color.BLACK)
        self.texture_img = pygame.transform.scale(self.texture_img, SCREEN_SIZE)
        self.texture_img.blit(self.layout_img, (0, 0))
        self.texture_img.set_colorkey(Color.WHITE)
        self.layout_sprite = Sprite(SpriteName.LAYOUT, image=self.layout)
        self.layout_sprite.rect.x = self.layout_sprite.rect.y = 0
        self.layouts = pygame.sprite.Group()
        self.layouts.add(self.layout_sprite)


class Sprite(pygame.sprite.Sprite):

    def __init__(self, name, activity="idle", image=None, position=(0, 0), h_direction="right", v_direction="none"):
        """
        Create a new sprite

        name -- (String. Mandatory) The sprite name. Use SpriteName enum
        activity -- (String. Optional. Defaults to "idle") The current activity of the sprite. Use Activity enum
        image -- (String. Optional. Defaults to None) Path to image file. If provided a static image will be used for
            the sprite and animations will be disabled.
        position -- (Tuple. Optional. Defaults to (0, 0)) The current position of the sprite
        h_direction -- (String. Optional. Defaults to "right") The current horizontal direction the sprite is facing.
            Use Direction enum.
        v_direction -- (String. Optional. Defaults to "right") The current vertical direction the sprite is moving in.
            Use Direction enum.
        """
        pygame.sprite.Sprite.__init__(self)

        self.activity = None
        self.animation = None
        self.h_direction = h_direction
        self.v_direction = v_direction
        self.is_carrying_bag = False
        self.is_climbing = self.activity == Activity.CLIMBING
        self.is_facing_down = None
        self.is_facing_left = None
        self.is_facing_right = None
        self.is_facing_up = None
        self.is_passed_out = self.activity == Activity.PASSED_OUT
        self.is_pulling_up = self.activity == Activity.PULLING_UP
        self.is_idle = self.activity == Activity.IDLE
        self.is_walking = self.activity == Activity.WALKING
        self.name = name
        self.speed = 3
        if image:
            self.animations = None
            self.image = pygame.image.load(image)
            self.image.set_colorkey(Color.WHITE)
        else:
            self.animations = SPRITE_ANIMATIONS[name]
            self.update(activity)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position
        self.mask = pygame.mask.from_surface(self.image)

    def collides(self, sprites):
        """
        Check if the sprite collides with another sprite

        - sprites -- (List, Tuple or object) The sprite or sprites to check for collision against

        Returns: Boolean
        """
        sprites = [sprites] if type(sprites) not in (list, tuple) else sprites
        return any([pygame.sprite.spritecollide(self, x, False, pygame.sprite.collide_mask) for x in sprites])

    def move(self, direction, speed=None, update_activity=True):
        """
        Move the sprite

        - direction -- (String. Mandatory) Use Direction enum
        - speed -- (Int or Float. Optional. Defaults to self.speed) The speed (number of pixels) to move the sprite in
        - update_activity -- (Boolean. Optional. Defaults to True) If False the activity (animation) of the sprite
            will not be updated.
        """
        activity = Activity.WALKING
        speed = self.speed if not speed else speed
        vertical = direction in (Direction.UP, Direction.DOWN)
        horizontal = direction in (Direction.LEFT, Direction.RIGHT)
        one_pixel = {True: 1, False: -1}[direction in (Direction.DOWN, Direction.RIGHT)]
        x = one_pixel if horizontal else 0
        y = one_pixel if vertical else 0
        self.v_direction = direction if vertical else self.v_direction
        self.h_direction = direction if horizontal else self.h_direction
        for i in range(1, speed + 1):
            self.rect.move_ip(x, y)
            if self.collides(room.layouts):
                self.rect.move_ip(-(one_pixel * i) if horizontal else 0, -y)
                activity = Activity.IDLE
                break
        if update_activity:
            self.update(activity)

    def update(self, activity):
        """Update the sprite animation"""
        self.is_facing_down = self.v_direction == Direction.DOWN
        self.is_facing_left = self.h_direction == Direction.LEFT
        self.is_facing_right = self.h_direction == Direction.RIGHT
        self.is_facing_up = self.v_direction == Direction.UP
        if activity != self.activity:
            self.animation = animation_loop(self.animations[activity])
        self.activity = activity
        self.image = next(self.animation)
        self.image.set_colorkey(Color.WHITE)
        if self.is_facing_left:
            self.image = pygame.transform.flip(self.image, True, False)


# Enums
class Activity(object):
    CLIMBING = "climbing"
    PASSED_OUT = "passed_out"
    PULLING_UP = "pulling_up"
    IDLE = "idle"
    WALKING = "walking"


class Animation(Activity):
    pass


class Color(object):
    BLACK = (0, 0, 0)
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)
    WHITE = (255, 255, 255)


class Direction(object):
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    NONE = "none"


class Folder(object):
    IMAGES = "images" + os.sep
    LAYOUTS = IMAGES + "layouts" + os.sep
    LEVELS = "levels" + os.sep
    SPRITES = IMAGES + "sprites" + os.sep
    IDLE_IMGS = SPRITES + "{}" + os.sep + "idle" + os.sep
    TEXTURES = IMAGES + "textures" + os.sep
    WALKING_IMGS = SPRITES + "{}" + os.sep + "walking" + os.sep


class FileName(object):
    LEVEL_DB = Folder.LEVELS + "level{}.json"


class SpriteName(object):
    GOLD = "gold"
    LAYOUT = "layout"
    PLAYER = "player"
    MINER = "miner"


# Load sprite animation images and store in a dict
SPRITE_ANIMATIONS = {
    SpriteName.GOLD: {
        Animation.IDLE: load_images(Animation.IDLE, SpriteName.GOLD)},
    SpriteName.PLAYER: {
        Animation.WALKING: load_images(Animation.WALKING, SpriteName.PLAYER),
        Animation.IDLE: load_images(Animation.IDLE, SpriteName.PLAYER)},
    SpriteName.MINER: {
        Animation.IDLE: load_images(Animation.IDLE, SpriteName.MINER)}}

# Variables and objects
clock = pygame.time.Clock()
game_is_running = True
room = Rooms()
room.load(1, 2)
players = generate_sprites(room, SpriteName.PLAYER)
player = players.sprites()[0]
miners = generate_sprites(room, SpriteName.MINER)
gold_sacks = generate_sprites(room, SpriteName.GOLD)
all_sprites = (players, miners, gold_sacks)
not_player = (miners, gold_sacks)

# Initialize PyGame
pygame.init()

########################################################################################################################
# MAIN LOOP
########################################################################################################################
while game_is_running:

    clock.tick(FPS)

    # Check for quit game request from user
    for event in pygame.event.get():
        game_is_running = \
            not (event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE))
        if event.type == pygame.KEYUP and event.key in (pygame.K_UP, pygame.K_DOWN):
            player.v_direction = Direction.NONE

    # Read key presses and move the player
    key_presses()

    # Apply gravity to all sprites
    gravity()

    if player.collides(not_player):
        print("Player collided with another sprite")

    # Update animation for gold sacks
    for s in gold_sacks.sprites():
        s.update(activity=Activity.IDLE)

    # Draw sprites and update the screen
    screen.blit(room.background_img, (0, 0))
    screen.blit(room.texture_img, (0, 0))
    for s in all_sprites:
        s.draw(screen)
    pygame.display.flip()
