import pygame as pg
import const


class Tile(pg.sprite.DirtySprite):
    def __init__(self, screen_x, screen_y, world_x, world_y, group: any, image: pg.Surface = None, facing: int = 0, editing: bool = False, text: str = ''):
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
        if self.rect.right < 0:
            self.dirty = 0
            self.visible = 0
        elif self.rect.left < const.sc_width + const.tile_side:
            self.visible = 1
            self.dirty = 2

        if self.editing:
            if 0 < self.rect.top < 16 * (const.tile_side + 1) + 1:
                self.visible = 1
                self.dirty = 2
            else:
                self.visible = 0
                self.dirty = 0

    def flip_horizontally(self):
        self.image = pg.transform.flip(self.image, False, True)


class Jumper(Tile):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, facing: int = 0, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, group, image=const.get_sprite('jumper', facing=facing), facing=facing, **kwargs)


class Spike(Tile):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, facing: int = 0, **kwargs):
        """
        side : n s e w
        """
        super().__init__(screen_x, screen_y, world_x, world_y, group, image=const.get_sprite('spike', facing=facing), facing=facing, **kwargs)


"""class Spike_N(Spike):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, 0, group, **kwargs)


class Spike_W(Spike):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, 2, group, **kwargs)


class Spike_E(Spike):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, 6, group, **kwargs)


class Spike_S(Spike):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, 4, group, **kwargs)


class Spike_NE(Spike):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, 1, group, **kwargs)


class Spike_NW(Spike):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, 7, group, **kwargs)


class Spike_SE(Spike):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, 3, group, **kwargs)


class Spike_SW(Spike):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, 5, group, **kwargs)

"""


class EndTile(Tile):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, group, image=const.get_sprite('end'), **kwargs)


class BackwardPusher(Tile):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, facing: int = 0, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, group, image=const.get_sprite('backward_jumper', facing=facing), facing=facing, **kwargs)


class InfoBlock(Tile):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, text, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, group, image=const.get_sprite('info_block'), **kwargs)
        self.text = text


class GravInverter(Tile):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, facing: int = 0, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, group, image=const.get_sprite('gravity_inverter', facing=facing), facing=facing, **kwargs)


class Minimizer(Tile):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, group, image=const.get_sprite('minimizer'), **kwargs)
        self.disabled = False


class PlayerSpawn(Tile):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, group, image=const.get_sprite('player_spawn'), **kwargs)


class Checkpoint(Tile):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, group, image=const.get_sprite('checkpoint'), **kwargs)


# key must match the name of its sprite in Background_Sprites/
"""building_tiles = {"tile": Tile, 'jumper': Jumper, 'spike0': Spike_N, 'spike2': Spike_W, 'spike4': Spike_E,
                  'spike6': Spike_S, 'spike1': Spike_NE, 'spike7': Spike_NW, 'spike3': Spike_SE, 'spike5': Spike_SW,
                  'end': EndTile, "backward_jumper": BackwardPusher, 'info_block': InfoBlock, 'gravity_inverter': GravInverter,
                  'minimizer': Minimizer, 'player_spawn': PlayerSpawn, 'checkpoint': Checkpoint}
"""

building_tiles = {"tile": Tile, 'jumper': Jumper, 'end': EndTile, "backward_jumper": BackwardPusher,
                  'info_block': InfoBlock, 'gravity_inverter': GravInverter, "spike": Spike,
                  'minimizer': Minimizer, 'player_spawn': PlayerSpawn, 'checkpoint': Checkpoint}
non_rotating_tiles = ["tile", 'info_block', 'player_spawn', 'checkpoint', 'minimizer', 'end']
