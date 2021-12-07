# This game is made as part of the graduation work
# All resources used in the game are free
# Images downloaded from: https://www.kenney.nl/, https://www.gameart2d.com/freebies.html
# Icons (menu images) downloaded from: https://iconmonstr.com/, https://www.flaticon.com/
# Sounds downloaded from: https://freesound.org/


from os import environ

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame as pg
from pygame.math import Vector2 as vec

from .config import WIDTH, HEIGHT, FPS, TARGET_FPS, GAME_TITLE, MAP1, MAP2, MAP3, PAUSE_COLOR, TILE_COLOR, GREEN
from .images import PLAYER_SPRITE_SHEET, ZOMBIE_SPRITE_SHEET, EXPLOSION_SPRITE_SHEET
from .sounds import BG_MUSIC
from .menu import MainMenu, SettingsMenu, HighScoresMenu, HowToPlayMenu, CreditsMenu, ConfirmationMenu, PauseMenu, \
    GameOverMenu
from .spritesheet import SpriteSheet
from .tilemap import TiledMap, Camera
from .timer import GameTimer
from .sprites import Player, Zombie, Obstacle, Acid, Spikes, Saw, LaserMachine, LaserBeam, LaserReceiver, Door, \
    DoorSwitch, Lever, Item


class Game:
    """
    Main game class.
    """

    def __init__(self):
        """
        Initialize the game and all game related data.
        """

        # initialization
        pg.mixer.pre_init(44100, -16, 2, 4096)
        pg.init()

        # display
        self.__screen_size = (WIDTH, HEIGHT)
        self.display = pg.Surface(self.__screen_size)
        self.window = pg.display.set_mode(self.__screen_size, pg.FULLSCREEN)
        pg.display.set_caption(GAME_TITLE)

        # timer, clock...
        self.timer = pg.USEREVENT + 1
        self.__clock = pg.time.Clock()

        # sound channel
        self.__channel1 = pg.mixer.Channel(0)

        # flags
        self.running = True
        self.playing = False
        self.paused = False
        self.game_over = False
        self.click = False
        self.time_up = False
        self.level_up = False

        # ===== Menus =====
        self.main_menu = MainMenu(self)
        self.settings_menu = SettingsMenu(self)
        self.high_scores_menu = HighScoresMenu(self)
        self.how_to_play_menu = HowToPlayMenu(self)
        self.credits_menu = CreditsMenu(self)
        self.confirmation_menu = ConfirmationMenu(self)
        self.__pause_menu = PauseMenu(self)
        self.__game_over_menu = GameOverMenu(self)
        self.current_menu = self.main_menu

        # load all game data
        self.__load_data()

        # levels
        self.level = 1

    def __load_data(self) -> None:
        """
        Load game data (maps, sprite sheets...).
        """

        # maps
        self.__level_1_map = MAP1
        self.__level_2_map = MAP2
        self.__level_3_map = MAP3

        # sprite sheets
        self.player_sprite_sheet = SpriteSheet(PLAYER_SPRITE_SHEET, True)
        self.zombies_sprite_sheet = SpriteSheet(ZOMBIE_SPRITE_SHEET, True)
        self.explosion_sprite_sheet = SpriteSheet(EXPLOSION_SPRITE_SHEET)

        # dim screen image (pause menu)
        self.pause_dim_image = pg.Surface(self.__screen_size).convert_alpha()
        self.pause_dim_image.fill(PAUSE_COLOR)

        # default font
        self.default_font = pg.font.SysFont('Arial', 30)

        # load background music & set volume (plays if turned on in settings)
        pg.mixer.music.load(BG_MUSIC)
        pg.mixer.music.set_volume(0.5)

    def run(self) -> None:
        """
        Run the game.
        Main game loop.
        """

        # make game timer
        self.game_timer = GameTimer(self)

        self.playing = True
        if self.playing:
            self.__level_1()
            # play game music (if turned on in settings)
            if self.main_menu.game_music_on:
                pg.mixer.music.play(-1)

        while self.playing:
            self.delta_time = min(self.__clock.tick(FPS) * 0.001 * TARGET_FPS, 3)
            self.__events()  # manage events

            # not paused
            if not self.paused:
                # unpause game music and sounds
                pg.mixer.music.unpause()
                pg.mixer.unpause()

                # if not game over
                if not self.game_over:
                    self.__update()  # update
            # paused
            else:
                self.__pause_menu.display_menu()  # display pause menu

            # draw everything
            self.__draw()

    def __events(self) -> None:
        """
        Manage game events.
        """
        for event in pg.event.get():
            # quit game
            if event.type == pg.QUIT:
                self.quit_game()

            # game timer
            if event.type == self.timer:
                self.game_timer.countdown()

            # key down
            if event.type == pg.KEYDOWN:
                pressed_keys = pg.key.get_pressed()

                # quit game (alt-f4)
                if event.key == pg.K_F4 and (pressed_keys[pg.K_LALT] or pressed_keys[pg.K_RALT]):
                    self.quit_game()

                # pause
                if self.playing and not self.game_over:
                    if event.key == pg.K_ESCAPE:
                        self.paused = not self.paused

                # player movement (jump & slide)
                if self.playing:
                    # jump
                    if event.key == self.player.get_control_key('jump'):
                        self.player.jump()
                    # slide
                    elif event.key == self.player.get_control_key('slide'):
                        self.player.slide()

            # key up
            if event.type == pg.KEYUP:
                if self.playing:
                    # short jump
                    if event.key == self.player.get_control_key('jump'):
                        self.player.jump_cut()

            # mouse click
            if event.type == pg.MOUSEBUTTONUP:
                # only when paused or game over
                if self.paused or self.game_over:
                    if event.button == 1:
                        self.click = True

    def __draw(self) -> None:
        """
        Draw everything.
        """
        # fill the screen
        self.display.fill(TILE_COLOR)

        # draw map
        self.display.blit(self.__map_img, self.__camera.apply_rect(self.__map_rect))

        # draw all sprites (& zombie health)
        for sprite in self.all_sprites:
            if isinstance(sprite, Zombie):
                sprite.draw_health()

            self.display.blit(sprite.image, self.__camera.apply(sprite))

        # drawing if not paused or game over
        if not self.paused and not self.game_over:
            # fps
            if self.__show_fps:
                self.__draw_fps()
            # player score
            if self.__show_score:
                self.player.draw_score()
            # player health bar
            if self.__show_health:
                self.player.draw_health()
            # gun bar
            if self.__show_gun_bar:
                self.player.draw_gun_bar()
            # game timer
            if self.__show_game_timer:
                self.game_timer.draw_timer()
        # draw game over menu
        elif self.game_over:
            self.__game_over_menu.display_menu()

        # draw everything
        self.window.blit(self.display, (0, 0))

        # update the display if not paused (fixes pause bug)
        if not self.paused:
            pg.display.update()

    def __update(self) -> None:
        """
        Main update function.
        """
        self.__check_level()  # check if next level
        self.all_sprites.update()  # update all sprites
        self.__camera.update(self.player)  # update the camera to follow player

    def quit_game(self) -> None:
        """
        Quit the game.
        """
        self.playing = False
        self.running = False
        pg.quit()
        exit()

    # ========== LEVEL FUNCTIONS ==========
    def __level_1(self) -> None:
        """
        Load level 1.
        """
        # set timer seconds
        self.game_timer.set_timer(180)

        # set flags
        self.__set_flags()

        # create groups
        self.__make_groups()

        # load the map & make a surface for it
        self.__make_level_map(TiledMap(self.__level_1_map))

        # spawn player
        self.__spawn_player()

        # spawn other sprites
        self.__spawn_sprites()

        # spawn camera
        self.__camera = Camera(self.__map.width, self.__map.height)

        # play level start sound
        self.__play_level_start_sound()

    def __level_2(self) -> None:
        """
        Load level 2.
        """
        # set timer seconds
        self.game_timer.set_timer(180)

        # get player health & score from previous level
        health, score = self.__get_player_data()

        # set flags
        self.__set_flags()

        # create groups
        self.__make_groups()

        # load the map & make a surface for it
        self.__make_level_map(TiledMap(self.__level_2_map))

        # spawn player
        self.__spawn_player()

        # set (keep) player's health & score
        self.__keep_player_data(health, score)

        # spawn other sprites
        self.__spawn_sprites()

        # spawn camera
        self.__camera = Camera(self.__map.width, self.__map.height)

        # play level start sound
        self.__play_level_start_sound()

    def __level_3(self) -> None:
        """
        Load level 3.
        """
        # Set timer seconds
        self.game_timer.set_timer(180)

        # get player health & score from previous level
        health, score = self.__get_player_data()

        # set flags
        self.__set_flags()

        # create groups
        self.__make_groups()

        # load the map & make a surface for it
        self.__make_level_map(TiledMap(self.__level_3_map))

        # spawn player
        self.__spawn_player()

        # set (keep) player's health & score
        self.__keep_player_data(health, score)

        # spawn other sprites
        self.__spawn_sprites()

        # spawn camera
        self.__camera = Camera(self.__map.width, self.__map.height)

        # play level start sound
        self.__play_level_start_sound()

    def __spawn_player(self) -> None:
        """
        Spawn player.
        Spawned separately from other objects to keep health & score in next levels.
        """
        for tile_object in self.__map.tmx_data.objects:
            object_center = vec(tile_object.x + tile_object.width / 2, tile_object.y + tile_object.height / 2)

            if tile_object.name == 'player':
                self.player = Player(self, object_center.x, object_center.y)

    def __get_player_data(self):
        """
        Get player's data (to keep in next levels).
        :return: player health & score
        """
        health = self.player.get_health()
        score = self.player.get_score()
        return health, score

    def __keep_player_data(self, health: int, score: int) -> None:
        """
        Keep player's data from previous levels.
        :param health: player health
        :param score: player score
        """
        self.player.keep_health(health)
        self.player.keep_score(score)

    def __set_flags(self) -> None:
        """
        Set flags (including settings flags) when starting a new level.
        Fixes certain bugs.
        """
        self.level_up = False
        self.click = False  # prevent accidental clicks after game over
        self.game_over = False  # fix game over bug after clicking new game
        self.time_up = False  # fix bug where 'Time is up' shows every time

        # settings flags (True if turned on in settings)
        self.__show_fps = self.main_menu.fps_on
        self.__show_score = self.main_menu.score_on
        self.__show_health = self.main_menu.health_on
        self.__show_gun_bar = self.main_menu.gun_bar_on
        self.__show_game_timer = self.main_menu.game_timer_on

        self.main_menu.burn_sound.stop()  # fix sound bug

    def __make_groups(self) -> None:
        """
        Create sprite groups.
        """
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.zombies = pg.sprite.Group()
        self.obstacles = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.laser_receivers = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.doors = pg.sprite.Group()
        self.acid = pg.sprite.Group()
        self.spikes = pg.sprite.Group()
        self.saws = pg.sprite.Group()
        self.laser_machines = pg.sprite.Group()
        self.lasers = pg.sprite.Group()
        self.levers = pg.sprite.Group()

    def __make_level_map(self, map_file: TiledMap) -> None:
        """
        Make a map.
        Load a map and make a surface for it.
        :param map_file: level map file
        """
        self.__map = map_file
        self.__map_img = self.__map.make_map()
        self.__map_rect = self.__map_img.get_rect()

    def __spawn_sprites(self) -> None:
        """
        Spawn sprites from tmx map (zombies, tiles, objects...).
        """
        for tile_object in self.__map.tmx_data.objects:
            x_pos = tile_object.x
            y_pos = tile_object.y
            width = tile_object.width
            height = tile_object.height
            object_type = tile_object.type
            object_center = vec(x_pos + width / 2, y_pos + height / 2)

            # obstacles - ground, screen limits and zombie boundaries
            if tile_object.name == 'obstacle':
                Obstacle(self, x_pos, y_pos, width, height, object_type)

            # zombies
            if tile_object.name == 'zombie':
                Zombie(self, object_center.x, object_center.y)

            # hazards
            if tile_object.name == 'acid':
                Acid(self, x_pos, y_pos, width, height)
            if tile_object.name == 'spikes':
                Spikes(self, x_pos, y_pos, width, height)
            if tile_object.name == 'saw':
                Saw(self, x_pos, y_pos, width, height, object_type)
            if tile_object.name == 'laser_machine':
                LaserMachine(self, x_pos, y_pos, width, height, object_type)
            if tile_object.name == 'laser_beam':
                LaserBeam(self, x_pos, y_pos, width, height, object_type)
            if tile_object.name == 'laser_receiver':
                LaserReceiver(self, x_pos, y_pos, width, height, object_type)

            # interactive sprites
            if tile_object.name == 'door':
                Door(self, x_pos, y_pos, width, height, object_type)
            if tile_object.name == 'door_switch':
                DoorSwitch(self, x_pos, y_pos, width, height)
            if tile_object.name == 'lever':
                Lever(self, x_pos, y_pos, width, height, object_type)

            # collectible items
            if tile_object.name in ('health', 'coin', 'key'):
                Item(self, object_center, tile_object.name)

    def __check_level(self) -> None:
        """
        Check if next level and change.
        """
        # changing levels
        if self.level_up:
            self.level += 1
            if self.level == 2:
                self.__level_2()
            elif self.level == 3:
                self.__level_3()
            else:
                self.__game_over_menu.set_game_completed()

    def __play_level_start_sound(self) -> None:
        """
        Play the level start sound.
        """
        if self.main_menu.level_start_sound_on:
            self.__channel1.play(self.main_menu.level_start_sound, loops=0)

    def __draw_fps(self) -> None:
        """
        Draw FPS on screen.
        """
        x = WIDTH / 2 + 730
        y = HEIGHT / 2 - 430
        fps = str(int(self.__clock.get_fps()))
        fps_text = self.default_font.render(fps, True, GREEN)
        self.display.blit(fps_text, (x, y))


game = Game()
