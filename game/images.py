from os.path import join
from .config import SPRITE_SHEET_DIR, IMAGES_DIR

PLAYER_SPRITE_SHEET = join(SPRITE_SHEET_DIR, 'player_sprites.png')
ZOMBIE_SPRITE_SHEET = join(SPRITE_SHEET_DIR, 'zombies.png')
EXPLOSION_SPRITE_SHEET = join(SPRITE_SHEET_DIR, 'explosion.png')

BULLET_ICON = join(IMAGES_DIR, 'objects/bullet_icon.png')

KEY_IMAGE = join(IMAGES_DIR, 'objects/key.png')
HEALTH_PACK_IMAGE = join(IMAGES_DIR, 'objects/health_pack.png')
XP_IMAGE = join(IMAGES_DIR, 'objects/xp.png')
COIN_IMAGES = [join(IMAGES_DIR, sound) for sound in ['objects/coins/coin_0.png',
                                                     'objects/coins/coin_1.png',
                                                     'objects/coins/coin_2.png',
                                                     'objects/coins/coin_3.png',
                                                     'objects/coins/coin_4.png',
                                                     'objects/coins/coin_5.png',
                                                     'objects/coins/coin_6.png',
                                                     'objects/coins/coin_7.png']]

DOOR_LOCKED_IMAGE = join(IMAGES_DIR, 'objects/door/door_locked.png')
DOOR_UNLOCKED_IMAGE = join(IMAGES_DIR, 'objects/door/door_unlocked.png')
DOOR_OPEN_IMAGE = join(IMAGES_DIR, 'objects/door/door_open.png')

DOOR_SWITCH_DISABLED_IMAGE = join(IMAGES_DIR, 'objects/door switch/switch_disabled.png')
DOOR_SWITCH_ENABLED_IMAGE = join(IMAGES_DIR, 'objects/door switch/switch_enabled.png')

SAW_IMAGE = join(IMAGES_DIR, 'objects/saw.png')

LASER_MACHINE_DOWN_SHOOT_IMAGE = join(IMAGES_DIR, 'objects/laser_machine/laser_machine_down_shoot.png')
LASER_MACHINE_DOWN_OFF_IMAGE = join(IMAGES_DIR, 'objects/laser_machine/laser_machine_down_off.png')
LASER_MACHINE_RIGHT_SHOOT_IMAGE = join(IMAGES_DIR, 'objects/laser_machine/laser_machine_right_shoot.png')
LASER_MACHINE_RIGHT_OFF_IMAGE = join(IMAGES_DIR, 'objects/laser_machine/laser_machine_right_off.png')
LASER_MACHINE_LEFT_SHOOT_IMAGE = join(IMAGES_DIR, 'objects/laser_machine/laser_machine_left_shoot.png')
LASER_MACHINE_LEFT_OFF_IMAGE = join(IMAGES_DIR, 'objects/laser_machine/laser_machine_left_off.png')

RED_LASER_IMAGE = join(IMAGES_DIR, 'objects/laser_beam/red_vertical.png')
BLUE_LASER_IMAGE = join(IMAGES_DIR, 'objects/laser_beam/blue_vertical.png')
GREEN_LASER_IMAGE = join(IMAGES_DIR, 'objects/laser_beam/green_horizontal.png')
YELLOW_LASER_IMAGE = join(IMAGES_DIR, 'objects/laser_beam/yellow_horizontal.png')
LASER_BULLET_IMAGE = join(IMAGES_DIR, 'objects/laser_beam/purple_laser_bullet.png')

LASER_RECEIVER_IMAGE = join(IMAGES_DIR, 'objects/laser_machine/laser_receiver.png')

RED_LEVER_ON_IMAGE = join(IMAGES_DIR, 'objects/lever/red_lever_on.png')
RED_LEVER_OFF_IMAGE = join(IMAGES_DIR, 'objects/lever/red_lever_off.png')
BLUE_LEVER_ON_IMAGE = join(IMAGES_DIR, 'objects/lever/blue_lever_on.png')
BLUE_LEVER_OFF_IMAGE = join(IMAGES_DIR, 'objects/lever/blue_lever_off.png')
GREEN_LEVER_ON_IMAGE = join(IMAGES_DIR, 'objects/lever/green_lever_on.png')
GREEN_LEVER_OFF_IMAGE = join(IMAGES_DIR, 'objects/lever/green_lever_off.png')
YELLOW_LEVER_ON_IMAGE = join(IMAGES_DIR, 'objects/lever/yellow_lever_on.png')
YELLOW_LEVER_OFF_IMAGE = join(IMAGES_DIR, 'objects/lever/yellow_lever_off.png')

SPLAT_IMAGES = [join(IMAGES_DIR, splat) for splat in ['splat/splat_0.png',
                                                      'splat/splat_1.png',
                                                      'splat/splat_2.png',
                                                      'splat/splat_3.png',
                                                      'splat/splat_4.png',
                                                      'splat/splat_5.png',
                                                      'splat/splat_6.png']]

VOLUME_UP_IMG = join(IMAGES_DIR, 'menu_images/volume/vol_up.png')
VOLUME_UP_HOVER_IMG = join(IMAGES_DIR, 'menu_images/volume/vol_up_hover.png')
VOLUME_DOWN_IMG = join(IMAGES_DIR, 'menu_images/volume/vol_down.png')
VOLUME_DOWN_HOVER_IMG = join(IMAGES_DIR, 'menu_images/volume/vol_down_hover.png')
ERROR_IMG = join(IMAGES_DIR, 'menu_images/volume/error.png')

MUTE_IMG = join(IMAGES_DIR, 'menu_images/volume/mute.png')
MUTE_HOVER_IMG = join(IMAGES_DIR, 'menu_images/volume/mute_hover.png')
UN_MUTE_IMG = join(IMAGES_DIR, 'menu_images/volume/un_mute.png')
UN_MUTE_HOVER_IMG = join(IMAGES_DIR, 'menu_images/volume/un_mute_hover.png')

VOLUME_INDICATOR_IMAGE = join(IMAGES_DIR, 'menu_images/volume/volume_indicator.png')

SWITCH_ON_IMG = join(IMAGES_DIR, 'menu_images/switches/on.png')
SWITCH_ON_HOVER_IMG = join(IMAGES_DIR, 'menu_images/switches/on_hover.png')
SWITCH_OFF_IMG = join(IMAGES_DIR, 'menu_images/switches/off.png')
SWITCH_OFF_HOVER_IMG = join(IMAGES_DIR, 'menu_images/switches/off_hover.png')
