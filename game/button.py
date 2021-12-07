from . import pg
from .config import WIDTH, HEIGHT, FONT, WHITE, RED
from .images import VOLUME_INDICATOR_IMAGE, VOLUME_DOWN_IMG, VOLUME_DOWN_HOVER_IMG, \
    VOLUME_UP_IMG, VOLUME_UP_HOVER_IMG, SWITCH_ON_HOVER_IMG, SWITCH_ON_IMG, SWITCH_OFF_HOVER_IMG, SWITCH_OFF_IMG, \
    MUTE_IMG, MUTE_HOVER_IMG, UN_MUTE_IMG, UN_MUTE_HOVER_IMG, ERROR_IMG


class Button:
    """
    Main button class.
    """

    hovered = False  # hovering a button

    def __init__(self, offset: tuple):
        """
        Initialize a button.
        Adjust the button's X & Y positions.
        Set the middle of the screen & adjust button X & Y position.
        :param offset: offset from the middle of the screen (x, y)
        """
        # button position
        self.x = WIDTH / 2 + offset[0]
        self.y = HEIGHT / 2 + offset[1]


class TextButton(Button):
    """
    Text buttons.
    """

    def __init__(self, text: str, size: int, offset: tuple):
        """
        Make a text button.
        :param text: button text
        :param size: font size
        :param offset: offset from the middle of the screen (x, y)
        """

        super().__init__(offset)

        # button text, text size & text font
        self.__text = text
        self.__size = size
        self.__font = pg.font.Font(FONT, self.__size)

        # shadow effect
        self.__shadow_x = self.x + 1
        self.__shadow_y = self.y + 1

        self.__set_rect()

    def __set_rect(self) -> None:
        """
        Set text rect for shadow & main text.
        Text shadow rect is set first because it's drawn below.
        Main text rect is set second because it's drawn on top of shadow.
        """
        self.__set_text_surfaces()

        # shadow text rect
        self.__shadow_rect = self.__shadow_text_surface.get_rect()
        self.__shadow_rect.center = (self.__shadow_x, self.__shadow_y)

        # main text rect
        self.rect = self.__main_text_surface.get_rect()
        self.rect.center = (self.x, self.y)

    def __set_text_surfaces(self) -> None:
        """
        Render text surfaces for shadow & main text.
        Shadow is drawn first because it's below the main text.
        Otherwise it would be inverted.
        """
        # shadow text surface (below)
        self.__shadow_text_surface = self.__font.render(self.__text, True, self.__get_shadow_color())

        # main text surface (above)
        self.__main_text_surface = self.__font.render(self.__text, True, self.__get_main_color())

    def __get_shadow_color(self) -> tuple:
        """
        Get text shadow color.
        Text shadow is drawn below the main text.
        :return: color tuple
        """
        if self.hovered:
            return WHITE
        else:
            return RED

    def __get_main_color(self) -> tuple:
        """
        Get main text color.
        Main text is drawn above the shadow.
        :return: color tuple
        """
        if self.hovered:
            return RED
        else:
            return WHITE

    def draw(self, surface: pg.Surface) -> None:
        """
        Draw button on screen.
        Draw the shadow first, then the main text.
        :param surface: surface to draw on (game display)
        """
        self.__set_text_surfaces()

        # draw the shadow & text
        surface.blit(self.__shadow_text_surface, self.__shadow_rect)
        surface.blit(self.__main_text_surface, self.rect)


class VolumeIndicator:
    """
    Volume indicator (little zombie image).
    """

    def __init__(self, volume: float, vol_down_btn, vol_up_btn):
        """
        Make a volume indicator.
        Volume down & up buttons are used for positioning volume indicator.

        :param volume: "settings.json" setting (volume), used for adjusting the starting X position
        :param vol_down_btn: volume down button
        :param vol_up_btn: volume up button
        """

        # how much to move left/right
        self.__step = 12.2

        self.__volume = volume

        # set indicator position
        self.__center_x = (vol_down_btn.rect.centerx + vol_up_btn.rect.centerx) / 2
        self.__center_y = vol_up_btn.rect.centery  # can use any button (center y is the same)

        self.__image = pg.image.load(VOLUME_INDICATOR_IMAGE).convert_alpha()
        self.__rect = self.__image.get_rect(center=(self.__set_x_position(), self.__center_y))

    def __set_x_position(self) -> float:
        """
        Adjust the indicator's starting X position.
        """
        if self.__volume == 1.0:
            return self.__center_x + self.__step * 5
        elif self.__volume == 0.9:
            return self.__center_x + self.__step * 4
        elif self.__volume == 0.8:
            return self.__center_x + self.__step * 3
        elif self.__volume == 0.7:
            return self.__center_x + self.__step * 2
        elif self.__volume == 0.6:
            return self.__center_x + self.__step
        elif self.__volume == 0.5:
            return self.__center_x
        elif self.__volume == 0.4:
            return self.__center_x - self.__step
        elif self.__volume == 0.3:
            return self.__center_x - self.__step * 2
        elif self.__volume == 0.2:
            return self.__center_x - self.__step * 3
        elif self.__volume == 0.1:
            return self.__center_x - self.__step * 4
        elif self.__volume == 0.0:
            return self.__center_x - self.__step * 5

    def move_left(self) -> None:
        """
        Move the indicator by step (12.2) to the LEFT.
        """
        self.__rect.move_ip(-self.__step, 0)

    def move_right(self) -> None:
        """
        Move the indicator by step (12.2) to the RIGHT.
        """
        self.__rect.move_ip(self.__step, 0)

    def draw(self, surface: pg.Surface) -> None:
        """
        Draw volume indicator.
        :param surface: surface to draw on (game display)
        """
        surface.blit(self.__image, self.__rect)


