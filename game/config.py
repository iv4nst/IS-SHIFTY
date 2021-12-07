from os.path import dirname, join

# directories
BASE_DIR = dirname(__file__)

ASSETS_DIR = join(BASE_DIR, 'assets')
FONTS_DIR = join(BASE_DIR, 'assets/fonts')
MAP_DIR = join(BASE_DIR, 'assets/map')

SPRITE_SHEET_DIR = join(BASE_DIR, 'assets/spritesheet')
IMAGES_DIR = join(BASE_DIR, 'assets/images')
MUSIC_DIR = join(BASE_DIR, 'assets/audio/music')
MENU_SOUNDS_DIR = join(BASE_DIR, 'assets/audio/snd/menu')
PLAYER_SOUNDS_DIR = join(BASE_DIR, 'assets/audio/snd/player')
ZOMBIE_SOUNDS_DIR = join(BASE_DIR, 'assets/audio/snd/mob')
SFX_DIR = join(BASE_DIR, 'assets/audio/snd/sfx')

# ========== GENERAL SETTINGS ==========
GAME_TITLE = 'IS-Shifty'
VERSION = 'v1.1'

WIDTH = 1920
HEIGHT = 1080

FPS = 60
TARGET_FPS = 60

SETTINGS_FILE = join(BASE_DIR, 'settings.json')

# ========== FONTS ==========
TITLE_FONT = join(FONTS_DIR, 'ZOMBIE.TTF')
FONT = join(FONTS_DIR, 'Impacted2.0.TTF')

# ========== MAPS ==========
MAP1 = join(MAP_DIR, 'map_1.tmx')
MAP2 = join(MAP_DIR, 'map_2.tmx')
MAP3 = join(MAP_DIR, 'map_3.tmx')

# ========== COLORS ==========
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GREY = (204, 204, 204)
DARK_GREY = (33, 35, 33)
TILE_COLOR = (56, 61, 80)
SUBMENU_GREY = (53, 55, 53)
PAUSE_COLOR = (0, 0, 0, 180)

# ========== SPRITES SETTINGS ==========
GRAVITY = 0.8

# player
PLAYER_HEALTH = 100
PLAYER_ACC = 0.45
PLAYER_FRICTION = -0.12  # negative number to slow down the player
PLAYER_JUMP = 15.5
GUN_COOL_DOWN = 100
GUN_COOL_DOWN_DECREASE_SPEED = 12
GUN_COOL_DOWN_INCREASE_SPEED = 0.15

# bullet
BARREL_OFFSET_R = (40, -27)
BARREL_OFFSET_WALKING_R = (50, -20)
BARREL_OFFSET_L = (1, -27)
BARREL_OFFSET_WALKING_L = (1, -20)
BULLET_SPEED = 5
BULLET_DAMAGE = 15
BULLET_UPGRADED_DAMAGE = 20
BULLET_RATE = 250
BULLET_LIFETIME = 1000

# zombie
ZOMBIE_ACC = 0.1
ZOMBIE_FRICTION = -0.12
ZOMBIE_HEALTH = 100
ZOMBIE_KNOCK_BACK = 10
ZOMBIE_DETECT_RADIUS = 170
ZOMBIE_DAMAGE = 10
ZOMBIE_MAX_SPEED = 0.4
ZOMBIE_RANDOM_TARGET_TIME = (4000, 7000)

# acid
ACID_DAMAGE = 35

# spikes
SPIKES_DAMAGE = 15

# saw
SAW_DAMAGE = 30
SAW_HEALTH = 16
SAW_SPEED = 1
SAW_KNOCK_BACK = (1, 1)

# laser
LASER_DAMAGE = 1
LASER_BULLET_SPEED = 5
LASER_BULLET_DAMAGE = 10
LASER_BULLET_FREQUENCY = (1000, 5000)
LASER_MACHINE_HEALTH = 20

# items
HEALTH_PACK_AMOUNT = 25
BOB_RANGE = 15
BOB_SPEED = 0.4

# points
COIN_POINTS = 25
XP_POINTS = 250
ZOMBIE_POINTS = 200
SAW_POINTS = 300
LASER_MACHINE_POINTS = 500
KEY_PICKUP_POINTS = 150
DOOR_SWITCH_POINTS = 100
NEXT_LEVEL_POINTS = 750
GAME_COMPLETED_POINTS = 5000

# layers - higher number is drawn over the lower one
LAYERS = {
    'first': 1,
    'second': 2,
    'third': 3,
    'fourth': 4,
    'fifth': 5
}

# effects
DAMAGE_ALPHA = [i for i in range(0, 255, 25)]
FLASH_DURATION = 40
EXPLOSION_DURATION = 800
