from . import pg, vec
from .config import *
from .images import *
from .sounds import play_sound

from pygame.transform import flip, scale
from random import randint, choice, random
from itertools import chain
from pytweening import easeInOutSine


# sprites
class Player(pg.sprite.Sprite):
    """
    Creates player sprite.
    Player position is set in Tiled editor.
    """

    def __init__(self, game, x: float, y: float):
        """
        Make the player.
        :param game: game
        :param x: X position to spawn
        :param y: Y position to spawn
        """
        self._layer = LAYERS['second']
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.main_menu = self.game.main_menu

        # load player data
        self.__load_data()

        # player image (starting)
        self.image = self.__idle_frames_right[0]
        self.rect = self.image.get_rect()

        # movement vectors
        self.__pos = vec(x, y)
        self.__vel = vec(0, 0)
        self.__acc = vec(0, 0)

        self.__health = PLAYER_HEALTH
        self.__dead_message = ''  # for game over messages

        self.__has_key = False  # key for door switch
        self.__score = 0

        # animations
        self.__FACING_RIGHT = True
        self.__walking = False
        self.__jumping = False
        self.__on_ground = False
        self.__sliding = False
        self.__sliding_counter = 0  # for auto-sliding
        self.__current_frame = 0
        self.__last_update = 0

        # attacking
        self.__shooting = False
        self.__walking_shooting = False
        self.__in_acid = False  # prevents shooting if in acid
        self.__last_shot = 0
        self.__gun_cool_down = GUN_COOL_DOWN
        self.__can_shoot = True  # prevents shooting if gun not cooled down

    def update(self) -> None:
        """
        Update player sprite.
        """
        self.__check_shooting()
        self.__process_animations()
        self.__process_movement()
        self.__check_collisions()
        self.__check_gun_cool_down()

        # player die
        if self.__health <= 0:
            # player explosion (game over)
            Explosion(self.game, self.__pos + (20, -20), self)
            self.main_menu.save_scores(self.__score)  # save score

    def __process_animations(self) -> None:
        """
        Animate player sprite.
        """
        now = pg.time.get_ticks()

        # walking/not walking
        if self.__vel.x != 0:
            self.__walking = True
        else:
            self.__walking = False

        # idle
        if self.__on_ground and not self.__walking:
            if now - self.__last_update > 90:
                self.__last_update = now
                self.__current_frame = (self.__current_frame + 1) % len(self.__idle_frames_right)
                bottom = self.rect.bottom
                if self.__FACING_RIGHT:
                    self.image = self.__idle_frames_right[self.__current_frame]
                else:
                    self.image = self.__idle_frames_left[self.__current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        # walking
        if self.__walking and not self.__jumping:
            if now - self.__last_update > 100:
                self.__last_update = now
                self.__current_frame = (self.__current_frame + 1) % len(self.__run_frames_right)
                bottom = self.rect.bottom
                if self.__vel.x > 0:  # run right
                    self.image = self.__run_frames_right[self.__current_frame]
                else:  # run left
                    self.image = self.__run_frames_left[self.__current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        # walking & jumping
        if self.__walking and self.__jumping:
            if now - self.__last_update > 100:
                self.__last_update = now
                self.__current_frame = (self.__current_frame + 1) % len(self.__jump_frames_right)
                bottom = self.rect.bottom
                if self.__vel.x > 0:  # run right
                    self.image = self.__jump_frames_right[self.__current_frame]
                else:  # run left
                    self.image = self.__jump_frames_left[self.__current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        # jumping (only)
        if self.__jumping and not self.__shooting:
            if now - self.__last_update > 100:
                self.__last_update = now
                self.__current_frame = (self.__current_frame + 1) % len(self.__jump_frames_right)
                if self.__FACING_RIGHT:
                    self.image = self.__jump_frames_right[self.__current_frame]
                else:
                    self.image = self.__jump_frames_left[self.__current_frame]
                self.rect = self.image.get_rect()

        # jumping & shooting
        if self.__jumping and self.__shooting:
            if now - self.__last_update > 80:
                self.__last_update = now
                bottom = self.rect.bottom
                self.__current_frame = (self.__current_frame + 1) % len(self.__jump_shoot_frames_right)
                if self.__FACING_RIGHT:
                    self.image = self.__jump_shoot_frames_right[self.__current_frame]
                else:
                    self.image = self.__jump_shoot_frames_left[self.__current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        # shooting
        if self.__shooting and not self.__walking:
            if now - self.__last_update > 70:
                self.__last_update = now
                bottom = self.rect.bottom
                self.__current_frame = (self.__current_frame + 1) % len(self.__shooting_frames_right)
                if self.__FACING_RIGHT:
                    self.image = self.__shooting_frames_right[self.__current_frame]
                else:
                    self.image = self.__shooting_frames_left[self.__current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        # walking & shooting
        if self.__walking and self.__shooting and not self.__jumping:
            self.__walking_shooting = True
            if now - self.__last_update > 80:
                self.__last_update = now
                bottom = self.rect.bottom
                self.__current_frame = (self.__current_frame + 1) % len(self.__run_shoot_frames_right)
                if self.__FACING_RIGHT:
                    self.image = self.__run_shoot_frames_right[self.__current_frame]
                else:
                    self.image = self.__run_shoot_frames_left[self.__current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        else:
            self.__walking_shooting = False

        # sliding
        if self.__sliding:
            if now - self.__last_update > 50:
                self.__last_update = now
                bottom = self.rect.bottom
                self.__current_frame = (self.__current_frame + 1) % len(self.__sliding_frames_right)
                self.__sliding_counter += 1  # increment sliding counter (auto sliding)
                if self.__FACING_RIGHT:
                    self.image = self.__sliding_frames_right[self.__current_frame]
                else:
                    self.image = self.__sliding_frames_left[self.__current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

                # stop sliding
                if self.__sliding_counter >= 10:
                    self.__sliding = False
                    self.__sliding_counter = 0

        # set the position of sprite
        self.rect.midbottom = self.__pos  # fix the bug where the player disappears

        # for precise collisions
        self.mask = pg.mask.from_surface(self.image)

    # ===== Load player data =====
    def __load_data(self) -> None:
        """
        Load all player data.
        Images, controls, sounds & sounds settings.
        """
        self.__load_images()
        self.__load_controls()
        self.__load_sounds()

    def __load_images(self) -> None:
        """
        Load all player related images.
        """
        # access player sprite sheet
        load_img = self.game.player_sprite_sheet.parse_sprite

        # idle
        self.__idle_frames_right = [load_img('idle_{}.png'.format(i)) for i in range(10)]
        self.__idle_frames_left = [flip(img, True, False) for img in self.__idle_frames_right]

        # jump
        self.__jump_frames_right = [load_img('jump_{}.png'.format(i)) for i in range(10)]
        self.__jump_frames_left = [flip(img, True, False) for img in self.__jump_frames_right]

        # falling
        self.__falling_frames_right = [self.__jump_frames_right[6], self.__jump_frames_right[7],
                                       self.__jump_frames_right[8]]
        self.__falling_frames_left = [flip(img, True, False) for img in self.__falling_frames_right]

        # jump shoot
        self.__jump_shoot_frames_right = [load_img('jump_shoot_{}.png'.format(i)) for i in range(5)]
        self.__jump_shoot_frames_left = [flip(img, True, False) for img in self.__jump_shoot_frames_right]

        # run
        self.__run_frames_right = [load_img('run_{}.png'.format(i)) for i in range(8)]
        self.__run_frames_left = [flip(img, True, False) for img in self.__run_frames_right]

        # run shoot
        self.__run_shoot_frames_right = [load_img('run_shoot_{}.png'.format(i)) for i in range(9)]
        self.__run_shoot_frames_left = [flip(img, True, False) for img in self.__run_shoot_frames_right]

        # shooting
        self.__shooting_frames_right = [load_img('shoot_{}.png'.format(i)) for i in range(4)]
        self.__shooting_frames_left = [flip(img, True, False) for img in self.__shooting_frames_right]

        # sliding
        self.__sliding_frames_right = [load_img('slide_{}.png'.format(i)) for i in range(10)]
        self.__sliding_frames_left = [flip(img, True, False) for img in self.__sliding_frames_right]

    def __load_sounds(self) -> None:
        """
        Load player sounds and sounds settings.
        """
        # settings
        self.__jump_sound_on = self.main_menu.player_jump_sound_on
        self.__hit_sound_on = self.main_menu.player_hit_sound_on
        self.__gun_sound_on = self.main_menu.gun_sound_on
        self.__burn_sound_on = self.main_menu.burn_sound_on
        self.__health_pickup_sound_on = self.main_menu.health_pickup_sound_on
        self.__xp_coin_sound_on = self.main_menu.xp_coin_sound_on
        self.__key_pickup_sound_on = self.main_menu.key_pickup_sound_on

        # sounds
        self.__jump_sound = self.main_menu.player_jump_sound
        self.__hit_sound = self.main_menu.player_hit_sound
        self.__gun_sound = self.main_menu.gun_sound
        self.__burn_sound = self.main_menu.burn_sound
        self.__health_pickup_sound = self.main_menu.health_pickup_sound
        self.__xp_pickup_sound = self.main_menu.xp_pickup_sound
        self.__coin_pickup_sound = self.main_menu.coin_pickup_sound
        self.__key_pickup_sound = self.main_menu.key_pickup_sound

    def __load_controls(self) -> None:
        """
        Load controls from main menu (settings.json) and convert them to integer (unicode).
        """
        self.__jump_key = ord(self.main_menu.jump_key)
        self.__right_key = ord(self.main_menu.right_key)
        self.__left_key = ord(self.main_menu.left_key)
        self.__slide_key = ord(self.main_menu.slide_key)
        self.__shoot_key = ord(self.main_menu.shoot_key)
        self.__interact_key = ord(self.main_menu.interact_key)
        self.__open_key = ord(self.main_menu.open_key)

    # getters
    def get_pos(self) -> vec:
        """
        Get position vector.
        :return: position vector
        """
        return self.__pos

    def get_acc(self) -> vec:
        """
        Get acceleration vector.
        :return: acceleration vector
        """
        return self.__acc

    def get_vel(self) -> vec:
        """
        Get velocity vector.
        :return: velocity vector
        """
        return self.__vel

    def get_control_key(self, control: str) -> int:
        """
        Get key associated with control provided as parameter.
        :param control: desired control
        :return: key corresponding to that control
        """
        key = ''
        if control.lower() == 'jump':
            key = self.__jump_key
        elif control.lower() == 'right':
            key = self.__right_key
        elif control.lower() == 'left':
            key = self.__left_key
        elif control.lower() == 'slide':
            key = self.__slide_key
        elif control.lower() == 'shoot':
            key = self.__shoot_key
        elif control.lower() == 'interact':
            key = self.__interact_key
        elif control.lower() == 'open':
            key = self.__open_key

        return key

    def get_health(self) -> int:
        """
        Get health.
        :return: player health
        """
        return self.__health

    def get_score(self) -> int:
        """
        Get score.
        :return: player score
        """
        return self.__score

    def get_dead_message(self) -> str:
        """
        Get player's cause of death (dead message).
        :return: dead message
        """
        return self.__dead_message

    # health
    def keep_health(self, health: int) -> None:
        """
        Keep player health in next levels.
        Keep health value between 1 and 100.
        :param health: health to keep
        """
        if health > PLAYER_HEALTH or health <= 0:
            health = PLAYER_HEALTH
        self.__health = health

    def __add_health(self) -> None:
        """
        Add health to player.
        """
        self.__health += HEALTH_PACK_AMOUNT
        play_sound(self.__health_pickup_sound_on, self.__health_pickup_sound)

        # prevent from going over 100
        if self.__health > PLAYER_HEALTH:
            self.__health = PLAYER_HEALTH

    def hurt(self, damage: int) -> None:
        """
        Reduce health by amount of damage.
        :param damage: damage amount
        """
        self.__health -= damage

    def set_dead_message(self, message: str) -> None:
        """
        Set message to display when player dies.
        :param message: message to display
        """
        if self.__health <= 0:
            self.__dead_message = message.lower()

    # score
    def keep_score(self, score: int) -> None:
        """
        Keep player score in next levels.
        Score can't be negative.
        :param score: score to keep
        """
        if score < 0:
            score = 0
        self.__score = score

    def add_points(self, points: int) -> None:
        """
        Add points to player's score.
        :param points: amount of points
        """
        self.__score = self.get_score() + points

    # shooting
    def __check_shooting(self) -> None:
        """
        Get pressed key.
        """
        keys = pg.key.get_pressed()
        if keys[self.__shoot_key]:
            if self.__can_shoot and not self.__sliding and not self.__in_acid:
                self.__shoot()
        else:
            self.__stop_shooting()

    def __shoot(self) -> None:
        """
        Shoot bullet.
        """
        self.__shooting = True  # for shooting animation
        now = pg.time.get_ticks()
        if now - self.__last_shot > BULLET_RATE:  # how often can shoot
            self.__last_shot = now

            self.__gun_cool_down -= GUN_COOL_DOWN_DECREASE_SPEED  # for each shot, decrease the gun cool down

            # adjust the barrel offset (where the bullet comes from)
            if self.__FACING_RIGHT:
                direction = vec(1, 0)
                if self.__walking_shooting:
                    offset = vec(BARREL_OFFSET_WALKING_R)
                else:
                    offset = vec(BARREL_OFFSET_R)
            else:
                direction = vec(-1, 0)
                if self.__walking_shooting:
                    offset = vec(BARREL_OFFSET_WALKING_L)
                else:
                    offset = vec(BARREL_OFFSET_L)
            pos = self.__pos + offset

            # spawn a bullet and muzzle flash
            Bullet(self.game, pos, direction)
            MuzzleFlash(self.game, pos)

            # gun sound (stop if playing on more than 2 channels)
            if self.__gun_sound.get_num_channels() > 2:
                self.__gun_sound.stop()
            play_sound(self.__gun_sound_on, self.__gun_sound)  # play sound

    def __check_gun_cool_down(self) -> None:
        """
        Check gun cool down.
        If greater than 10, shoot, otherwise prevent shooting.
        """
        if self.__gun_cool_down > 10:
            self.__can_shoot = True
        else:
            self.__can_shoot = False

    def __stop_shooting(self) -> None:
        """
        Stop shooting.
        """
        if self.__shooting:
            self.__shooting = False

    # movement & collision
    def __process_movement(self) -> None:
        """
        Player movement and collision with walls.
        """
        self.__horizontal_movement()
        self.__check_collisions_x()
        self.__vertical_movement()
        self.__check_collisions_y()
        self.__limit_walking_area()

    def __horizontal_movement(self) -> None:
        """
        Player horizontal movement.
        """
        delta_time = self.game.delta_time
        self.__acc.x = 0  # start by assuming the player is not accelerating, so acceleration is 0

        # walking & sliding (auto sliding)
        key = pg.key.get_pressed()
        if not self.__sliding:  # move only if not sliding
            # left
            if key[self.__left_key]:
                self.__acc.x = -PLAYER_ACC
                self.__FACING_RIGHT = False
            # right
            if key[self.__right_key]:
                self.__acc.x = PLAYER_ACC
                self.__FACING_RIGHT = True
        else:
            if self.__FACING_RIGHT:
                self.__acc.x = PLAYER_ACC
            else:
                self.__acc.x = -PLAYER_ACC

        # simulate friction (slowing down the player)
        self.__acc.x += self.__vel.x * PLAYER_FRICTION

        # Newton's first law of motion
        self.__vel.x += self.__acc.x * delta_time  # accelerate in the direction it's moving

        # limit x-velocity (prevent infinite acceleration)
        min(-4, max(self.__vel.x, 4))  # max speed is 4px/frame
        if abs(self.__vel.x) < 0.1:  # stop if speed is less than 0.1
            self.__vel.x = 0

        # Newton's second law of motion (to get position)
        self.__pos.x += self.__vel.x * delta_time + (self.__acc.x * 0.5) * (delta_time * delta_time)

        # set the new position to the player's rect.x (top-left)
        self.rect.x = self.__pos.x

    def __vertical_movement(self) -> None:
        """
        Player vertical movement.
        """
        delta_time = self.game.delta_time

        self.__acc = vec(0, GRAVITY)

        # Newton's first law to simulate gravity
        self.__vel.y += self.__acc.y * delta_time

        # limit y velocity (same reason as limiting x-velocity)
        if self.__vel.y > 7:
            self.__vel.y = 7

        # use the same formula as in horizontal movement (just y instead of x)
        self.__pos.y += self.__vel.y * delta_time + (self.__acc.y * 0.5) * (delta_time * delta_time)

        # falling image
        condition = not self.__on_ground and not self.__walking and not self.__jumping
        if condition and self.__vel.y > 0:
            self.__set_falling_image()

        # set rect equal to position
        self.rect.bottom = self.__pos.y

    def __check_collisions_x(self) -> None:
        """
        Check for collisions when moving left-right.
        """
        hits = pg.sprite.spritecollide(self, self.game.obstacles, False)
        for obstacle in hits:
            if obstacle.get_type() == 'ground':
                # right
                if self.__vel.x > 0:
                    self.__pos.x = obstacle.rect.left - (self.rect.w + 2)  # 2 fixes collision
                    self.rect.x = self.__pos.x - 5  # -5 prevents snapping player on the upper platform
                # left
                elif self.__vel.x < 0:
                    self.__pos.x = obstacle.rect.right
                    self.rect.x = self.__pos.x + 5  # +5 prevents snapping player on the upper platform

    def __check_collisions_y(self) -> None:
        """
        Check for collisions when moving up-down.
        """
        hits = pg.sprite.spritecollide(self, self.game.obstacles, False)
        for obstacle in hits:
            if obstacle.get_type() == 'ground':
                # falling
                if self.__vel.y > 0:
                    self.__on_ground = True
                    self.__jumping = False
                    self.__vel.y = 0
                    self.__pos.y = obstacle.rect.top
                    self.rect.bottom = self.__pos.y + 4  # set player's bottom to that position (+4 puts player down)
                # going up (jumping)
                if self.__vel.y < 0:
                    self.__vel.y = 0
                    self.__pos.y = obstacle.rect.bottom + self.rect.h
                    self.rect.bottom = self.__pos.y

    def __limit_walking_area(self) -> None:
        """
        Prevent from going off the edges of the screen.
        """
        # horizontal edges
        if self.__pos.x <= 0:  # left
            self.__acc.x = 0
        elif self.__pos.x >= WIDTH:  # right
            self.__acc.x = 0

        # vertical edges
        if self.__pos.y >= 1664:  # down
            self.__pos.y = 1664
        elif self.__pos.y <= 0:  # up
            self.__pos.y = 0

    def __set_falling_image(self) -> None:
        """
        Set falling image.
        Used when player is free falling, or in acid.
        """
        if self.__FACING_RIGHT:
            self.image = self.__falling_frames_right[0]
        else:
            self.image = self.__falling_frames_left[0]

    # jump & slide
    def jump(self) -> None:
        """
        Player jump.
        Jump only if on ground and if jumping is not disabled.
        """
        if self.__on_ground and not self.__sliding and not self.__in_acid:
            self.__jumping = True
            self.__vel.y = -PLAYER_JUMP
            self.__on_ground = False

            # play jump sound
            play_sound(self.__jump_sound_on, self.__jump_sound)

    def jump_cut(self) -> None:
        """
        Short jump.
        If jumping, multiply player y velocity by 0.25 to slow down the jump and make it cut.
        """
        if self.__jumping:
            self.__vel.y *= 0.25
            self.__jumping = False

    def slide(self) -> None:
        """
        Player slide.
        Only slide if on ground and walking.
        """
        if self.__on_ground and self.__walking:
            self.__sliding = True

    # collisions
    def __check_collisions(self) -> None:
        """
        Check all collisions.
        """
        self.__check_acid_collision()
        self.__check_spikes_collision()
        self.__check_zombie_attacks()
        self.__check_saw_collision()
        self.__check_item_pickup()

    def __check_acid_collision(self) -> None:
        """
        Check for acid collision.
        """
        hits = pg.sprite.spritecollide(self, self.game.acid, False)
        if hits:
            self.__in_acid = True  # prevent shooting
            self.__vel.x = 0  # prevent moving
            self.__set_falling_image()
            self.acid_damage_alpha()
            for hit in hits:
                if self.__burn_sound_on:
                    self.__burn_sound.play()
                self.__vel.y = 0.01
                hit.acid_damage()
                # game over message
                self.set_dead_message('acid')
        else:
            self.__burn_sound.stop()

    def __check_spikes_collision(self) -> None:
        """
        Check for spikes collision.
        """
        hits = pg.sprite.spritecollide(self, self.game.spikes, False)
        if hits:
            self.__pos.y = hits[0].rect.top
            self.rect.bottom = self.__pos.y
            self.__vel.y = -4  # going up-down on spikes
            for hit in hits:
                hit.spikes_damage()
                play_sound(self.__hit_sound_on, self.__hit_sound)
                # game over message
                self.set_dead_message('spikes')

    def __check_saw_collision(self) -> None:
        """
        Check for saw collision.
        """
        hits = pg.sprite.spritecollide(self, self.game.saws, False, pg.sprite.collide_circle_ratio(0.9))
        if hits:
            self.__pos += vec(SAW_KNOCK_BACK)
            for saw in hits:
                saw.deal_damage()
                play_sound(self.__hit_sound_on, self.__hit_sound)
                # game over message
                self.set_dead_message('saw')

    def __check_zombie_attacks(self) -> None:
        """
        Zombie attacking player.
        """
        hit_zombies = pg.sprite.spritecollide(self, self.game.zombies, False, pg.sprite.collide_mask)
        if hit_zombies:
            for zombie in hit_zombies:
                if zombie.is_attacking():
                    if zombie.get_pos().x > self.__pos.x:  # player is left
                        self.__pos += vec(-ZOMBIE_KNOCK_BACK, 0)
                    elif zombie.get_pos().x < self.__pos.x:  # player is right
                        self.__pos += vec(ZOMBIE_KNOCK_BACK, 0)
                    self.hurt(zombie.get_damage())
                    play_sound(self.__hit_sound_on, self.__hit_sound)
                    # game over message
                    self.set_dead_message('zombies')

    # items
    def __check_item_pickup(self) -> None:
        """
        Check for item collision (pickup).
        """
        collected_items = pg.sprite.spritecollide(self, self.game.items, False, pg.sprite.collide_mask)
        for item in collected_items:
            # key (for door switch)
            if item.get_type() == 'key':
                self.__pick_up_key()
                item.kill()

            # health pack
            if item.get_type() == 'health':
                if self.__health < PLAYER_HEALTH:  # if current health less than 100
                    item.kill()
                    self.__add_health()

            # xp
            if item.get_type() == 'xp':
                item.kill()
                self.__add_xp()

            # coin
            if item.get_type() == 'coin':
                item.kill()
                self.__add_coin()

    def __add_xp(self) -> None:
        """
        Add XP to player.
        Also add 3 seconds to the game timer.
        """
        self.__score += XP_POINTS
        play_sound(self.__xp_coin_sound_on, self.__xp_pickup_sound)
        self.game.game_timer.add_seconds()  # add 3 seconds to game timer

    def __add_coin(self) -> None:
        """
        Add coin to player.
        """
        self.__score += COIN_POINTS
        play_sound(self.__xp_coin_sound_on, self.__coin_pickup_sound)

    def __pick_up_key(self) -> None:
        """
        Pick up the key to the door switch.
        """
        self.__has_key = True
        self.__score += KEY_PICKUP_POINTS
        play_sound(self.__key_pickup_sound_on, self.__key_pickup_sound)

    def has_the_key(self) -> bool:
        """
        Check if player has the key.
        :return: True/False
        """
        if self.__has_key:
            return True
        else:
            return False

    def remove_key(self) -> None:
        """
        Remove the key from player, when used.
        Removes only if the door switch is unlocked.
        This prevents removing the key elsewhere.
        """
        for sprite in self.game.all_sprites:
            if isinstance(sprite, DoorSwitch):
                if sprite.is_unlocked():
                    self.__has_key = False

    # drawing
    def draw_health(self) -> None:
        """
        Draw player health bar.
        """
        health_icon = scale(pg.image.load(HEALTH_PACK_IMAGE), (27, 27)).convert_alpha()

        surface = self.game.display

        x = WIDTH / 2 - 720
        y = HEIGHT / 2 - 420

        percentage = self.__health / PLAYER_HEALTH  # health percentage

        # don't go below 0
        if percentage < 0:
            percentage = 0

        bar_width = 100
        bar_height = 20
        fill_width = percentage * bar_width

        outline_rect = pg.Rect(x, y, bar_width, bar_height)
        filled_rect = pg.Rect(x, y, fill_width, bar_height)

        # color
        if percentage >= 0.6:
            color = GREEN
        elif percentage >= 0.3:
            color = YELLOW
        else:
            color = RED

        # drawing
        surface.blit(health_icon, (x - 35, y - 5))  # health icon next to health bar
        pg.draw.rect(surface, DARK_GREY, outline_rect)  # fix drawing bug (color below health color)
        pg.draw.rect(surface, color, filled_rect)  # filled rect (health color)
        pg.draw.rect(surface, color, outline_rect, 2)  # outline rect

    def draw_gun_bar(self) -> None:
        """
        Draw player gun cool down bar.
        """
        bullet_icon = scale(pg.image.load(BULLET_ICON), (27, 27)).convert_alpha()

        surface = self.game.display

        # adjust drawing position
        if self.main_menu.health_on:
            offset = 380
        else:
            offset = 420
        x = WIDTH / 2 - 720
        y = HEIGHT / 2 - offset

        percentage = self.__gun_cool_down / 100  # gun fill percentage

        self.__gun_cool_down += GUN_COOL_DOWN_INCREASE_SPEED  # increase (reset) gun cool down
        if self.__gun_cool_down <= 0:  # prevent from going below 0
            self.__gun_cool_down = 0
        elif self.__gun_cool_down >= GUN_COOL_DOWN:  # prevent from going above max
            self.__gun_cool_down = GUN_COOL_DOWN

        bar_width = 100
        bar_height = 20
        fill_width = percentage * bar_width

        outline_rect = pg.Rect(x, y, bar_width, bar_height)
        filled_rect = pg.Rect(x, y, fill_width, bar_height)

        # color
        if percentage >= 0.6:
            color = GREEN
        elif percentage >= 0.3:
            color = YELLOW
        else:
            color = RED

        # drawing
        surface.blit(bullet_icon, (x - 35, y - 5))  # draw health icon next to health bar
        pg.draw.rect(surface, DARK_GREY, outline_rect)  # fix drawing bug (color below health color)
        pg.draw.rect(surface, color, filled_rect)  # filled rect (gun cool down color)
        pg.draw.rect(surface, color, outline_rect, 2)  # outline rect (fixed)

    def draw_score(self) -> None:
        """
        Draw player score on screen.
        """
        health_on = self.main_menu.health_on
        gun_bar_on = self.main_menu.gun_bar_on

        # adjust drawing position
        if health_on and gun_bar_on:  # all on
            offset = 350
        elif health_on and not gun_bar_on or not health_on and gun_bar_on:  # only one on
            offset = 390
        else:  # all off
            offset = 430
        x = WIDTH / 2 - 750
        y = HEIGHT / 2 - offset

        font = pg.font.Font(FONT, 25)
        score_text = font.render(f'Score: {str(self.__score)}', True, WHITE)
        self.game.display.blit(score_text, (x, y))

    def acid_damage_alpha(self) -> None:
        """
        Apply acid damage color on player.
        """
        damage_alpha = chain(DAMAGE_ALPHA)
        self.image.fill((255, 0, 0, next(damage_alpha)), special_flags=pg.BLEND_RGBA_MULT)


class Bullet(pg.sprite.Sprite):
    """
    Player's bullet.
    """

    def __init__(self, game, pos: vec, direction: vec):
        """
        Make a bullet.
        :param game: game
        :param pos: position where to spawn
        :param direction: direction in which to go (left/right)
        """
        self._layer = LAYERS['fourth']
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        # player reference
        self.__player = self.game.player

        # image
        self.__load_images()
        self.image = self.__images[0]
        self.rect = self.image.get_rect()

        # movement
        self.__direction = direction
        self.__pos = vec(pos)
        self.__vel = self.__direction * BULLET_SPEED
        self.rect.center = pos

        # animation
        self.__spawn_time = pg.time.get_ticks()  # for killing it
        self.__last_update = 0
        self.__current_frame = 0

        # if gun upgrade on
        self.__gun_upgrade_on = self.game.main_menu.gun_upgrade_on
        self.__adjust_bullet_damage()

        self.mask = pg.mask.from_surface(self.image)

    def update(self) -> None:
        """
        Update bullet sprite.
        """
        self.__animate()
        self.__move()
        self.__check_collisions()
        self.__check_lifetime()

    def __load_images(self) -> None:
        """
        Parse bullet images from player sprite sheet.
        """
        self.__images = [self.game.player_sprite_sheet.parse_sprite('bullet_{}.png'.format(i)) for i in range(5)]
        self.__images = [scale(img, (int(img.get_width() // 1.5), int(img.get_height() // 1.5))) for img in
                         self.__images]

    def __adjust_bullet_damage(self) -> None:
        """
        Adjust bullet damage if gun upgrade turned on.
        If ON, deal double damage to saw & laser machine; deal more damage to zombie.
        Otherwise, deal regular damage.
        """
        if self.__gun_upgrade_on:
            self.__damage = BULLET_UPGRADED_DAMAGE
            self.__hazard_damage_amount = 2
        else:
            self.__damage = BULLET_DAMAGE
            self.__hazard_damage_amount = 1

        self.__hazard_damage = self.__hazard_damage_amount

    def get_damage(self) -> int:
        """
        Get bullet damage.
        :return: bullet damage
        """
        return self.__damage

    def __animate(self) -> None:
        """
        Animate the bullet sprite.
        """
        now = pg.time.get_ticks()
        if now - self.__last_update > 30:
            self.__last_update = now
            self.__current_frame = (self.__current_frame + 1) % len(self.__images)
            if self.__direction == vec(1, 0):
                self.image = self.__images[self.__current_frame]
            else:
                self.image = flip(self.__images[self.__current_frame], True, False)
            self.rect = self.image.get_rect()

    def __move(self) -> None:
        """
        Move the bullet.
        Must be called AFTER animate() function.
        """
        self.__pos += self.__vel * self.game.delta_time
        self.rect.center = self.__pos  # update rect to that location

    def __check_collisions(self) -> None:
        """
        Check for collision and kill the bullet if something is hit.
        """

        # zombies
        self.__check_zombie_hit()

        # walls
        self.__check_wall_hit()

        # saws
        self.__check_saw_hit()

        # spikes
        self.__check_spikes_hit()

        # lasers
        self.__check_laser_hit()

        # laser machines
        self.__check_laser_machine_hit()

    def __check_laser_machine_hit(self) -> None:
        """
        Check laser machine hits.
        """
        hits = pg.sprite.spritecollide(self, self.game.laser_machines, False, pg.sprite.collide_mask)
        if hits:
            for machine in hits:
                self.kill()
                machine.damage_laser_machine(self.__hazard_damage)
                if machine.get_times_hit() == machine.get_health():
                    machine.kill()
                    Explosion(self.game, machine.get_pos() + (32, 32))
                    self.__player.add_points(LASER_MACHINE_POINTS)

    def __check_wall_hit(self) -> None:
        """
        Check if wall hit and kill the bullet.
        """
        hits = pg.sprite.spritecollide(self, self.game.obstacles, False)
        for obstacle in hits:
            if obstacle.get_type() == 'ground':
                self.kill()

    def __check_saw_hit(self) -> None:
        """
        Check if saw hit and kill the bullet.
        If saw is hit x number of times, destroy it and create explosion.
        """
        saw_hits = pg.sprite.spritecollide(self, self.game.saws, False, pg.sprite.collide_mask)
        if saw_hits:
            for saw in saw_hits:
                self.kill()  # kill the bullet
                saw.damage_saw(self.__hazard_damage)
                if saw.get_times_hit() == saw.get_health():
                    saw.kill()  # kill the saw
                    Explosion(self.game, saw.get_pos())
                    self.__player.add_points(SAW_POINTS)

    def __check_laser_hit(self) -> None:
        """
        Check if laser hit and kill the bullet.
        """
        if pg.sprite.spritecollide(self, self.game.lasers, False, pg.sprite.collide_mask):
            self.kill()

    def __check_zombie_hit(self) -> None:
        """
        Check for zombie hits.
        """
        zombies_hit = pg.sprite.groupcollide(self.game.zombies, self.game.bullets, False, True, pg.sprite.collide_mask)
        if zombies_hit:
            for zombie in zombies_hit:
                for bullet in zombies_hit[zombie]:
                    play_sound(self.game.main_menu.zombie_hit_sound_on, self.game.main_menu.zombie_hit_sound)
                    zombie.hurt(bullet.__damage)

    def __check_spikes_hit(self) -> None:
        """
        Check if spike hit and kill the bullet.
        """
        if pg.sprite.spritecollideany(self, self.game.spikes):
            self.kill()

    def __check_lifetime(self) -> None:
        """
        If bullet lifetime is exceeded, kill it.
        """
        if pg.time.get_ticks() - self.__spawn_time > BULLET_LIFETIME:
            self.kill()


class Zombie(pg.sprite.Sprite):
    """
    Zombie (mob) class.
    Zombie position is set in Tiled editor.
    """

    def __init__(self, game, x: float, y: float):
        """
        Make a zombie.
        :param game: game
        :param x: X position to spawn
        :param y: Y position to spawn
        """
        self._layer = LAYERS['third']
        self.groups = game.all_sprites, game.zombies
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.main_menu = self.game.main_menu

        # player reference
        self.__player = self.game.player

        # image
        self.__load_data()
        self.image = self.__idle_frames_right[0]
        self.rect = self.image.get_rect()
        self.rect.center = (round(x), round(y))

        # movement vectors
        self.__pos = vec(x, y)
        self.__vel = vec(0, 0)
        self.__acc = vec(0, 0)

        self.__health = ZOMBIE_HEALTH
        self.__damage = ZOMBIE_DAMAGE

        # animations
        self.__FACING_RIGHT = True
        self.__walking = False
        self.__prevent_moving = False  # fix idle movement bug
        self.__attacking_animation = False
        self.__attacking = False
        self.__current_frame = 0
        self.__last_update = 0

        # wandering
        self.__random_target = vec(randint(0, WIDTH), randint(0, HEIGHT))
        self.__last_target = 0

    def update(self) -> None:
        """
        Update zombie sprite.
        """
        self.__process_animations()
        self.__movement_and_collisions()

        # kill
        if self.__health <= 0:
            self.__kill()

    def __process_animations(self) -> None:
        """
        Animate zombie sprite.
        """
        now = pg.time.get_ticks()

        # walking/not walking
        if self.__vel.x != 0:
            self.__walking = True
        else:
            self.__walking = False

        # idle
        if not self.__walking:
            self.__prevent_moving = True
            if now - self.__last_update > 80:
                self.__last_update = now
                self.__current_frame = (self.__current_frame + 1) % len(self.__idle_frames_right)
                bottom = self.rect.bottom
                if self.__FACING_RIGHT:
                    self.image = self.__idle_frames_right[self.__current_frame]
                else:
                    self.image = self.__idle_frames_left[self.__current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
                self.__prevent_moving = False

        # walking
        if self.__walking:
            if now - self.__last_update > 100:
                self.__last_update = now
                self.__current_frame = (self.__current_frame + 1) % len(self.__walk_frames_right)
                bottom = self.rect.bottom
                if self.__vel.x > 0:  # going right
                    self.image = self.__walk_frames_right[self.__current_frame]
                else:  # going left
                    self.image = self.__walk_frames_left[self.__current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        # attack
        if self.__attacking_animation:
            if now - self.__last_update > 82:
                self.__last_update = now
                bottom = self.rect.bottom
                self.__current_frame = (self.__current_frame + 1) % len(self.__attack_frames_right)
                if self.__FACING_RIGHT:
                    self.image = self.__attack_frames_right[self.__current_frame]
                    # if current frame is not first, attack player (fixes damage bug)
                    if self.image != self.__attack_frames_right[0]:
                        self.__attacking = True
                else:
                    self.image = self.__attack_frames_left[self.__current_frame]
                    # if current frame is not first, attack player (fixes damage bug)
                    if self.image != self.__attack_frames_left[0]:
                        self.__attacking = True
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        self.rect.midbottom = self.__pos

        # for precise collisions
        self.mask = pg.mask.from_surface(self.image)

    def __load_data(self) -> None:
        """
        Load zombie sprite images & sounds.
        """
        load_img = self.game.zombies_sprite_sheet.parse_sprite

        # attack
        self.__attack_frames_right = [load_img('attack_{}.png'.format(i)) for i in range(8)]
        self.__attack_frames_left = [flip(img, True, False) for img in self.__attack_frames_right]

        # idle
        self.__idle_frames_right = [load_img('idle_{}.png'.format(i)) for i in range(15)]
        self.__idle_frames_left = [flip(img, True, False) for img in self.__idle_frames_right]

        # walk
        self.__walk_frames_right = [load_img('walk_{}.png'.format(i)) for i in range(10)]
        self.__walk_frames_left = [flip(img, True, False) for img in self.__walk_frames_right]

        # sound settings
        self.__hit_sound_on = self.main_menu.zombie_hit_sound_on
        self.__die_sound_on = self.main_menu.zombie_die_sound_on
        self.__moan_sound_on = self.main_menu.zombie_moan_sound_on

        # sounds
        self.__hit_sound = self.main_menu.zombie_hit_sound
        self.__die_sound = self.main_menu.zombie_die_sound
        self.__moan_sounds = self.main_menu.zombie_moan_sounds

    # getters
    def get_pos(self) -> vec:
        """
        Get position vector.
        :return: position vector
        """
        return self.__pos

    def get_acc(self) -> vec:
        """
        Get acceleration vector.
        :return: acceleration vector
        """
        return self.__acc

    def get_vel(self) -> vec:
        """
        Get velocity vector.
        :return: velocity vector
        """
        return self.__vel

    # health
    def get_health(self) -> int:
        """
        Get health.
        :return: zombie health
        """
        return self.__health

    def hurt(self, damage):
        """
        Reduce health by amount of damage.
        :param damage: damage amount
        """
        self.__health -= damage

    def __kill(self) -> None:
        """
        Kill the zombie, make splat & spawn XP.
        """
        play_sound(self.__die_sound_on, self.__die_sound)

        Splat(self.game, self.__pos)
        self.kill()  # kill it
        self.__player.add_points(ZOMBIE_POINTS)

        # spawn xp points after killing it
        Item(self.game, self.__pos + (30, -20), 'xp')

    # attack
    def get_damage(self) -> int:
        """
        Get damage.
        :return: zombie damage
        """
        return self.__damage

    def is_attacking(self) -> bool:
        """
        Check if attacking animation is in progress.
        :return: True/False
        """
        return self.__attacking

    # movement
    def __movement_and_collisions(self) -> None:
        """
        Zombie movement and collisions.
        """
        self.__move_and_attack()
        self.__check_collisions_x()
        self.__gravity()
        self.__check_collisions_y()
        self.__limit_walking_area()

    def __move_and_attack(self) -> None:
        """
        Movement and player attacking.
        """
        delta_time = self.game.delta_time

        if not self.__prevent_moving:
            self.__chase_player()

        self.__acc.x += self.__vel.x * ZOMBIE_FRICTION
        self.__vel.x += self.__acc.x * delta_time

        # limit x velocity
        min(-4, max(self.__vel.x, 4))
        if abs(self.__vel.x) < 0.1:  # stop if below 0.1
            self.__vel.x = 0

        self.__pos.x += self.__vel.x * delta_time + (self.__acc.x * 0.5) * (delta_time * delta_time)
        self.rect.x = self.__pos.x

    def __gravity(self) -> None:
        """
        Simulating gravity.
        """
        delta_time = self.game.delta_time

        self.__acc = vec(0, GRAVITY)

        # Newton's first law to simulate gravity
        self.__vel.y += self.__acc.y * delta_time

        # limit y velocity
        if self.__vel.y > 7:
            self.__vel.y = 7

        # use the same formula used in horizontal movement (just y instead of x)
        self.__pos.y += self.__vel.y * delta_time + (self.__acc.y * 0.5) * (delta_time * delta_time)

        # set rect equal to position
        self.rect.bottom = self.__pos.y

    def __chase_player(self) -> None:
        """
        Chase the player.
        """
        x_distance, y_distance = self.__calculate_distances()

        # within detect radius - chase & attack
        if self.__is_in_detect_radius():
            if random() < 0.009:
                play_sound(self.__moan_sound_on, choice(self.__moan_sounds))

            # get player's position (left/right of zombie)
            player_left, player_right = self.__check_player_position()

            # chase & attack player
            if player_left:
                self.__acc.x = -ZOMBIE_ACC
                self.__FACING_RIGHT = False
                self.__attack_player(x_distance, y_distance, 26)
            elif player_right:
                self.__acc.x = ZOMBIE_ACC
                self.__FACING_RIGHT = True
                self.__attack_player(x_distance, y_distance, 46)
        # wander
        else:
            self.__acc = self.__wander()

    def __calculate_distances(self):
        """
        Calculate the distance between the player and zombie.
        :return: x & y distance
        """
        x_distance = self.__pos.x - self.__player.get_pos().x  # x distance
        y_distance = self.__pos.y - self.__player.get_pos().y  # y distance

        return x_distance, y_distance

    def __is_in_detect_radius(self) -> bool:
        """
        Check if player is within the detect radius.
        :return: True if within detect radius
        """
        x_distance, y_distance = self.__calculate_distances()

        # ff on the same level
        if abs(x_distance) < ZOMBIE_DETECT_RADIUS and y_distance == 0:
            return True
        # otherwise
        elif abs(x_distance) > ZOMBIE_DETECT_RADIUS or y_distance != 0:
            return False

    def __check_player_position(self):
        """
        Check player's position relative to the zombie.
        :return: two boolean values - 1. if player is left, 2. if player is right
        """
        player_left = self.__pos.x > self.__player.get_pos().x  # player is left
        player_right = self.__pos.x < self.__player.get_pos().x  # player is right
        return player_left, player_right

    def __attack_player(self, x_distance: float, y_distance: float, attacking_distance: int) -> None:
        """
        Attack the player if within the attack distance.
        :param x_distance: x-distance between zombie and player
        :param y_distance: y-distance between zombie and player
        :param attacking_distance: how close to player zombie has to be to attack (28/45)
        """
        within_attacking_distance = abs(x_distance) <= attacking_distance and y_distance == 0
        # if within attacking distance
        if within_attacking_distance:
            self.__vel = vec(0, 0)  # briefly slow down the zombie
            self.__attacking_animation = True
        else:
            self.__attacking_animation = False

    def __wander(self) -> vec:
        """
        Zombie wandering left-right.
        :return: seek random target defined in seek() function
        """
        now = pg.time.get_ticks()
        if now - self.__last_target > randint(ZOMBIE_RANDOM_TARGET_TIME[0], ZOMBIE_RANDOM_TARGET_TIME[1]):
            self.__last_target = now
            self.__random_target = vec(randint(0, WIDTH), randint(0, HEIGHT))

            # adjust facing direction when idle & new random target is chosen
            if abs(self.__random_target.x) < abs(self.__pos.x):
                self.__FACING_RIGHT = False
            else:
                self.__FACING_RIGHT = True

        return self.__seek(self.__random_target)

    def __seek(self, target: vec) -> vec:
        """
        Look for a random target defined in wander() function and go towards that target.
        :param target: random target chosen in wander() function
        :return: steering force (force that pulls zombie towards that random target)
        """
        desired = (target - self.__pos).normalize() * ZOMBIE_MAX_SPEED
        steer = (desired - self.__vel)
        return steer

    def __limit_walking_area(self) -> None:
        """
        Prevent from going off the edges of the screen.
        """
        # horizontal edges
        if self.__pos.x <= 0:  # left
            self.__acc.x = 0
        elif self.__pos.x >= WIDTH:  # right
            self.__acc.x = 0

        # vertical edges
        if self.__pos.y >= 1664:  # down
            self.__pos.y = 1664
        elif self.__pos.y <= 0:  # up
            self.__pos.y = 0

    # collisions
    def __check_collisions_x(self) -> None:
        """
        Check for collisions when moving left-right.
        """
        hits = pg.sprite.spritecollide(self, self.game.obstacles, False)
        for obstacle in hits:
            # going right
            if self.__vel.x > 0:
                self.__pos.x = obstacle.rect.left - self.rect.w
                self.rect.x = self.__pos.x
                self.__random_target = vec(randint(0, obstacle.rect.x - 10), randint(0, HEIGHT))
            # going left
            elif self.__vel.x < 0:
                self.__pos.x = obstacle.rect.right
                self.rect.x = self.__pos.x
                self.__random_target = vec(randint(obstacle.rect.x + 10, WIDTH), randint(0, HEIGHT))

    def __check_collisions_y(self) -> None:
        """
        Check for collisions when moving up-down.
        Not checking for y < 0, because zombie can't jump.
        """
        hits = pg.sprite.spritecollide(self, self.game.obstacles, False)
        for obstacle in hits:
            if self.__vel.y > 0:
                self.__vel.y = 0
                self.__pos.y = obstacle.rect.top
                self.rect.bottom = self.__pos.y + 1  # set zombie's bottom to that position

    # drawing
    def draw_health(self) -> None:
        """
        Draw zombie health bar.
        """
        surface = self.image

        percentage = self.__health / ZOMBIE_HEALTH  # health percentage

        # don't go below 0
        if percentage < 0:
            percentage = 0

        bar_width = 54
        bar_height = 7
        fill_width = percentage * bar_width

        outline_rect = pg.Rect(0, 0, bar_width, bar_height)
        filled_rect = pg.Rect(0, 0, fill_width, bar_height)

        # color
        if percentage >= 0.6:
            color = GREEN
        elif percentage >= 0.3:
            color = YELLOW
        else:
            color = RED

        # drawing
        pg.draw.rect(surface, DARK_GREY, outline_rect)
        pg.draw.rect(surface, color, filled_rect)


# effects
class MuzzleFlash(pg.sprite.Sprite):
    """
    Muzzle flash effect when shooting (player).
    """

    def __init__(self, game, pos: vec):
        """
        Make a muzzle flash effect
        :param game: game
        :param pos: position where to spawn
        """

        self._layer = LAYERS['fifth']
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        # image
        self.__images = [self.game.player_sprite_sheet.parse_sprite('muzzle_{}.png'.format(i)) for i in range(5)]
        self.__images = [scale(img, (int(img.get_width() * 2), int(img.get_height() * 1.2))) for img in self.__images]
        self.image = self.__images[0]
        self.rect = self.image.get_rect()

        self.rect.center = pos

        self.__spawn_time = pg.time.get_ticks()  # for the effect to disappear
        self.__flash_duration = FLASH_DURATION

        # animation
        self.__last_update = 0
        self.__current_frame = 0

    def update(self) -> None:
        """
        Update muzzle flash sprite (kill it).
        """
        # kill the effect
        self.__current_frame = (self.__current_frame + 1) % len(self.__images)
        self.image = self.__images[self.__current_frame]
        if pg.time.get_ticks() - self.__spawn_time > self.__flash_duration:
            self.kill()


class Explosion(pg.sprite.Sprite):
    """
    Explosion effect.
    Appears when player, saw or laser machine explode.
    """

    def __init__(self, game, pos: vec, player: Player = None):
        """
        Make explosion.
        :param game: game
        :param pos: position to spawn
        :param player: player
        """
        self._layer = LAYERS['fifth']
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.__main_menu = self.game.main_menu

        # for player to explode
        self.__player = player

        # image
        self.__images = [self.game.explosion_sprite_sheet.parse_sprite('explosion_{}.png'.format(i)) for i in range(9)]
        self.__images = [scale(img, (int(img.get_width() // 2), int(img.get_height() // 2))) for img in self.__images]
        self.image = self.__images[0]
        self.rect = self.image.get_rect()

        self.rect.center = pos

        # animation
        self.__spawn_time = pg.time.get_ticks()  # for the effect to disappear
        self.__last_update = 0
        self.__current_frame = 0

        self.__set_sounds()

        # if player is given, kill him when spawning explosion
        if self.__player is not None:
            self.__player.kill()

    def __set_sounds(self) -> None:
        """
        Stop certain sounds and play explosion sound.
        """
        self.__main_menu.laser_sound.stop()
        self.__main_menu.burn_sound.stop()  # stop the burning sound (acid)
        play_sound(self.__main_menu.explosion_sound_on, self.__main_menu.explosion_sound)

    def update(self) -> None:
        """
        Update the explosion sprite.
        """
        # explosion animation
        now = pg.time.get_ticks()
        if now - self.__last_update > 100:
            self.__last_update = now

            # animate
            self.__current_frame = (self.__current_frame + 1) % len(self.__images)
            center = self.rect.center
            self.image = self.__images[self.__current_frame]
            self.rect = self.image.get_rect()
            self.rect.center = center

            # kill the explosion
            if now - self.__spawn_time > EXPLOSION_DURATION:
                self.kill()

                # if player is given, when animation finishes, game is over
                if self.__player is not None:
                    # play game over music
                    play_sound(self.__main_menu.game_over_music_on, self.__main_menu.game_over_music)
                    # if new high score, play sound
                    if self.__player.get_score() >= self.__main_menu.get_high_score():
                        play_sound(self.__main_menu.high_score_sound_on, self.__main_menu.high_score_sound)
                    self.game.game_over = True


class Splat(pg.sprite.Sprite):
    """
    Blood splat.
    Spawns when zombie is killed.
    """

    def __init__(self, game, pos: vec):
        """
        Make a splat effect.
        :param game: game
        :param pos: position to spawn
        """

        self._layer = LAYERS['first']
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        # image
        self.__load_images()
        self.image = choice(self.__images)  # random image
        self.rect = self.image.get_rect()
        self.rect.center = pos + (25, -30)

    def __load_images(self):
        """
        Load splat images.
        """
        self.__images = [pg.image.load(img) for img in SPLAT_IMAGES]
        self.__images = [scale(img, (int(img.get_width() // 2.5), int(img.get_height() // 2.5))) for img in
                         self.__images]


# hazards
class Acid(pg.sprite.Sprite):
    """
    Acid class.
    Acid image and position are set in Tiled editor.
    """

    def __init__(self, game, x: float, y: float, width: float, height: float):
        """
        Make acid
        :param game: game
        :param x: x position to spawn
        :param y: y position to spawn
        :param width: acid width
        :param height: acid height
        """

        self.groups = game.acid
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        # player reference
        self.__player = self.game.player

        # acid rect
        self.rect = pg.Rect(x, y, width, height)

        self.__damage = ACID_DAMAGE
        self.__last_attack = 0

    def acid_damage(self) -> None:
        """
        Deal acid damage to sprite.
        """
        now = pg.time.get_ticks()
        if now - self.__last_attack > 300:
            self.__last_attack = now
            self.__player.hurt(self.__damage)
            self.__player.get_vel().x = 0


class Spikes(pg.sprite.Sprite):
    """
    Spikes class.
    Spikes image and position are set in Tiled editor.
    """

    def __init__(self, game, x: float, y: float, width: float, height: float):
        """
        Make spikes.
        :param game: game
        :param x: x position to spawn
        :param y: y position to spawn
        :param width: spikes width
        :param height: spikes height
        """

        self.groups = game.spikes
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        # spikes rect
        self.rect = pg.Rect(x, y, width, height)

        self.__damage = SPIKES_DAMAGE
        self.__last_attack = 0

    def spikes_damage(self) -> None:
        """
        Deal spikes damage to player.
        """
        now = pg.time.get_ticks()
        if now - self.__last_attack > 300:
            self.__last_attack = now
            self.game.player.hurt(self.__damage)


class Saw(pg.sprite.Sprite):
    """
    Saw class.
    Saw position is set in Tiled editor.
    """

    def __init__(self, game, x: float, y: float, width: float, height: float, saw_type=None):
        """
        Make a saw.
        :param game: game
        :param x: x position to spawn
        :param y: y position to spawn
        :param width: saw width
        :param height: saw height
        :param saw_type: for movement (none, vertical, horizontal)
        """

        self.groups = game.all_sprites, game.saws
        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.__width = width
        self.__height = height
        self.__type = saw_type

        # image
        self.__load_images()
        self.image = self.__images[0]
        self.rect = self.image.get_rect(center=(x, y))

        # adjust position by the offset
        self.radius = int(self.__width / 2)  # circle radius
        self.__offset = self.radius
        self.__x = x + self.__offset
        self.__y = y + self.__offset
        self.__pos = (self.__x, self.__y)  # position for explosion spawning (updating in animation function)

        # rotation
        self.__last_rot = 0
        self.__current_frame = 0

        # attack
        self.__damage = SAW_DAMAGE
        self.__last_attack = 0

        # health
        self.__health = SAW_HEALTH
        self.__times_hit = 0  # keep track of number of times it's hit by the bullet (used for killing it)

        # movement flags
        self.__set_saw_type()

    def update(self) -> None:
        """
        Update the saw sprite.
        """
        self.__animate()

        # saw sound
        self.__adjust_sound()

    def __load_images(self) -> None:
        """
        Load saw sprite image and make images by rotating it.
        """
        image = pg.image.load(SAW_IMAGE).convert_alpha()
        image = scale(image, (int(self.__width), int(self.__height)))
        image.set_colorkey(BLACK)
        rot = 0
        self.__images = []
        for i in range(360):
            self.__images.append(pg.transform.rotozoom(image, rot, 1))  # prevent rotating the background
            rot += 1

    def __set_saw_type(self) -> None:
        """
        Set saw type based on tile object type in Tiled.
        By default, the saw cannot move.
        It can move if type is specified (vertical/horizontal).
        """
        self.__can_move_vertically = False
        self.__can_move_horizontally = False
        if self.__type is not None:
            if self.__type == 'vertical':
                self.__can_move_vertically = True
            elif self.__type == 'horizontal':
                self.__can_move_horizontally = True
            self.__change_direction = False

    def __adjust_sound(self) -> None:
        """
        Adjust the saw sound.
        """
        # stop if playing on more than 2 channels
        if self.game.main_menu.saw_sound.get_num_channels() > 1:
            self.game.main_menu.saw_sound.stop()
        play_sound(self.game.main_menu.saw_sound_on, self.game.main_menu.saw_sound)

    def get_pos(self) -> tuple:
        """
        Get position.
        :return: position tuple
        """
        return self.__pos

    def get_health(self) -> int:
        """
        Get health.
        :return: health
        """
        return self.__health

    def get_times_hit(self) -> int:
        """
        Get how many times the saw is hit.
        :return: times hit
        """
        return self.__times_hit

    def damage_saw(self, times_hit: int) -> None:
        """
        Damage the saw.
        Increase times hit.
        :param times_hit: number of hits to increase
        """
        self.__times_hit += times_hit

    def deal_damage(self) -> None:
        """
        Deal damage to player.
        """
        now = pg.time.get_ticks()
        if now - self.__last_attack > 300:
            self.__last_attack = now
            self.game.player.hurt(self.__damage)

    # movement animation
    def __animate(self) -> None:
        """
        Animate the saw sprite.
        """
        # move the saw if it is movable
        self.__move()

        # position for explosion spawning
        self.__pos = (self.__x, self.__y)

        # rotating animation
        self.__rotate()

        self.mask = pg.mask.from_surface(self.image)

    def __rotate(self) -> None:
        """
        Rotate the saw.
        """
        now = pg.time.get_ticks()
        if now - self.__last_rot > 30:
            self.__last_rot = now
            self.__current_frame = (self.__current_frame + 15) % len(self.__images)
            self.image = self.__images[self.__current_frame]
            self.rect = self.image.get_rect(center=(self.__x, self.__y))

    def __move(self) -> None:
        """
        Move the saw.
        It can move only if the type is specified (vertical/horizontal).
        """
        if self.__type is not None:
            if self.__can_move_vertically:
                self.__move_vertically()
            if self.__can_move_horizontally:
                self.__move_horizontally()

    def __move_vertically(self) -> None:
        """
        Move the saw vertically.
        If it hits the limit obstacle, change direction.
        """
        hits = pg.sprite.spritecollide(self, self.game.obstacles, False)
        for limit in hits:
            if limit.get_type() == 'saw_limit_down':
                self.__change_direction = True
            elif limit.get_type() == 'saw_limit_up':
                self.__change_direction = False

        if not self.__change_direction:
            self.__y += SAW_SPEED
        else:
            self.__y -= SAW_SPEED

    def __move_horizontally(self) -> None:
        """
        Move the saw horizontally.
        If it hits the limit obstacle, change direction.
        """
        hits = pg.sprite.spritecollide(self, self.game.obstacles, False)
        for limit in hits:
            if limit.get_type() == 'saw_limit_right':
                self.__change_direction = True
            elif limit.get_type() == 'saw_limit_left':
                self.__change_direction = False

        if not self.__change_direction:
            self.__x += SAW_SPEED
        else:
            self.__x -= SAW_SPEED


class LaserMachine(pg.sprite.Sprite):
    """
    Creates laser machine.
    Position is set in Tiled editor.
    """

    def __init__(self, game, x: float, y: float, width: float, height: float, laser_type: str):
        """
        Make a laser machine.
        :param game: game
        :param x: x position to spawn
        :param y: y position to spawn
        :param width: laser machine width
        :param height: laser machine height
        :param laser_type:
        """

        self._layer = LAYERS['first']
        self.groups = game.all_sprites, game.laser_machines
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.__width = width
        self.__height = height
        self.__type = laser_type

        # image
        self.__make_laser()
        self.image = self.__laser_shoot
        self.rect = self.image.get_rect()

        # set position
        self.__pos = vec(x, y)
        self.rect.x = x
        self.rect.y = y

        # attack
        self.__shooting = True
        self.__last_shot = 0

        # health
        self.__health = LASER_MACHINE_HEALTH
        self.__times_hit = 0  # keep track of number of times it's hit by the bullet (for killing it)

    def update(self) -> None:
        """
        Update laser machine.
        """
        self.__shoot_bullet()

        self.__set_image()

    def __make_laser(self) -> None:
        """
        Make laser machine based on it's type (in tiled).
        """
        self.__load_images()

        # down
        if self.__type == 'down blue' or self.__type == 'down red':
            self.__laser_shoot = self.__laser_down_shoot
            self.__laser_off = self.__laser_down_off
        # right
        elif self.__type in ('right', 'right_bullet'):
            self.__laser_shoot = self.__laser_right_shoot
            self.__laser_off = self.__laser_right_off
            self.__bullet_offset = (64, 35)
        # left
        elif self.__type in ('left', 'left_bullet'):
            self.__laser_shoot = self.__laser_left_shoot
            self.__laser_off = self.__laser_left_off
            self.__bullet_offset = (0, 35)

    def __load_images(self) -> None:
        """
        Load laser machine images.
        """
        load_img = pg.image.load

        scale_factor = (int(self.__width), int(self.__height))

        # load images
        laser_down_shoot_image = scale(load_img(LASER_MACHINE_DOWN_SHOOT_IMAGE), scale_factor).convert_alpha()
        laser_down_off_image = scale(load_img(LASER_MACHINE_DOWN_OFF_IMAGE), scale_factor).convert_alpha()
        laser_right_shoot_image = scale(load_img(LASER_MACHINE_RIGHT_SHOOT_IMAGE), scale_factor).convert_alpha()
        laser_right_off_image = scale(load_img(LASER_MACHINE_RIGHT_OFF_IMAGE), scale_factor).convert_alpha()
        laser_left_shoot_image = scale(load_img(LASER_MACHINE_LEFT_SHOOT_IMAGE), scale_factor).convert_alpha()
        laser_left_off_image = scale(load_img(LASER_MACHINE_LEFT_OFF_IMAGE), scale_factor).convert_alpha()

        # down
        self.__laser_down_shoot = laser_down_shoot_image
        self.__laser_down_off = laser_down_off_image
        # right
        self.__laser_right_shoot = laser_right_shoot_image
        self.__laser_right_off = laser_right_off_image
        # left
        self.__laser_left_shoot = laser_left_shoot_image
        self.__laser_left_off = laser_left_off_image

    def __set_image(self) -> None:
        """
        Set laser machine image (shooting/not shooting).
        """
        if self.__shooting:
            self.image = self.__laser_shoot
        else:
            self.image = self.__laser_off

    def __shoot_bullet(self) -> None:
        """
        Shoot laser bullet.
        """
        if self.__type == 'right_bullet':
            self.__laser_bullet(self.__bullet_offset, vec(1, 0))
        elif self.__type == 'left_bullet':
            self.__laser_bullet(self.__bullet_offset, vec(-1, 0))

    def __laser_bullet(self, offset: tuple, direction: vec) -> None:
        """
        Make laser bullet.
        :param offset: bullet offset
        :param direction: direction in which the bullet goes
        """
        now = pg.time.get_ticks()
        self.__shooting = False
        if random() < 0.3:
            if now - self.__last_shot > randint(LASER_BULLET_FREQUENCY[0], LASER_BULLET_FREQUENCY[1]):
                self.__last_shot = now
                self.__shooting = True
                LaserBullet(self.game, self.__pos, offset, direction)
                play_sound(self.game.main_menu.laser_sound_on, self.game.main_menu.laser_gun_sound)

    def turn_off(self) -> None:
        """
        Turn off the laser machine.
        """
        self.__shooting = False

    def get_type(self) -> str:
        """
        Get laser machine type.
        :return: laser machine type
        """
        return self.__type

    def get_pos(self) -> vec:
        """
        Get position.
        :return: position tuple
        """
        return self.__pos

    # health
    def get_health(self) -> int:
        """
        Get health.
        :return: health
        """
        return self.__health

    def get_times_hit(self) -> int:
        """
        Get how many times the saw is hit.
        :return: times hit
        """
        return self.__times_hit

    def damage_laser_machine(self, times_hit: int) -> None:
        """
        Damage the laser machine.
        Increase times hit.
        :param times_hit: number of hits to increase
        """
        self.__times_hit += times_hit


class LaserBullet(pg.sprite.Sprite):
    """
    Spawn laser bullet.
    """

    def __init__(self, game, pos: vec, offset: tuple, direction: vec):
        """
        Make a laser bullet.
        :param game: game
        :param pos: position to spawn
        :param offset: offset
        :param direction: direction in which the bullet goes
        """

        self._layer = LAYERS['fourth']
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.__player = self.game.player

        # bullet size
        self.__width = 10
        self.__height = 10

        self.__pos = vec(pos) + offset

        # image
        self.image = pg.image.load(LASER_BULLET_IMAGE).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = self.__pos

        # bullet movement
        self.__direction = direction
        self.__vel = self.__direction * LASER_BULLET_SPEED

        self.__spawn_time = pg.time.get_ticks()  # for killing it

        self.__damage = LASER_BULLET_DAMAGE

        self.mask = pg.mask.from_surface(self.image)

    def update(self) -> None:
        """
        Update laser bullet sprite.
        """
        self.__move()
        self.__check_collisions()

    def __move(self) -> None:
        """
        Move the bullet.
        """
        self.__pos += self.__vel * self.game.delta_time
        self.rect.center = self.__pos  # update rect to that location

    def __check_collisions(self) -> None:
        """
        Check for collision and kill the bullet if something is hit.
        """

        # player
        self.__check_player_hit()

        # laser receiver
        self.__check_receiver_hit()

    def __check_player_hit(self) -> None:
        """
        Check if player is hit.
        """
        if pg.sprite.collide_mask(self, self.__player):
            self.kill()
            self.__player.hurt(self.__damage)
            play_sound(self.game.main_menu.player_hit_sound_on, self.game.main_menu.player_hit_sound)
            # game over message
            self.__player.set_dead_message('laser gun')

    def __check_receiver_hit(self) -> None:
        """
        Check if laser receiver is hit.
        """
        if pg.sprite.spritecollide(self, self.game.laser_receivers, False, pg.sprite.collide_mask):
            self.kill()


class LaserBeam(pg.sprite.Sprite):
    """
    Creates laser beam.
    Laser beam position is set in Tiled editor.
    """

    def __init__(self, game, x: float, y: float, width: float, height: float, laser_type: str):
        """
        Make a laser beam.
        :param game: game
        :param x: x position to spawn
        :param y: y position to spawn
        :param width: laser beam width
        :param height: laser beam height
        :param laser_type: type of laser beam (by color)
        """

        self._layer = LAYERS['first']
        self.groups = game.all_sprites, game.lasers
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.__type = laser_type
        self.__laser_machines = self.game.laser_machines
        self.__player = self.game.player

        self.__x = x
        self.__y = y
        self.__width = width
        self.__height = height

        self.__damage = LASER_DAMAGE

        self.__make_laser_beam()

    def update(self) -> None:
        """
        Update the laser sprite.
        """
        # Check player collision
        if pg.sprite.spritecollide(self.__player, self.game.lasers, False, pg.sprite.collide_mask):
            play_sound(self.game.main_menu.laser_sound_on, self.game.main_menu.laser_sound)
            self.__player.hurt(self.__damage)
            # game over message
            self.__player.set_dead_message('laser')
        else:
            self.game.main_menu.laser_sound.stop()

    def __make_laser_beam(self) -> None:
        """
        Make laser beam.
        """
        self.__load_images()

        for machine in self.__laser_machines:
            # down red
            if machine.get_type() == 'down red':
                if self.__type == 'red':
                    self.image = self.red_laser
                    self.__adjust_position(self.image)

            # down blue
            if machine.get_type() == 'down blue':
                if self.__type == 'blue':
                    self.image = self.blue_laser
                    self.__adjust_position(self.image)

            # left green
            if machine.get_type() == 'left':
                if self.__type == 'green':
                    self.image = self.green_laser
                    self.__adjust_position(self.image)

            # right yellow
            if machine.get_type() == 'right':
                if self.__type == 'yellow':
                    self.image = self.yellow_laser
                    self.__adjust_position(self.image)

        self.mask = pg.mask.from_surface(self.image)

    def __adjust_position(self, image: pg.Surface) -> None:
        """
        Adjust laser beam image position (based on color).
        Color indicates if the laser is vertical or horizontal.
        :param image: laser beam image
        """
        self.rect = image.get_rect()
        if self.__type == 'red' or self.__type == 'blue':
            self.__x_offset = 27
            self.__y_offset = 4
        elif self.__type == 'green':
            self.__x_offset = 0
            self.__y_offset = 30
        elif self.__type == 'yellow':
            self.__x_offset = 4
            self.__y_offset = 33

        # set position
        self.rect.x = self.__x - self.__x_offset  # left-right position
        self.rect.y = self.__y - self.__y_offset  # up-down position

    def __load_images(self) -> None:
        """
        Load laser beam images.
        """
        load_img = pg.image.load

        # scale factor values
        scale_vertical = (int(self.__width * 12), int(self.__height + 4))
        scale_horizontal = (int(self.__height + 6), int(self.__width * 12))

        # load images
        red_img = load_img(RED_LASER_IMAGE).convert_alpha()
        blue_img = load_img(BLUE_LASER_IMAGE).convert_alpha()
        green_img = load_img(GREEN_LASER_IMAGE).convert_alpha()
        yellow_img = load_img(YELLOW_LASER_IMAGE).convert_alpha()

        # scale images
        self.red_laser = scale(red_img, scale_vertical)
        self.blue_laser = scale(blue_img, scale_vertical)
        self.green_laser = scale(green_img, scale_horizontal)
        self.yellow_laser = scale(yellow_img, scale_horizontal)

    def get_type(self) -> str:
        """
        Get laser beam type.
        :return: laser beam type
        """
        return self.__type


class LaserReceiver(pg.sprite.Sprite):
    """
    Creates laser receiver.
    "Collects" laser beam and laser bullets.
    Laser receiver position is set in Tiled editor.
    """

    def __init__(self, game, x: float, y: float, width: float, height: float, receiver_type: str):
        """
        Make a laser receiver.
        :param game: game
        :param x: x position to spawn
        :param y: y position to spawn
        :param width: laser receiver width
        :param height: laser receiver height
        :param receiver_type: type of receiver (down/left/right)
        """

        self._layer = LAYERS['first']
        self.groups = game.all_sprites, game.laser_receivers
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.__type = receiver_type

        self.__width = width
        self.__height = height
        self.__x = x
        self.__y = y

        self.__make_receiver()

    def __make_receiver(self) -> None:
        """
        Make laser receiver.
        """
        # load image
        receiver_img = pg.image.load(LASER_RECEIVER_IMAGE)

        down_image = scale(receiver_img, (int(self.__width), int(self.__height))).convert_alpha()
        right_image = pg.transform.rotate(down_image, 90)
        left_image = pg.transform.rotate(down_image, 270)

        # set image (based on type)
        if self.__type == 'down':
            self.image = down_image
            self.__adjust_image(self.image)
        elif self.__type == 'left':
            self.image = left_image
            self.__adjust_image(self.image, -12, 1)
        elif self.__type == 'right':
            self.image = right_image
            self.__adjust_image(self.image, -12)

        self.mask = pg.mask.from_surface(self.image)

    def __adjust_image(self, image: pg.Surface, offset_x: int = 0, offset_y: int = 0) -> None:
        """
        Adjust laser receiver image position.
        :param image: laser receiver image
        :param offset_x: x offset
        :param offset_y: y offset
        """
        self.rect = image.get_rect()
        self.rect.x = self.__x + offset_x
        self.rect.y = self.__y + offset_y


# interactive sprites
class DoorSwitch(pg.sprite.Sprite):
    """
    Creates door switch.
    Door switch position is set in Tiled editor.
    """

    def __init__(self, game, x: float, y: float, width: float, height: float):
        """
        Make a door switch.
        :param game: game
        :param x: x position to spawn
        :param y: y position to spawn
        :param width: door switch width
        :param height: door switch height
        """

        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)

        # references
        self.game = game
        self.__player = self.game.player
        self.__doors = self.game.doors

        self.__width = width
        self.__height = height

        # image
        self.__load_images()
        self.image = self.__disabled_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=(x, y))
        self.rect.x = x
        self.rect.y = y

        self.__UNLOCKED = False

        # load sounds settings
        self.__sound_on = self.game.main_menu.door_switch_sound_on
        self.__press_sound = self.game.main_menu.door_switch_press_sound
        self.__fail_sound = self.game.main_menu.door_switch_fail_sound

    def __load_images(self) -> None:
        """
        Load door switch images.
        """
        scale_factor = (int(self.__width), int(self.__height))

        # load images
        disabled_img = pg.image.load(DOOR_SWITCH_DISABLED_IMAGE).convert()
        enabled_img = pg.image.load(DOOR_SWITCH_ENABLED_IMAGE).convert()

        # set images
        self.__disabled_img = scale(disabled_img, scale_factor)
        self.__enabled_img = scale(enabled_img, scale_factor)

    def update(self) -> None:
        """
        Update the door switch.
        """
        # player-door switch collision
        if pg.sprite.collide_rect(self.__player, self):  # if player collides with the door switch
            keys = pg.key.get_pressed()

            # if interact key is pressed
            if keys[self.__player.get_control_key('interact')]:
                # if not unlocked (works only if locked)
                if not self.__UNLOCKED:
                    if self.__player.has_the_key():
                        self.__UNLOCKED = True  # unlocks door switch
                        play_sound(self.__sound_on, self.__press_sound)  # unlock sound
                        self.__player.add_points(DOOR_SWITCH_POINTS)
                        self.__player.remove_key()  # remove the key when used
                    else:
                        play_sound(self.__sound_on, self.__fail_sound)  # fail sound

        # if door switch is pressed (unlocked)
        if self.__UNLOCKED:
            self.image = self.__enabled_img
            for door in self.__doors:
                if door.get_type() == 'level_up':
                    door.unlock()  # unlock the door

    def is_unlocked(self) -> bool:
        """
        Is it unlocked or not.
        If key is picked up, it's unlocked.
        :return: True if unlocked, otherwise False
        """
        return self.__UNLOCKED


class Door(pg.sprite.Sprite):
    """
    Creates door.
    There are two type of doors:
        1. Level up door - when open, go to next level
        2. Disabled door - player spawns next to it; not usable
    Door position is set in Tiled editor.
    """

    def __init__(self, game, x: float, y: float, width: float, height: float, door_type: str):
        """
        Make a door.
        :param game: game
        :param x: x position to spawn
        :param y: y position to spawn
        :param width: door width
        :param height: door height
        :param door_type: type of door (level-up/disabled)
        """

        self.groups = game.all_sprites, game.doors
        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = game
        self.__player = self.game.player

        self.__type = door_type

        self.__width = width
        self.__height = height

        # image
        self.__load_images()
        self.image = self.__locked_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=(x, y))
        self.rect.x = x
        self.rect.y = y

        self.__UNLOCKED = False
        self.__OPEN = False

        # load sounds
        self.__open_sound_on = self.game.main_menu.door_open_sound_on
        self.__open_sound = self.game.main_menu.door_open_sound

    def __load_images(self) -> None:
        """
        Load door images.
        """
        load_img = pg.image.load
        scale_by = (int(self.__width), int(self.__height))

        # load images
        locked_img = load_img(DOOR_LOCKED_IMAGE).convert()
        unlocked_img = load_img(DOOR_UNLOCKED_IMAGE).convert()
        opened_img = load_img(DOOR_OPEN_IMAGE).convert()

        # set images
        self.__locked_img = scale(locked_img, scale_by)
        self.__unlocked_img = scale(unlocked_img, scale_by)
        self.__opened_img = scale(opened_img, scale_by)

    def update(self) -> None:
        """
        Update the door sprite.
        """
        if self.__type == 'level_up':
            self.game.level_up = False  # fix level up bug

        # player-door collision
        if self.__type == 'level_up':
            # if door is unlocked
            if self.__UNLOCKED:
                self.image = self.__unlocked_img

                # check player collision
                if pg.sprite.collide_rect(self.__player, self):
                    keys = pg.key.get_pressed()
                    # allow click if player not dead
                    if self.__player.get_health() > 0:
                        # if interact key is pressed
                        if keys[self.__player.get_control_key('interact')]:
                            # only if not already open, play the door open sound
                            if not self.__OPEN:
                                play_sound(self.__open_sound_on, self.__open_sound)
                                self.__OPEN = True  # opens the door

            # if door is open
            if self.__OPEN:
                self.image = self.__opened_img
                # check player collision
                if pg.sprite.collide_rect(self.__player, self):
                    keys = pg.key.get_pressed()
                    # allow click if player not dead (fix next level bug)
                    if self.__player.get_health() > 0:
                        if keys[self.__player.get_control_key('open')]:  # if open key is pressed
                            self.game.level_up = True  # go to next level
                            self.__player.add_points(NEXT_LEVEL_POINTS)

    def get_type(self) -> str:
        """
        Get door type (level-up/disabled).
        :return: door type
        """
        return self.__type

    def unlock(self) -> None:
        """
        Unlock the door.
        Unlocked when door switch is pressed (key required).
        """
        self.__UNLOCKED = True


class Lever(pg.sprite.Sprite):
    """
    Creates laser machine lever.
    Turns off laser beams.
    Lever position is set in Tiled editor.
    """

    def __init__(self, game, x: float, y: float, width: float, height: float, lever_type: str):
        """
        Make a lever.
        :param game: game
        :param x: x position to spawn
        :param y: y position to spawn
        :param width: lever width
        :param height: lever height
        :param lever_type: lever type (by color)
        """

        self.groups = game.all_sprites, game.levers
        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.__type = lever_type
        self.__width = width
        self.__height = height

        self.__pulled = False

        # image
        self.__make_lever()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.mask = pg.mask.from_surface(self.image)

        # load sounds
        self.__pull_sound_on = game.main_menu.lever_pull_sound_on
        self.__pull_sound = game.main_menu.lever_pull_sound

    def update(self) -> None:
        """
        Update the lever sprite.
        """
        # check if lever is pulled
        self.__check_if_lever_pulled()

        # if lever is pulled, set it to off
        if self.__pulled:
            self.__set_off_image()

    def __make_lever(self) -> None:
        """
        Make lever based on type.
        Lever type is color, it indicates which laser machine the lever is for.
        """
        self.__load_images()

        # red
        if self.__type == 'red':
            self.image = self.__red_lever_on_img
        # blue
        elif self.__type == 'blue':
            self.image = self.__blue_lever_on_img
        # green
        elif self.__type == 'green':
            self.image = self.__green_lever_on_img
        # yellow
        else:
            self.image = self.__yellow_lever_on_img

    def __load_images(self) -> None:
        """
        Load lever images.
        """
        load_img = pg.image.load
        scale_factor = (int(self.__width), int(self.__height))

        # load images
        blue_lever_on = load_img(BLUE_LEVER_ON_IMAGE).convert_alpha()
        blue_lever_off = load_img(BLUE_LEVER_OFF_IMAGE).convert_alpha()
        red_lever_on = load_img(RED_LEVER_ON_IMAGE).convert_alpha()
        red_lever_off = load_img(RED_LEVER_OFF_IMAGE).convert_alpha()
        green_lever_on = load_img(GREEN_LEVER_ON_IMAGE).convert_alpha()
        green_lever_off = load_img(GREEN_LEVER_OFF_IMAGE).convert_alpha()
        yellow_lever_on = load_img(YELLOW_LEVER_ON_IMAGE).convert_alpha()
        yellow_lever_off = load_img(YELLOW_LEVER_OFF_IMAGE).convert_alpha()

        # set images
        self.__blue_lever_on_img = scale(blue_lever_on, scale_factor)
        self.__blue_lever_off_img = scale(blue_lever_off, scale_factor)
        self.__red_lever_on_img = scale(red_lever_on, scale_factor)
        self.__red_lever_off_img = scale(red_lever_off, scale_factor)
        self.__green_lever_on_img = scale(green_lever_on, scale_factor)
        self.__green_lever_off_img = scale(green_lever_off, scale_factor)
        self.__yellow_lever_on_img = scale(yellow_lever_on, scale_factor)
        self.__yellow_lever_off_img = scale(yellow_lever_off, scale_factor)

    def __set_off_image(self) -> None:
        """
        Set lever off image (when pulled).
        """
        # red
        if self.__type == 'red':
            self.image = self.__red_lever_off_img
        # blue
        elif self.__type == 'blue':
            self.image = self.__blue_lever_off_img
        # green
        elif self.__type == 'green':
            self.image = self.__green_lever_off_img
        # yellow
        else:
            self.image = self.__yellow_lever_off_img

    def __check_if_lever_pulled(self) -> None:
        """
        Check if lever is pulled.
        """
        keys = pg.key.get_pressed()
        levers_touched = pg.sprite.spritecollide(self.game.player, self.game.levers, False, pg.sprite.collide_mask)
        for lever in levers_touched:
            # if interact key is pressed
            if keys[self.game.player.get_control_key('interact')]:
                # if not already pulled
                if not lever.__pulled:
                    play_sound(self.__pull_sound_on, self.__pull_sound)  # play pull sound

                    # turn off the laser machine & kill the laser
                    for laser_machine in self.game.laser_machines:
                        for laser in self.game.lasers:

                            # blue lever - blue laser
                            if lever.__type == 'blue':
                                lever.__pulled = True
                                if laser_machine.get_type() == 'down blue':
                                    if laser.get_type() == 'blue':
                                        self.__turn_laser_off(laser_machine, laser)

                            # red lever - red laser
                            elif lever.__type == 'red':
                                lever.__pulled = True
                                if laser_machine.get_type() == 'down red':
                                    if laser.get_type() == 'red':
                                        self.__turn_laser_off(laser_machine, laser)

                            # green lever - green laser
                            elif lever.__type == 'green':
                                lever.__pulled = True
                                if laser_machine.get_type() == 'left':
                                    if laser.get_type() == 'green':
                                        self.__turn_laser_off(laser_machine, laser)

                            # yellow lever - yellow laser
                            elif lever.__type == 'yellow':
                                lever.__pulled = True
                                if laser_machine.get_type() == 'right':
                                    if laser.get_type() == 'yellow':
                                        self.__turn_laser_off(laser_machine, laser)

    @staticmethod
    def __turn_laser_off(laser_machine: LaserMachine, laser_beam: LaserBeam) -> None:
        """
        Turn off the laser machine & kill the laser.
        :param laser_machine: laser machine to turn off
        :param laser_beam: laser beam to kill
        """
        laser_machine.turn_off()
        laser_beam.kill()


class Item(pg.sprite.Sprite):
    """
    Creates items.
    There are 4 items:
        1. Health pack
        2. XP
        3. Coin
        4. Key
    Each item is for player to pick up.
    Item position is set in Tiled editor.
    """

    def __init__(self, game, pos: vec, item_type: str):
        """
        Make an item.
        :param game: game
        :param pos: item position to spawn
        :param item_type: item type (health, xp, coin, key)
        """

        self._layer = LAYERS['first']
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)

        self.__type = item_type  # item type is item name in tiled
        self.__pos = pos

        # spawn
        self.__spawn_item()
        self.rect = self.image.get_rect()
        self.rect.center = pos

        # animations
        self.__tween = easeInOutSine  # up-down animation
        self.__step = 0  # keep track of where it is between 0 and 1 (start and end point)
        self.__direction = 1  # bob up, and then bob down (changes between 1 and -1)
        self.__last_update = 0
        self.__current_frame = 0

    def update(self) -> None:
        """
        Update the item sprite.
        """
        self.__animate()

    def __spawn_item(self) -> None:
        """
        Spawn an item based on their type.
        """
        self.__load_images()

        # spawn item by type
        if self.__type == 'health':
            self.image = self.__health_pack_image
        elif self.__type == 'xp':
            self.image = self.__xp_image
        elif self.__type == 'coin':
            self.image = self.__coin_images[0]
        elif self.__type == 'key':
            self.image = self.__key_img

        self.mask = pg.mask.from_surface(self.image)

    def __load_images(self) -> None:
        """
        Load items images.
        """
        load_img = pg.image.load

        # health pack
        self.__health_pack_image = scale(load_img(HEALTH_PACK_IMAGE), (22, 22)).convert_alpha()
        # xp
        self.__xp_image = load_img(XP_IMAGE).convert_alpha()
        # coin
        self.__coins = [load_img(img).convert_alpha() for img in COIN_IMAGES]
        self.__coin_images = [scale(img, (20, 20)) for img in self.__coins]
        # key
        self.__key_img = scale(load_img(KEY_IMAGE), (22, 22)).convert_alpha()

    def get_type(self) -> str:
        """
        Get item type.
        :return: item type
        """
        return self.__type

    # animations
    def __animate(self) -> None:
        """
        Do the appropriate animation for each type of item.
        """
        if self.__type in ('health', 'key', 'xp'):
            self.__bobbing_motion()
        elif self.__type == 'coin':
            self.__spin_coin()

    def __bobbing_motion(self) -> None:
        """
        Bobbing motion (up-down).
        """
        offset = BOB_RANGE * (self.__tween(self.__step / BOB_RANGE) - 0.5)
        self.rect.centery = self.__pos.y + offset * self.__direction  # when flips, goes in different direction
        self.__step += BOB_SPEED
        if self.__step > BOB_RANGE:
            self.__step = 0  # reset the step
            self.__direction *= -1  # reverse the direction

    def __spin_coin(self) -> None:
        """
        Coin spinning animation.
        """
        now = pg.time.get_ticks()
        if now - self.__last_update > 80:
            self.__last_update = now
            self.__current_frame = (self.__current_frame + 1) % len(self.__coin_images)
            self.image = self.__coin_images[self.__current_frame]


# obstacle
class Obstacle(pg.sprite.Sprite):
    """
    Creates obstacles.
    Obstacle positions are set in Tiled editor.
    """

    def __init__(self, game, x: float, y: float, width: float, height: float, obstacle_type: str):
        """
        Make an obstacle.
        :param game: game
        :param x: x position to spawn
        :param y: y position to spawn
        :param width: obstacle width
        :param height: obstacle height
        :param obstacle_type: obstacle type (ground, limit...)
        """

        self._layer = LAYERS['first']
        self.groups = game.obstacles
        pg.sprite.Sprite.__init__(self, self.groups)

        self.__type = obstacle_type

        # make obstacle rect
        self.rect = pg.Rect(x, y, width, height)

    def get_type(self) -> str:
        """
        Get obstacle type.
        :return: obstacle type
        """
        return self.__type
