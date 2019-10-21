import pygame
import os
import json
import ctypes

# Define Screen and sprite sizes and other constants
CLIMBABLE_PIX = 1
FPS = 25
GRAVITY = 20
MAX_FALL_PIX = 100
MAX_CONTROL_WHILE_FALLING_PIX = 50
PLAYER_SPEED = 8
PLAYER_SPEED_WHEN_CARRYING_GOLD = 5
PLAYER_LIVES = 5
SCREEN_SIZE = (1440, 1080)
SPRITE_SIZE = (120, 120)
WAKE_UP_TIME_MS = 5000

# Make sure we get the right screen resolution
ctypes.windll.user32.SetProcessDPIAware()

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


def drop_gold_sack():
    dropped_in_truck = False
    player.update(Activity.IDLE)
    player.speed = PLAYER_SPEED
    for t in trucks.sprites():
        if t.collides(players):
            player.gold_delivered += 1
            print(player.gold_delivered, "/", room.gold_sacks)
            t.update(Activity.IDLE_WITH_GOLD)
            dropped_in_truck = True
    if not dropped_in_truck:
        player.gold_sack_sprite.rect.x = player.rect.x
        player.gold_sack_sprite.rect.y = player.rect.y
        gold_sacks.add(player.gold_sack_sprite)
    player.gold_sack_sprite = None


def flatten_list(l):
    """
    Make a list of lists into a single list. CURRENTLY NOT IN USE!

    - l -- (List. Mandatory)

    Returns: List
    """
    return [item for sublist in l for item in sublist]


def generate_sprites(room_obj, name, image=None, animation_freq_ms=0):
    """
    Generate a sprites group from room setup dictionary

    - room_obj -- (Object. Mandatory) An instance of Room class
    - name -- (String. Mandatory) The name of the sprite to generate. Use SpriteNames enum.
    - image -- (String. Optional. Defaults to None) Use a specific image instead of an animation
    - animation_freq_ms -- (Integer. Optional. Defaults to 0) The update frequency of the sprite animation in
            milliseconds.

    returns: An instance of pygame.sprites.Group()
    """
    if name not in room_obj.database[str(room_obj.room)]["sprites"]:
        return
    sprites_db = room_obj.database[str(room_obj.room)]["sprites"][name]
    sprites = []
    group = pygame.sprite.Group()
    for spr in sprites_db:
        activity = spr["activity"] if "activity" in spr else Activity.IDLE
        h_direction = spr["h_direction"] if "h_direction" in spr else Direction.RIGHT
        v_direction = spr["v_direction"] if "v_direction" in spr else Direction.NONE
        length = spr["length"] if "length" in spr else None
        sprites.append(Sprite(
            name=name, position=spr["position"], image=image, activity=activity, h_direction=h_direction,
            v_direction=v_direction, length=length, animation_freq_ms=animation_freq_ms))
    for spr in sprites:
        group.add(spr)
    return group


def gravity():
    """Apply gravity effect to all affected sprites"""
    for sp in affected_by_gravity:
        for spr in sp.sprites():
            if not (spr.collides(ladders) and spr.can_climb_ladders) or not spr.can_climb_ladders:
                spr.move(Direction.DOWN, GRAVITY)


