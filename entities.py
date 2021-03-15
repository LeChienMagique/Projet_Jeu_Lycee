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
    def __init__(self, screen_x, screen_y, world_x, world_y, group, facing: int = 0, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, group, image=const.get_sprite('jumper', facing=facing), facing=facing, **kwargs)


class Spike(Tile):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, facing: int = 0, **kwargs):
        """
        side : n s e w
        """
        super().__init__(screen_x, screen_y, world_x, world_y, group, image=const.get_sprite('spike', facing=facing), facing=facing, **kwargs)


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

building_tiles = {"tile": Tile, 'jumper': Jumper, 'end': EndTile, "backward_jumper": BackwardPusher,
                  'info_block': InfoBlock, 'gravity_inverter': GravInverter, "spike": Spike,
                  'minimizer': Minimizer, 'player_spawn': PlayerSpawn, 'checkpoint': Checkpoint}
non_rotating_tiles = ["tile", 'info_block', 'player_spawn', 'checkpoint', 'minimizer', 'end']
