from os.path import join
from .config import MUSIC_DIR, MENU_SOUNDS_DIR, PLAYER_SOUNDS_DIR, ZOMBIE_SOUNDS_DIR, SFX_DIR


def play_sound(sound_on, sound, volume=None) -> None:
    """
    Play sound if turned on.
    :param sound_on: check if it's turned on in settings
    :param sound: sound to play
    :param volume: sound volume
    """
    if sound_on:
        if volume:
            sound.set_volume(volume)
        else:
            sound.set_volume(sound.get_volume())
        if sound.get_num_channels() > 1:
            sound.stop()
        sound.play()


# ========== SOUNDS ==========
BG_MUSIC = join(MUSIC_DIR, 'game_music.ogg')

# menu sounds
HIGH_SCORE_SOUND = join(SFX_DIR, 'high_score.ogg')
MENU_MUSIC = join(MUSIC_DIR, 'menu_music.ogg')
MENU_IN_SOUND = join(MENU_SOUNDS_DIR, 'menu_in.ogg')
MENU_OUT_SOUND = join(MENU_SOUNDS_DIR, 'menu_out.ogg')
SWITCH_TOGGLE_SOUND = join(MENU_SOUNDS_DIR, 'toggle.ogg')
GAME_OVER_MUSIC = join(MUSIC_DIR, 'game_over_music.ogg')

# player sounds
PLAYER_HIT_SOUND = join(PLAYER_SOUNDS_DIR, 'hit/player_hit.ogg')
PLAYER_JUMP_SOUND = join(PLAYER_SOUNDS_DIR, 'jump/player_jump.ogg')
GUN_SOUND = join(SFX_DIR, 'gun.ogg')

# mob sounds
ZOMBIE_MOAN_SOUNDS = [join(ZOMBIE_SOUNDS_DIR, sound) for sound in ['moan/zombie_brains1.ogg',
                                                                   'moan/zombie_brains2.ogg',
                                                                   'moan/zombie_roar_1.ogg',
                                                                   'moan/zombie_roar_2.ogg',
                                                                   'moan/zombie_roar_3.ogg',
                                                                   'moan/zombie_roar_5.ogg',
                                                                   'moan/zombie_roar_6.ogg',
                                                                   'moan/zombie_roar_7.ogg',
                                                                   'moan/zombie_roar_8.ogg']]
ZOMBIE_HIT_SOUND = join(ZOMBIE_SOUNDS_DIR, 'hit/zombie_hit.ogg')
ZOMBIE_DIE_SOUND = join(ZOMBIE_SOUNDS_DIR, 'die/zombie_die.ogg')

# sound effects
LEVEL_START_SOUND = join(SFX_DIR, 'level_start.ogg')
DOOR_SWITCH_PRESS_SOUND = join(SFX_DIR, 'door_switch_press.ogg')
DOOR_SWITCH_FAIL_SOUND = join(SFX_DIR, 'door_switch_fail.ogg')
DOOR_OPEN_SOUND = join(SFX_DIR, 'door_open.ogg')
XP_PICKUP_SOUND = join(SFX_DIR, 'xp_pickup.ogg')
KEY_PICKUP_SOUND = join(SFX_DIR, 'key_pickup_sound.ogg')
HEALTH_PICKUP_SOUND = join(SFX_DIR, 'health_pack.ogg')
COIN_PICKUP_SOUND = join(SFX_DIR, 'coin_pickup.ogg')
LEVER_PULL_SOUND = join(SFX_DIR, 'lever_pull.ogg')
LASER_GUN_SOUND = join(SFX_DIR, 'laser_gun.ogg')
LASER_SOUND = join(SFX_DIR, 'laser.ogg')
BURN_SOUND = join(SFX_DIR, 'burn_sound.ogg')
SAW_SOUND = join(SFX_DIR, 'saw.ogg')
EXPLOSION_SOUND = join(SFX_DIR, 'explosion.ogg')