def key_presses(interact_with_gold_sack):
    """
    Check key presses and control the player sprite

    - interact_with_gold_sack -- (Boolean. Mandatory) Specifies whether the user wants to pick up or drop a gold sack.
    """

    # Get key presses
    key_press = pygame.key.get_pressed()
    down = key_press[pygame.K_DOWN] and player.collides(ladders)
    left = key_press[pygame.K_LEFT] and not player.is_falling()
    right = key_press[pygame.K_RIGHT] and not player.is_falling()
    up = key_press[pygame.K_UP] and player.collides(ladders)
    pick_up_gold = interact_with_gold_sack and player.collides(gold_sacks) and not player.is_carrying_gold()
    drop_gold = interact_with_gold_sack and player.is_carrying_gold()
    no_key_presses = not any((down, left, right, up))
    move_vertical = up or down
    move_horizontal = left or right

    # No interaction is possible if the player is passed out
    if player.is_passed_out():
        return

    # Player is idle if no keys are pressed
    if no_key_presses:
        if player.is_carrying_gold() and player.is_climbing():
            player.update(Activity.IDLE_CLIMBING_WITH_GOLD)
        elif player.is_climbing():
            player.update(Activity.IDLE_CLIMBING)
        elif player.is_carrying_gold():
            player.update(Activity.IDLE_WITH_GOLD)
        elif player.is_pushing_wheelbarrow():
            player.update(Activity.IDLE_WITH_WHEELBARROW)
        else:
            player.update(Activity.IDLE)

    # Move up and down
    if move_vertical:
        activity = Activity.CLIMBING_WITH_GOLD if player.is_carrying_gold() else Activity.CLIMBING
        player.move(Direction.DOWN if down else Direction.UP, activity=activity)

    # Move left and right
    if move_horizontal:
        if player.is_carrying_gold():
            activity = Activity.CLIMBING_WITH_GOLD \
                if player.is_climbing() and player.collides(ladders) else Activity.WALKING_WITH_GOLD
        else:
            activity = Activity.CLIMBING if player.is_climbing() and player.collides(ladders) else Activity.WALKING
        player.move(Direction.LEFT if left else Direction.RIGHT, activity=activity)

    # Pick up or drop a gold sack
    if pick_up_gold:
        player.update(Activity.IDLE_WITH_GOLD)
        for g in gold_sacks:
            if g.collides(players):
                player.gold_sack_sprite = g
                g.remove(gold_sacks)
                player.speed = PLAYER_SPEED_WHEN_CARRYING_GOLD
                break
    elif drop_gold:
        drop_gold_sack()


def load_db(database):
    """
    Read a json file and return as dict

    - database -- (String. Mandatory) The json-file to read.

    Returns: Dict
    """
    with open(database, "r") as f:
        return json.loads(f.read())


def load_images(animation, sprite_name, multiply_size_by=1):
    """
    Read all image files in a folder and return as a list of pyGame images

    - animation -- (String. Mandatory) The name of the requested animation. Use Animation enum
    - sprite_name -- (String. Optional) The name of the sprite. Use SpriteName enum.
    - multiply_size_by -- (Integer. Optional. Defaults to 1) Multiply the size of the sprite with the given number

    Returns: List
    """
    folder = {
        Animation.CLIMBING: Folder.CLIMBING_IMGS.format(sprite_name),
        Animation.CLIMBING_WITH_GOLD: Folder.CLIMBING_WITH_GOLD_IMGS.format(sprite_name),
        Animation.FALLING: Folder.IDLE_IMGS.format(sprite_name),
        Animation.IDLE: Folder.IDLE_IMGS.format(sprite_name),
        Animation.IDLE_CLIMBING: Folder.IDLE_CLIMBING_IMGS.format(sprite_name),
        Animation.IDLE_CLIMBING_WITH_GOLD: Folder.IDLE_CLIMBING_WITH_GOLD_IMGS.format(sprite_name),
        Animation.IDLE_WITH_GOLD: Folder.IDLE_WITH_GOLD_IMGS.format(sprite_name),
        Animation.PASSED_OUT: Folder.PASSED_OUT_IMGS.format(sprite_name),
        Animation.WALKING: Folder.WALKING_IMGS.format(sprite_name),
        Animation.WALKING_WITH_GOLD: Folder.WALKING_WITH_GOLD_IMGS.format(sprite_name)}[animation]
    size = (SPRITE_SIZE[0] * multiply_size_by, SPRITE_SIZE[1] * multiply_size_by)
    if not os.path.exists(folder):
        return
    return [pygame.transform.scale(pygame.image.load(folder + i).convert(), size) for i in os.listdir(folder)]


