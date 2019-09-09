import pygame
import itertools

pygame.init()


class Sprite(pygame.sprite.Sprite):

    def __init__(self, image):

        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load(image)
        self.image.set_colorkey(WHITE)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()


# Set screen size and create a screen object
SCREEN_SIZE = (750, 500)
screen = pygame.display.set_mode(SCREEN_SIZE)

# COLOR CONSTANTS (SHOULD BE ENUM!)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

#background = pygame.image.load("background1.png")
game_is_running = True
background_img = pygame.image.load("pattern1.jpg")
walls_img = pygame.image.load("background1.png")
walls_img.set_colorkey(BLACK)
pattern = pygame.image.load("pattern2.jpg")
#merged = walls_img.copy()
pattern.blit(walls_img, (0, 0))
pattern.set_colorkey(WHITE)
walls = Sprite("background1.png")
walls.rect.x = walls.rect.y = 0
player = Sprite("robot1.png")
player.rect.x = 100
player.rect.y = 150
block = Sprite("robot2.png")
block.rect.x = 400
block.rect.y = 200
blocks = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
blocks.add(block)
walls_group = pygame.sprite.Group()
walls_group.add(walls)
for s in (player, block):
    all_sprites.add(s)

###########
# MAIN LOOP
###########
while game_is_running:
    for event in pygame.event.get():
        game_is_running = \
            not (event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE))

    key_press = pygame.key.get_pressed()
    if key_press[pygame.K_DOWN]:
        player.rect.y += 1
    elif key_press[pygame.K_UP]:
        player.rect.y -= 1
    if key_press[pygame.K_RIGHT]:
        player.rect.x += 1
    elif key_press[pygame.K_LEFT]:
        player.rect.x -= 1

    if pygame.sprite.spritecollide(player, blocks, False, pygame.sprite.collide_mask):
        print("sprites have collided!")
    if pygame.sprite.spritecollide(player, walls_group, False, pygame.sprite.collide_mask):
        print("Player hit a wall")

    screen.blit(background_img, (0, 0))
    #screen.fill(WHITE)
    walls_group.draw(screen)
    screen.blit(pattern, (0, 0))
    #x = pygame.transform.chop(screen, walls.mask)

    all_sprites.draw(screen)
    pygame.display.flip()
