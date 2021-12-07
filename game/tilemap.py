from . import pg
from .config import WIDTH, HEIGHT
import pytmx


class TiledMap:
    """
    Map made with Tiled map editor.
    """

    def __init__(self, filename: str):
        """
        Initialize tiled map.
        The map dimensions are 26x26 tiles.
        Each tile is 64x64 px.
        :param filename: .tmx (map) file
        """

        tiled_map = pytmx.load_pygame(filename, pixelalpha=True)

        # map width & height
        self.width = tiled_map.width * tiled_map.tilewidth
        self.height = tiled_map.height * tiled_map.tileheight

        # hold all this stuff so we can refer to it
        self.tmx_data = tiled_map

    def __render(self, surface: pg.Surface):
        """
        Draw all the tiles of the map onto the surface.
        :param surface: pygame surface
        """
        # visible_layers - if checked as visible in tiled
        for layer in self.tmx_data.visible_layers:
            # if layer is of TiledTileLayer type
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    # find the image that goes with the number (tile)
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    # if there is a tile (image) with that ID, draw it on screen
                    if tile:
                        surface.blit(tile, (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight))

    def make_map(self) -> pg.Surface:
        """
        Create a surface to draw the map onto.
        :return: temp_surface (pg.Surface)
        """
        temp_surface = pg.Surface((self.width, self.height))
        self.__render(temp_surface)
        return temp_surface


class Camera:
    """
    Camera to follow player and other sprites.
    """

    def __init__(self, width: int, height: int):
        """
        Make the camera.
        Camera is a pygame.Rect object.
        Camera width & height are the same as map's.
        :param width: camera width
        :param height: camera height
        """
        self.__camera = pg.Rect(0, 0, width, height)  # default camera rect
        self.width = width
        self.height = height

    def apply(self, sprite):
        """
        Applying the offset to a sprite.
        Shifting the sprite's rect to where it needs to be.
        Used when drawing sprites on screen.

        :param sprite: a sprite (player, mobs, obstacles...)
        :return: sprite's rect moved by camera's top-left coordinates
        """
        return sprite.rect.move(self.__camera.topleft)

    def apply_rect(self, rect):
        """
        Applying the offset to a rect.
        Take a rectangle, and move it by whatever the camera offset is.
        Used when drawing the map on screen.

        :param rect: a rectangle
        :return: moved rectangle
        """
        return rect.move(self.__camera.topleft)

    def update(self, player):
        """
        Update the camera to follow player.
        Go the opposite direction to the player.
        :param player: player
        """

        # player's X & Y position (keep the player in camera's center)
        player_x = -player.rect.centerx + int(WIDTH / 2)
        player_y = -player.rect.centery + int(HEIGHT / 2)

        # screen limits (don't draw beyond map borders)
        left = min(190, player_x)
        right = -(self.width - WIDTH) - 190
        top = min(0, player_y) + 108
        bottom = -(self.height - HEIGHT) - 108

        # camera's X & Y positions
        x = max(right, left)
        y = max(bottom, top)

        # update camera rect
        self.__camera = pg.Rect(x, y, self.width, self.height)