class VolumeControl(Button):
    """
    Volume control button.
    """

    def __init__(self, button_type: str, offset: tuple):
        """
        Makes a volume control button.
        :param button_type: type of the button (volume up or down)
        :param offset: offset from the middle of the screen (x, y)
        """

        super().__init__(offset)

        self.click = False  # for preventing clicks

        self.__type = button_type.lower()

        # set images
        self.__set_images()

    def __set_images(self) -> None:
        """
        Load & set images based on the button type.
        """
        load_img = pg.image.load

        # down
        if self.__type == 'down':
            self.__image_normal = load_img(VOLUME_DOWN_IMG).convert_alpha()
            self.__image_hover = load_img(VOLUME_DOWN_HOVER_IMG).convert_alpha()
        # up
        elif self.__type == 'up':
            self.__image_normal = load_img(VOLUME_UP_IMG).convert_alpha()
            self.__image_hover = load_img(VOLUME_UP_HOVER_IMG).convert_alpha()
        # otherwise (error)
        else:
            self.__image_normal = load_img(ERROR_IMG).convert_alpha()
            self.__image_hover = load_img(ERROR_IMG).convert_alpha()

        self.__image = self.__image_normal
        self.rect = self.__image.get_rect()
        self.rect.center = (self.x, self.y)

    def __get_image(self) -> pg.Surface:
        """
        Get image.
        Used to draw the volume control button.
        :return: image
        """
        self.__image = self.__image_normal
        if self.hovered:
            self.__image = self.__image_hover
        return self.__image

    def volume_control(self, indicator: VolumeIndicator, sound: pg.mixer.Sound, sound2: pg.mixer.Sound = None) -> None:
        """
        Change volume (DOWN or UP) based on the button type.
        :param indicator: volume indicator (little zombie image)
        :param sound: sound (required)
        :param sound2: sound 2 (optional)
        """
        # VolumeControl DOWN click
        if self.__type == 'down':
            # sound 1
            vol_change = round(sound.get_volume(), 1) - 0.1
            # sound 2
            if sound2:
                vol_change = round(sound2.get_volume(), 1) - 0.1

            # check volume level
            try:
                # sound 1
                if sound.get_volume() == 0.0:  # if volume is 0.0
                    raise ValueError  # raise ValueError to break
                # sound 2
                if sound2:
                    if sound2.get_volume() == 0.0:  # if volume is 0.0
                        raise ValueError  # raise ValueError to break
            except ValueError:
                self.click = False  # prevents clicks if volume is 0.0 (break)
            # change volume (executed only if except block is not)
            else:
                indicator.move_left()  # move the volume indicator
                # sound 1
                sound.set_volume(max(vol_change, 0.0))  # set volume (max prevents from going below 0.0)
                # sound 2
                if sound2:
                    sound2.set_volume(max(vol_change, 0.0))  # set volume (max prevents from going below 0.0)

        # VolumeControl UP click
        elif self.__type == 'up':
            # sound 1
            vol_change = round(sound.get_volume(), 1) + 0.1
            # sound 2
            if sound2:
                vol_change = round(sound2.get_volume(), 1) + 0.1

            # check volume level
            try:
                # sound 1
                if sound.get_volume() == 1.0:  # if volume is 1.0
                    raise ValueError  # raise ValueError to break
                # sound 2
                if sound2:
                    if sound2.get_volume() == 1.0:  # if volume is 1.0
                        raise ValueError  # raise ValueError to break
            except ValueError:
                self.click = False  # prevents clicks if volume is 1.0 (break)
            # change volume (executed only if except block is not)
            else:
                indicator.move_right()  # move the volume indicator
                # sound 1
                sound.set_volume(min(vol_change, 1.0))  # set volume (min prevents from going over 1.0)
                # sound 2
                if sound2:
                    sound2.set_volume(min(vol_change, 1.0))  # set volume (min prevents from going over 1.0)

    def draw(self, surface: pg.Surface) -> None:
        """
        Draw volume button.
        Get the image & draw it on screen.
        :param surface: surface to draw on (game display)
        """
        surface.blit(self.__get_image(), self.rect)


