import pygame
import os
import json
import ctypes
import random
import itertools

# Constants that are useful during development
CHICKEN_MODE = True
SHOW_START_SCREEN = True
START_MINE = 1
PLAYER_LIVES = 5

# Other constants
BONUS_POINTS = 10
CLIMBABLE_PIX = 1
FPS = 25
GRAVITY = 20
IMG_SEMI_TRANSPARENCY = 80
IMG_FULLY_OPAQUE = 255
IMG_TRANSPARENCY_INCREMENTATION = 1
IMMORTAL_TIME = 5000
MAX_FALL_PIX = 100
MAX_CONTROL_WHILE_FALLING_PIX = 50
STANDARD_SPEED = 9
SLOW_SPEED = 5
MINER_SPEED = 8
MINER_WARNING_DISTANCE_PIX = 200
SCREEN_SIZE = (1440, 1080)
SPRITE_SIZE = (120, 120)
WAKE_UP_TIME_MS = 5000
WARNINGS_ANIMATION_FREQ_MS = 100
WARNINGS_DURATION_MS = 1000

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


def change_direction(direction):
    """
    Returns the opposite direction of received argument

    - direction -- (String. Mandatory) Use Direction ENUM

    Returns: String
    """
    return {
        Direction.RIGHT: Direction.LEFT, Direction.LEFT: Direction.RIGHT, Direction.UP: Direction.DOWN,
        Direction.DOWN: Direction.UP}[direction]


def exit_room(exits_, sprites_):
    """
    Check whether a sprite walks through an exit and if so transport to a different room

    - exits_ -- (List. Mandatory) A list of exit point sprites
    - sprites_ -- (List. Mandatory) A list of sprites to check collision agains. Probably player or miners.

    Returns: None
    """
    for e in exits_:
        for spr in sprites_:
            if spr.collides(e) and e.exit_direction in (spr.h_direction, spr.v_direction):
                if spr.is_player:
                    mine.set(mine.mine, e.leads_to["room"])
                    warnings.empty()
                else:
                    # Randomly decide whether the sprite should go through the exit or turn around
                    if bool(random.randrange(0, 2)):
                        spr.v_direction = change_direction(spr.v_direction)
                        spr.h_direction = change_direction(spr.h_direction)
                        continue
                    spr.remove(mine.rooms[str(mine.room)]["miners"])
                    mine.rooms[str(e.leads_to["room"])]["miners"].add(spr)
                spr.rect.x = e.leads_to["x"]
                spr.rect.y = e.leads_to["y"]


def flatten_list(l):
    """
    Make a list of lists into a single list.

    - l -- (List. Mandatory)

    Returns: List
    """
    return [item for sublist in l for item in sublist]


def game_over():
    """Display the game over screen"""
    text = {mine.seconds_remaining <= 0: out_of_time, mine.player.lives <= 0: game_over_}[True]
    screen.blit(text.text, text.rect)
    pygame.display.flip()


def get_caught():
    """Check whether the player is caught by a miner"""
    for mi in mine.miners.sprites():
        if mi.collides(mine.player) and not mine.player.is_passed_out() and not mi.is_passed_out() \
                and not CHICKEN_MODE and not mine.player.immortality_timer:
            mine.player.pass_out()


def hit_miner():
    """
    Check if a miner is hit by a falling gold sack
    """
    for gold_ in mine.gold_sacks.sprites():
        for miner_ in mine.miners.sprites():
            if miner_.collides(gold_) and gold_.is_falling() and not miner_.is_passed_out():
                miner_.pass_out()
                mine.bonus += BONUS_POINTS


def key_presses(interact_key_pressed):
    """
    Check key presses and control the player sprite

    - interact_key_pressed -- (Boolean. Mandatory) Specifies whether one of the interact keys were pressed
    """

    # Get key presses
    key_press = pygame.key.get_pressed()
    down = key_press[pygame.K_DOWN] and mine.player.collides(mine.ladders)
    left = key_press[pygame.K_LEFT] and not mine.player.is_falling()
    right = key_press[pygame.K_RIGHT] and not mine.player.is_falling()
    up = key_press[pygame.K_UP] and mine.player.collides(mine.ladders)
    pick_up_gold = interact_key_pressed and mine.player.collides(mine.gold_sacks) and not mine.player.saved_sprite
    drop_gold = interact_key_pressed and mine.player.is_carrying_gold()
    pick_up_wheelbarrow = \
        interact_key_pressed and mine.player.collides(mine.wheelbarrows) and not mine.player.saved_sprite
    drop_or_empty_wheelbarrow = interact_key_pressed and mine.player.is_pushing_wheelbarrow()
    drop = drop_gold or drop_or_empty_wheelbarrow
    no_key_presses = not any((down, left, right, up))
    move_vertical = (up or down) and not mine.player.is_pushing_wheelbarrow()
    move_horizontal = left or right

    # No interaction is possible if the player is passed out
    if mine.player.is_passed_out():
        return

    # Player is idle if no keys are pressed
    if no_key_presses:
        if mine.player.is_carrying_gold() and mine.player.is_climbing():
            mine.player.update(Activity.IDLE_CLIMBING_WITH_GOLD)
        elif mine.player.is_climbing():
            mine.player.update(Activity.IDLE_CLIMBING)
        elif mine.player.is_carrying_gold():
            mine.player.update(Activity.IDLE_WITH_GOLD)
        elif mine.player.is_pushing_empty_wheelbarrow():
            mine.player.update(Activity.IDLE_WITH_EMPTY_WHEELBARROW)
        elif mine.player.is_pushing_loaded_01_wheelbarrow():
            mine.player.update(Activity.IDLE_WITH_LOADED_01_WHEELBARROW)
        elif mine.player.is_pushing_loaded_02_wheelbarrow():
            mine.player.update(Activity.IDLE_WITH_LOADED_02_WHEELBARROW)
        elif mine.player.is_pushing_loaded_03_wheelbarrow():
            mine.player.update(Activity.IDLE_WITH_LOADED_03_WHEELBARROW)
        else:
            mine.player.update(Activity.IDLE)

    # Move up and down
    if move_vertical:
        activity = Activity.CLIMBING_WITH_GOLD if mine.player.is_carrying_gold() else Activity.CLIMBING
        mine.player.move(Direction.DOWN if down else Direction.UP, activity=activity)

    # Move left and right
    if move_horizontal:
        if mine.player.is_carrying_gold():
            activity = Activity.CLIMBING_WITH_GOLD \
                if mine.player.is_climbing() and mine.player.collides(mine.ladders) else Activity.WALKING_WITH_GOLD
        elif mine.player.is_pushing_empty_wheelbarrow():
            activity = Activity.PUSHING_EMPTY_WHEELBARROW
        elif mine.player.is_pushing_loaded_01_wheelbarrow():
            activity = Activity.PUSHING_LOADED_01_WHEELBARROW
        elif mine.player.is_pushing_loaded_02_wheelbarrow():
            activity = Activity.PUSHING_LOADED_02_WHEELBARROW
        elif mine.player.is_pushing_loaded_03_wheelbarrow():
            activity = Activity.PUSHING_LOADED_03_WHEELBARROW
        else:
            activity = \
                Activity.CLIMBING if mine.player.is_climbing() and mine.player.collides(mine.ladders) else Activity.WALKING
        mine.player.move(Direction.LEFT if left else Direction.RIGHT, activity=activity)

    # Pick up or drop another sprite
    if pick_up_gold:
        mine.player.pick_up(mine.gold_sacks)
    elif pick_up_wheelbarrow:
        mine.player.pick_up(mine.wheelbarrows)
    elif drop:
        mine.player.drop_sprite()


def load_db(database):
    """
    Read a json file and return as dict

    - database -- (String. Mandatory) The json-file to read.

    Returns: Dict
    """
    with open(database, "r") as f:
        return json.loads(f.read())


