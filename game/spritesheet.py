from . import pg
from .config import BLACK
import json


class SpriteSheet:
    """
    Utility class for loading and parsing sprite sheets.
    """

    def __init__(self, filename: str, is_sprite: bool = False):
        """
        Initialize sprite sheet.
        :param filename: sprite sheet file
        :param is_sprite: True if sprite sheet contains player/zombie sprites
        """
        self.__is_sprite = is_sprite

        self.__sprite_sheet = pg.image.load(filename).convert()

        # load data
        self.__meta_data = filename.replace('png', 'json')  # change .png to .json (because the name is the same)
        with open(self.__meta_data) as f:
            self.__data = json.load(f)  # converts data from the json file into python dictionary

    def __get_sprite(self, x: int, y: int, width: int, height: int) -> pg.Surface:
        """
        Get sprite image.
        :param x: x from .json file
        :param y: y from .json file
        :param width: width from .json file
        :param height: height from .json file
        :return: pygame surface (sprite image)
        """
        sprite = pg.Surface((width, height))
        sprite.set_colorkey(BLACK)
        sprite.blit(self.__sprite_sheet, (0, 0), (x, y, width, height))

        # scale if sprite (player or zombie)
        if self.__is_sprite:
            scale_width = sprite.get_width() // 2
            scale_height = int(sprite.get_height() // 2.5)
            sprite = pg.transform.scale(sprite, (scale_width, scale_height))

        return sprite

    def parse_sprite(self, name: str) -> pg.Surface:
        """
        Parse the sprite.
        :param name: name of the sprite image in .json file
        :return: pygame surface (sprite image)
        """
        sprite = self.__data['frames'][name]['frame']
        x, y, width, height = sprite['x'], sprite['y'], sprite['w'], sprite['h']
        return self.__get_sprite(x, y, width, height)