def pass_out():
    """Make the player pass out, remove one life etc"""
    if player.is_passed_out():
        return
    if player.gold_sack_sprite:
        drop_gold_sack()
    player.update(Activity.PASSED_OUT)
    player.lives -= 1
    if not player.lives:
        print("GAME OVER!")
        quit()


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
        self.gold_sacks = 0

    def load(self, level, room_):
        """Load a new room"""
        dark_overlay = pygame.Surface(SCREEN_SIZE, flags=pygame.SRCALPHA)
        dark_overlay.fill((90, 90, 90, 0))
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
        self.gold_sacks = \
            len(self.database[str(room_)]["sprites"]["gold"]) if "gold" in self.database[str(room_)]["sprites"] else 0


class Sprite(pygame.sprite.Sprite):

    def __init__(
            self, name, activity="idle", image=None, position=(0, 0), h_direction="right", v_direction="none",
            length=None, animation_freq_ms=0):
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
        length -- (Integer. Optional. Defaults to None) Crop the sprites image to a certain length. If this is provided
            the image will not be scaled.
        animation_freq_ms -- (Integer. Optional. Defaults to 0) The update frequency of the sprite animation in
            milliseconds.
        """
        pygame.sprite.Sprite.__init__(self)

        self.activity = None
        self.animation = None
        self.h_direction = h_direction
        self.v_direction = v_direction
        self.is_facing_down = None
        self.is_facing_left = None
        self.is_facing_right = None
        self.is_facing_up = None
        self.name = name
        self.speed = PLAYER_SPEED
        self.animation_freq_ms = animation_freq_ms
        self.next_img = 0
        self.wake_up_time = 0
        self.fall_pix = 0
        self.lives = PLAYER_LIVES
        self.gold_sack_sprite = None
        self.can_climb_ladders = self.name in (SpriteName.PLAYER, SpriteName.MINER)
        self.gold_delivered = 0
        if image:
            self.animations = None
            self.image = pygame.image.load(image).convert()
            if length:
                cropped = pygame.Surface((self.image.get_size()[0], length))
                cropped.blit(self.image, (0, 0))
                self.image = cropped
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

    def move(self, direction, speed=None, activity=None):
        """
        Move the sprite

        - direction -- (String. Mandatory) Use Direction enum
        - speed -- (Int or Float. Optional. Defaults to self.speed) The speed (number of pixels) to move the sprite in
        - activity -- (String. Optional. Defaults to None) The activity (animation) of the sprite. Will not be updated
            if set to None. Use Activity enum.
        """
        # Set variables
        speed = self.speed if not speed else speed
        vertical = direction in (Direction.UP, Direction.DOWN)
        horizontal = direction in (Direction.LEFT, Direction.RIGHT)
        one_pixel = {True: 1, False: -1}[direction in (Direction.DOWN, Direction.RIGHT)]
        x = one_pixel if horizontal else 0
        y = one_pixel if vertical else 0
        self.v_direction = direction if vertical else self.v_direction
        self.h_direction = direction if horizontal else self.h_direction

        # Move the sprite one pixel at a time and check for wall collisions
        for i in range(1, speed + 1):

            # Move the sprite one pixel
            self.rect.move_ip(x, y)

            # Check if sprite is outside of screen
            if not (0 < self.rect.center[0] < SCREEN_SIZE[0]) and (0 < self.rect.center[1] < SCREEN_SIZE[1]):
                self.rect.move_ip(-x, -y)
                break

            # Check for wall collision
            if self.collides(room.layouts):
                climbed = False

                # Check if the sprite has fallen too far
                if self.fall_pix >= MAX_FALL_PIX:
                    pass_out()

                # Reset fall distance count
                self.fall_pix = 0 if vertical else self.fall_pix

                # Try climbing up slope
                for _ in range(CLIMBABLE_PIX):
                    self.rect.move_ip(0, -1)
                    if not self.collides(room.layouts):
                        climbed = True
                        break
                if climbed and not self.is_passed_out():
                    continue
                else:
                    self.rect.move_ip(0, CLIMBABLE_PIX)

                # Stop the sprite if impossible to get passed obstacle
                self.rect.move_ip(-(one_pixel * i) if horizontal else 0, -y)
                if self.is_carrying_gold() and self.is_climbing():
                    activity = Activity.CLIMBING_WITH_GOLD
                elif self.is_climbing():
                    activity = Activity.CLIMBING
                elif self.is_carrying_gold():
                    activity = Activity.IDLE_WITH_GOLD
                elif self.is_passed_out():
                    activity = Activity.PASSED_OUT
                else:
                    activity = Activity.IDLE
                break

            # Keep track of how many pixels the sprite has fallen
            elif vertical and self.v_direction == Direction.DOWN and not self.collides(ladders):
                self.fall_pix += 1
                if self.fall_pix >= MAX_CONTROL_WHILE_FALLING_PIX:
                    activity = Activity.FALLING_WITH_GOLD if self.is_carrying_gold() else Activity.FALLING
        self.update(activity if activity else self.activity)

    def update(self, activity):
        """Update the sprite animation"""
        now = pygame.time.get_ticks()
        self.is_facing_down = self.v_direction == Direction.DOWN
        self.is_facing_left = self.h_direction == Direction.LEFT
        self.is_facing_right = self.h_direction == Direction.RIGHT
        self.is_facing_up = self.v_direction == Direction.UP

        # Check if the sprite activity has changed and if so change animation
        if activity != self.activity:
            self.animation = animation_loop(self.animations[activity])

            # Start the wake up timer if the player is passed out
            if activity == Activity.PASSED_OUT:
                self.wake_up_time = now + WAKE_UP_TIME_MS

        # Check if it's time to wake up the player from passed out state
        elif self.is_passed_out() and now >= self.wake_up_time:
            activity = Activity.IDLE
            self.animation = animation_loop(self.animations[activity])
            # This is temporary and will be removed when miners can move
            self.rect.x -= 10
            self.rect.y -= 5

        self.activity = activity

        # Load the next image in the animation
        if now >= self.next_img:
            self.image = next(self.animation)
            self.next_img = now + self.animation_freq_ms
            self.image.set_colorkey(Color.WHITE)
            if self.is_facing_left:
                self.image = pygame.transform.flip(self.image, True, False)

    def is_passed_out(self):
        return self.activity == Activity.PASSED_OUT

    def is_walking(self):
        return self.activity in (Activity.WALKING, Activity.WALKING_WITH_GOLD, Activity.PUSHING_WHEELBARROW)

    def is_climbing(self):
        return self.activity in (
            Activity.CLIMBING, Activity.CLIMBING_WITH_GOLD, Activity.IDLE_CLIMBING, Activity.IDLE_CLIMBING_WITH_GOLD)

    def is_falling(self):
        return self.activity in (Activity.FALLING, Activity.FALLING_WITH_GOLD)

    def is_idle(self):
        return self.activity in (
            Activity.IDLE, Activity.IDLE_CLIMBING_WITH_GOLD, Activity.IDLE_CLIMBING, Activity.IDLE_WITH_GOLD,
            Activity.IDLE_WITH_WHEELBARROW)

    def is_carrying_gold(self):
        return self.activity in (
            Activity.WALKING_WITH_GOLD, Activity.IDLE_WITH_GOLD, Activity.IDLE_CLIMBING_WITH_GOLD,
            Activity.CLIMBING_WITH_GOLD, Activity.FALLING_WITH_GOLD)

    def is_pulling_up(self):
        return self.activity == Activity.PULLING_UP

    def is_pushing_wheelbarrow(self):
        return self.activity in (Activity.PUSHING_WHEELBARROW, Activity.IDLE_WITH_WHEELBARROW)


# Enums
class Activity(object):
    CLIMBING = "climbing"
    CLIMBING_WITH_GOLD = "climbing_with_gold"
    FALLING = "falling"
    FALLING_WITH_GOLD = "falling_with_gold"
    IDLE = "idle"
    IDLE_CLIMBING = "idle_climbing"
    IDLE_CLIMBING_WITH_GOLD = "idle_climbing_with_gold"
    IDLE_WITH_GOLD = "idle_with_gold"
    IDLE_WITH_WHEELBARROW = "idle_with_wheelbarrow"
    PASSED_OUT = "passed_out"
    PULLING_UP = "pulling_up"
    PUSHING_WHEELBARROW = "pushing_wheelbarrow"
    RIDING_CART = "riding cart"
    WALKING = "walking"
    WALKING_WITH_GOLD = "walking_with_gold"


class Animation(Activity):
    pass


class Color(object):
    BLACK = (0, 0, 0)
    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)
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
    TEXTURES = IMAGES + "textures" + os.sep
    CLIMBING_IMGS = SPRITES + "{}" + os.sep + "climbing" + os.sep
    CLIMBING_WITH_GOLD_IMGS = SPRITES + "{}" + os.sep + "climbing_with_gold" + os.sep
    IDLE_IMGS = SPRITES + "{}" + os.sep + "idle" + os.sep
    IDLE_CLIMBING_IMGS = SPRITES + "{}" + os.sep + "idle_climbing" + os.sep
    IDLE_CLIMBING_WITH_GOLD_IMGS = SPRITES + "{}" + os.sep + "idle_climbing_with_gold" + os.sep
    IDLE_WITH_GOLD_IMGS = SPRITES + "{}" + os.sep + "idle_with_gold" + os.sep
    PASSED_OUT_IMGS = SPRITES + "{}" + os.sep + "passed_out" + os.sep
    WALKING_IMGS = SPRITES + "{}" + os.sep + "walking" + os.sep
    WALKING_WITH_GOLD_IMGS = SPRITES + "{}" + os.sep + "walking_with_gold" + os.sep


class FileName(object):
    LEVEL_DB = Folder.LEVELS + "level{}.json"


class SpriteName(object):
    AXE = "axe"
    CART = "cart"
    ELEVATOR = "elevator"
    GOLD = "gold"
    HANDLE = "handle"
    LADDER = "ladder"
    LAYOUT = "layout"
    PLAYER = "player"
    TRUCK = "truck"
    MINER = "miner"
    WHEELBARROW = "wheelbarrow"


# Load sprite animation images and store in a dict
SPRITE_ANIMATIONS = {
    SpriteName.GOLD: {
        Animation.IDLE: load_images(Animation.IDLE, SpriteName.GOLD)},
    SpriteName.MINER: {
        Animation.IDLE: load_images(Animation.IDLE, SpriteName.MINER),
        Animation.WALKING: load_images(Animation.WALKING, SpriteName.MINER)},
    SpriteName.PLAYER: {
        Animation.CLIMBING: load_images(Animation.CLIMBING, SpriteName.PLAYER),
        Animation.CLIMBING_WITH_GOLD: load_images(Animation.CLIMBING_WITH_GOLD, SpriteName.PLAYER),
        Animation.FALLING: load_images(Animation.IDLE, SpriteName.PLAYER),
        Animation.FALLING_WITH_GOLD: load_images(Animation.IDLE_WITH_GOLD, SpriteName.PLAYER),
        Animation.IDLE: load_images(Animation.IDLE, SpriteName.PLAYER),
        Animation.IDLE_CLIMBING: load_images(Animation.IDLE_CLIMBING, SpriteName.PLAYER),
        Animation.IDLE_CLIMBING_WITH_GOLD: load_images(Animation.IDLE_CLIMBING_WITH_GOLD, SpriteName.PLAYER),
        Animation.IDLE_WITH_GOLD: load_images(Animation.IDLE_WITH_GOLD, SpriteName.PLAYER),
        Animation.PASSED_OUT: load_images(Animation.PASSED_OUT, SpriteName.PLAYER),
        Animation.WALKING: load_images(Animation.WALKING, SpriteName.PLAYER),
        Animation.WALKING_WITH_GOLD: load_images(Animation.WALKING_WITH_GOLD, SpriteName.PLAYER)},
    SpriteName.TRUCK: {
        Animation.IDLE: load_images(Animation.IDLE, SpriteName.TRUCK, multiply_size_by=4),
        Animation.IDLE_WITH_GOLD: load_images(Animation.IDLE_WITH_GOLD, SpriteName.TRUCK, multiply_size_by=4)}}

# Initialize PyGame
pygame.init()

# Various variables and objects
clock = pygame.time.Clock()
game_is_running = True

# Load mine and room
room = Rooms()
room.load(1, 3)

# Generate sprites
players = generate_sprites(room, SpriteName.PLAYER, animation_freq_ms=8)
player = players.sprites()[0]
miners = generate_sprites(room, SpriteName.MINER)
gold_sacks = generate_sprites(room, SpriteName.GOLD, animation_freq_ms=500)
ladders = generate_sprites(room, SpriteName.LADDER, image=Folder.IDLE_IMGS.format(SpriteName.LADDER) + "001.png")
trucks = generate_sprites(room, SpriteName.TRUCK, animation_freq_ms=100)
all_sprites = (ladders, miners, trucks, gold_sacks, players)
not_player = (miners, gold_sacks, ladders, trucks)
affected_by_gravity = (miners, gold_sacks, players, trucks)

# On-screen text
default_font = "comicsansms"
font_name = default_font if default_font in pygame.font.get_fonts() else "freesansbold.ttf"
font = pygame.font.SysFont(font_name, 30)
font.set_bold(True)
title_text = font.render("- GOLD THIEF -", True, Color.GREEN)
title_text_rect = title_text.get_rect()
title_text_rect.center = (SCREEN_SIZE[0] // 2, 40)
lives_text = font.render("Lives: {}".format(player.lives), True, Color.GREEN)
lives_text_rect = title_text.get_rect()
lives_text_rect.center = (SCREEN_SIZE[0] - 150, 40)

########################################################################################################################
# MAIN LOOP
########################################################################################################################
while game_is_running:

    clock.tick(FPS)
    gold_sack_interaction = False

    # Read events
    for event in pygame.event.get():

        # Check for quit game request from user
        game_is_running = \
            not (event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE))

        # Check whether one of the gold sack interaction buttons are pressed
        l_control = event.type == pygame.KEYUP and event.key == pygame.K_LCTRL
        l_alt = event.type == pygame.KEYUP and event.key == pygame.K_LALT
        space = event.type == pygame.KEYUP and event.key == pygame.K_SPACE
        r_control = event.type == pygame.KEYUP and event.key == pygame.K_RCTRL
        r_alt = event.type == pygame.KEYUP and event.key == pygame.K_RALT
        gold_sack_interaction = any((l_control, l_alt, space, r_control, r_alt))

    # Read key presses and move the player
    key_presses(gold_sack_interaction)

    # Apply gravity to all sprites. This will also update sprite animations.
    gravity()

    # Check if the player is caught by a miner
    if player.collides(miners) and not player.is_passed_out():
        pass_out()

    # Draw background and walls
    screen.blit(room.background_img, (0, 0))
    screen.blit(room.texture_img, (0, 0))

    # Draw sprites
    for s in all_sprites:
        s.draw(screen)

    # Draw text
    lives_text = font.render("Lives: {}".format(player.lives), True, Color.GREEN)
    screen.blit(title_text, title_text_rect)
    screen.blit(lives_text, lives_text_rect)

    # Update the screen
    pygame.display.flip()
    #print(player.activity)