class OnOffSwitch(Button):
    """
    On-Off switch.
    Toggles settings ON/OFF.
    """

    def __init__(self, setting: bool, offset: tuple):
        """
        Make the ON-OFF switch toggle.
        :param setting: "settings.json" setting (True/False)
        :param offset: offset from the middle of the screen (x, y)
        """

        super().__init__(offset)

        # flags
        self.switched_on = False  # for image flip
        self.__setting = setting  # for setting flip

        self.__set_image()

    def __set_image(self) -> None:
        """
        Set switch image.
        """
        self.__load_images()

        # if ON (True)
        if self.__setting:
            self.switched_on = True
            self.__image = self.__on_img
        # if OFF (False)
        else:
            self.switched_on = False
            self.__image = self.__off_img

        self.rect = self.__image.get_rect()
        self.rect.center = (self.x, self.y)
        self.mask = pg.mask.from_surface(self.__image)  # for precise clicks

    def __load_images(self) -> None:
        """
        Load switch images.
        """
        load_img = pg.image.load

        # on
        self.__on_img = load_img(SWITCH_ON_IMG).convert_alpha()
        self.__on_hover_img = load_img(SWITCH_ON_HOVER_IMG).convert_alpha()

        # off
        self.__off_img = load_img(SWITCH_OFF_IMG).convert_alpha()
        self.__off_hover_img = load_img(SWITCH_OFF_HOVER_IMG).convert_alpha()

    def __get_image(self) -> pg.Surface:
        """
        Get image.
        Used to draw the switch.
        :return: image
        """
        # if ON
        if self.switched_on:
            self.__image = self.__on_img
            if self.hovered:
                self.__image = self.__on_hover_img
        # if OFF
        else:
            self.__image = self.__off_img
            if self.hovered:
                self.__image = self.__off_hover_img

        return self.__image

    def flip_switch(self) -> None:
        """
        Flip the switch & setting ON/OFF (True/False).
        """
        self.switched_on = not self.switched_on
        self.__setting = not self.__setting

    def draw(self, surface: pg.Surface) -> None:
        """
        Draw the ON-OFF switch.
        Get the image & draw it on screen.
        :param surface: surface to draw on (game display)
        """
        surface.blit(self.__get_image(), self.rect)


class MuteToggle(Button):
    """
    Mute sounds.
    """

    def __init__(self, setting: bool, offset: tuple):
        """
        Make a mute toggle button.
        :param setting: "settings.json" setting (True/False)
        :param offset: offset from the middle of the screen (x, y)
        """

        super().__init__(offset)

        # flags
        self.mute = False  # for image flip
        self.__setting = setting  # for setting flip

        # initialize images
        self.__set_image()  # set the starting image

    def __load_images(self) -> None:
        """
        Load mute toggle images.
        """
        load_img = pg.image.load

        # mute images
        self.__mute_normal = load_img(MUTE_IMG).convert_alpha()
        self.__mute_hover = load_img(MUTE_HOVER_IMG).convert_alpha()

        # un-mute images
        self.__un_mute_normal = load_img(UN_MUTE_IMG).convert_alpha()
        self.__un_mute_hover = load_img(UN_MUTE_HOVER_IMG).convert_alpha()

    def __set_image(self) -> None:
        """
        Set the default (starting) image.
        """
        self.__load_images()

        # mute
        if self.__setting:
            self.mute = False  # image flip
            self.__image = self.__mute_normal  # set image
        # un-mute
        else:
            self.mute = True  # image flip
            self.__image = self.__un_mute_normal  # set image

        self.rect = self.__image.get_rect()
        self.rect.center = (self.x, self.y)

    def __get_image(self) -> pg.Surface:
        """
        Get image.
        Used to draw the mute toggle.
        :return: image
        """
        # mute
        if self.mute:
            self.__image = self.__mute_normal
            if self.hovered:
                self.__image = self.__mute_hover
        # not mute
        else:
            self.__image = self.__un_mute_normal
            if self.hovered:
                self.__image = self.__un_mute_hover

        return self.__image

    def toggle(self) -> None:
        """
        Toggle mute/un-mute.
        """
        self.mute = not self.mute
        self.__setting = not self.__setting

    def draw(self, surface: pg.Surface) -> None:
        """
        Draw the mute toggle.
        Get the image & draw it on screen.
        :param surface: surface to draw on (game display)
        """
        surface.blit(self.__get_image(), self.rect)