def load_images(animation, sprite_name, multiply_x_by=1, multiply_y_by=1):
    """
    Read all image files in a folder and return as a list of pyGame images

    - animation -- (String. Mandatory) The name of the requested animation. Use Animation enum
    - sprite_name -- (String. Optional) The name of the sprite. Use SpriteName enum.
    - multiply_x_by -- (Integer. Optional. Defaults to 1) Multiply the horizontal size of the image with the given
        number
    - multiply_y_by -- (Integer. Optional. Defaults to 1) Multiply the vertical size of the image with the given number

    Returns: List
    """
    folder = {
        Animation.CLIMBING: Folder.CLIMBING_IMGS.format(sprite_name),
        Animation.CLIMBING_UP: Folder.CLIMBING_UP_IMGS.format(sprite_name),
        Animation.CLIMBING_DOWN: Folder.CLIMBING_DOWN_IMGS.format(sprite_name),
        Animation.CLIMBING_WITH_GOLD: Folder.CLIMBING_WITH_GOLD_IMGS.format(sprite_name),
        Animation.FALLING: Folder.IDLE_IMGS.format(sprite_name),
        Animation.IDLE: Folder.IDLE_IMGS.format(sprite_name),
        Animation.IDLE_CLIMBING: Folder.IDLE_CLIMBING_IMGS.format(sprite_name),
        Animation.IDLE_CLIMBING_WITH_GOLD: Folder.IDLE_CLIMBING_WITH_GOLD_IMGS.format(sprite_name),
        Animation.IDLE_WITH_EMPTY_WHEELBARROW: Folder.IDLE_WITH_EMPTY_WHEELBARROW_IMGS.format(sprite_name),
        Animation.IDLE_WITH_GOLD: Folder.IDLE_WITH_GOLD_IMGS.format(sprite_name),
        Animation.IDLE_WITH_LOADED_01_WHEELBARROW: Folder.IDLE_WITH_LOADED_01_WHEELBARROW_IMGS.format(sprite_name),
        Animation.IDLE_WITH_LOADED_02_WHEELBARROW: Folder.IDLE_WITH_LOADED_02_WHEELBARROW_IMGS.format(sprite_name),
        Animation.IDLE_WITH_LOADED_03_WHEELBARROW: Folder.IDLE_WITH_LOADED_03_WHEELBARROW_IMGS.format(sprite_name),
        Animation.LOADED_01: Folder.LOADED_01.format(sprite_name),
        Animation.LOADED_02: Folder.LOADED_02.format(sprite_name),
        Animation.LOADED_03: Folder.LOADED_03.format(sprite_name),
        Animation.LOADED_04: Folder.LOADED_04.format(sprite_name),
        Animation.LOADED_05: Folder.LOADED_05.format(sprite_name),
        Animation.PASSED_OUT: Folder.PASSED_OUT_IMGS.format(sprite_name),
        Animation.PUSHING_EMPTY_WHEELBARROW: Folder.PUSHING_EMPTY_WHEELBARROW_IMGS.format(sprite_name),
        Animation.PUSHING_LOADED_01_WHEELBARROW: Folder.PUSHING_LOADED_01_WHEELBARROW_IMGS.format(sprite_name),
        Animation.PUSHING_LOADED_02_WHEELBARROW: Folder.PUSHING_LOADED_02_WHEELBARROW_IMGS.format(sprite_name),
        Animation.PUSHING_LOADED_03_WHEELBARROW: Folder.PUSHING_LOADED_03_WHEELBARROW_IMGS.format(sprite_name),
        Animation.WALKING: Folder.WALKING_IMGS.format(sprite_name),
        Animation.WALKING_WITH_GOLD: Folder.WALKING_WITH_GOLD_IMGS.format(sprite_name)}[animation]
    size = (SPRITE_SIZE[0] * multiply_x_by, SPRITE_SIZE[1] * multiply_y_by)
    if not os.path.exists(folder):
        return
    return [pygame.transform.scale(pygame.image.load(folder + i).convert(), size) for i in os.listdir(folder)]


def move_sprites():
    """
    Iterate though all rooms in the mine, move the miners and apply gravity to all applicable sprites
    """

    # Remember original room, i.e. the room where the player is
    original_room = mine.room

    # Start iteration
    for ro in range(1, mine.no_of_rooms + 1):

        # Change room temporarily
        mine.set(mine_=mine.mine, room_=ro)

        # Apply gravity to all sprites. This will also update sprite animations.
        for sp in mine.affected_by_gravity + ([mine.players] if mine.room == original_room else []):
            for spr in sp.sprites():
                if not (spr.can_climb_ladders and spr.collides(mine.ladders)) \
                        or not spr.can_climb_ladders or spr.is_passed_out():
                    spr.move(Direction.DOWN, GRAVITY)

        # Move miners
        for m in mine.miners.sprites():
            m.move_cc()

        # Check if a miner collides with an exit point to another room
        exit_room(mine.exits.sprites(), mine.miners.sprites())

        # Check miner is close to an exit point leading to the same room as the player and if so present a warning
        for ex, mi in itertools.product(mine.exits.sprites(), mine.miners.sprites()):
            if mi.is_placeholder:
                continue
            heading_left = mi.h_direction == Direction.LEFT and mi.is_walking()
            heading_right = mi.h_direction == Direction.RIGHT and mi.is_walking()
            heading_up = mi.v_direction == Direction.UP and mi.is_climbing()
            heading_down = mi.v_direction == Direction.DOWN and mi.is_climbing()
            right_of_exit = ex.rect.right + MINER_WARNING_DISTANCE_PIX >= mi.rect.x > ex.rect.right
            left_of_exit = ex.rect.x - MINER_WARNING_DISTANCE_PIX <= mi.rect.right < ex.rect.x
            below_exit = ex.rect.bottom + MINER_WARNING_DISTANCE_PIX >= mi.rect.y > ex.rect.bottom
            above_exit = ex.rect.y - MINER_WARNING_DISTANCE_PIX <= mi.rect.bottom < ex.rect.y
            same_v_pos = mi.rect.y <= ex.rect.bottom and mi.rect.bottom >= ex.rect.y
            same_h_pos = mi.rect.x <= ex.rect.right and mi.rect.right >= ex.rect.x
            same_room_as_player = ex.leads_to["room"] == original_room
            warning_right = heading_left and right_of_exit
            warning_left = heading_right and left_of_exit
            warning_below = heading_up and below_exit
            warning_above = heading_down and above_exit
            existing_warnings = [(w.rect.x, w.rect.y) for w in warnings.sprites()]
            exists = (ex.leads_to["x"], ex.leads_to["y"]) in existing_warnings
            h_warning = same_v_pos and same_room_as_player and (warning_left or warning_right) and not exists
            v_warning = same_h_pos and same_room_as_player and (warning_above or warning_below) and not exists
            add_warning = h_warning or v_warning
            activity = (
                Activity.CLIMBING_UP if heading_up else Activity.CLIMBING_DOWN) if v_warning else Activity.WALKING

            if add_warning:
                warnings.add(Sprite(
                    SpriteName.WARNING, position=(ex.leads_to["x"], ex.leads_to["y"]), h_direction=mi.h_direction,
                    activity=activity, longevity_ms=WARNINGS_DURATION_MS,
                    animation_freq_ms=WARNINGS_ANIMATION_FREQ_MS))

    # Update warnings animations
    warnings.update()

    # Change back to the original room where the player is
    mine.set(mine_=mine.mine, room_=original_room)


def start_screen():
    """Display the start screen"""
    screen.blit(mine.background_img, (0, 0))
    screen.blit(start_screen_01.text, start_screen_01.rect)
    screen.blit(start_screen_02.text, start_screen_02.rect)
    pygame.display.flip()


