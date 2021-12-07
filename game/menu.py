from . import pg
from .config import VERSION, WIDTH, HEIGHT, GAME_TITLE, TITLE_FONT, FONT, SETTINGS_FILE, WHITE, RED, DARK_GREY, \
    SUBMENU_GREY, GAME_COMPLETED_POINTS
from .sounds import *
from .button import TextButton, VolumeControl, VolumeIndicator, MuteToggle, OnOffSwitch
import json


class Menu:
    """
    Parent menu class.
    """

    settings = {
        'left': 'a',
        'right': 'd',
        'jump': 'w',
        'slide': 's',
        'shoot': 'space',
        'interact': 'f',
        'open': 'e',
        'high_scores': {0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
        'game_music_on': True,
        'show_fps': True,
        'show_score': True,
        'show_health_bar': True,
        'show_gun_bar': True,
        'gun_upgrade_on': True,
        'show_game_timer': True,
        'menu_music_on': True,
        'menu_music_volume': 1.0,
        'menu_nav_sounds_on': True,
        'menu_nav_volume': 1.0,
        'switch_toggle_sound_on': True,
        'switch_toggle_volume': 1.0,
        'high_score_sound_on': True,
        'high_score_volume': 1.0,
        'game_over_music_on': True,
        'game_over_volume': 1.0,
        'level_start_sound_on': True,
        'level_start_volume': 1.0,
        'door_switch_sound_on': True,
        'door_switch_volume': 1.0,
        'door_open_sound_on': True,
        'door_open_volume': 1.0,
        'xp_coin_sound_on': True,
        'xp_coin_volume': 1.0,
        'health_pickup_sound_on': True,
        'health_pickup_volume': 1.0,
        'key_pickup_sound_on': True,
        'key_pickup_volume': 1.0,
        'lever_pull_sound_on': True,
        'lever_pull_volume': 1.0,
        'laser_sound_on': True,
        'laser_volume': 1.0,
        'burn_sound_on': True,
        'burn_volume': 1.0,
        'saw_sound_on': True,
        'saw_volume': 1.0,
        'explosion_sound_on': True,
        'explosion_volume': 1.0,
        'player_jump_sound_on': True,
        'player_jump_volume': 1.0,
        'player_hit_sound_on': True,
        'player_hit_volume': 1.0,
        'gun_sound_on': True,
        'gun_volume': 1.0,
        'zombie_hit_sound_on': True,
        'zombie_hit_volume': 1.0,
        'zombie_die_sound_on': True,
        'zombie_die_volume': 1.0,
        'zombie_moan_sound_on': True,
        'zombie_moan_volume': 1.0
    }

    def __init__(self, game):
        """
        Initialize menu.
        :param game: game
        """
        self.game = game

        self.mid_x = WIDTH / 2
        self.mid_y = HEIGHT / 2

        # for drawing
        self.game_display = self.game.display

        self.__load_settings()

        self.run_display = True
        self.click = False

    def draw_menu(self) -> None:
        """
        Draw menu on screen.
        """
        self.game.window.blit(self.game_display, (0, 0))
        pg.display.update()

    def check_menu_events(self) -> None:
        """
        Check menu events.
        """
        for event in pg.event.get():
            # quit
            if event.type == pg.QUIT:
                self.quit_menu()

            # key down
            if event.type == pg.KEYDOWN:
                pressed_keys = pg.key.get_pressed()

                # esc/backspace - go back
                if event.key == pg.K_ESCAPE or event.key == pg.K_BACKSPACE:
                    if self.game.current_menu != self.game.main_menu:
                        play_sound(self.game.main_menu.menu_nav_sounds_on, self.game.main_menu.menu_out_sound)
                        self.game.current_menu = self.game.main_menu

                # quit (alt-f4)
                if event.key == pg.K_F4 and (pressed_keys[pg.K_LALT] or pressed_keys[pg.K_RALT]):
                    self.quit_menu()

            # mouse click
            if event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    self.click = True

    def __make_text(self, text: str, font_name: pg.font.Font, size: int, color: tuple, pos: tuple) -> None:
        """
        Draw text on screen.
        :param text: text to draw
        :param font_name: font name
        :param size: font size
        :param color: font color
        :param pos: position (x, y)
        """
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (pos[0], pos[1])
        self.game.display.blit(text_surface, text_rect)

    def draw_text(self, text: str, size: int, shadow_color: tuple, main_color: tuple, offset: tuple) -> None:
        """
        Draw text with shadow effect.
        :param text: text to draw
        :param size: text size
        :param shadow_color: text shadow color
        :param main_color: main text color
        :param offset: X & Y offset
        """
        x = self.mid_x + offset[0]
        y = self.mid_y + offset[1]

        # font name
        if text == GAME_TITLE:
            font_name = TITLE_FONT
        else:
            font_name = FONT

        # make text with shadow
        self.__make_text(text, font_name, size, shadow_color, (x + 1, y + 1))
        self.__make_text(text, font_name, size, main_color, (x, y))

    def draw_buttons(self, buttons) -> None:
        """
        Draw buttons on screen.
        :param buttons: button or buttons tuple to draw
        """
        # many buttons (tuple)
        if type(buttons) is tuple:
            for button in buttons:
                button.draw(self.game_display)
        # one button
        else:
            buttons.draw(self.game_display)

    def quit_menu(self) -> None:
        """
        Quit menu & game.
        """
        self.run_display = False
        self.game.quit_game()

    # settings file
    def __load_settings(self) -> None:
        """
        Load the settings.json file.
        """
        try:
            with open(SETTINGS_FILE) as f:
                _settings = json.load(f)
        except FileNotFoundError:
            _settings = {}
        save_file = False

        for k, v in self.settings.items():
            try:
                self.settings[k] = _settings[k]
            except KeyError:
                save_file = True

        if save_file:
            self.save_settings()

    def save_settings(self) -> None:
        """
        Save settings.json file.
        """
        with open(SETTINGS_FILE, 'w') as fp:
            json.dump(self.settings, fp, indent=4)

    def save_scores(self, player_score: int) -> bool:
        """
        Save player score to settings.json file.
        :param player_score: player game score
        :return: True/False
        """
        scores = self.settings['high_scores']
        index = None
        for i, score in enumerate(scores):
            if player_score > score:
                index = i
                break
        if index is not None:
            scores.insert(index, player_score)
            scores.pop()
            self.save_settings()
            return True
        return False

    def get_high_score(self) -> int:
        """
        Get high score.
        :return: highest score
        """
        return max(self.settings['high_scores'])


class MainMenu(Menu):
    """
    Main menu.
    Displays when the game is started.
    """

    def __init__(self, game):
        """
        Make the main menu.
        :param game: game
        """

        super().__init__(game)

        self.accidental_click = False  # fix accidental clicks bug

        # make buttons
        self.__initialize_buttons()

        # load settings
        self.__load_settings()

        # initialize sounds
        self.__init_sounds()

        # play menu music
        if self.menu_music_on:
            self.menu_music.play(-1)

    def display_menu(self) -> None:
        """
        Display menu.
        """
        self.run_display = True
        while self.run_display:
            self.check_menu_events()
            self.game_display.fill(DARK_GREY)
            self.__draw_buttons_and_text()
            self.__check_clicks()
            self.draw_menu()

    def __initialize_buttons(self) -> None:
        """
        Make main menu buttons.
        """
        # buttons
        self.start_game_btn = TextButton('Start game', 50, (0, -60))
        self.settings_btn = TextButton('Settings', 50, (0, 0))
        self.high_scores_btn = TextButton('High Scores', 50, (0, 60))
        self.how_to_play_btn = TextButton('How to play', 50, (0, 120))
        self.credits_btn = TextButton('Credits', 50, (0, 180))
        self.quit_btn = TextButton('Quit', 50, (0, 240))

        # all buttons
        self.buttons = (self.start_game_btn,
                        self.settings_btn,
                        self.high_scores_btn,
                        self.how_to_play_btn,
                        self.credits_btn,
                        self.quit_btn)

    def __draw_buttons_and_text(self) -> None:
        """
        Draw main menu buttons and text.
        """
        # draw game title
        self.draw_text(GAME_TITLE, 130, WHITE, RED, (0, -300))

        # draw buttons
        self.draw_buttons(self.buttons)

        # draw if restart required
        if self.game.settings_menu.restart_required:
            self.draw_text('Restart required to play the game', 40, WHITE, RED, (0, 300))

        # draw game version
        self.draw_text(VERSION, 20, RED, WHITE, (720, 400))

    def __check_clicks(self) -> None:
        """
        Check main menu clicks.
        """
        self.accidental_click = False  # fix accidental clicks bug

        for button in self.buttons:
            if button.rect.collidepoint(pg.mouse.get_pos()):
                button.hovered = True

                if not self.accidental_click:  # allow clicks only if not coming from game over menu
                    # start game
                    if button == self.start_game_btn:
                        if self.click:
                            if not self.game.settings_menu.restart_required:
                                self.game.level = 1  # ensure level is 1 on new game start
                                self.menu_music.stop()  # stop menu music
                                self.game.run()  # run the game

                    # settings
                    if button == self.settings_btn:
                        if self.click:
                            play_sound(self.menu_nav_sounds_on, self.menu_in_sound)
                            self.game.current_menu = self.game.settings_menu

                    # high scores
                    if button == self.high_scores_btn:
                        if self.click:
                            play_sound(self.menu_nav_sounds_on, self.menu_in_sound)
                            self.game.current_menu = self.game.high_scores_menu

                    # how to play
                    if button == self.how_to_play_btn:
                        if self.click:
                            play_sound(self.menu_nav_sounds_on, self.menu_in_sound)
                            self.game.current_menu = self.game.how_to_play_menu

                    # credits
                    if button == self.credits_btn:
                        if self.click:
                            play_sound(self.menu_nav_sounds_on, self.menu_in_sound)
                            self.game.current_menu = self.game.credits_menu

                    # quit
                    if button == self.quit_btn:
                        if self.click:
                            play_sound(self.menu_nav_sounds_on, self.menu_in_sound)
                            self.game.current_menu = self.game.confirmation_menu
            else:
                button.hovered = False

        self.click = False
        self.run_display = False

    # loading from settings.json
    def __load_settings(self) -> None:
        """
        Load game settings from settings.json file.
        """
        # settings flags
        self.game_music_on = self.settings['game_music_on']
        self.fps_on = self.settings['show_fps']
        self.score_on = self.settings['show_score']
        self.health_on = self.settings['show_health_bar']
        self.gun_bar_on = self.settings['show_gun_bar']
        self.gun_upgrade_on = self.settings['gun_upgrade_on']
        self.game_timer_on = self.settings['show_game_timer']

        # sound, volume & controls settings
        self.__load_sound_flags()
        self.__load_sound_volumes()
        self.__load_controls()

    def __load_sound_flags(self) -> None:
        """
        Load sounds flags from settings.json.
        """
        # general sounds
        self.menu_music_on = self.settings['menu_music_on']
        self.menu_nav_sounds_on = self.settings['menu_nav_sounds_on']
        self.switch_toggle_sound_on = self.settings['switch_toggle_sound_on']
        self.high_score_sound_on = self.settings['high_score_sound_on']
        self.game_over_music_on = self.settings['game_over_music_on']
        self.level_start_sound_on = self.settings['level_start_sound_on']

        # game sfx
        self.door_switch_sound_on = self.settings['door_switch_sound_on']
        self.door_open_sound_on = self.settings['door_open_sound_on']
        self.xp_coin_sound_on = self.settings['xp_coin_sound_on']
        self.health_pickup_sound_on = self.settings['health_pickup_sound_on']
        self.key_pickup_sound_on = self.settings['key_pickup_sound_on']
        self.lever_pull_sound_on = self.settings['lever_pull_sound_on']
        self.laser_sound_on = self.settings['laser_sound_on']
        self.burn_sound_on = self.settings['burn_sound_on']
        self.saw_sound_on = self.settings['saw_sound_on']
        self.explosion_sound_on = self.settings['explosion_sound_on']

        # sprites sounds
        self.player_jump_sound_on = self.settings['player_jump_sound_on']
        self.player_hit_sound_on = self.settings['player_hit_sound_on']
        self.gun_sound_on = self.settings['gun_sound_on']
        self.zombie_hit_sound_on = self.settings['zombie_hit_sound_on']
        self.zombie_die_sound_on = self.settings['zombie_die_sound_on']
        self.zombie_moan_sound_on = self.settings['zombie_moan_sound_on']

    def __load_sound_volumes(self) -> None:
        """
        Load sound volumes from settings.json.
        """
        # general sounds volumes
        self.menu_music_volume = self.settings['menu_music_volume']
        self.menu_nav_volume = self.settings['menu_nav_volume']
        self.switch_toggle_volume = self.settings['switch_toggle_volume']
        self.high_score_volume = self.settings['high_score_volume']
        self.game_over_volume = self.settings['game_over_volume']
        self.level_start_volume = self.settings['level_start_volume']

        # game sfx volumes
        self.door_switch_sound_volume = self.settings['door_switch_volume']
        self.door_open_sound_volume = self.settings['door_open_volume']
        self.xp_coin_sound_volume = self.settings['xp_coin_volume']
        self.health_pickup_sound_volume = self.settings['health_pickup_volume']
        self.key_pickup_sound_volume = self.settings['key_pickup_volume']
        self.lever_pull_sound_volume = self.settings['lever_pull_volume']
        self.laser_sound_volume = self.settings['laser_volume']
        self.burn_sound_volume = self.settings['burn_volume']
        self.saw_sound_volume = self.settings['saw_volume']
        self.explosion_sound_volume = self.settings['explosion_volume']

        # sprites sounds volumes
        self.player_jump_sound_volume = self.settings['player_jump_volume']
        self.player_hit_sound_volume = self.settings['player_hit_volume']
        self.gun_sound_volume = self.settings['gun_volume']
        self.zombie_hit_sound_volume = self.settings['zombie_hit_volume']
        self.zombie_die_sound_volume = self.settings['zombie_die_volume']
        self.zombie_moan_sounds_volume = self.settings['zombie_moan_volume']

    def __load_controls(self) -> None:
        """
        Load controls from settings.json.
        """
        self.jump_key = self.settings['jump']
        self.right_key = self.settings['right']
        self.left_key = self.settings['left']
        self.slide_key = self.settings['slide']
        self.shoot_key = self.settings['shoot']
        self.interact_key = self.settings['interact']
        self.open_key = self.settings['open']

        self.controls = (self.jump_key,
                         self.right_key,
                         self.left_key,
                         self.slide_key,
                         self.shoot_key,
                         self.interact_key,
                         self.open_key)

    # initialize sounds
    def __init_sounds(self) -> None:
        """
        Make sounds and set their starting volume (based on settings.json).
        """
        # general sounds
        self.menu_music = pg.mixer.Sound(MENU_MUSIC)
        self.menu_in_sound = pg.mixer.Sound(MENU_IN_SOUND)
        self.menu_out_sound = pg.mixer.Sound(MENU_OUT_SOUND)
        self.switch_toggle_sound = pg.mixer.Sound(SWITCH_TOGGLE_SOUND)
        self.high_score_sound = pg.mixer.Sound(HIGH_SCORE_SOUND)
        self.game_over_music = pg.mixer.Sound(GAME_OVER_MUSIC)
        self.level_start_sound = pg.mixer.Sound(LEVEL_START_SOUND)

        # game sfx
        self.door_switch_press_sound = pg.mixer.Sound(DOOR_SWITCH_PRESS_SOUND)
        self.door_switch_fail_sound = pg.mixer.Sound(DOOR_SWITCH_FAIL_SOUND)
        self.door_open_sound = pg.mixer.Sound(DOOR_OPEN_SOUND)
        self.xp_pickup_sound = pg.mixer.Sound(XP_PICKUP_SOUND)
        self.coin_pickup_sound = pg.mixer.Sound(COIN_PICKUP_SOUND)
        self.health_pickup_sound = pg.mixer.Sound(HEALTH_PICKUP_SOUND)
        self.key_pickup_sound = pg.mixer.Sound(KEY_PICKUP_SOUND)
        self.lever_pull_sound = pg.mixer.Sound(LEVER_PULL_SOUND)
        self.laser_sound = pg.mixer.Sound(LASER_SOUND)
        self.laser_gun_sound = pg.mixer.Sound(LASER_GUN_SOUND)
        self.burn_sound = pg.mixer.Sound(BURN_SOUND)
        self.saw_sound = pg.mixer.Sound(SAW_SOUND)
        self.explosion_sound = pg.mixer.Sound(EXPLOSION_SOUND)

        # sprites sounds
        self.player_jump_sound = pg.mixer.Sound(PLAYER_JUMP_SOUND)
        self.player_hit_sound = pg.mixer.Sound(PLAYER_HIT_SOUND)
        self.gun_sound = pg.mixer.Sound(GUN_SOUND)
        self.zombie_hit_sound = pg.mixer.Sound(ZOMBIE_HIT_SOUND)
        self.zombie_die_sound = pg.mixer.Sound(ZOMBIE_DIE_SOUND)
        self.zombie_moan_sounds = [pg.mixer.Sound(sound) for sound in ZOMBIE_MOAN_SOUNDS]

        # set volumes for sounds
        self.__set_volumes()

    def __set_volumes(self) -> None:
        """
        Set volume for all sounds based on settings.json file.
        """
        # general sounds
        self.menu_music.set_volume(self.menu_music_volume)
        self.menu_in_sound.set_volume(self.menu_nav_volume)
        self.menu_out_sound.set_volume(self.menu_nav_volume)
        self.switch_toggle_sound.set_volume(self.switch_toggle_volume)
        self.high_score_sound.set_volume(self.high_score_volume)
        self.game_over_music.set_volume(self.game_over_volume)
        self.level_start_sound.set_volume(self.level_start_volume)

        # game sfx
        self.door_switch_press_sound.set_volume(self.door_switch_sound_volume)
        self.door_switch_fail_sound.set_volume(self.door_switch_sound_volume)
        self.door_open_sound.set_volume(self.door_open_sound_volume)
        self.xp_pickup_sound.set_volume(self.xp_coin_sound_volume)
        self.coin_pickup_sound.set_volume(self.xp_coin_sound_volume)
        self.health_pickup_sound.set_volume(self.health_pickup_sound_volume)
        self.key_pickup_sound.set_volume(self.key_pickup_sound_volume)
        self.lever_pull_sound.set_volume(self.lever_pull_sound_volume)
        self.laser_sound.set_volume(self.laser_sound_volume)
        self.laser_gun_sound.set_volume(self.laser_sound_volume)
        self.burn_sound.set_volume(self.burn_sound_volume)
        self.saw_sound.set_volume(self.saw_sound_volume)
        self.explosion_sound.set_volume(self.explosion_sound_volume)

        # sprites sounds
        self.player_jump_sound.set_volume(self.player_jump_sound_volume)
        self.player_hit_sound.set_volume(self.player_hit_sound_volume)
        self.gun_sound.set_volume(self.gun_sound_volume)
        self.zombie_hit_sound.set_volume(self.zombie_hit_sound_volume)
        self.zombie_die_sound.set_volume(self.zombie_die_sound_volume)
        for sound in self.zombie_moan_sounds:
            sound.set_volume(self.zombie_moan_sounds_volume)


class SettingsMenu(Menu):
    """
    Settings menu.
    """

    def __init__(self, game):
        """
        Make the settings menu.
        :param game: game
        """

        super().__init__(game)

        self.main_menu = self.game.main_menu

        # initialize buttons
        self.back_btn = TextButton('Back', 50, (0, 360))
        self.__initialize_tabs()  # tabs for switching settings (left side)
        self.__initialize_general_settings_buttons()
        self.__initialize_sounds_settings_buttons()
        self.__initialize_controls_settings_buttons()

        # set default active tab & sub tab
        self.active_tab = self.general_settings_menu_tab
        self.active_sub_tab = self.general_sounds_submenu

        # control changing
        self.changing_control = False  # when changing control (on click)
        self.button_changing = []  # list of buttons being changed
        self.error_changing = False  # True if error occurred when changing control
        self.restart_required = False  # True if control is changed

    def display_menu(self) -> None:
        """
        Display settings menu.
        """
        self.run_display = True
        while self.run_display:
            self.check_menu_events()
            self.game_display.fill(DARK_GREY)
            self.__draw_buttons_and_text()
            self.__check_clicks()
            self.draw_menu()
            self.__check_for_control_change()

    def __check_clicks(self) -> None:
        """
        Main function for checking clicks.
        """
        # check for active tab (default button events)
        self.__check_tabs_clicks()

        # back button
        if self.back_btn.rect.collidepoint(pg.mouse.get_pos()):
            self.back_btn.hovered = True
            if self.click:
                play_sound(self.main_menu.menu_nav_sounds_on, self.main_menu.menu_out_sound)
                self.game.current_menu = self.game.main_menu
        else:
            self.back_btn.hovered = False

        # check for current active tab and clicks only if the submenu is showing
        if self.active_tab == self.general_settings_menu_tab:
            self.general_settings_menu_tab.hovered = True  # make it red if active
            self.__check_general_settings_clicks()
        elif self.active_tab == self.sounds_settings_menu_tab:
            self.sounds_settings_menu_tab.hovered = True  # make it red if active
            self.__check_sound_settings_clicks()
        elif self.active_tab == self.controls_settings_menu_tab:
            self.controls_settings_menu_tab.hovered = True  # make it red if active
            self.__check_controls_settings_clicks()

        self.click = False
        self.run_display = False

    # default tabs
    def __initialize_tabs(self) -> None:
        """
        Initialize tabs buttons (left side).
        """
        # make tabs buttons (left side)
        self.general_settings_menu_tab = TextButton('General', 40, (-647, -100))
        self.sounds_settings_menu_tab = TextButton('Sounds', 40, (-650, 0))
        self.controls_settings_menu_tab = TextButton('Controls', 40, (-633, 100))

        # all tabs
        self.all_tabs = (self.general_settings_menu_tab,
                         self.sounds_settings_menu_tab,
                         self.controls_settings_menu_tab)

    def __check_tabs_clicks(self) -> None:
        """
        Checks for default tabs (button) clicks, settings menu navigation.
        """
        # tabs navigation
        for button in self.all_tabs:
            if button.rect.collidepoint(pg.mouse.get_pos()):
                button.hovered = True

                # general settings
                if button == self.general_settings_menu_tab:
                    if self.click:
                        play_sound(self.main_menu.menu_nav_sounds_on, self.main_menu.menu_in_sound)
                        self.active_tab = self.general_settings_menu_tab

                # sounds settings
                if button == self.sounds_settings_menu_tab:
                    if self.click:
                        play_sound(self.main_menu.menu_nav_sounds_on, self.main_menu.menu_in_sound)
                        self.active_tab = self.sounds_settings_menu_tab

                # controls settings
                if button == self.controls_settings_menu_tab:
                    if self.click:
                        play_sound(self.main_menu.menu_nav_sounds_on, self.main_menu.menu_in_sound)
                        self.active_tab = self.controls_settings_menu_tab
            else:
                button.hovered = False

    # general settings
    def __initialize_general_settings_buttons(self) -> None:
        """
        Make general settings buttons.
        """
        # game music
        self.game_music_btn = TextButton('Game music', 50, (-100, -255))
        self.game_music_switch = OnOffSwitch(self.main_menu.game_music_on, (220, -250))

        # fps
        self.show_fps_btn = TextButton('Show FPS', 50, (-100, -170))
        self.show_fps_switch = OnOffSwitch(self.main_menu.fps_on, (220, -165))

        # score
        self.show_score_btn = TextButton('Score', 50, (-100, -85))
        self.show_score_switch = OnOffSwitch(self.main_menu.score_on, (220, -80))

        # player health bar
        self.show_health_btn = TextButton('Health bar', 50, (-100, 0))
        self.show_health_switch = OnOffSwitch(self.main_menu.health_on, (220, 5))

        # gun bar
        self.show_gun_bar_btn = TextButton('Gun bar', 50, (-100, 85))
        self.show_gun_bar_switch = OnOffSwitch(self.main_menu.gun_bar_on, (220, 90))

        # gun upgrade
        self.gun_upgrade_btn = TextButton('Gun upgrade', 50, (-100, 170))
        self.gun_upgrade_switch = OnOffSwitch(self.main_menu.gun_upgrade_on, (220, 175))

        # game timer
        self.show_game_timer_btn = TextButton('Game timer', 50, (-100, 255))
        self.show_game_timer_switch = OnOffSwitch(self.main_menu.game_timer_on, (220, 260))

        # all buttons in general settings (for drawing)
        self.all_general_settings_buttons = (self.game_music_btn,
                                             self.show_fps_btn,
                                             self.show_score_btn,
                                             self.show_health_btn,
                                             self.show_gun_bar_btn,
                                             self.gun_upgrade_btn,
                                             self.show_game_timer_btn,
                                             self.game_music_switch,
                                             self.show_fps_switch,
                                             self.show_score_switch,
                                             self.show_health_switch,
                                             self.show_gun_bar_switch,
                                             self.gun_upgrade_switch,
                                             self.show_game_timer_switch)
        # switches
        self.on_off_switches = (self.game_music_switch,
                                self.show_fps_switch,
                                self.show_score_switch,
                                self.show_health_switch,
                                self.show_gun_bar_switch,
                                self.gun_upgrade_switch,
                                self.show_game_timer_switch)

    def __check_general_settings_clicks(self) -> None:
        """
        Check general settings clicks.
        """
        # on-off switches
        for switch in self.on_off_switches:
            pos = pg.mouse.get_pos()
            pos_in_mask = pos[0] - switch.rect.x, pos[1] - switch.rect.y
            hovering = switch.rect.collidepoint(*pos) and switch.mask.get_at(pos_in_mask)
            if hovering:
                switch.hovered = True

                # game music switch
                if switch == self.game_music_switch:
                    if self.click:
                        switch.flip_switch()
                        play_sound(self.main_menu.switch_toggle_sound_on, self.main_menu.switch_toggle_sound)
                        if switch.switched_on:
                            self.main_menu.game_music_on = True
                            self.settings['game_music_on'] = True
                            self.save_settings()
                        else:
                            self.main_menu.game_music_on = False
                            self.settings['game_music_on'] = False
                            self.save_settings()

                # fps switch
                if switch == self.show_fps_switch:
                    if self.click:
                        switch.flip_switch()
                        play_sound(self.main_menu.switch_toggle_sound_on, self.main_menu.switch_toggle_sound)
                        if switch.switched_on:
                            self.main_menu.fps_on = True
                            self.settings['show_fps'] = True
                            self.save_settings()
                        else:
                            self.main_menu.fps_on = False
                            self.settings['show_fps'] = False
                            self.save_settings()

                # score switch
                if switch == self.show_score_switch:
                    if self.click:
                        switch.flip_switch()
                        play_sound(self.main_menu.switch_toggle_sound_on, self.main_menu.switch_toggle_sound)
                        if switch.switched_on:
                            self.main_menu.score_on = True  # flip the button
                            self.settings['show_score'] = True  # change in settings.json
                            self.save_settings()
                        else:
                            self.main_menu.score_on = False  # flip the button
                            self.settings['show_score'] = False  # change in settings.json
                            self.save_settings()

                # health switch
                if switch == self.show_health_switch:
                    if self.click:
                        switch.flip_switch()
                        play_sound(self.main_menu.switch_toggle_sound_on, self.main_menu.switch_toggle_sound)
                        if switch.switched_on:
                            self.main_menu.health_on = True
                            self.settings['show_health_bar'] = True
                            self.save_settings()
                        else:
                            self.main_menu.health_on = False  # flip the button
                            self.settings['show_health_bar'] = False  # change in settings.json
                            self.save_settings()

                # gun bar switch
                if switch == self.show_gun_bar_switch:
                    if self.click:
                        switch.flip_switch()
                        play_sound(self.main_menu.switch_toggle_sound_on, self.main_menu.switch_toggle_sound)
                        if switch.switched_on:
                            self.main_menu.gun_bar_on = True
                            self.settings['show_gun_bar'] = True
                            self.save_settings()
                        else:
                            self.main_menu.gun_bar_on = False
                            self.settings['show_gun_bar'] = False
                            self.save_settings()

                # gun upgrade switch
                if switch == self.gun_upgrade_switch:
                    if self.click:
                        switch.flip_switch()
                        play_sound(self.main_menu.switch_toggle_sound_on, self.main_menu.switch_toggle_sound)
                        if switch.switched_on:
                            self.main_menu.gun_upgrade_on = True
                            self.settings['gun_upgrade_on'] = True
                            self.save_settings()
                        else:
                            self.main_menu.gun_upgrade_on = False
                            self.settings['gun_upgrade_on'] = False
                            self.save_settings()

                # game timer switch
                if switch == self.show_game_timer_switch:
                    if self.click:
                        switch.flip_switch()
                        play_sound(self.main_menu.switch_toggle_sound_on, self.main_menu.switch_toggle_sound)
                        if switch.switched_on:
                            self.main_menu.game_timer_on = True
                            self.settings['show_game_timer'] = True
                            self.save_settings()
                        else:
                            self.main_menu.game_timer_on = False
                            self.settings['show_game_timer'] = False
                            self.save_settings()
            else:
                switch.hovered = False

    # sounds settings
    def __initialize_sounds_settings_buttons(self) -> None:
        """
        Make sounds settings tabs and buttons in each tab.
        """
        # make sounds tabs buttons
        self.general_sounds_submenu = TextButton('General', 40, (-245, -290))
        self.game_sfx_submenu = TextButton('Game sfx', 40, (33, -290))
        self.sprites_sounds_submenu = TextButton('Sprites', 40, (311, -290))

        # make sounds submenus buttons
        self.__make_general_sounds_buttons()
        self.__make_game_sfx_buttons()
        self.__make_sprites_sounds_buttons()

        # all tabs
        self.sounds_tabs = (self.general_sounds_submenu,
                            self.game_sfx_submenu,
                            self.sprites_sounds_submenu)

    def __make_general_sounds_buttons(self) -> None:
        """
        Make general sounds buttons.
        """
        # menu music
        self.menu_music_vol_down = VolumeControl('down', (-356, -90))
        self.menu_music_vol_up = VolumeControl('up', (-170, -90))
        self.menu_music_vol_indicator = VolumeIndicator(self.main_menu.menu_music_volume,
                                                        self.menu_music_vol_down,
                                                        self.menu_music_vol_up)
        self.menu_music_mute_toggle = MuteToggle(self.main_menu.menu_music_on, (-109, -90))

        # menu navigation (in/out)
        self.menu_nav_snd_vol_down = VolumeControl('down', (-356, 60))
        self.menu_nav_snd_vol_up = VolumeControl('up', (-170, 60))
        self.menu_nav_snd_vol_indicator = VolumeIndicator(self.main_menu.menu_nav_volume,
                                                          self.menu_nav_snd_vol_down,
                                                          self.menu_nav_snd_vol_up)
        self.menu_nav_snd_mute_toggle = MuteToggle(self.main_menu.menu_nav_sounds_on, (-109, 60))

        # switch toggle (setting on/off press)
        self.switch_toggle_snd_vol_down = VolumeControl('down', (-356, 210))
        self.switch_toggle_snd_vol_up = VolumeControl('up', (-170, 210))
        self.switch_toggle_snd_vol_indicator = VolumeIndicator(self.main_menu.switch_toggle_volume,
                                                               self.switch_toggle_snd_vol_down,
                                                               self.switch_toggle_snd_vol_up)
        self.switch_toggle_snd_mute_toggle = MuteToggle(self.main_menu.switch_toggle_sound_on, (-109, 210))

        # high score
        self.high_score_snd_vol_down = VolumeControl('down', (156, -90))
        self.high_score_snd_vol_up = VolumeControl('up', (342, -90))
        self.high_score_snd_vol_indicator = VolumeIndicator(self.main_menu.high_score_volume,
                                                            self.high_score_snd_vol_down,
                                                            self.high_score_snd_vol_up)
        self.high_score_mute_toggle = MuteToggle(self.main_menu.high_score_sound_on, (403, -90))

        # game over music
        self.game_over_snd_vol_down = VolumeControl('down', (156, 60))
        self.game_over_snd_vol_up = VolumeControl('up', (342, 60))
        self.game_over_snd_vol_indicator = VolumeIndicator(self.main_menu.game_over_volume,
                                                           self.game_over_snd_vol_down,
                                                           self.game_over_snd_vol_up)
        self.game_over_snd_mute_toggle = MuteToggle(self.main_menu.game_over_music_on, (403, 60))

        # level start sound
        self.level_start_snd_vol_down = VolumeControl('down', (156, 210))
        self.level_start_snd_vol_up = VolumeControl('up', (342, 210))
        self.level_start_snd_vol_indicator = VolumeIndicator(self.main_menu.level_start_volume,
                                                             self.level_start_snd_vol_down,
                                                             self.level_start_snd_vol_up)
        self.level_start_snd_mute_toggle = MuteToggle(self.main_menu.level_start_sound_on, (403, 210))

        # all general sounds buttons (for drawing)
        self.all_general_sounds_buttons = (self.menu_music_vol_down,
                                           self.menu_music_vol_up,
                                           self.menu_nav_snd_vol_down,
                                           self.menu_nav_snd_vol_up,
                                           self.switch_toggle_snd_vol_down,
                                           self.switch_toggle_snd_vol_up,
                                           self.high_score_snd_vol_down,
                                           self.high_score_snd_vol_up,
                                           self.game_over_snd_vol_down,
                                           self.game_over_snd_vol_up,
                                           self.level_start_snd_vol_down,
                                           self.level_start_snd_vol_up,
                                           self.menu_music_vol_indicator,
                                           self.menu_nav_snd_vol_indicator,
                                           self.switch_toggle_snd_vol_indicator,
                                           self.high_score_snd_vol_indicator,
                                           self.game_over_snd_vol_indicator,
                                           self.level_start_snd_vol_indicator,
                                           self.menu_music_mute_toggle,
                                           self.menu_nav_snd_mute_toggle,
                                           self.switch_toggle_snd_mute_toggle,
                                           self.high_score_mute_toggle,
                                           self.game_over_snd_mute_toggle,
                                           self.level_start_snd_mute_toggle)
        # general sounds volume up/down buttons
        self.general_sounds_vol_up_down_buttons = (self.menu_music_vol_down,
                                                   self.menu_music_vol_up,
                                                   self.menu_nav_snd_vol_down,
                                                   self.menu_nav_snd_vol_up,
                                                   self.switch_toggle_snd_vol_down,
                                                   self.switch_toggle_snd_vol_up,
                                                   self.high_score_snd_vol_down,
                                                   self.high_score_snd_vol_up,
                                                   self.game_over_snd_vol_down,
                                                   self.game_over_snd_vol_up,
                                                   self.level_start_snd_vol_down,
                                                   self.level_start_snd_vol_up)
        # general sounds mute toggles
        self.general_sounds_mute_toggles = (self.menu_music_mute_toggle,
                                            self.menu_nav_snd_mute_toggle,
                                            self.switch_toggle_snd_mute_toggle,
                                            self.high_score_mute_toggle,
                                            self.game_over_snd_mute_toggle,
                                            self.level_start_snd_mute_toggle)

    def __make_game_sfx_buttons(self) -> None:
        """
        Make game SFX buttons.
        """
        # door switch sound
        self.door_switch_snd_vol_down = VolumeControl('down', (-356, -150))
        self.door_switch_snd_vol_up = VolumeControl('up', (-170, -150))
        self.door_switch_snd_vol_indicator = VolumeIndicator(self.main_menu.door_switch_sound_volume,
                                                             self.door_switch_snd_vol_down, self.door_switch_snd_vol_up)
        self.door_switch_snd_mute_toggle = MuteToggle(self.main_menu.door_switch_sound_on, (-109, -150))

        # door sound
        self.door_open_snd_vol_down = VolumeControl('down', (-356, -50))
        self.door_open_snd_vol_up = VolumeControl('up', (-170, -50))
        self.door_open_snd_vol_indicator = VolumeIndicator(self.main_menu.door_open_sound_volume,
                                                           self.door_open_snd_vol_down,
                                                           self.door_open_snd_vol_up)
        self.door_open_snd_mute_toggle = MuteToggle(self.main_menu.door_open_sound_on, (-109, -50))

        # xp & coin sound
        self.xp_coin_snd_vol_down = VolumeControl('down', (-356, 50))
        self.xp_coin_snd_vol_up = VolumeControl('up', (-170, 50))
        self.xp_coin_snd_vol_indicator = VolumeIndicator(self.main_menu.xp_coin_sound_volume, self.xp_coin_snd_vol_down,
                                                         self.xp_coin_snd_vol_up)
        self.xp_coin_snd_mute_toggle = MuteToggle(self.main_menu.xp_coin_sound_on, (-109, 50))

        # health pickup sound
        self.health_pickup_snd_vol_down = VolumeControl('down', (-356, 150))
        self.health_pickup_snd_vol_up = VolumeControl('up', (-170, 150))
        self.health_pickup_snd_vol_indicator = VolumeIndicator(self.main_menu.health_pickup_sound_volume,
                                                               self.health_pickup_snd_vol_down,
                                                               self.health_pickup_snd_vol_up)
        self.health_pickup_snd_mute_toggle = MuteToggle(self.main_menu.health_pickup_sound_on, (-109, 150))

        # key pickup sound
        self.key_pickup_snd_vol_down = VolumeControl('down', (-356, 250))
        self.key_pickup_snd_vol_up = VolumeControl('up', (-170, 250))
        self.key_pickup_snd_vol_indicator = VolumeIndicator(self.main_menu.key_pickup_sound_volume,
                                                            self.key_pickup_snd_vol_down, self.key_pickup_snd_vol_up)
        self.key_pickup_snd_mute_toggle = MuteToggle(self.main_menu.key_pickup_sound_on, (-109, 250))

        # level sound
        self.lever_snd_vol_down = VolumeControl('down', (156, -150))
        self.lever_snd_vol_up = VolumeControl('up', (342, -150))
        self.lever_snd_vol_indicator = VolumeIndicator(self.main_menu.lever_pull_sound_volume, self.lever_snd_vol_down,
                                                       self.lever_snd_vol_up)
        self.lever_snd_mute_toggle = MuteToggle(self.main_menu.lever_pull_sound_on, (403, -150))

        # laser sound
        self.laser_snd_vol_down = VolumeControl('down', (156, -50))
        self.laser_snd_vol_up = VolumeControl('up', (342, -50))
        self.laser_snd_vol_indicator = VolumeIndicator(self.main_menu.laser_sound_volume, self.laser_snd_vol_down,
                                                       self.laser_snd_vol_up)
        self.laser_snd_mute_toggle = MuteToggle(self.main_menu.laser_sound_on, (403, -50))

        # burn sound
        self.burn_snd_vol_down = VolumeControl('down', (156, 50))
        self.burn_snd_vol_up = VolumeControl('up', (342, 50))
        self.burn_snd_vol_indicator = VolumeIndicator(self.main_menu.burn_sound_volume, self.burn_snd_vol_down,
                                                      self.burn_snd_vol_up)
        self.burn_snd_mute_toggle = MuteToggle(self.main_menu.burn_sound_on, (403, 50))

        # saw sound
        self.saw_snd_vol_down = VolumeControl('down', (156, 150))
        self.saw_snd_vol_up = VolumeControl('up', (342, 150))
        self.saw_snd_vol_indicator = VolumeIndicator(self.main_menu.saw_sound_volume, self.saw_snd_vol_down,
                                                     self.saw_snd_vol_up)
        self.saw_snd_mute_toggle = MuteToggle(self.main_menu.saw_sound_on, (403, 150))

        # explosion sound
        self.explosion_snd_vol_down = VolumeControl('down', (156, 250))
        self.explosion_snd_vol_up = VolumeControl('up', (342, 250))
        self.explosion_snd_vol_indicator = VolumeIndicator(self.main_menu.explosion_sound_volume,
                                                           self.explosion_snd_vol_down,
                                                           self.explosion_snd_vol_up)
        self.explosion_snd_mute_toggle = MuteToggle(self.main_menu.explosion_sound_on, (403, 250))

        # all game sfx buttons (for drawing)
        self.all_game_sfx_buttons = (self.door_switch_snd_vol_down,
                                     self.door_switch_snd_vol_up,
                                     self.door_open_snd_vol_down,
                                     self.door_open_snd_vol_up,
                                     self.xp_coin_snd_vol_down,
                                     self.xp_coin_snd_vol_up,
                                     self.health_pickup_snd_vol_down,
                                     self.health_pickup_snd_vol_up,
                                     self.key_pickup_snd_vol_down,
                                     self.key_pickup_snd_vol_up,
                                     self.lever_snd_vol_down,
                                     self.lever_snd_vol_up,
                                     self.laser_snd_vol_down,
                                     self.laser_snd_vol_up,
                                     self.burn_snd_vol_down,
                                     self.burn_snd_vol_up,
                                     self.saw_snd_vol_down,
                                     self.saw_snd_vol_up,
                                     self.explosion_snd_vol_down,
                                     self.explosion_snd_vol_up,
                                     self.door_switch_snd_vol_indicator,
                                     self.door_open_snd_vol_indicator,
                                     self.xp_coin_snd_vol_indicator,
                                     self.health_pickup_snd_vol_indicator,
                                     self.key_pickup_snd_vol_indicator,
                                     self.lever_snd_vol_indicator,
                                     self.laser_snd_vol_indicator,
                                     self.burn_snd_vol_indicator,
                                     self.saw_snd_vol_indicator,
                                     self.explosion_snd_vol_indicator,
                                     self.door_switch_snd_mute_toggle,
                                     self.door_open_snd_mute_toggle,
                                     self.xp_coin_snd_mute_toggle,
                                     self.health_pickup_snd_mute_toggle,
                                     self.key_pickup_snd_mute_toggle,
                                     self.lever_snd_mute_toggle,
                                     self.laser_snd_mute_toggle,
                                     self.burn_snd_mute_toggle,
                                     self.saw_snd_mute_toggle,
                                     self.explosion_snd_mute_toggle)
        # game sfx volume up/down buttons
        self.game_sfx_vol_up_down_buttons = (self.door_switch_snd_vol_down,
                                             self.door_switch_snd_vol_up,
                                             self.door_open_snd_vol_down,
                                             self.door_open_snd_vol_up,
                                             self.xp_coin_snd_vol_down,
                                             self.xp_coin_snd_vol_up,
                                             self.health_pickup_snd_vol_down,
                                             self.health_pickup_snd_vol_up,
                                             self.key_pickup_snd_vol_down,
                                             self.key_pickup_snd_vol_up,
                                             self.lever_snd_vol_down,
                                             self.lever_snd_vol_up,
                                             self.laser_snd_vol_down,
                                             self.laser_snd_vol_up,
                                             self.burn_snd_vol_down,
                                             self.burn_snd_vol_up,
                                             self.saw_snd_vol_down,
                                             self.saw_snd_vol_up,
                                             self.explosion_snd_vol_down,
                                             self.explosion_snd_vol_up)
        # game sfx mute toggles
        self.game_sfx_mute_toggles = (self.door_switch_snd_mute_toggle,
                                      self.door_open_snd_mute_toggle,
                                      self.xp_coin_snd_mute_toggle,
                                      self.health_pickup_snd_mute_toggle,
                                      self.key_pickup_snd_mute_toggle,
                                      self.lever_snd_mute_toggle,
                                      self.laser_snd_mute_toggle,
                                      self.burn_snd_mute_toggle,
                                      self.saw_snd_mute_toggle,
                                      self.explosion_snd_mute_toggle)

    def __make_sprites_sounds_buttons(self) -> None:
        """
        Make sprites sounds buttons.
        """
        # player jump sound
        self.player_jump_snd_vol_down = VolumeControl('down', (-356, -90))
        self.player_jump_snd_vol_up = VolumeControl('up', (-170, -90))
        self.player_jump_snd_vol_indicator = VolumeIndicator(self.main_menu.player_jump_sound_volume,
                                                             self.player_jump_snd_vol_down, self.player_jump_snd_vol_up)
        self.player_jump_snd_mute_toggle = MuteToggle(self.main_menu.player_jump_sound_on, (-109, -90))

        # player hit sound
        self.player_hit_snd_vol_down = VolumeControl('down', (-356, 60))
        self.player_hit_snd_vol_up = VolumeControl('up', (-170, 60))
        self.player_hit_snd_vol_indicator = VolumeIndicator(self.main_menu.player_hit_sound_volume,
                                                            self.player_hit_snd_vol_down, self.player_hit_snd_vol_up)
        self.player_hit_snd_mute_toggle = MuteToggle(self.main_menu.player_hit_sound_on, (-109, 60))

        # gun sound
        self.gun_snd_vol_down = VolumeControl('down', (-356, 210))
        self.gun_snd_vol_up = VolumeControl('up', (-170, 210))
        self.gun_snd_vol_indicator = VolumeIndicator(self.main_menu.gun_sound_volume, self.gun_snd_vol_down,
                                                     self.gun_snd_vol_up)
        self.gun_snd_mute_toggle = MuteToggle(self.main_menu.gun_sound_on, (-109, 210))

        # zombie hit sound
        self.zombie_hit_snd_vol_down = VolumeControl('down', (156, -90))
        self.zombie_hit_snd_vol_up = VolumeControl('up', (342, -90))
        self.zombie_hit_snd_vol_indicator = VolumeIndicator(self.main_menu.zombie_hit_sound_volume,
                                                            self.zombie_hit_snd_vol_down, self.zombie_hit_snd_vol_up)
        self.zombie_hit_snd_mute_toggle = MuteToggle(self.main_menu.zombie_hit_sound_on, (403, -90))

        # zombie die sound
        self.zombie_die_snd_vol_down = VolumeControl('down', (156, 60))
        self.zombie_die_snd_vol_up = VolumeControl('up', (342, 60))
        self.zombie_die_snd_vol_indicator = VolumeIndicator(self.main_menu.zombie_die_sound_volume,
                                                            self.zombie_die_snd_vol_down, self.zombie_die_snd_vol_up)
        self.zombie_die_snd_mute_toggle = MuteToggle(self.main_menu.zombie_die_sound_on, (403, 60))

        # zombie moan sound
        self.zombie_moan_snd_vol_down = VolumeControl('down', (156, 210))
        self.zombie_moan_snd_vol_up = VolumeControl('up', (342, 210))
        self.zombie_moan_snd_vol_indicator = VolumeIndicator(self.main_menu.zombie_moan_sounds_volume,
                                                             self.zombie_moan_snd_vol_down, self.zombie_moan_snd_vol_up)
        self.zombie_moan_snd_mute_toggle = MuteToggle(self.main_menu.zombie_moan_sound_on, (403, 210))

        # all sprites sounds buttons (for drawing)
        self.all_sprites_sounds_buttons = (self.player_jump_snd_vol_down,
                                           self.player_jump_snd_vol_up,
                                           self.player_hit_snd_vol_down,
                                           self.player_hit_snd_vol_up,
                                           self.gun_snd_vol_down,
                                           self.gun_snd_vol_up,
                                           self.zombie_hit_snd_vol_down,
                                           self.zombie_hit_snd_vol_up,
                                           self.zombie_die_snd_vol_down,
                                           self.zombie_die_snd_vol_up,
                                           self.zombie_moan_snd_vol_down,
                                           self.zombie_moan_snd_vol_up,
                                           self.player_jump_snd_vol_indicator,
                                           self.player_hit_snd_vol_indicator,
                                           self.gun_snd_vol_indicator,
                                           self.zombie_hit_snd_vol_indicator,
                                           self.zombie_die_snd_vol_indicator,
                                           self.zombie_moan_snd_vol_indicator,
                                           self.player_jump_snd_mute_toggle,
                                           self.player_hit_snd_mute_toggle,
                                           self.gun_snd_mute_toggle,
                                           self.zombie_hit_snd_mute_toggle,
                                           self.zombie_die_snd_mute_toggle,
                                           self.zombie_moan_snd_mute_toggle)
        # sSprites sounds volume up/down buttons
        self.sprites_sounds_vol_up_down_buttons = (self.player_jump_snd_vol_down,
                                                   self.player_jump_snd_vol_up,
                                                   self.player_hit_snd_vol_down,
                                                   self.player_hit_snd_vol_up,
                                                   self.gun_snd_vol_down,
                                                   self.gun_snd_vol_up,
                                                   self.zombie_hit_snd_vol_down,
                                                   self.zombie_hit_snd_vol_up,
                                                   self.zombie_die_snd_vol_down,
                                                   self.zombie_die_snd_vol_up,
                                                   self.zombie_moan_snd_vol_down,
                                                   self.zombie_moan_snd_vol_up)
        # sprites sounds mute toggles
        self.sprites_sounds_mute_toggles = (self.player_jump_snd_mute_toggle,
                                            self.player_hit_snd_mute_toggle,
                                            self.gun_snd_mute_toggle,
                                            self.zombie_hit_snd_mute_toggle,
                                            self.zombie_die_snd_mute_toggle,
                                            self.zombie_moan_snd_mute_toggle)

    def __check_sound_settings_clicks(self) -> None:
        """
        Checks for sounds sub tabs (button) clicks - sound settings submenu navigation.
        """
        # Sub tabs navigation
        for button in self.sounds_tabs:
            if button.rect.collidepoint(pg.mouse.get_pos()):
                button.hovered = True

                # general sounds tab (default)
                if button == self.general_sounds_submenu:
                    if self.click:
                        play_sound(self.main_menu.menu_nav_sounds_on, self.main_menu.menu_in_sound)
                        self.active_sub_tab = self.general_sounds_submenu

                # game SFX tab
                if button == self.game_sfx_submenu:
                    if self.click:
                        play_sound(self.main_menu.menu_nav_sounds_on, self.main_menu.menu_in_sound)
                        self.active_sub_tab = self.game_sfx_submenu

                # sprites sounds tab
                if button == self.sprites_sounds_submenu:
                    if self.click:
                        play_sound(self.main_menu.menu_nav_sounds_on, self.main_menu.menu_in_sound)
                        self.active_sub_tab = self.sprites_sounds_submenu
            else:
                button.hovered = False

        # check clicks in active sound sub tabs
        self.__check_active_sub_tab_clicks()

    def __check_active_sub_tab_clicks(self) -> None:
        """
        Check button clicks in each sub tab (only if active).
        """
        # general sounds sub tab
        if self.active_sub_tab == self.general_sounds_submenu:
            self.general_sounds_submenu.hovered = True  # make it red if in that submenu

            # volume up/down
            for button in self.general_sounds_vol_up_down_buttons:
                if button.rect.collidepoint(pg.mouse.get_pos()):
                    button.hovered = True

                    # menu music
                    if button == self.menu_music_vol_up:
                        if self.click:
                            indicator = self.menu_music_vol_indicator
                            sound = self.main_menu.menu_music
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['menu_music_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()
                    if button == self.menu_music_vol_down:
                        if self.click:
                            indicator = self.menu_music_vol_indicator
                            sound = self.main_menu.menu_music
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['menu_music_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()

                    # menu sound
                    if button == self.menu_nav_snd_vol_up:
                        if self.click:
                            indicator = self.menu_nav_snd_vol_indicator
                            sound = self.main_menu.menu_in_sound
                            sound2 = self.main_menu.menu_out_sound
                            button.volume_control(indicator, sound, sound2)  # change volume
                            self.settings['menu_nav_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()
                    if button == self.menu_nav_snd_vol_down:
                        if self.click:
                            indicator = self.menu_nav_snd_vol_indicator
                            sound = self.main_menu.menu_in_sound
                            sound2 = self.main_menu.menu_out_sound
                            button.volume_control(indicator, sound, sound2)  # change volume
                            self.settings['menu_nav_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()

                    # switch toggle sound
                    if button == self.switch_toggle_snd_vol_up:
                        if self.click:
                            indicator = self.switch_toggle_snd_vol_indicator
                            sound = self.main_menu.switch_toggle_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['switch_toggle_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()
                    if button == self.switch_toggle_snd_vol_down:
                        if self.click:
                            indicator = self.switch_toggle_snd_vol_indicator
                            sound = self.main_menu.switch_toggle_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['switch_toggle_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()

                    # high score sound
                    if button == self.high_score_snd_vol_up:
                        if self.click:
                            indicator = self.high_score_snd_vol_indicator
                            sound = self.main_menu.high_score_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['high_score_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()
                    if button == self.high_score_snd_vol_down:
                        if self.click:
                            indicator = self.high_score_snd_vol_indicator
                            sound = self.main_menu.high_score_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['high_score_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()

                    # game over sound
                    if button == self.game_over_snd_vol_up:
                        if self.click:
                            indicator = self.game_over_snd_vol_indicator
                            sound = self.main_menu.game_over_music
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['game_over_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()
                    if button == self.game_over_snd_vol_down:
                        if self.click:
                            indicator = self.game_over_snd_vol_indicator
                            sound = self.main_menu.game_over_music
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['game_over_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()

                    # level start sound
                    if button == self.level_start_snd_vol_up:
                        if self.click:
                            indicator = self.level_start_snd_vol_indicator
                            sound = self.main_menu.level_start_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['level_start_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()
                    if button == self.level_start_snd_vol_down:
                        if self.click:
                            indicator = self.level_start_snd_vol_indicator
                            sound = self.main_menu.level_start_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['level_start_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()
                else:
                    button.hovered = False

            # check mute toggles hover and clicks
            for toggle in self.general_sounds_mute_toggles:
                if toggle.rect.collidepoint(pg.mouse.get_pos()):
                    toggle.hovered = True

                    # menu music mute
                    if toggle == self.menu_music_mute_toggle:
                        if self.click:
                            toggle.toggle()
                            if toggle.mute:
                                self.main_menu.menu_music_on = False  # flip the setting
                                self.settings['menu_music_on'] = False
                                self.save_settings()
                                self.main_menu.menu_music.stop()
                            else:
                                self.main_menu.menu_music_on = True  # flip the setting
                                self.settings['menu_music_on'] = True
                                self.save_settings()
                                self.main_menu.menu_music.play()

                    # menu sounds mute
                    if toggle == self.menu_nav_snd_mute_toggle:
                        if self.click:
                            toggle.toggle()
                            if toggle.mute:
                                self.main_menu.menu_nav_sounds_on = False  # flip the setting
                                self.settings['menu_nav_sounds_on'] = False
                                self.save_settings()
                            else:
                                self.main_menu.menu_nav_sounds_on = True  # flip the setting
                                self.settings['menu_nav_sounds_on'] = True
                                self.save_settings()

                    # switch toggle mute
                    if toggle == self.switch_toggle_snd_mute_toggle:
                        if self.click:
                            toggle.toggle()
                            if toggle.mute:
                                self.main_menu.switch_toggle_sound_on = False  # flip the setting
                                self.settings['switch_toggle_sound_on'] = False
                                self.save_settings()
                            else:
                                self.main_menu.switch_toggle_sound_on = True  # flip the setting
                                self.settings['switch_toggle_sound_on'] = True
                                self.save_settings()

                    # game music mute
                    if toggle == self.high_score_mute_toggle:
                        if self.click:
                            toggle.toggle()
                            if toggle.mute:
                                self.main_menu.high_score_sound_on = False  # flip the setting
                                self.settings['high_score_sound_on'] = False
                                self.save_settings()
                            else:
                                self.main_menu.high_score_sound_on = True  # flip the setting
                                self.settings['high_score_sound_on'] = True
                                self.save_settings()

                    # game over mute
                    if toggle == self.game_over_snd_mute_toggle:
                        if self.click:
                            toggle.toggle()
                            if toggle.mute:
                                self.main_menu.game_over_music_on = False  # flip the setting
                                self.settings['game_over_music_on'] = False
                                self.save_settings()
                            else:
                                self.main_menu.game_over_music_on = True  # flip the setting
                                self.settings['game_over_music_on'] = True
                                self.save_settings()

                    # level start mute
                    if toggle == self.level_start_snd_mute_toggle:
                        if self.click:
                            toggle.toggle()
                            if toggle.mute:
                                self.main_menu.level_start_sound_on = False  # flip the setting
                                self.settings['level_start_sound_on'] = False
                                self.save_settings()
                            else:
                                self.main_menu.level_start_sound_on = True  # flip the setting
                                self.settings['level_start_sound_on'] = True
                                self.save_settings()
                else:
                    toggle.hovered = False

        # game SFX sub tab
        if self.active_sub_tab == self.game_sfx_submenu:
            self.game_sfx_submenu.hovered = True  # make it red if in that submenu

            # volume up/down
            for button in self.game_sfx_vol_up_down_buttons:
                if button.rect.collidepoint(pg.mouse.get_pos()):
                    button.hovered = True

                    # door switch press
                    if button == self.door_switch_snd_vol_up:
                        if self.click:
                            indicator = self.door_switch_snd_vol_indicator
                            sound = self.main_menu.door_switch_press_sound
                            sound2 = self.main_menu.door_switch_fail_sound
                            button.volume_control(indicator, sound, sound2)  # change volume
                            self.settings['door_switch_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()
                    if button == self.door_switch_snd_vol_down:
                        if self.click:
                            indicator = self.door_switch_snd_vol_indicator
                            sound = self.main_menu.door_switch_press_sound
                            sound2 = self.main_menu.door_switch_fail_sound
                            button.volume_control(indicator, sound, sound2)  # change volume
                            self.settings['door_switch_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()

                    # door open
                    if button == self.door_open_snd_vol_up:
                        if self.click:
                            indicator = self.door_open_snd_vol_indicator
                            sound = self.main_menu.door_open_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['door_open_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()
                    if button == self.door_open_snd_vol_down:
                        if self.click:
                            indicator = self.door_open_snd_vol_indicator
                            sound = self.main_menu.door_open_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['door_open_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()

                    # xp & coin pickup
                    if button == self.xp_coin_snd_vol_up:
                        if self.click:
                            indicator = self.xp_coin_snd_vol_indicator
                            sound = self.main_menu.xp_pickup_sound
                            sound2 = self.main_menu.coin_pickup_sound
                            button.volume_control(indicator, sound, sound2)  # change volume
                            self.settings['xp_coin_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()
                    if button == self.xp_coin_snd_vol_down:
                        if self.click:
                            indicator = self.xp_coin_snd_vol_indicator
                            sound = self.main_menu.xp_pickup_sound
                            sound2 = self.main_menu.coin_pickup_sound
                            button.volume_control(indicator, sound, sound2)  # change volume
                            self.settings['xp_coin_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()

                    # health pickup
                    if button == self.health_pickup_snd_vol_up:
                        if self.click:
                            indicator = self.health_pickup_snd_vol_indicator
                            sound = self.main_menu.health_pickup_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['health_pickup_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()
                    if button == self.health_pickup_snd_vol_down:
                        if self.click:
                            indicator = self.health_pickup_snd_vol_indicator
                            sound = self.main_menu.health_pickup_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['health_pickup_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()

                    # key pickup
                    if button == self.key_pickup_snd_vol_up:
                        if self.click:
                            indicator = self.key_pickup_snd_vol_indicator
                            sound = self.main_menu.key_pickup_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['key_pickup_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()
                    if button == self.key_pickup_snd_vol_down:
                        if self.click:
                            indicator = self.key_pickup_snd_vol_indicator
                            sound = self.main_menu.key_pickup_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['key_pickup_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()

                    # lever pull
                    if button == self.lever_snd_vol_up:
                        if self.click:
                            indicator = self.lever_snd_vol_indicator
                            sound = self.main_menu.lever_pull_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['lever_pull_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()
                    if button == self.lever_snd_vol_down:
                        if self.click:
                            indicator = self.lever_snd_vol_indicator
                            sound = self.main_menu.lever_pull_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['lever_pull_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()

                    # laser
                    if button == self.laser_snd_vol_up:
                        if self.click:
                            indicator = self.laser_snd_vol_indicator
                            sound = self.main_menu.laser_sound
                            sound2 = self.main_menu.laser_gun_sound
                            button.volume_control(indicator, sound, sound2)  # change volume
                            self.settings['laser_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()
                    if button == self.laser_snd_vol_down:
                        if self.click:
                            indicator = self.laser_snd_vol_indicator
                            sound = self.main_menu.laser_sound
                            sound2 = self.main_menu.laser_gun_sound
                            button.volume_control(indicator, sound, sound2)  # change volume
                            self.settings['laser_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()

                    # burn
                    if button == self.burn_snd_vol_up:
                        if self.click:
                            indicator = self.burn_snd_vol_indicator
                            sound = self.main_menu.burn_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['burn_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()
                    if button == self.burn_snd_vol_down:
                        if self.click:
                            indicator = self.burn_snd_vol_indicator
                            sound = self.main_menu.burn_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['burn_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()

                    # saw
                    if button == self.saw_snd_vol_up:
                        if self.click:
                            indicator = self.saw_snd_vol_indicator
                            sound = self.main_menu.saw_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['saw_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()
                    if button == self.saw_snd_vol_down:
                        if self.click:
                            indicator = self.saw_snd_vol_indicator
                            sound = self.main_menu.saw_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['saw_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()

                    # explosion
                    if button == self.explosion_snd_vol_up:
                        if self.click:
                            indicator = self.explosion_snd_vol_indicator
                            sound = self.main_menu.explosion_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['explosion_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()
                    if button == self.explosion_snd_vol_down:
                        if self.click:
                            indicator = self.explosion_snd_vol_indicator
                            sound = self.main_menu.explosion_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['explosion_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()
                else:
                    button.hovered = False

            # check mute toggles hover and clicks
            for toggle in self.game_sfx_mute_toggles:
                if toggle.rect.collidepoint(pg.mouse.get_pos()):
                    toggle.hovered = True

                    # door switch press mute
                    if toggle == self.door_switch_snd_mute_toggle:
                        if self.click:
                            toggle.toggle()
                            if toggle.mute:
                                self.main_menu.door_switch_sound_on = False  # flip the setting
                                self.settings['door_switch_sound_on'] = False
                                self.save_settings()
                            else:
                                self.main_menu.door_switch_sound_on = True  # flip the setting
                                self.settings['door_switch_sound_on'] = True
                                self.save_settings()

                    # door open mute
                    if toggle == self.door_open_snd_mute_toggle:
                        if self.click:
                            toggle.toggle()
                            if toggle.mute:
                                self.main_menu.door_open_sound_on = False  # flip the setting
                                self.settings['door_open_sound_on'] = False
                                self.save_settings()
                            else:
                                self.main_menu.door_open_sound_on = True  # flip the setting
                                self.settings['door_open_sound_on'] = True
                                self.save_settings()

                    # burn mute
                    if toggle == self.burn_snd_mute_toggle:
                        if self.click:
                            toggle.toggle()
                            if toggle.mute:
                                self.main_menu.burn_sound_on = False  # flip the setting
                                self.settings['burn_sound_on'] = False
                                self.save_settings()
                            else:
                                self.main_menu.burn_sound_on = True  # flip the setting
                                self.settings['burn_sound_on'] = True
                                self.save_settings()

                    # lever pull mute
                    if toggle == self.lever_snd_mute_toggle:
                        if self.click:
                            toggle.toggle()
                            if toggle.mute:
                                self.main_menu.lever_pull_sound_on = False  # flip the setting
                                self.settings['lever_pull_sound_on'] = False
                                self.save_settings()
                            else:
                                self.main_menu.lever_pull_sound_on = True  # flip the setting
                                self.settings['lever_pull_sound_on'] = True
                                self.save_settings()

                    # laser mute
                    if toggle == self.laser_snd_mute_toggle:
                        if self.click:
                            toggle.toggle()
                            if toggle.mute:
                                self.main_menu.laser_sound_on = False  # flip the setting
                                self.settings['laser_sound_on'] = False
                                self.save_settings()
                            else:
                                self.main_menu.laser_sound_on = True  # flip the setting
                                self.settings['laser_sound_on'] = True
                                self.save_settings()

                    # xp & coin mute
                    if toggle == self.xp_coin_snd_mute_toggle:
                        if self.click:
                            toggle.toggle()
                            if toggle.mute:
                                self.main_menu.xp_coin_sound_on = False  # flip the setting
                                self.settings['xp_coin_sound_on'] = False
                                self.save_settings()
                            else:
                                self.main_menu.xp_coin_sound_on = True  # flip the setting
                                self.settings['xp_coin_sound_on'] = True
                                self.save_settings()

                    # health pickup mute
                    if toggle == self.health_pickup_snd_mute_toggle:
                        if self.click:
                            toggle.toggle()
                            if toggle.mute:
                                self.main_menu.health_pickup_sound_on = False  # flip the setting
                                self.settings['health_pickup_sound_on'] = False
                                self.save_settings()
                            else:
                                self.main_menu.health_pickup_sound_on = True  # flip the setting
                                self.settings['health_pickup_sound_on'] = True
                                self.save_settings()

                    # coin pickup mute
                    if toggle == self.key_pickup_snd_mute_toggle:
                        if self.click:
                            toggle.toggle()
                            if toggle.mute:
                                self.main_menu.key_pickup_sound_on = False  # flip the setting
                                self.settings['key_pickup_sound_on'] = False
                                self.save_settings()
                            else:
                                self.main_menu.key_pickup_sound_on = True  # flip the setting
                                self.settings['key_pickup_sound_on'] = True
                                self.save_settings()

                    # saw mute
                    if toggle == self.saw_snd_mute_toggle:
                        if self.click:
                            toggle.toggle()
                            if toggle.mute:
                                self.main_menu.saw_sound_on = False  # flip the setting
                                self.settings['saw_sound_on'] = False
                                self.save_settings()
                            else:
                                self.main_menu.saw_sound_on = True  # flip the setting
                                self.settings['saw_sound_on'] = True
                                self.save_settings()

                    # explosion mute
                    if toggle == self.explosion_snd_mute_toggle:
                        if self.click:
                            toggle.toggle()
                            if toggle.mute:
                                self.main_menu.explosion_sound_on = False  # flip the setting
                                self.settings['explosion_sound_on'] = False
                                self.save_settings()
                            else:
                                self.main_menu.explosion_sound_on = True  # flip the setting
                                self.settings['explosion_sound_on'] = True
                                self.save_settings()
                else:
                    toggle.hovered = False

        # sprites sounds sub tab
        if self.active_sub_tab == self.sprites_sounds_submenu:
            self.sprites_sounds_submenu.hovered = True  # make it red if in that submenu
            # volume up/down
            for button in self.sprites_sounds_vol_up_down_buttons:
                if button.rect.collidepoint(pg.mouse.get_pos()):
                    button.hovered = True

                    # player jump volume
                    if button == self.player_jump_snd_vol_up:
                        if self.click:
                            indicator = self.player_jump_snd_vol_indicator
                            sound = self.main_menu.player_jump_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['player_jump_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()
                    if button == self.player_jump_snd_vol_down:
                        if self.click:
                            indicator = self.player_jump_snd_vol_indicator
                            sound = self.main_menu.player_jump_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['player_jump_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()

                    # player hit volume
                    if button == self.player_hit_snd_vol_up:
                        if self.click:
                            indicator = self.player_hit_snd_vol_indicator
                            sound = self.main_menu.player_hit_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['player_hit_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()
                    if button == self.player_hit_snd_vol_down:
                        if self.click:
                            indicator = self.player_hit_snd_vol_indicator
                            sound = self.main_menu.player_hit_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['player_hit_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()

                    # gun volume
                    if button == self.gun_snd_vol_up:
                        if self.click:
                            indicator = self.gun_snd_vol_indicator
                            sound = self.main_menu.gun_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['gun_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()
                    if button == self.gun_snd_vol_down:
                        if self.click:
                            indicator = self.gun_snd_vol_indicator
                            sound = self.main_menu.gun_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['gun_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()

                    # zombie hit volume
                    if button == self.zombie_hit_snd_vol_up:
                        if self.click:
                            indicator = self.zombie_hit_snd_vol_indicator
                            sound = self.main_menu.zombie_hit_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['zombie_hit_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()
                    if button == self.zombie_hit_snd_vol_down:
                        if self.click:
                            indicator = self.zombie_hit_snd_vol_indicator
                            sound = self.main_menu.zombie_hit_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['zombie_hit_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()

                    # zombie die volume
                    if button == self.zombie_die_snd_vol_up:
                        if self.click:
                            indicator = self.zombie_die_snd_vol_indicator
                            sound = self.main_menu.zombie_die_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['zombie_die_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()
                    if button == self.zombie_die_snd_vol_down:
                        if self.click:
                            indicator = self.zombie_die_snd_vol_indicator
                            sound = self.main_menu.zombie_die_sound
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['zombie_die_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()

                    # zombie moan volume
                    if button == self.zombie_moan_snd_vol_up:
                        if self.click:
                            indicator = self.zombie_moan_snd_vol_indicator
                            sound = self.main_menu.zombie_moan_sounds[0]
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['zombie_moan_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()
                    if button == self.zombie_moan_snd_vol_down:
                        if self.click:
                            indicator = self.zombie_moan_snd_vol_indicator
                            sound = self.main_menu.zombie_moan_sounds[0]
                            button.volume_control(indicator, sound)  # change volume
                            self.settings['zombie_moan_volume'] = round(sound.get_volume(), 1)
                            self.save_settings()
                else:
                    button.hovered = False

            # check mute toggles hover and clicks
            for toggle in self.sprites_sounds_mute_toggles:
                if toggle.rect.collidepoint(pg.mouse.get_pos()):
                    toggle.hovered = True

                    # player jump
                    if toggle == self.player_jump_snd_mute_toggle:
                        if self.click:
                            toggle.toggle()
                            if toggle.mute:
                                self.main_menu.player_jump_sound_on = False
                                self.settings['player_jump_sound_on'] = False
                                self.save_settings()
                            else:
                                self.main_menu.player_jump_sound_on = True
                                self.settings['player_jump_sound_on'] = True
                                self.save_settings()
                    # player hit
                    if toggle == self.player_hit_snd_mute_toggle:
                        if self.click:
                            toggle.toggle()
                            if toggle.mute:
                                self.main_menu.player_hit_sound_on = False
                                self.settings['player_hit_sound_on'] = False
                                self.save_settings()
                            else:
                                self.main_menu.player_hit_sound_on = True
                                self.settings['player_hit_sound_on'] = True
                                self.save_settings()
                    # gun
                    if toggle == self.gun_snd_mute_toggle:
                        if self.click:
                            toggle.toggle()
                            if toggle.mute:
                                self.main_menu.gun_sound_on = False
                                self.settings['gun_sound_on'] = False
                                self.save_settings()
                            else:
                                self.main_menu.gun_sound_on = True
                                self.settings['gun_sound_on'] = True
                                self.save_settings()

                    # zombie hit
                    if toggle == self.zombie_hit_snd_mute_toggle:
                        if self.click:
                            toggle.toggle()
                            if toggle.mute:
                                self.main_menu.zombie_hit_sound_on = False
                                self.settings['zombie_hit_sound_on'] = False
                                self.save_settings()
                            else:
                                self.main_menu.zombie_hit_sound_on = True
                                self.settings['zombie_hit_sound_on'] = True
                                self.save_settings()
                    # zombie die
                    if toggle == self.zombie_die_snd_mute_toggle:
                        if self.click:
                            toggle.toggle()
                            if toggle.mute:
                                self.main_menu.zombie_die_sound_on = False
                                self.settings['zombie_die_sound_on'] = False
                                self.save_settings()
                            else:
                                self.main_menu.zombie_die_sound_on = True
                                self.settings['zombie_die_sound_on'] = True
                                self.save_settings()
                    # zombie moan
                    if toggle == self.zombie_moan_snd_mute_toggle:
                        if self.click:
                            toggle.toggle()
                            if toggle.mute:
                                self.main_menu.zombie_moan_sound_on = False
                                self.settings['zombie_moan_sound_on'] = False
                                self.save_settings()
                            else:
                                self.main_menu.zombie_moan_sound_on = True
                                self.settings['zombie_moan_sound_on'] = True
                                self.save_settings()
                else:
                    toggle.hovered = False

    # controls settings
    def __initialize_controls_settings_buttons(self) -> None:
        """
        Make controls settings buttons.
        """
        # control names
        self.move_left_text_btn = TextButton('Move left', 45, (-100, -240))
        self.move_right_text_btn = TextButton('Move right', 45, (-100, -165))
        self.jump_text_btn = TextButton('Jump', 45, (-100, -90))
        self.slide_text_btn = TextButton('Slide', 45, (-100, -15))
        self.shoot_text_btn = TextButton('Shoot', 45, (-100, 60))
        self.interact_text_btn = TextButton('Interact', 45, (-100, 135))
        self.open_text_btn = TextButton('Open', 45, (-100, 210))

        # control buttons
        self.move_left_btn = TextButton(self.main_menu.left_key, 40, (150, -240))
        self.move_right_btn = TextButton(self.main_menu.right_key, 40, (150, -165))
        self.jump_btn = TextButton(self.main_menu.jump_key, 40, (150, -90))
        self.slide_btn = TextButton(self.main_menu.slide_key, 40, (150, -15))
        if self.main_menu.shoot_key == ' ':
            self.shoot_btn = TextButton('Space', 40, (150, 60))
        else:
            self.shoot_btn = TextButton(self.main_menu.shoot_key, 40, (150, 60))
        self.interact_btn = TextButton(self.main_menu.interact_key, 40, (150, 135))
        self.open_btn = TextButton(self.main_menu.open_key, 40, (150, 210))

        # cll control buttons (for drawing)
        self.all_control_buttons = (self.move_left_text_btn,
                                    self.move_right_text_btn,
                                    self.jump_text_btn,
                                    self.slide_text_btn,
                                    self.shoot_text_btn,
                                    self.interact_text_btn,
                                    self.open_text_btn,
                                    self.move_left_btn,
                                    self.move_right_btn,
                                    self.jump_btn,
                                    self.slide_btn,
                                    self.shoot_btn,
                                    self.interact_btn,
                                    self.open_btn)
        self.control_buttons = (self.move_left_btn,
                                self.move_right_btn,
                                self.jump_btn,
                                self.slide_btn,
                                self.shoot_btn,
                                self.interact_btn,
                                self.open_btn)
        self.allowed_keys = ('a',
                             'b',
                             'c',
                             'd',
                             'e',
                             'f',
                             'g',
                             'h',
                             'i',
                             'j',
                             'k',
                             'l',
                             'm',
                             'n',
                             'o',
                             'p',
                             'q',
                             'r',
                             's',
                             't',
                             'u',
                             'v',
                             'w',
                             'x',
                             'y',
                             'z',
                             ' ')

        self.used_keys = [control for control in self.main_menu.controls]

    def __check_controls_settings_clicks(self) -> None:
        """
        Check controls menu clicks (control change).
        If button (control) is clicked, then it is being changed.
        """
        # control buttons
        for button in self.control_buttons:
            if button.rect.collidepoint(pg.mouse.get_pos()):

                button.hovered = True
                # move left
                if button == self.move_left_btn:
                    if self.click:
                        self.changing_control = True
                        self.control_to_change = 'left'
                        self.button_to_change = self.move_left_btn

                # move right
                if button == self.move_right_btn:
                    if self.click:
                        self.changing_control = True
                        self.control_to_change = 'right'
                        self.button_to_change = self.move_right_btn

                # jump
                if button == self.jump_btn:
                    if self.click:
                        self.changing_control = True
                        self.control_to_change = 'jump'
                        self.button_to_change = self.jump_btn

                # slide
                if button == self.slide_btn:
                    if self.click:
                        self.changing_control = True
                        self.control_to_change = 'slide'
                        self.button_to_change = self.slide_btn

                # shoot
                if button == self.shoot_btn:
                    if self.click:
                        self.changing_control = True
                        self.control_to_change = 'shoot'
                        self.button_to_change = self.shoot_btn

                # interact
                if button == self.interact_btn:
                    if self.click:
                        self.changing_control = True
                        self.control_to_change = 'interact'
                        self.button_to_change = self.interact_btn

                # open
                if button == self.open_btn:
                    if self.click:
                        self.changing_control = True
                        self.control_to_change = 'open'
                        self.button_to_change = self.open_btn
            else:
                button.hovered = False

    def __check_for_control_change(self) -> None:
        """
        Check if control is being changed and if so, change it.
        """
        if self.changing_control:
            self.__change_control(self.control_to_change, self.button_to_change)

    def __change_control(self, control: str, button: TextButton) -> None:
        """
        Change the control.
        Get event key pressed.
        If key already in use or not allowed, set self.error_changing to True.
        If esc is pressed, cancel the control change.
        Otherwise, apply the change.
        :param control: control to change (in settings.json -> 'left', 'right'...)
        :param button: button (control) being changed
        """
        changed = False
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                # ff key already in use, error
                if chr(event.key) in self.used_keys:
                    self.error_changing = True
                else:
                    # if esc is pressed, cancel the change
                    if pg.key.name(event.key) == 'escape':
                        self.changing_control = False
                    else:
                        # if key is allowed, apply change
                        if chr(event.key) in self.allowed_keys:
                            self.settings[control] = chr(event.key)
                            self.save_settings()
                            self.button_changing.append(button)
                            changed = True
                        # otherwise, error
                        else:
                            self.error_changing = True

        # if control is changed
        if changed:
            self.changing_control = False
            self.error_changing = False

    def __set_feedback_text(self) -> None:
        """
        Set feedback text for control changing.
        """
        # if not changing control
        if not self.changing_control:
            self.draw_text('Click a key to change control', 30, RED, WHITE, (0, 270))

        # if changing control (clicked on a control)
        if self.changing_control:
            self.draw_text('Press a key', 30, WHITE, RED, (0, 270))
            if self.error_changing:
                self.draw_text('Error changing, chose another key', 30, WHITE, RED, (0, 305))

        # draw 'Changed' next to changed control (also fixes drawing text over another text bug)
        for button in self.button_changing:
            # must subtract mid_x & mid_y (because of how the function works)
            x = button.x + 150 - self.mid_x
            y = button.y - self.mid_y
            self.draw_text('Changed', 40, WHITE, RED, (x, y))
            if self.error_changing:
                self.draw_text('Error changing, chose another key', 30, WHITE, RED, (0, 305))
            else:
                self.draw_text('Restart to apply changes', 30, WHITE, RED, (0, 305))
            self.restart_required = True

    # draw functions
    def __draw_buttons_and_text(self) -> None:
        """
        Draw everything.
        """
        # title & shadow effect
        self.draw_text('Settings', 80, WHITE, RED, (0, -385))

        # draw current active submenu
        self.__draw_current_active_submenu()

        # draw back button
        self.draw_buttons(self.back_btn)
        # draw tabs buttons
        self.draw_buttons(self.all_tabs)

    def __draw_current_active_submenu(self) -> None:
        """
        Check and draw the current active submenu (tab).
        - First draw polygon that outlines submenu
        - Then draw current active submenu buttons
        """
        # draw current active submenu (must be above buttons drawing, to prevent drawing over text)
        self.__draw_tab(self.active_tab)
        self.__draw_buttons_border(self.active_tab)

        # check current active submenu (tab) and draw submenu buttons (based on current active tab)
        if self.active_tab == self.general_settings_menu_tab:
            # draw general settings buttons
            self.draw_buttons(self.all_general_settings_buttons)

        elif self.active_tab == self.sounds_settings_menu_tab:
            # draw submenu (only when sounds tab is active)
            self.__draw_tab(self.active_sub_tab)

            # draw tabs (top) with shadow effect
            self.draw_buttons(self.sounds_tabs)

            # general sounds submenu
            if self.active_sub_tab == self.general_sounds_submenu:
                # draw settings names
                self.draw_text('Menu Music', 50, RED, WHITE, (-256, -150))
                self.draw_text('Menu Navigation', 50, RED, WHITE, (-256, 0))
                self.draw_text('Switch toggle', 50, RED, WHITE, (-256, 150))
                self.draw_text('High score', 50, RED, WHITE, (256, -150))
                self.draw_text('Game over music', 50, RED, WHITE, (256, 0))
                self.draw_text('Level start', 50, RED, WHITE, (256, 150))

                # draw buttons
                self.draw_buttons(self.all_general_sounds_buttons)

            # game sounds submenu
            elif self.active_sub_tab == self.game_sfx_submenu:
                # draw settings names
                self.draw_text('Door switch sound', 35, RED, WHITE, (-256, -200))
                self.draw_text('Door open', 35, RED, WHITE, (-256, -100))
                self.draw_text('XP & Coin sound', 35, RED, WHITE, (-256, 0))
                self.draw_text('Health pickup', 35, RED, WHITE, (-256, 100))
                self.draw_text('Key pickup', 35, RED, WHITE, (-256, 200))
                self.draw_text('Lever sound', 35, RED, WHITE, (256, -200))
                self.draw_text('Laser sounds', 35, RED, WHITE, (256, -100))
                self.draw_text('Burn sound', 35, RED, WHITE, (256, 0))
                self.draw_text('Saw sound', 35, RED, WHITE, (256, 100))
                self.draw_text('Explosion sound', 35, RED, WHITE, (256, 200))

                # draw buttons
                self.draw_buttons(self.all_game_sfx_buttons)

            # sprites sounds submenu
            elif self.active_sub_tab == self.sprites_sounds_submenu:
                # player
                self.draw_text('Player', 37, WHITE, RED, (-256, -220))
                self.draw_text('Jump sound', 50, RED, WHITE, (-256, -150))
                self.draw_text('Hit sound', 50, RED, WHITE, (-256, -0))
                self.draw_text('Gun sound', 50, RED, WHITE, (-256, 150))

                # zombie
                self.draw_text('Zombie', 37, WHITE, RED, (260, -220))
                self.draw_text('Hit sound', 50, RED, WHITE, (256, -150))
                self.draw_text('Die sound', 50, RED, WHITE, (256, 0))
                self.draw_text('Moan sound', 50, RED, WHITE, (256, 150))

                # draw buttons
                self.draw_buttons(self.all_sprites_sounds_buttons)

        elif self.active_tab == self.controls_settings_menu_tab:
            # text above controls
            self.draw_text('Control', 40, WHITE, RED, (-100, -300))
            self.draw_text('Key', 40, WHITE, RED, (150, -300))

            # draw control names and buttons
            self.draw_buttons(self.all_control_buttons)

            # draw feedback text
            self.__set_feedback_text()

    def __draw_tab(self, tab: TextButton) -> None:
        """
        Draw active tab (menu) and sub tab (submenu).
        :param tab: current active tab (general settings, sound settings...)
        """
        # default tabs (settings menu) - left side buttons
        if tab in self.all_tabs:
            # fixed screen points
            screen_top_left = (self.mid_x - 534, self.mid_y - 320)
            screen_top_right = (self.mid_x + 600, self.mid_y - 320)
            screen_bottom_left = (self.mid_x - 534, self.mid_y + 330)
            screen_bottom_right = (self.mid_x + 600, self.mid_y + 330)

            # tab positions
            tab_top_left = (tab.rect.left - 5, tab.rect.top)
            tab_bottom_left = (tab.rect.left - 5, tab.rect.bottom + 5)
            tab_top_right = (tab.rect.left + 180, tab.rect.top)
            tab_bottom_right = (tab.rect.left + 180, tab.rect.bottom + 5)

            # draw submenu
            points = (tab_top_left,
                      tab_top_right,
                      screen_top_left,
                      screen_top_right,
                      screen_bottom_right,
                      screen_bottom_left,
                      tab_bottom_right,
                      tab_bottom_left,
                      tab_top_left)
            pg.draw.polygon(self.game_display, SUBMENU_GREY, points)
        # sub tabs (submenus)
        else:
            # fixed screen points
            screen_top_left = (self.mid_x - 494, self.mid_y - 254)
            screen_top_right = (self.mid_x + 570, self.mid_y - 254)
            screen_bottom_left = (self.mid_x - 494, self.mid_y + 300)
            screen_bottom_right = (self.mid_x + 570, self.mid_y + 300)

            # tab positions
            tab_top_left = (tab.rect.left - 5, tab.rect.top)
            tab_bottom_left = (tab.rect.left - 5, tab.rect.bottom + 10)
            tab_top_right = (tab.rect.right + 5, tab.rect.top)
            tab_bottom_right = (tab.rect.right + 5, tab.rect.bottom + 10)

            # draw submenu
            points = (tab_top_left,
                      tab_bottom_left,
                      screen_top_left,
                      screen_bottom_left,
                      screen_bottom_right,
                      screen_top_right,
                      tab_bottom_right,
                      tab_top_right,
                      tab_top_left)
            pg.draw.polygon(self.game_display, DARK_GREY, points)

    def __draw_buttons_border(self, tab: TextButton) -> None:
        """
        Draw border in active tab around buttons (settings names, on/off buttons, controls...)
        Tab is used to figure out buttons on each active tab, to be able to draw border around them.
        Change number values to reshape the buttons:
            -e.g. increase first number in "top_right"
            -e.g. decrease the first number in "bottom_left"
        :param tab: tab (active menu)
        """
        # general settings
        if tab == self.general_settings_menu_tab:
            # right side (on/off switches)
            for switch in self.on_off_switches:
                top_left = (switch.rect.topleft[0] - 10, switch.rect.topleft[1] + 4)
                bottom_left = (switch.rect.bottomleft[0] - 10, switch.rect.bottomleft[1] - 5)
                top_right = (switch.rect.topright[0] + 10, switch.rect.topright[1] + 4)
                bottom_right = (switch.rect.bottomright[0] + 10, switch.rect.bottomright[1] - 5)

                # midline end point on X-axis
                self.line_end = switch.rect.left - 10

                points = (top_left, bottom_left, bottom_right, top_right)

                pg.draw.polygon(self.game_display, DARK_GREY, points)

            # left side (setting names)
            for button in self.all_general_settings_buttons:
                if button not in self.on_off_switches:
                    top_left = (button.rect.topleft[0] - 10, button.rect.topleft[1])
                    bottom_left = (button.rect.bottomleft[0] - 10, button.rect.bottomleft[1] + 8)
                    top_right = (button.rect.topright[0] + 10, button.rect.topright[1])
                    bottom_right = (button.rect.bottomright[0] + 10, button.rect.bottomright[1] + 8)

                    points = (top_left, bottom_left, bottom_right, top_right)

                    pg.draw.polygon(self.game_display, DARK_GREY, points)

                    # draw mid line between setting names and on/off buttons
                    mid_line_start = (button.rect.midright[0] + 10, button.rect.midright[1] + 4)
                    mid_line_end = (self.line_end, button.rect.midright[1] + 4)
                    pg.draw.line(self.game_display, DARK_GREY, mid_line_start, mid_line_end, 20)

        # control settings
        elif tab == self.controls_settings_menu_tab:
            # control buttons (right side)
            for button in self.control_buttons:
                top_left = (button.rect.topleft[0] - 10, button.rect.topleft[1] + 4)
                bottom_left = (button.rect.bottomleft[0] - 10, button.rect.bottomleft[1] + 4)
                top_right = (button.rect.topright[0] + 10, button.rect.topright[1] + 4)
                bottom_right = (button.rect.bottomright[0] + 10, button.rect.bottomright[1] + 4)

                # midline end point on X-axis
                self.line_end = button.rect.left - 5

                points = (top_left,
                          bottom_left,
                          bottom_right,
                          top_right)

                pg.draw.polygon(self.game_display, DARK_GREY, points)

            # control names (left side)
            for button in self.all_control_buttons:
                if button not in self.control_buttons:
                    top_left = (button.rect.topleft[0] - 10, button.rect.topleft[1])
                    bottom_left = (button.rect.bottomleft[0] - 10, button.rect.bottomleft[1] + 7)
                    top_right = (button.rect.topright[0] + 10, button.rect.topright[1])
                    bottom_right = (button.rect.bottomright[0] + 10, button.rect.bottomright[1] + 7)

                    points = (top_left,
                              bottom_left,
                              bottom_right,
                              top_right)
                    pg.draw.polygon(self.game_display, DARK_GREY, points)

                    # draw mid line between control names and control buttons
                    mid_line_start = (button.rect.midright[0] + 5, button.rect.midright[1] + 4)
                    mid_line_end = (self.line_end, button.rect.midright[1] + 4)
                    pg.draw.line(self.game_display, DARK_GREY, mid_line_start, mid_line_end, 20)


class HighScoresMenu(Menu):
    """
    Create high scores menu.
    """

    def __init__(self, game):
        """
        Make the high scores menu.
        :param game: game
        """

        super().__init__(game)

        self.main_menu = self.game.main_menu

        # back button
        self.back_btn = TextButton('Back', 50, (0, 360))

    def display_menu(self) -> None:
        """
        Display menu.
        """
        self.run_display = True
        while self.run_display:
            self.check_menu_events()
            self.game_display.fill(DARK_GREY)
            self.__draw_buttons_and_text()
            self.__check_clicks()
            self.draw_menu()

    def __draw_buttons_and_text(self) -> None:
        """
        Draw high scores menu (back button, text, high scores).
        """
        # draw title
        self.draw_text('High scores', 80, WHITE, RED, (0, -350))

        # draw high scores
        self.__draw_high_scores()

        # draw back button with shadow effect
        self.draw_buttons(self.back_btn)

    def __check_clicks(self) -> None:
        """
        Check high scores menu clicks.
        """
        if self.back_btn.rect.collidepoint(pg.mouse.get_pos()):
            self.back_btn.hovered = True
            if self.click:
                play_sound(self.main_menu.menu_nav_sounds_on, self.main_menu.menu_out_sound)
                self.game.current_menu = self.game.main_menu
        else:
            self.back_btn.hovered = False

        self.click = False
        self.run_display = False

    def __draw_high_scores(self) -> None:
        """
        Draw high scores (from settings.json).
        """
        y_pos = -225
        for i, score in enumerate(self.settings['high_scores']):
            self.draw_text(str(score), 45, RED, WHITE, (0, y_pos))
            y_pos += 50


class HowToPlayMenu(Menu):
    """
    Create how to play menu.
    """

    def __init__(self, game):
        """
        Make the how to play menu.
        :param game: game
        """

        super().__init__(game)

        self.main_menu = self.game.main_menu

        # back button
        self.back_btn = TextButton('Back', 50, (0, 360))

    def display_menu(self) -> None:
        """
        Display menu.
        """
        self.run_display = True
        while self.run_display:
            self.check_menu_events()
            self.game_display.fill(DARK_GREY)
            self.__draw_buttons_and_text()
            self.__check_clicks()
            self.draw_menu()

    def __draw_buttons_and_text(self) -> None:
        """
        Draw how to play menu text and back button.
        """
        # draw title and other text
        self.draw_text('How to play', 80, WHITE, RED, (0, -350))

        self.__draw_instructions()

        # draw back button with shadow
        self.draw_buttons(self.back_btn)

    def __draw_instructions(self) -> None:
        """
        Draw instructions (how to play text).
        """
        # instructions
        self.draw_text('Instructions', 65, WHITE, RED, (0, -200))
        self.draw_text('Pick up the key & unlock the door', 30, RED, WHITE, (0, -125))
        self.draw_text('Open the door & go to the next level', 30, RED, WHITE, (0, -75))
        self.draw_text('Pull the levers to turn off the lasers', 30, RED, WHITE, (0, -25))
        self.draw_text('Collect coins & XP to increase the score', 30, RED, WHITE, (0, 25))

        # warning
        self.draw_text('WARNING', 65, WHITE, RED, (0, 125))
        self.draw_text('Beware of zombies & other hazards', 30, RED, WHITE, (0, 200))
        self.draw_text('Finish before the time runs out', 30, RED, WHITE, (0, 250))

    def __check_clicks(self) -> None:
        """
        Check how to play menu clicks.
        """
        if self.back_btn.rect.collidepoint(pg.mouse.get_pos()):
            self.back_btn.hovered = True
            if self.click:
                play_sound(self.main_menu.menu_nav_sounds_on, self.main_menu.menu_out_sound)
                self.game.current_menu = self.game.main_menu
        else:
            self.back_btn.hovered = False

        self.click = False
        self.run_display = False


class CreditsMenu(Menu):
    """
    Create credits menu.
    """

    def __init__(self, game):
        """
        Make the credits menu.
        :param game: game
        """

        super().__init__(game)

        self.main_menu = self.game.main_menu

        # back button
        self.back_btn = TextButton('Back', 50, (0, 360))

    def display_menu(self) -> None:
        """
        Display menu.
        """
        self.run_display = True
        while self.run_display:
            self.check_menu_events()
            self.game_display.fill(DARK_GREY)
            self.__draw_buttons_and_text()
            self.__check_clicks()
            self.draw_menu()

    def __draw_buttons_and_text(self) -> None:
        """
        Draw credits menu text and back button.
        """
        # draw text
        self.draw_text('Credits', 80, WHITE, RED, (0, -350))
        self.draw_text(GAME_TITLE, 130, WHITE, RED, (0, -100))
        self.draw_text('Made by Ivan Stankovic', 50, RED, WHITE, (0, 90))

        # draw back button with shadow
        self.draw_buttons(self.back_btn)

    def __check_clicks(self) -> None:
        """
        Check credits menu clicks.
        """
        if self.back_btn.rect.collidepoint(pg.mouse.get_pos()):
            self.back_btn.hovered = True
            if self.click:
                play_sound(self.main_menu.menu_nav_sounds_on, self.main_menu.menu_out_sound)
                self.game.current_menu = self.game.main_menu
        else:
            self.back_btn.hovered = False

        self.click = False
        self.run_display = False


class ConfirmationMenu(Menu):
    """
    Creates confirmation (yes/no) menu.
    """

    def __init__(self, game):
        """
        Make the confirmation menu.
        :param game: game
        """

        super().__init__(game)

        self.main_menu = self.game.main_menu

        # buttons
        self.yes_btn = TextButton('Yes', 50, (-103, 100))
        self.no_btn = TextButton('No', 50, (109, 100))

        self.buttons = (self.yes_btn, self.no_btn)

    def display_menu(self) -> None:
        """
        Display menu.
        """
        self.run_display = True
        while self.run_display:
            self.check_menu_events()
            self.game_display.fill(DARK_GREY)
            self.__draw_buttons_and_text()
            self.__check_click()
            self.draw_menu()

    def __draw_buttons_and_text(self) -> None:
        """
        Draw confirmation menu text and buttons.
        """
        # draw text
        self.draw_text(GAME_TITLE, 130, WHITE, RED, (0, -300))
        self.draw_text('Are you sure you want to quit?', 50, WHITE, RED, (0, 0))

        # draw buttons with shadow effect
        self.draw_buttons(self.buttons)

    def __check_click(self) -> None:
        """
        Check confirmation menu clicks.
        """
        for button in self.buttons:
            if button.rect.collidepoint(pg.mouse.get_pos()):
                button.hovered = True

                # yes - quit the game
                if button == self.yes_btn:
                    if self.click:
                        self.quit_menu()

                # no - go back to main menu
                if button == self.no_btn:
                    if self.click:
                        play_sound(self.main_menu.menu_nav_sounds_on, self.main_menu.menu_out_sound)
                        self.game.current_menu = self.game.main_menu
            else:
                button.hovered = False

        self.click = False
        self.run_display = False


# pause & game over menus
class PauseMenu:
    """
    Creates pause menu.
    """

    def __init__(self, game):
        """
        Make the pause menu.
        :param game: game
        """

        self.game = game

        self.main_menu = self.game.main_menu

    def display_menu(self) -> None:
        """
        Display pause menu.
        """
        self.__draw_menu()
        self.__check_clicks()
        self.game.window.blit(self.game.display, (0, 0))
        pg.display.update()

    def __init_buttons(self) -> None:
        """
        Make pause menu buttons.
        """
        # initialize buttons
        self.resume_btn = TextButton('Resume', 50, (0, 0))
        self.main_menu_btn = TextButton('Main Menu', 50, (0, 60))
        self.quit_btn = TextButton('Quit', 50, (0, 120))

        # all buttons (for drawing)
        self.buttons = (self.resume_btn, self.main_menu_btn, self.quit_btn)

    def __draw_menu(self) -> None:
        """
        Draw pause menu buttons and other.
        """
        # pause sounds
        PauseMenu.__pause_sounds()

        # initialize buttons
        self.__init_buttons()

        # draw pause dim image
        self.game.display.blit(self.game.pause_dim_image, (0, 0))

        # draw text
        self.main_menu.draw_text(GAME_TITLE, 130, WHITE, RED, (0, -300))
        self.main_menu.draw_text('Paused', 100, RED, WHITE, (0, -180))

        # draw buttons
        self.main_menu.draw_buttons(self.buttons)

    def __check_clicks(self) -> None:
        """
        Check pause menu clicks.
        """
        for button in self.buttons:
            if button.rect.collidepoint(pg.mouse.get_pos()):
                button.hovered = True

                # resume
                if button == self.resume_btn:
                    if self.game.click:
                        self.game.paused = False

                # main menu
                if button == self.main_menu_btn:
                    if self.game.click:
                        self.game.current_menu.accidental_click = True  # fix accidental clicks bug
                        self.game.playing = False  # break the game loop (go to main menu)
                        self.game.paused = False  # fix pause bug on next game start
                        if self.game.main_menu.menu_music_on:
                            self.game.main_menu.menu_music.play(-1)

                # quit
                if button == self.quit_btn:
                    if self.game.click:
                        self.game.quit_game()

                # to draw hover effect (pause menu doesn't inherit "Menu" class)
                self.main_menu.draw_buttons(button)
            else:
                button.hovered = False

        self.game.click = False

    @staticmethod
    def __pause_sounds() -> None:
        """
        Pause all sounds and music.
        """
        pg.mixer.music.pause()
        pg.mixer.pause()


class GameOverMenu:
    """
    Creates game over menu.
    """

    def __init__(self, game):
        """
        Make the game over menu.
        :param game: game
        """

        self.game = game

        self.main_menu = self.game.main_menu

        self.game_completed = False
        self.new_high_score = False

        # sounds to stop
        self.__sounds_to_stop = (self.main_menu.saw_sound,
                                 self.main_menu.player_jump_sound,
                                 self.main_menu.burn_sound,
                                 self.main_menu.laser_sound)

    def display_menu(self) -> None:
        """
        Display game over menu.
        """
        self.__draw_menu()
        self.__check_clicks()
        pg.display.update()

    def __init_buttons(self) -> None:
        """
        Make game over buttons.
        """
        # initialize buttons
        self.new_game_btn = TextButton('New Game', 50, (0, 0))
        self.main_menu_btn = TextButton('Main Menu', 50, (0, 60))
        self.quit_btn = TextButton('Quit', 50, (0, 120))

        # all buttons
        self.buttons = (self.new_game_btn, self.main_menu_btn, self.quit_btn)

    def __draw_menu(self) -> None:
        """
        Draw game over menu.
        """
        # stop sounds
        self.__stop_sounds()

        # make game over buttons
        self.__init_buttons()

        # fill the display with dark grey color
        self.game.display.fill(DARK_GREY)

        # draw game over text & message
        self.__draw_text()

        # draw buttons
        self.main_menu.draw_buttons(self.buttons)

    def __draw_text(self) -> None:
        """
        Draw game over text and message.
        """
        # game completed text
        if self.game_completed:
            self.main_menu.draw_text('CONGRATULATIONS', 100, WHITE, RED, (0, -300))
            self.main_menu.draw_text('You beat the game', 70, WHITE, RED, (0, -175))
        # game over text
        else:
            self.main_menu.draw_text('GAME OVER', 100, WHITE, RED, (0, -325))

            # draw game over message
            self.__draw_message()

        # if new high score
        if self.game.player.get_score() >= self.main_menu.get_high_score() or self.new_high_score:
            self.main_menu.draw_text('New high score', 50, RED, WHITE, (0, -100))

    def __draw_message(self) -> None:
        """
        Draw game over player death message.
        """
        messages = ('acid', 'saw', 'spikes', 'zombies', 'laser', 'laser gun')
        for message in messages:
            if self.game.player.get_dead_message() == message.lower():
                if not self.game.time_up:  # fix text overlap bug (draw this only if not time up)
                    self.main_menu.draw_text(f'Avoid {message}', 50, WHITE, RED, (0, -175))

        # time is up
        if self.game.time_up:
            self.main_menu.draw_text('Time is up', 50, WHITE, RED, (0, -175))

    def __check_clicks(self) -> None:
        """
        Check game over menu button clicks.
        """
        for button in self.buttons:
            if button.rect.collidepoint(pg.mouse.get_pos()):
                button.hovered = True

                # new game
                if button == self.new_game_btn:
                    if self.game.click:
                        self.main_menu.game_over_music.stop()
                        self.game.playing = False
                        self.game.level = 1  # ensure level is 1 on new game start
                        self.game.run()

                # main menu
                if button == self.main_menu_btn:
                    if self.game.click:
                        self.main_menu.game_over_music.stop()
                        self.game.current_menu.accidental_click = True  # fix accidental clicks bug
                        self.game.playing = False  # break the game loop (go to main menu)
                        if self.game.main_menu.menu_music_on:
                            self.game.main_menu.menu_music.play(-1)

                # quit
                if button == self.quit_btn:
                    if self.game.click:
                        self.game.quit_game()

                # to draw hover effect (game over menu doesn't inherit "Menu" class)
                self.main_menu.draw_buttons(button)
            else:
                button.hovered = False

        self.game.click = False

    def __stop_sounds(self) -> None:
        """
        Stop sounds and game music.
        """
        for sound in self.__sounds_to_stop:
            sound.stop()
        # stop zombie moan sounds
        for sound in self.main_menu.zombie_moan_sounds:
            sound.stop()
        pg.mixer.music.stop()

    def set_game_completed(self) -> None:
        """
        Game completed.
        Save score, play game over music & high score music (used here as an indicator that the game is finished).
        """
        self.__save_final_score()
        play_sound(self.main_menu.high_score_sound_on, self.main_menu.high_score_sound)
        play_sound(self.main_menu.game_over_music_on, self.main_menu.game_over_music)
        self.game.game_over = True
        self.game_completed = True

    def __save_final_score(self) -> None:
        """
        Calculate and save final score.
        If the game is finished, add the bonus points to the current score.
        """
        current_score = self.game.player.get_score()

        # add bonus points for completing the game
        final_score = current_score + GAME_COMPLETED_POINTS

        # if new high score
        if final_score >= self.main_menu.get_high_score():
            self.new_high_score = True

        # save final score
        self.main_menu.save_scores(final_score)
