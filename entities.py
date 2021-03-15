import pygame as pg
import const


class Tile(pg.sprite.DirtySprite):
    """
    Classe mère de toutes les types de blocs, est aussi la classe du bloc de construction de base
    """

    def __init__(self, screen_x, screen_y, world_x, world_y, group: any, image: pg.Surface = None, facing: int = 0, editing: bool = False):
        super().__init__()
        group.add(self)
        self.facing = facing
        if image is None:
            self.image = const.get_sprite('tile')
        else:
            self.image = image
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        self.editing = editing
        self.rect.x = screen_x
        self.rect.y = screen_y
        self.x = world_x
        self.y = world_y
        self.visible = 0
        self.dirty = 0

    def update(self, *args, **kwargs) -> None:
        """
        Actualise la tile, la rend invisible quand elle ne doit pas être visible
        :param args:
        :param kwargs:
        """
        if self.rect.right < 0 or self.rect.top > const.sc_height or self.rect.bottom < 0:
            self.dirty = 0
            self.visible = 0
        else:
            self.visible = 1
            self.dirty = 2

        if self.editing:
            if 0 < self.rect.bottom <= 21 * const.tile_side + 1:
                self.visible = 1
                self.dirty = 2
            else:
                self.visible = 0
                self.dirty = 0


class Jumper(Tile):
    """
    Crée une tile jumper
    """

    def __init__(self, screen_x, screen_y, world_x, world_y, group, facing: int = 0, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, group, image=const.get_sprite('jumper', facing=facing), facing=facing, **kwargs)


class Spike(Tile):
    """
    Crée une tile spike
    """

    def __init__(self, screen_x, screen_y, world_x, world_y, group, facing: int = 0, **kwargs):
        """
        side : n s e w
        """
        super().__init__(screen_x, screen_y, world_x, world_y, group, image=const.get_sprite('spike', facing=facing), facing=facing, **kwargs)


class EndTile(Tile):
    """
    Crée une tile end
    """

    def __init__(self, screen_x, screen_y, world_x, world_y, group, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, group, image=const.get_sprite('end'), **kwargs)


class BackwardPusher(Tile):
    """
    Crée une tile backward jumper
    """

    def __init__(self, screen_x, screen_y, world_x, world_y, group, facing: int = 0, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, group, image=const.get_sprite('backward_jumper', facing=facing), facing=facing, **kwargs)


class InfoBlock(Tile):
    """
    Crée une tile info block
    """

    def __init__(self, screen_x, screen_y, world_x, world_y, group, text, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, group, image=const.get_sprite('info_block'), **kwargs)
        self.text = text


class GravInverter(Tile):
    """
    Crée une tile gravity inverter
    """

    def __init__(self, screen_x, screen_y, world_x, world_y, group, facing: int = 0, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, group, image=const.get_sprite('gravity_inverter', facing=facing), facing=facing, **kwargs)


class Minimizer(Tile):
    """
    Crée une tile minimizer
    """

    def __init__(self, screen_x, screen_y, world_x, world_y, group, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, group, image=const.get_sprite('minimizer'), **kwargs)
        self.disabled = False


class PlayerSpawn(Tile):
    """
    Crée une tile player spawn
    """

    def __init__(self, screen_x, screen_y, world_x, world_y, group, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, group, image=const.get_sprite('player_spawn'), **kwargs)


class Checkpoint(Tile):
    """
    Crée une tile checkpoint
    """

    def __init__(self, screen_x, screen_y, world_x, world_y, group, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, group, image=const.get_sprite('checkpoint'), **kwargs)


# key must match the name of its sprite in Background_Sprites/
building_tiles = {"tile": Tile, 'jumper': Jumper, 'end': EndTile, "backward_jumper": BackwardPusher,
                  'info_block': InfoBlock, 'gravity_inverter': GravInverter, "spike": Spike,
                  'minimizer': Minimizer, 'player_spawn': PlayerSpawn, 'checkpoint': Checkpoint}
non_rotating_tiles = ["tile", 'info_block', 'player_spawn', 'checkpoint', 'minimizer', 'end']