# Classes
class Mines(object):
    """Class for loading all room layouts in a mine (level) and it's sprites"""

    def __init__(self):

        self.mine = None
        self.room = None
        self.database = None
        self.rooms = {}
        self.background_img = None
        self.layout = None
        self.layouts = None
        self.layout_img = None
        self.layout_sprite = None
        self.texture = None
        self.texture_img = None
        self.no_of_gold_sacks = 0
        self.players = None
        self.player = None
        self.miners = None
        self.gold_sacks = None
        self.ladders = None
        self.trucks = None
        self.wheelbarrows = None
        self.exits = None
        self.all_sprites = None
        self.not_player = None
        self.affected_by_gravity = None
        self.gold_delivered = 0
        self.no_of_rooms = 0
        self.time_limit_mins = 0
        self.seconds_remaining = 0
        self.bonus = 0
        self.score = 0
        self.tot_number_of_mines = range(1, len(os.listdir(Folder.MINES))+1)
        self.game_completed = False
        self.total_score = []
        self.scores = {}

    def set(self, mine_, room_):
        """
        Set what mine and room is currently displayed on screen

        - mine -- (Integer. Mandatory) The requested mine
        - room_ -- (Integer. Mandatory) The requested room

        returns: None
        """

        # Load a new mine if requested
        if mine_ != self.mine:
            self.load(mine_)

        # Point all class variables to the correct room in the rooms dictionary
        self.room = room_
        self.texture_img = self.rooms[str(self.room)]["texture_img"]
        self.layout = self.rooms[str(self.room)]["layout"]
        self.background_img = self.rooms[str(self.room)]["background_img"]
        self.layout_img = self.rooms[str(self.room)]["layout_img"]
        self.layout_sprite = self.rooms[str(self.room)]["layout_sprite"]
        self.layouts = self.rooms[str(self.room)]["layouts"]
        self.miners = self.rooms[str(self.room)]["miners"]
        self.gold_sacks = self.rooms[str(self.room)]["gold_sacks"]
        self.ladders = self.rooms[str(self.room)]["ladders"]
        self.trucks = self.rooms[str(self.room)]["trucks"]
        self.wheelbarrows = self.rooms[str(self.room)]["wheelbarrows"]
        self.exits = self.rooms[str(self.room)]["exits"]
        self.all_sprites = self.rooms[str(self.room)]["all_sprites"]
        self.not_player = self.rooms[str(self.room)]["not_player"]
        self.affected_by_gravity = self.rooms[str(self.room)]["affected_by_gravity"]
        self.player = self.rooms[str(self.room)]["player"] if not self.player else self.player
        self.players = self.rooms[str(self.room)]["players"] if not self.players else self.players

    def load(self, mine_):
        """
        Load all rooms in a mine (level)

        - mine -- (Integer. Mandatory) The requested mine

        returns: None
        """
        # Load mine database
        self.mine = mine_
        self.database = load_db(FileName.MINE_DB.format(self.mine))
        self.gold_delivered = 0
        self.texture = Folder.TEXTURES + self.database["texture"]
        self.time_limit_mins = self.database["time_limit_mins"]
        self.seconds_remaining = self.time_limit_mins * 60
        self.bonus = 0

        # Load layout for each room in the mine
        dark_overlay = pygame.Surface(SCREEN_SIZE, flags=pygame.SRCALPHA)
        dark_overlay.fill((90, 90, 90, 0))
        for r in self.database["rooms"]:
            self.rooms[r] = {}
        for r in self.database["rooms"]:
            self.rooms[r]["texture_img"] = pygame.image.load(self.texture)
            self.rooms[r]["layout"] = Folder.LAYOUTS + self.database["rooms"][r]["layout"]
            self.rooms[r]["background_img"] = pygame.image.load(self.texture)
            self.rooms[r]["background_img"] = pygame.transform.scale(self.rooms[r]["texture_img"], SCREEN_SIZE)
            self.rooms[r]["background_img"].blit(dark_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
            self.rooms[r]["layout_img"] = pygame.image.load(self.rooms[r]["layout"]).convert()
            self.rooms[r]["layout_img"].set_colorkey(Color.BLACK)
            self.rooms[r]["texture_img"] = pygame.transform.scale(self.rooms[r]["texture_img"], SCREEN_SIZE)
            self.rooms[r]["texture_img"].blit(self.rooms[r]["layout_img"], (0, 0))
            self.rooms[r]["texture_img"].set_colorkey(Color.WHITE)
            self.rooms[r]["layout_sprite"] = Sprite(SpriteName.LAYOUT, image=self.rooms[r]["layout"])
            self.rooms[r]["layouts"] = pygame.sprite.Group()
            self.rooms[r]["layouts"].add(self.rooms[r]["layout_sprite"])
            self.no_of_gold_sacks = len(flatten_list([
                self.database["rooms"][r]["sprites"]["gold"] for r in self.database["rooms"]
                if "gold" in self.database["rooms"][r]["sprites"]]))
            self.no_of_rooms = len(self.database["rooms"])

            # Load sprites
            self.rooms[r]["players"] = self.generate_sprites(r, SpriteName.PLAYER, animation_freq_ms=8)
            self.rooms[r]["player"] = self.rooms[r]["players"].sprites()[0]
            self.rooms[r]["miners"] = self.generate_sprites(
                r, SpriteName.MINER, standard_speed=MINER_SPEED, animation_freq_ms=8)
            self.rooms[r]["gold_sacks"] = self.generate_sprites(r, SpriteName.GOLD, animation_freq_ms=500)
            self.rooms[r]["ladders"] = self.generate_sprites(
                r, SpriteName.LADDER, image=Folder.IDLE_IMGS.format(SpriteName.LADDER) + "001.png")
            self.rooms[r]["trucks"] = self.generate_sprites(r, SpriteName.TRUCK, animation_freq_ms=100)
            self.rooms[r]["wheelbarrows"] = self.generate_sprites(r, SpriteName.WHEELBARROW)
            self.rooms[r]["exits"] = self.generate_sprites(
                r, SpriteName.EXIT, image=Folder.IDLE_IMGS.format(SpriteName.EXIT) + "001.png")
            self.rooms[r]["all_sprites"] = (
                self.rooms[r]["ladders"], self.rooms[r]["trucks"], self.rooms[r]["gold_sacks"],
                self.rooms[r]["wheelbarrows"], self.rooms[r]["miners"])
            self.rooms[r]["not_player"] = (
                self.rooms[r]["miners"], self.rooms[r]["gold_sacks"], self.rooms[r]["ladders"], self.rooms[r]["trucks"],
                self.rooms[r]["wheelbarrows"])
            self.rooms[r]["affected_by_gravity"] = [
                self.rooms[r]["miners"], self.rooms[r]["gold_sacks"], self.rooms[r]["trucks"],
                self.rooms[r]["wheelbarrows"]]

    def reset(self, mine_=None):
        """
        Reset all sprites in the mine to their start positions

        - mine_ -- (Integer or string. Mandatory. Optional) The requested mine. Will default to the current mine.
        """
        mine_ = self.mine if not mine_ else mine_
        self.load(mine_)
        self.set(mine_, 1)
        self.player.lives = PLAYER_LIVES
        player_db = self.database["rooms"]["1"]["sprites"]["player"][0]
        self.player.rect.x = player_db["position"][0]
        self.player.rect.y = player_db["position"][1]
        self.player.activity = Activity.IDLE
        self.player.h_direction = player_db["h_direction"]
        self.player.saved_sprite = None

    def generate_sprites(
            self, room_, name, image=None, animation_freq_ms=0, standard_speed=STANDARD_SPEED, slow_speed=SLOW_SPEED):
        """
        Generate a sprites group from room setup dictionary

        - room_ - (String or Integer. Mandatory) Refers to the room/mine database
        - name -- (String. Mandatory) The name of the sprite to generate. Use SpriteNames enum.
        - image -- (String. Optional. Defaults to None) Use a specific image instead of an animation
        - animation_freq_ms -- (Integer. Optional. Defaults to 0) The update frequency of the sprite animation in
            milliseconds.
        - standard_speed -- (Integer. Optional. Defaults to STANDARD_SPEED constant value) The sprite's speed when not
            carrying a gold sack
        - slow_speed -- (Integer. Optional. Defaults to SLOW_SPEED constant value) The sprite's speed when carrying a
            gold sack

        returns: An instance of pygame.sprites.Group()
        """
        if name not in self.database["rooms"][str(room_)]["sprites"]:
            name = SpriteName.PLACEHOLDER
            sprites_db = [{"position": [-10, -10]}]
            image = FileName.PLACEHOLDER_IMG
        else:
            sprites_db = self.database["rooms"][str(room_)]["sprites"][name]
        sprites = []
        group = pygame.sprite.Group()
        for spr in sprites_db:
            activity = spr["activity"] if "activity" in spr else Activity.IDLE
            h_direction = spr["h_direction"] if "h_direction" in spr else Direction.RIGHT
            v_direction = spr["v_direction"] if "v_direction" in spr else Direction.DOWN
            height = spr["height"] if "height" in spr else None
            leads_to = spr["leads_to"] if "leads_to" in spr else None
            exit_dir = spr["exit_dir"] if "exit_dir" in spr else None
            sprites.append(Sprite(
                name=name, position=spr["position"], image=image, activity=activity, h_direction=h_direction,
                v_direction=v_direction, height=height, animation_freq_ms=animation_freq_ms,
                standard_speed=standard_speed,
                slow_speed=slow_speed, leads_to=leads_to, exit_dir=exit_dir))
        for spr in sprites:
            group.add(spr)
        return group

    def is_completed(self):
        done = self.gold_delivered >= self.no_of_gold_sacks
        if done:
            if self.mine not in self.scores:
                self.scores[self.mine] = self.score
                self.total_score = sum([sc for sc in self.scores.values()])
            screen.blit(mine_is_completed_01.update(self.mine), mine_is_completed_01.rect)
            screen.blit(mine_is_completed_02.update(self.mine), mine_is_completed_02.rect)
            screen.blit(score.update(
                int(self.seconds_remaining), self.player.lives, self.bonus, f"{self.score:,}", get_rect=True),
                score.rect)
            screen.blit(tot_score.update(f"{self.total_score:,}", get_rect=True), tot_score.rect)
            pygame.display.flip()
        return done

    def next(self):
        """Load the next mine"""
        next_mine = self.mine + 1
        if next_mine not in self.tot_number_of_mines:
            next_mine = 1
            self.game_completed = True
        self.set(next_mine, 1)
        self.reset()

    def is_game_completed(self):
        if self.game_completed:
            screen.blit(mine.background_img, (0, 0))
            screen.blit(game_completed_01.text, game_completed_01.rect)
            screen.blit(game_completed_02.text, game_completed_02.rect)
            screen.blit(tot_score.update(f"{self.total_score:,}", get_rect=True), tot_score.rect)
            pygame.display.flip()
        return self.game_completed

    def is_game_over(self):
        return self.seconds_remaining <= 0 or self.player.lives <= 0


class Sprite(pygame.sprite.Sprite):

    def __init__(
            self, name, activity="idle", image=None, position=(0, 0), h_direction="right", v_direction="none",
            height=None, animation_freq_ms=0, standard_speed=STANDARD_SPEED, slow_speed=SLOW_SPEED, leads_to=None,
            exit_dir=None, longevity_ms=None):
        """
        Create a new sprite

        - name -- (String. Mandatory) The sprite name. Use SpriteName enum
        - activity -- (String. Optional. Defaults to "idle") The current activity of the sprite. Use Activity enum
        - image -- (String. Optional. Defaults to None) Path to image file. If provided a static image will be used for
            the sprite and animations will be disabled.
        - position -- (Tuple. Optional. Defaults to (0, 0)) The current position of the sprite
        - h_direction -- (String. Optional. Defaults to "right") The current horizontal direction the sprite is facing.
            Use Direction enum.
        - v_direction -- (String. Optional. Defaults to "right") The current vertical direction the sprite is moving in.
            Use Direction enum.
        - height -- (Integer. Optional. Defaults to None) Crop the sprites image to a certain height. If this is
            provided the image will not be scaled.
        - animation_freq_ms -- (Integer. Optional. Defaults to 0) The update frequency of the sprite animation in
            milliseconds.
        - standard_speed -- (Integer. Optional. Defaults to STANDARD_SPEED constant value) The sprite's speed when not
            carrying a gold sack
        - slow_speed -- (Integer. Optional. Defaults to SLOW_SPEED constant value) The sprite's speed when carrying a
            gold sack
        - leads_to -- (Dict. Optional. Defaults to None) Only valid for exit sprites. A dictionary containing the
            room number and x/y-position to where the exit leads
        - exit_dir -- (String. Optional. Defaults to None) Only valid for exit sprites. The direction the player must be
            facing to go through the exit.
        - longevity_ms -- (Integer. Optional. Defaults to None) If set to a positive value the sprite will expire after
            the given number of milliseconds
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
        self.is_player = self.name == SpriteName.PLAYER
        self.is_miner = self.name == SpriteName.MINER
        self.is_gold_sack = self.name == SpriteName.GOLD
        self.is_ladder = self.name == SpriteName.LADDER
        self.is_truck = self.name == SpriteName.TRUCK
        self.is_wheelbarrow = self.name == SpriteName.WHEELBARROW
        self.is_axe = self.name == SpriteName.AXE
        self.is_cart = self.name == SpriteName.CART
        self.is_elevator = self.name == SpriteName.ELEVATOR
        self.is_handle = self.name == SpriteName.HANDLE
        self.standard_speed = standard_speed
        self.slow_speed = slow_speed
        self.speed = standard_speed
        self.animation_freq_ms = animation_freq_ms
        self.next_img = 0
        self.wake_up_time = 0
        self.fall_pix = 0
        self.lives = PLAYER_LIVES
        self.saved_sprite = None
        self.can_climb_ladders = self.name in (SpriteName.PLAYER, SpriteName.MINER)
        self.carries_gold_sacks = 0
        self.group_single = pygame.sprite.GroupSingle()
        self.group_single.add(self)
        self.is_computer_controlled = not self.is_player
        self.ladder_enter_selection = False
        self.ladder_exit_selection = [False, False]
        self.just_entered_ladder = False
        self.can_pass_out = self.name in (SpriteName.PLAYER, SpriteName.MINER)
        self.is_mortal = self.name == SpriteName.PLAYER
        self.is_placeholder = self.name == SpriteName.PLACEHOLDER
        self.is_static = bool(image)
        self.leads_to = leads_to
        self.exit_direction = exit_dir
        self.max_control_while_falling_pix = 0 if self.name == SpriteName.GOLD else MAX_CONTROL_WHILE_FALLING_PIX
        self.immortality_timer = 0
        self.image_transparency_val = 255
        self.longevity_ms = longevity_ms
        self.expiration_ms = pygame.time.get_ticks() + self.longevity_ms if self.longevity_ms else 0
        self.ignore_screen_boundaries = self.is_truck
        if image:
            self.animations = None
            self.image = pygame.image.load(image).convert()
            if height:
                cropped = pygame.Surface((self.image.get_size()[0], height))
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
        sprites = [sprites[0].group_single] if type(sprites[0]) is not pygame.sprite.Group else sprites
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

        # Move the sprite one pixel at a time and check for wall collisions etc
        for i in range(1, speed + 1):

            # Move the sprite one pixel
            self.rect.move_ip(x, y)

            # Check if sprite is outside of screen
            outside_of_screen_h = not (0 < self.rect.center[0] < SCREEN_SIZE[0])
            outside_of_screen_v = not (0 < self.rect.y < SCREEN_SIZE[1] - SPRITE_SIZE[1])
            outside_of_screen = outside_of_screen_h or outside_of_screen_v
            applies_to_sprite = not self.ignore_screen_boundaries
            if outside_of_screen and applies_to_sprite:
                self.rect.move_ip(-x, -y)

                # Change direction for computer controlled sprites
                if self.is_computer_controlled:
                    self.v_direction = change_direction(self.v_direction)
                    self.h_direction = change_direction(self.h_direction)
                break

            # Check for wall collision
            if self.collides(mine.layouts):
                climbed = False

                # Check if the sprite has fallen too far
                if self.fall_pix >= MAX_FALL_PIX and self.can_pass_out:
                    self.pass_out()

                # Reset fall distance count
                self.fall_pix = 0 if vertical else self.fall_pix

                # Try climbing up slope
                if self.is_walking() or self.is_idle():
                    for _ in range(CLIMBABLE_PIX):
                        self.rect.move_ip(0, -1)
                        if not self.collides(mine.layouts):
                            climbed = True
                            break
                    if climbed:
                        continue
                    else:
                        self.rect.move_ip(0, CLIMBABLE_PIX)

                # Stop the sprite or change direction if impossible to get passed obstacle
                self.rect.move_ip(-(one_pixel * i) if horizontal else 0, -y)
                if self.is_carrying_gold() and self.is_climbing():
                    activity = Activity.CLIMBING_WITH_GOLD
                elif self.is_climbing():
                    activity = Activity.CLIMBING
                    self.v_direction = \
                        change_direction(self.v_direction) if self.is_computer_controlled else self.v_direction
                elif self.is_carrying_gold():
                    activity = Activity.IDLE_WITH_GOLD
                elif self.is_passed_out():
                    activity = Activity.PASSED_OUT
                elif self.is_loaded():
                    activity = self.activity
                elif self.is_computer_controlled and self.is_walking():
                    self.h_direction = change_direction(self.h_direction)
                elif self.is_pushing_wheelbarrow():
                    activity = self.activity
                else:
                    activity = Activity.WALKING if self.is_miner else Activity.IDLE
                break

            # Keep track of how many pixels the sprite has fallen
            elif vertical and self.v_direction == Direction.DOWN and not (
                    self.collides(mine.ladders) and self.can_climb_ladders):
                self.fall_pix += 1
                if self.fall_pix >= self.max_control_while_falling_pix:
                    if self.is_passed_out():
                        activity = Activity.PASSED_OUT
                    elif self.is_carrying_gold():
                        activity = Activity.FALLING_WITH_GOLD
                    else:
                        activity = Activity.FALLING

        self.update(activity if activity else self.activity)

    def move_cc(self):
        """Move a computer controlled sprite"""

        # Get sprite position and size and calculate different movement possibilities
        y_pos = self.rect.y
        bottom_pos = self.rect.bottom - 1
        x_pos = self.rect.center[0]
        r_range = x_pos + SPRITE_SIZE[0]
        l_range = x_pos - SPRITE_SIZE[0]
        ladder_center = [l.rect.center[0] for l in mine.ladders.sprites() if l.collides(self)]
        ladder_center = ladder_center[0] if ladder_center else -10
        close_to_center = ladder_center in range(x_pos - self.speed, x_pos + self.speed)
        can_climb_ladder = close_to_center and not self.is_climbing() and not self.ladder_enter_selection

        # If the sprite is currently able to start climbing a ladder then make a random selection whether to start
        # climbing and if so, if what direction, or to keep walking
        if can_climb_ladder:
            random_no = random.randrange(0, 3)
            direction = {0: self.h_direction, 1: Direction.UP, 2: Direction.DOWN}[random_no]
            activity = {0: self.activity, 1: Activity.CLIMBING, 2: Activity.CLIMBING}[random_no]
            self.update(activity)
            self.h_direction = direction if random_no == 0 else self.h_direction
            self.v_direction = direction if random_no in (1, 2) else self.v_direction
            self.ladder_enter_selection = True
            self.just_entered_ladder = True if random_no > 0 else False
        elif not self.collides(mine.ladders):
            self.ladder_enter_selection = False

        # If the sprite is walking, then just keep walking
        if self.is_walking():
            self.move(self.h_direction)

        # If the sprite is currently climbing a ladder then look for points where the sprite can exit the ladder and
        # make a random selection whether to exit or keep climbing.
        elif self.is_climbing():

            # Check whether the sprite can exit the ladder from the current position by checking if the background
            # color in the room layout image to the left and right of the sprite is white.
            can_exit_left = can_exit_right = False
            if x_pos <= (SCREEN_SIZE[0]-SPRITE_SIZE[0]):
                top_right = [mine.layout_img.get_at([i, y_pos])[:3] for i in range(x_pos, r_range)]
                bottom_right = [mine.layout_img.get_at([i, bottom_pos])[:3] for i in range(x_pos, r_range)]
                down_right_diagonal = [mine.layout_img.get_at(z)[:3] for z in zip([i for i in range(
                    x_pos, x_pos + SPRITE_SIZE[0])], [n for n in range(y_pos, bottom_pos)])]
                up_right_diagonal = [mine.layout_img.get_at(z)[:3] for z in zip([i for i in range(
                    x_pos, x_pos + SPRITE_SIZE[0])], [n for n in range(bottom_pos, y_pos, -1)])]
                right_vertical = [
                    mine.layout_img.get_at([x_pos + SPRITE_SIZE[0], i])[:3] for i in range(y_pos, bottom_pos)]
                can_exit_right = all([
                    i == Color.WHITE for i in
                    top_right + up_right_diagonal + bottom_right + down_right_diagonal + right_vertical])
            if SPRITE_SIZE[0] <= x_pos:
                top_left = [mine.layout_img.get_at([i, y_pos])[:3] for i in range(l_range, x_pos)]
                bottom_left = [mine.layout_img.get_at([i, bottom_pos])[:3] for i in range(l_range, x_pos)]
                down_left_diagonal = [mine.layout_img.get_at(z)[:3] for z in zip([i for i in range(
                    x_pos - SPRITE_SIZE[0], x_pos)], [n for n in range(bottom_pos, y_pos, -1)])]
                up_left_diagonal = [mine.layout_img.get_at(z)[:3] for z in zip([i for i in range(
                    x_pos - SPRITE_SIZE[0], x_pos)], [n for n in range(y_pos, bottom_pos)])]
                left_vertical = [
                    mine.layout_img.get_at([x_pos - SPRITE_SIZE[0], i])[:3] for i in range(y_pos, bottom_pos)]
                can_exit_left = all([
                    i == Color.WHITE for i in
                    top_left + bottom_left + up_left_diagonal + down_left_diagonal + left_vertical])

            # Prevent the sprite from immediately exiting the ladder it just entered
            if self.just_entered_ladder and (can_exit_right or can_exit_left):
                can_exit_right = can_exit_left = False
            elif self.just_entered_ladder and not (can_exit_left or can_exit_right):
                self.just_entered_ladder = False

            # Make sure the sprite only gets to make one exit/keep climbing choice per exit
            if can_exit_right and not self.ladder_exit_selection[1]:
                self.ladder_exit_selection[1] = can_exit_right = True
            elif not can_exit_right:
                self.ladder_exit_selection[1] = can_exit_right = False
            if can_exit_left and not self.ladder_exit_selection[0]:
                self.ladder_exit_selection[0] = can_exit_left = True
            elif not can_exit_left:
                self.ladder_exit_selection[0] = can_exit_left = False

            # If it's possible to exit the ladder make a random selection and remember the selection for the current
            # position.
            if can_exit_left or can_exit_right:
                options = [0]
                options += [1] if can_exit_right else []
                options += [2] if can_exit_left else []
                random_no = random.randrange(0, len(options))
                option = options[random_no]
                direction = {0: self.v_direction, 1: Direction.RIGHT, 2: Direction.LEFT}[option]
                activity = {0: self.activity, 1: Activity.WALKING, 2: Activity.WALKING}[option]
                self.h_direction = direction if option > 0 else self.h_direction
                self.v_direction = direction if option == 0 else self.v_direction
                self.update(activity)
                if option > 0:
                    self.ladder_exit_selection = [False, False]
                    return

            self.move(self.v_direction)

    def update(self, activity=None):
        """
        Update the sprite status

        - activity -- (String. Optional. Defaults to None) The new activity to assign the sprite. If not provided
            animation will be unchanged.
        """
        # Static sprites can't be updated
        if self.is_static:
            return

        activity = self.activity if not activity else activity
        now = pygame.time.get_ticks()
        self.is_facing_down = self.v_direction == Direction.DOWN
        self.is_facing_left = self.h_direction == Direction.LEFT
        self.is_facing_right = self.h_direction == Direction.RIGHT
        self.is_facing_up = self.v_direction == Direction.UP

        # Kill sprite if it has expired
        if now >= self.expiration_ms and self.longevity_ms:
            self.kill()
            return

        # Check if the sprite activity has changed and if so change animation
        if activity != self.activity:
            self.animation = animation_loop(self.animations[activity])

            # Start the wake up timer if the sprite has passed out
            if activity == Activity.PASSED_OUT:
                self.wake_up_time = now + WAKE_UP_TIME_MS

        # Check if it's time to wake up the sprite from passed out state
        elif self.is_passed_out() and now >= self.wake_up_time:
            if self.is_computer_controlled and self.collides(mine.ladders):
                activity = Activity.CLIMBING
            elif self.is_computer_controlled:
                activity = Activity.WALKING
            else:
                activity = Activity.IDLE
            self.animation = animation_loop(self.animations[activity])
            self.immortality_timer = IMMORTAL_TIME if self.is_player else 0
            self.image_transparency_val = IMG_SEMI_TRANSPARENCY if self.is_player else IMG_FULLY_OPAQUE

        # Update immortality timer if sprite is in immortal state after waking up from passed out state
        if self.immortality_timer > 0:
            self.immortality_timer -= clock.get_time()
            self.image_transparency_val += IMG_TRANSPARENCY_INCREMENTATION
        else:
            self.immortality_timer = 0
            self.image_transparency_val = IMG_FULLY_OPAQUE

        # Load the next image in the animation
        if (now >= self.next_img) or (activity != self.activity):
            self.image = next(self.animation)
            self.next_img = now + self.animation_freq_ms
            self.image.set_colorkey(Color.WHITE)
            if self.is_facing_left:
                self.image = pygame.transform.flip(self.image, True, False)
            self.image.set_alpha(self.image_transparency_val)

        self.activity = activity

    def pass_out(self):
        """Make the sprite pass out, remove one life etc"""
        if self.is_passed_out():
            return
        if self.saved_sprite:
            self.drop_sprite()
        self.update(Activity.PASSED_OUT)
        self.lives -= 1 if self.is_mortal else 0

    def pick_up(self, sprites_group):
        """
        Pick up another sprite

        - sprites_group -- (Object. Mandatory) A sprites group to which the sprite you want to pick up belongs

        Returns: None
        """

        # You can't pick up a sprite if you're already carrying one
        if self.saved_sprite:
            return

        # Activities
        activity = None
        activities = {
            0: Activity.IDLE_WITH_EMPTY_WHEELBARROW, 1: Activity.IDLE_WITH_LOADED_01_WHEELBARROW,
            2: Activity.IDLE_WITH_LOADED_02_WHEELBARROW, 3: Activity.IDLE_WITH_LOADED_03_WHEELBARROW}

        # Pick up the correct sprite
        for sprite in sprites_group:
            if sprite.collides(self):
                self.saved_sprite = sprite
                sprite.remove(sprites_group)

                if sprite.is_gold_sack:
                    self.speed = self.slow_speed
                    self.carries_gold_sacks = 1
                    activity = Activity.IDLE_WITH_GOLD

                elif sprite.is_wheelbarrow:
                    activity = activities[sprite.carries_gold_sacks]
                    self.rect.x -= 120 if self.is_facing_left else 0

                break

        if activity:
            self.update(activity)

    def drop_sprite(self):
        """
        Drop a gold sack or a wheelbarrow

        Returns: None
        """

        # You can't drop a sprite if you're not carrying one
        if not self.saved_sprite:
            return

        # Set various start values
        carries_wheelbarrow = self.saved_sprite.is_wheelbarrow
        carries_gold = self.saved_sprite.is_gold_sack
        loaded_truck = {
            range(0, 3): Activity.LOADED_01, range(3, 6): Activity.LOADED_02, range(6, 9): Activity.LOADED_03,
            range(9, 12): Activity.LOADED_04, range(12, 1000): Activity.LOADED_05}
        loaded_wheelbarrow = {1: Activity.LOADED_01, 2: Activity.LOADED_02, 3: Activity.LOADED_03}
        dropped_in_truck = False
        dropped_in_wheelbarrow = False
        group = {carries_gold: mine.gold_sacks, carries_wheelbarrow: mine.wheelbarrows}[True]

        # Empty gold in the truck
        for t in mine.trucks.sprites():
            if t.collides(self) and not self.is_pushing_empty_wheelbarrow():
                t.carries_gold_sacks += self.saved_sprite.carries_gold_sacks if carries_wheelbarrow else 1
                mine.gold_delivered += self.saved_sprite.carries_gold_sacks if carries_wheelbarrow else 1
                t.update([loaded_truck[a] for a in loaded_truck if t.carries_gold_sacks in a][0])
                dropped_in_truck = True
                mine.bonus += int((
                    BONUS_POINTS * abs(mine.seconds_remaining / 100))
                    * (self.saved_sprite.carries_gold_sacks if carries_wheelbarrow else 1))
                break

        # Drop gold in a wheelbarrow
        if carries_gold:
            for w in mine.wheelbarrows.sprites():
                if w.collides(self) and w.carries_gold_sacks < 3 and not self.collides(mine.trucks):
                    w.carries_gold_sacks += 1
                    w.update(loaded_wheelbarrow[w.carries_gold_sacks])
                    dropped_in_wheelbarrow = True
                    break

        # Drop the sprite on the ground
        if not (dropped_in_wheelbarrow or dropped_in_truck):
            self.saved_sprite.rect.center = self.rect.center
            group.add(self.saved_sprite)
            if carries_wheelbarrow:
                self.saved_sprite.h_direction = self.h_direction
                self.saved_sprite.rect.x = self.rect.x
                self.rect.x += 120 if self.is_facing_left else 0
                self.saved_sprite.rect.y = self.rect.y

        # Reset sprite data
        if carries_wheelbarrow and dropped_in_truck:
            self.saved_sprite.update(Activity.IDLE)
            self.saved_sprite.carries_gold_sacks = 0
        self.update(Activity.IDLE_WITH_EMPTY_WHEELBARROW if dropped_in_truck and carries_wheelbarrow else Activity.IDLE)
        self.carries_gold_sacks = 0
        self.speed = self.standard_speed
        self.saved_sprite = self.saved_sprite if carries_wheelbarrow and dropped_in_truck else None

    def is_passed_out(self):
        return self.activity == Activity.PASSED_OUT

    def is_walking(self):
        return self.activity in (
            Activity.WALKING, Activity.WALKING_WITH_GOLD, Activity.PUSHING_EMPTY_WHEELBARROW,
            Activity.PUSHING_LOADED_01_WHEELBARROW, Activity.PUSHING_LOADED_02_WHEELBARROW,
            Activity.PUSHING_LOADED_03_WHEELBARROW)

    def is_climbing(self):
        return self.activity in (
            Activity.CLIMBING, Activity.CLIMBING_WITH_GOLD, Activity.IDLE_CLIMBING, Activity.IDLE_CLIMBING_WITH_GOLD)

    def is_falling(self):
        return self.activity in (Activity.FALLING, Activity.FALLING_WITH_GOLD)

    def is_idle(self):
        return self.activity in (
            Activity.IDLE, Activity.IDLE_CLIMBING_WITH_GOLD, Activity.IDLE_CLIMBING, Activity.IDLE_WITH_GOLD,
            Activity.IDLE_WITH_EMPTY_WHEELBARROW, Activity.IDLE_WITH_LOADED_01_WHEELBARROW,
            Activity.IDLE_WITH_LOADED_02_WHEELBARROW, Activity.IDLE_WITH_LOADED_03_WHEELBARROW)

    def is_carrying_gold(self):
        return self.activity in (
            Activity.WALKING_WITH_GOLD, Activity.IDLE_WITH_GOLD, Activity.IDLE_CLIMBING_WITH_GOLD,
            Activity.CLIMBING_WITH_GOLD, Activity.FALLING_WITH_GOLD)

    def is_pulling_up(self):
        return self.activity == Activity.PULLING_UP

    def is_pushing_empty_wheelbarrow(self):
        return self.activity in (Activity.PUSHING_EMPTY_WHEELBARROW, Activity.IDLE_WITH_EMPTY_WHEELBARROW)

    def is_pushing_loaded_01_wheelbarrow(self):
        return self.activity in (Activity.PUSHING_LOADED_01_WHEELBARROW, Activity.IDLE_WITH_LOADED_01_WHEELBARROW)

    def is_pushing_loaded_02_wheelbarrow(self):
        return self.activity in (Activity.PUSHING_LOADED_02_WHEELBARROW, Activity.IDLE_WITH_LOADED_02_WHEELBARROW)

    def is_pushing_loaded_03_wheelbarrow(self):
        return self.activity in (Activity.PUSHING_LOADED_03_WHEELBARROW, Activity.IDLE_WITH_LOADED_03_WHEELBARROW)

    def is_pushing_loaded_wheelbarrow(self):
        return self.is_pushing_loaded_01_wheelbarrow() or self.is_pushing_loaded_02_wheelbarrow() \
            or self.is_pushing_loaded_03_wheelbarrow()

    def is_pushing_wheelbarrow(self):
        return self.is_pushing_empty_wheelbarrow() or self.is_pushing_loaded_wheelbarrow()

    def is_loaded(self):
        return "loaded" in self.activity


class OnScreenTexts(object):

    def __init__(self, text, center=None, x=None, y=None, right=None, bottom=None, size=30):
        """
        Object for managing on-screen texts

        - text -- (String. Mandatory) The text to print
        - center -- (Integer. Optional. Defaults to None) Position of text
        - x -- (Integer. Optional. Defaults to None) Position of text
        - y -- (Integer. Optional. Defaults to None) Position of text
        - right -- (Integer. Optional. Defaults to None) Position of text
        - bottom -- (Integer. Optional. Defaults to None) Position of text
        - size -- (Integer. Optional. Defaults to 30) The font size
        """
        default_font = "comicsansms"
        font_name = default_font if default_font in pygame.font.get_fonts() else "freesansbold.ttf"
        self.font = pygame.font.SysFont(font_name, size)
        self.font.set_bold(True)
        self.original_text = text
        self.text = self.font.render(text, True, Color.GREEN)
        self.rect = self.text.get_rect()
        self.rect.center = center if center else self.rect.center
        self.rect.x = x if x else self.rect.x
        self.rect.y = y if y else self.rect.y
        self.rect.right = right if right else self.rect.right
        self.rect.bottom = bottom if bottom else self.rect.bottom

    def update(self, *args, get_rect=False):
        """Updates and returns a formatted copy of the original text"""
        self.text = self.font.render(self.original_text.format(*args), True, Color.GREEN)
        if get_rect:
            center = self.rect.center
            self.rect = self.text.get_rect()
            self.rect.center = center
        return self.text


# Enums
class Activity(object):
    CLIMBING = "climbing"
    CLIMBING_UP = "climbing_up"
    CLIMBING_DOWN = "climbing_down"
    CLIMBING_WITH_GOLD = "climbing_with_gold"
    FALLING = "falling"
    FALLING_WITH_GOLD = "falling_with_gold"
    IDLE = "idle"
    IDLE_CLIMBING = "idle_climbing"
    IDLE_CLIMBING_WITH_GOLD = "idle_climbing_with_gold"
    IDLE_WITH_EMPTY_WHEELBARROW = "idle_with_empty_wheelbarrow"
    IDLE_WITH_GOLD = "idle_with_gold"
    IDLE_WITH_LOADED_01_WHEELBARROW = "idle_with_loaded_01_wheelbarrow"
    IDLE_WITH_LOADED_02_WHEELBARROW = "idle_with_loaded_02_wheelbarrow"
    IDLE_WITH_LOADED_03_WHEELBARROW = "idle_with_loaded_03_wheelbarrow"
    LOADED_01 = "loaded_01"
    LOADED_02 = "loaded_02"
    LOADED_03 = "loaded_03"
    LOADED_04 = "loaded_04"
    LOADED_05 = "loaded_05"
    PASSED_OUT = "passed_out"
    PULLING_UP = "pulling_up"
    PUSHING_EMPTY_WHEELBARROW = "pushing_empty_wheelbarrow"
    PUSHING_LOADED_01_WHEELBARROW = "pushing_loaded_01_wheelbarrow"
    PUSHING_LOADED_02_WHEELBARROW = "pushing_loaded_02_wheelbarrow"
    PUSHING_LOADED_03_WHEELBARROW = "pushing_loaded_03_wheelbarrow"
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
    MINES = "mines" + os.sep
    SPRITES = IMAGES + "sprites" + os.sep
    TEXTURES = IMAGES + "textures" + os.sep
    CLIMBING_IMGS = SPRITES + "{}" + os.sep + "climbing" + os.sep
    CLIMBING_UP_IMGS = SPRITES + "{}" + os.sep + "climbing_up" + os.sep
    CLIMBING_DOWN_IMGS = SPRITES + "{}" + os.sep + "climbing_down" + os.sep
    CLIMBING_WITH_GOLD_IMGS = SPRITES + "{}" + os.sep + "climbing_with_gold" + os.sep
    IDLE_IMGS = SPRITES + "{}" + os.sep + "idle" + os.sep
    IDLE_CLIMBING_IMGS = SPRITES + "{}" + os.sep + "idle_climbing" + os.sep
    IDLE_CLIMBING_WITH_GOLD_IMGS = SPRITES + "{}" + os.sep + "idle_climbing_with_gold" + os.sep
    IDLE_WITH_EMPTY_WHEELBARROW_IMGS = SPRITES + "{}" + os.sep + "idle_with_empty_wheelbarrow" + os.sep
    IDLE_WITH_GOLD_IMGS = SPRITES + "{}" + os.sep + "idle_with_gold" + os.sep
    IDLE_WITH_LOADED_01_WHEELBARROW_IMGS = SPRITES + "{}" + os.sep + "idle_with_loaded_01_wheelbarrow" + os.sep
    IDLE_WITH_LOADED_02_WHEELBARROW_IMGS = SPRITES + "{}" + os.sep + "idle_with_loaded_02_wheelbarrow" + os.sep
    IDLE_WITH_LOADED_03_WHEELBARROW_IMGS = SPRITES + "{}" + os.sep + "idle_with_loaded_03_wheelbarrow" + os.sep
    LOADED_01 = SPRITES + "{}" + os.sep + "loaded_01" + os.sep
    LOADED_02 = SPRITES + "{}" + os.sep + "loaded_02" + os.sep
    LOADED_03 = SPRITES + "{}" + os.sep + "loaded_03" + os.sep
    LOADED_04 = SPRITES + "{}" + os.sep + "loaded_04" + os.sep
    LOADED_05 = SPRITES + "{}" + os.sep + "loaded_05" + os.sep
    PUSHING_EMPTY_WHEELBARROW_IMGS = SPRITES + "{}" + os.sep + "pushing_empty_wheelbarrow" + os.sep
    PUSHING_LOADED_01_WHEELBARROW_IMGS = SPRITES + "{}" + os.sep + "pushing_loaded_01_wheelbarrow" + os.sep
    PUSHING_LOADED_02_WHEELBARROW_IMGS = SPRITES + "{}" + os.sep + "pushing_loaded_02_wheelbarrow" + os.sep
    PUSHING_LOADED_03_WHEELBARROW_IMGS = SPRITES + "{}" + os.sep + "pushing_loaded_03_wheelbarrow" + os.sep
    PASSED_OUT_IMGS = SPRITES + "{}" + os.sep + "passed_out" + os.sep
    WALKING_IMGS = SPRITES + "{}" + os.sep + "walking" + os.sep
    WALKING_WITH_GOLD_IMGS = SPRITES + "{}" + os.sep + "walking_with_gold" + os.sep


class FileName(object):
    MINE_DB = Folder.MINES + "mine{}.json"
    PLACEHOLDER_IMG = Folder.IDLE_IMGS.format("placeholder") + "001.png"


class SpriteName(object):
    AXE = "axe"
    CART = "cart"
    ELEVATOR = "elevator"
    EXIT = "exit"
    GOLD = "gold"
    HANDLE = "handle"
    LADDER = "ladder"
    LAYOUT = "layout"
    PLACEHOLDER = "placeholder"
    PLAYER = "player"
    TRUCK = "truck"
    MINER = "miner"
    WARNING = "warning"
    WHEELBARROW = "wheelbarrow"


class Text(object):
    TITLE = "- GOLD THIEF -"
    LIVES = "Lives: {}"
    BONUS = "Bonus: {}"
    GAME_OVER = "GAME OVER"
    GAME_COMPLETED_01 = "WELL DONE!"
    GAME_COMPLETED_02 = "YOU'VE EMPTIED ALL THE MINES"
    GOLD_DELIVERED = "Gold delivered: {0}/{1}"
    PAUSED = "PAUSED"
    SECONDS_LEFT = "Time left: {}"
    START_SCREEN_01 = "GOLD THIEF"
    START_SCREEN_02 = "Press any key to start"
    MINE_COMPLETED_01 = "CONGRATULATIONS!"
    MINE_COMPLETED_02 = "MINE {} COMPLETED!"
    TOTAL_SCORE = "TOTAL SCORE: {}"
    SCORE = "SCORE: {} x {} x {} = {}"
    MINE_NO = "Mine: {}"
    OUT_OF_TIME = "TIME'S UP!"


# Load sprite animation images and store in a dict
SPRITE_ANIMATIONS = {
    SpriteName.GOLD: {
        Animation.IDLE: load_images(Animation.IDLE, SpriteName.GOLD),
        Animation.FALLING: load_images(Animation.IDLE, SpriteName.GOLD)},
    SpriteName.MINER: {
        Animation.CLIMBING: load_images(Animation.CLIMBING, SpriteName.MINER),
        Animation.FALLING: load_images(Animation.IDLE, SpriteName.MINER),
        Animation.IDLE: load_images(Animation.IDLE, SpriteName.MINER),
        Animation.PASSED_OUT: load_images(Animation.PASSED_OUT, SpriteName.MINER),
        Animation.WALKING: load_images(Animation.WALKING, SpriteName.MINER)},
    SpriteName.PLAYER: {
        Animation.CLIMBING: load_images(Animation.CLIMBING, SpriteName.PLAYER),
        Animation.CLIMBING_WITH_GOLD: load_images(Animation.CLIMBING_WITH_GOLD, SpriteName.PLAYER),
        Animation.FALLING: load_images(Animation.IDLE, SpriteName.PLAYER),
        Animation.FALLING_WITH_GOLD: load_images(Animation.IDLE_WITH_GOLD, SpriteName.PLAYER),
        Animation.IDLE: load_images(Animation.IDLE, SpriteName.PLAYER),
        Animation.IDLE_CLIMBING: load_images(Animation.IDLE_CLIMBING, SpriteName.PLAYER),
        Animation.IDLE_CLIMBING_WITH_GOLD: load_images(Animation.IDLE_CLIMBING_WITH_GOLD, SpriteName.PLAYER),
        Animation.IDLE_WITH_EMPTY_WHEELBARROW: load_images(
            Animation.IDLE_WITH_EMPTY_WHEELBARROW, SpriteName.PLAYER, multiply_x_by=2),
        Animation.IDLE_WITH_GOLD: load_images(Animation.IDLE_WITH_GOLD, SpriteName.PLAYER),
        Animation.IDLE_WITH_LOADED_01_WHEELBARROW: load_images(
            Animation.IDLE_WITH_LOADED_01_WHEELBARROW, SpriteName.PLAYER, multiply_x_by=2),
        Animation.IDLE_WITH_LOADED_02_WHEELBARROW: load_images(
            Animation.IDLE_WITH_LOADED_02_WHEELBARROW, SpriteName.PLAYER, multiply_x_by=2),
        Animation.IDLE_WITH_LOADED_03_WHEELBARROW: load_images(
            Animation.IDLE_WITH_LOADED_03_WHEELBARROW, SpriteName.PLAYER, multiply_x_by=2),
        Animation.PASSED_OUT: load_images(Animation.PASSED_OUT, SpriteName.PLAYER),
        Animation.PUSHING_EMPTY_WHEELBARROW: load_images(
            Animation.PUSHING_EMPTY_WHEELBARROW, SpriteName.PLAYER, multiply_x_by=2),
        Animation.PUSHING_LOADED_01_WHEELBARROW: load_images(
            Animation.PUSHING_LOADED_01_WHEELBARROW, SpriteName.PLAYER, multiply_x_by=2),
        Animation.PUSHING_LOADED_02_WHEELBARROW: load_images(
            Animation.PUSHING_LOADED_02_WHEELBARROW, SpriteName.PLAYER, multiply_x_by=2),
        Animation.PUSHING_LOADED_03_WHEELBARROW: load_images(
            Animation.PUSHING_LOADED_03_WHEELBARROW, SpriteName.PLAYER, multiply_x_by=2),
        Animation.WALKING: load_images(Animation.WALKING, SpriteName.PLAYER),
        Animation.WALKING_WITH_GOLD: load_images(Animation.WALKING_WITH_GOLD, SpriteName.PLAYER)},
    SpriteName.TRUCK: {
        Animation.IDLE: load_images(Animation.IDLE, SpriteName.TRUCK, multiply_x_by=4, multiply_y_by=4),
        Animation.LOADED_01: load_images(Animation.LOADED_01, SpriteName.TRUCK, multiply_x_by=4, multiply_y_by=4),
        Animation.LOADED_02: load_images(Animation.LOADED_02, SpriteName.TRUCK, multiply_x_by=4, multiply_y_by=4),
        Animation.LOADED_03: load_images(Animation.LOADED_03, SpriteName.TRUCK, multiply_x_by=4, multiply_y_by=4),
        Animation.LOADED_04: load_images(Animation.LOADED_04, SpriteName.TRUCK, multiply_x_by=4, multiply_y_by=4),
        Animation.LOADED_05: load_images(Animation.LOADED_05, SpriteName.TRUCK, multiply_x_by=4, multiply_y_by=4)},
    SpriteName.WARNING: {
        Animation.CLIMBING_UP: load_images(Animation.CLIMBING_UP, SpriteName.WARNING),
        Animation.CLIMBING_DOWN: load_images(Animation.CLIMBING_DOWN, SpriteName.WARNING),
        Animation.WALKING: load_images(Animation.WALKING, SpriteName.WARNING)},
    SpriteName.WHEELBARROW: {
        Animation.IDLE: load_images(Animation.IDLE, SpriteName.WHEELBARROW, multiply_x_by=2),
        Animation.FALLING: load_images(Animation.IDLE, SpriteName.WHEELBARROW, multiply_x_by=2),
        Animation.LOADED_01: load_images(Animation.LOADED_01, SpriteName.WHEELBARROW, multiply_x_by=2),
        Animation.LOADED_02: load_images(Animation.LOADED_02, SpriteName.WHEELBARROW, multiply_x_by=2),
        Animation.LOADED_03: load_images(Animation.LOADED_03, SpriteName.WHEELBARROW, multiply_x_by=2)}}

# Initialize PyGame
pygame.init()

# Instantiate clock and set game to running state
clock = pygame.time.Clock()
game_is_running = True
game_is_paused = False
show_start_screen = SHOW_START_SCREEN

# Load mine 1 and room 1
mine = Mines()
mine.set(START_MINE, 1)

# On-screen text
title = OnScreenTexts(Text.TITLE, center=(SCREEN_SIZE[0] // 2, 40))
lives = OnScreenTexts(Text.LIVES, x=SCREEN_SIZE[0] - 250, y=20)
gold_delivered = OnScreenTexts(Text.GOLD_DELIVERED, x=40, y=20)
paused = OnScreenTexts(Text.PAUSED, center=(SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2))
seconds_left = OnScreenTexts(Text.SECONDS_LEFT, x=40, y=60)
bonus = OnScreenTexts(Text.BONUS, x=SCREEN_SIZE[0] - 250, y=60)
mine_is_completed_01 = OnScreenTexts(
    Text.MINE_COMPLETED_01, center=(SCREEN_SIZE[0] / 2, (SCREEN_SIZE[1] / 2)-150))
mine_is_completed_02 = OnScreenTexts(
    Text.MINE_COMPLETED_02, center=(SCREEN_SIZE[0] / 2, (SCREEN_SIZE[1] / 2)-50), size=100)
score = OnScreenTexts(Text.SCORE, center=(SCREEN_SIZE[0] / 2, (SCREEN_SIZE[1] / 2)+50))
tot_score = OnScreenTexts(Text.TOTAL_SCORE, center=(SCREEN_SIZE[0] / 2, (SCREEN_SIZE[1] / 2)+150), size=50)
mine_no = OnScreenTexts(Text.MINE_NO, center=(SCREEN_SIZE[0] // 2, 80))
start_screen_01 = OnScreenTexts(Text.START_SCREEN_01, center=(SCREEN_SIZE[0] / 2, (SCREEN_SIZE[1] / 2)-50), size=100)
start_screen_02 = OnScreenTexts(Text.START_SCREEN_02, center=(SCREEN_SIZE[0] / 2, (SCREEN_SIZE[1] / 2)+50))
game_over_ = OnScreenTexts(Text.GAME_OVER, center=(SCREEN_SIZE[0] / 2, (SCREEN_SIZE[1] / 2)-50), size=100)
out_of_time = OnScreenTexts(Text.OUT_OF_TIME, center=(SCREEN_SIZE[0] / 2, (SCREEN_SIZE[1] / 2)-50), size=100)
game_completed_01 = OnScreenTexts(
    Text.GAME_COMPLETED_01, center=(SCREEN_SIZE[0] / 2, (SCREEN_SIZE[1] / 2)-50), size=100)
game_completed_02 = OnScreenTexts(Text.GAME_COMPLETED_02, center=(SCREEN_SIZE[0] / 2, (SCREEN_SIZE[1] / 2)+50))


# Warning sign sprites to be displayed when a miner might soon enter the room
warnings = pygame.sprite.Group()

########################################################################################################################
# MAIN LOOP
########################################################################################################################
while game_is_running:

    clock.tick(FPS)
    player_pressed_interact_key = False
    player_pressed_any_key = False
    mine.score = int((mine.seconds_remaining * mine.player.lives * mine.bonus))

    # Read events
    for event in pygame.event.get():

        # Check for quit or pause game request from user
        game_is_running = \
            not (event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE))
        game_is_paused = (not game_is_paused) and (event.type == pygame.KEYUP and event.key == pygame.K_p)

        # Check for specific key presses
        l_control = event.type == pygame.KEYUP and event.key == pygame.K_LCTRL
        l_alt = event.type == pygame.KEYUP and event.key == pygame.K_LALT
        space = event.type == pygame.KEYUP and event.key == pygame.K_SPACE
        r_control = event.type == pygame.KEYUP and event.key == pygame.K_RCTRL
        r_alt = event.type == pygame.KEYUP and event.key == pygame.K_RALT
        player_pressed_interact_key = any((l_control, l_alt, space, r_control, r_alt))
        player_pressed_any_key = event.type == pygame.KEYDOWN

    # Pause game
    if game_is_paused:
        screen.blit(paused.text, paused.rect)
        pygame.display.flip()
        continue

    # Check if player has collected all the gold in the mine
    if mine.is_completed():
        if player_pressed_any_key:
            mine.next()
        continue

    # Open the start screen
    if show_start_screen:
        show_start_screen = not player_pressed_any_key
        start_screen()
        continue

    # Check if time is up or player has no lives left
    if mine.is_game_over():
        game_over()
        if player_pressed_any_key:
            mine.reset(START_MINE)
        continue

    # Check if the player has completed the whole game
    if mine.is_game_completed():
        if player_pressed_any_key:
            mine.scores = {}
            mine.game_completed = False
            show_start_screen = True
        continue

    # Read key presses and move the player
    key_presses(player_pressed_interact_key)

    # Move miners and apply gravity to all applicable sprites
    move_sprites()

    # Check if the player is caught by a miner
    get_caught()

    # Check if the player exits the room
    exit_room(mine.exits.sprites(), mine.players.sprites())

    # Check if a miner is hit by a falling gold sack
    hit_miner()

    # Draw background and walls
    screen.blit(mine.background_img, (0, 0))
    screen.blit(mine.texture_img, (0, 0))

    # Draw sprites
    for s in mine.all_sprites:
        s.draw(screen)
    warnings.draw(screen)
    mine.players.draw(screen)

    # Update remaining time
    mine.seconds_remaining -= clock.get_time() / 1000

    # Draw text
    screen.blit(lives.update(mine.player.lives), lives.rect)
    screen.blit(gold_delivered.update(mine.gold_delivered, mine.no_of_gold_sacks), gold_delivered.rect)
    screen.blit(seconds_left.update(int(mine.seconds_remaining)), seconds_left.rect)
    screen.blit(bonus.update(mine.bonus), bonus.rect)
    screen.blit(title.text, title.rect)
    screen.blit(mine_no.update(mine.mine), mine_no.rect)

    # Update the screen
    pygame.display.flip()
