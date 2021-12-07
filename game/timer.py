from . import pg
from .config import WIDTH, HEIGHT, WHITE
from time import strftime, gmtime


class GameTimer:
    """
    Game timer.
    Used to count down to 0.
    """

    def __init__(self, game):
        """
        Make game timer.
        :param game: game
        """

        self.__game = game
        self.__font = self.__game.default_font
        self.__timer_seconds = 0

        pg.time.set_timer(self.__game.timer, 1000)

    def __play_sounds(self) -> None:
        """
        Play high score (if high score) & game over sound.
        """
        # high score sound
        if self.__game.player.get_score() >= self.__game.main_menu.get_high_score():
            if self.__game.main_menu.high_score_sound_on:
                self.__game.main_menu.high_score_sound.play()

        # game over music
        if self.__game.main_menu.game_over_music_on:
            self.__game.main_menu.game_over_music.play()

    def set_timer(self, seconds: int) -> None:
        """
        Set the timer to specified number of seconds.
        :param seconds: timer seconds
        """
        self.__timer_seconds = seconds

    def countdown(self) -> None:
        """
        Count down to 0.
        When the timer reaches 0, the game is over.
        If the game is paused or over, don't count down.
        """
        if not self.__game.paused and not self.__game.game_over:
            if self.__timer_seconds > 0:
                self.__timer_seconds -= 1
            else:
                self.__game.time_up = True

                # save player score
                self.__game.main_menu.save_scores(self.__game.player.get_score())

                # play sounds
                self.__play_sounds()

                # turn off timer event
                pg.time.set_timer(self.__game.timer, 0)

                # game is over
                self.__game.game_over = True

    def add_seconds(self) -> None:
        """
        Add 3 seconds to the game timer.
        """
        self.__timer_seconds += 3

    def draw_timer(self) -> None:
        """
        Draw the timer on screen.
        """
        timer_text = self.__font.render(strftime('%M:%S', gmtime(self.__timer_seconds)), True, WHITE)
        self.__game.display.blit(timer_text, (WIDTH / 2, HEIGHT / 2 - 420))
