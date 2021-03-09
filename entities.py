import pygame as pg
import const


class Tile(pg.sprite.DirtySprite):
    def __init__(self, screen_x, screen_y, world_x, world_y, group: pg.sprite.LayeredDirty, editing=False, text=''):
        super().__init__()
        group.add(self)
        self.image = pg.Surface([const.tile_side, const.tile_side])
        self.image.fill(pg.Color(255, 0, 0))
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


class Jumper(Tile):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, group, **kwargs)
        self.image = const.load_sprite('jumper')


class Spike(Tile):
    def __init__(self, screen_x, screen_y, world_x, world_y, side, group, **kwargs):
        """
        side : n s e w
        """
        super().__init__(screen_x, screen_y, world_x, world_y, group, **kwargs)
        self.image = const.load_sprite('spike_' + side)
        self.side = side


class Spike_N(Spike):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, 'n', group, **kwargs)


class Spike_W(Spike):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, 'w', group, **kwargs)


class Spike_E(Spike):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, 'e', group, **kwargs)


class Spike_S(Spike):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, 's', group, **kwargs)


class Spike_NE(Spike):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, 'ne', group, **kwargs)


class Spike_NW(Spike):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, 'nw', group, **kwargs)


class Spike_SE(Spike):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, 'se', group, **kwargs)


class Spike_SW(Spike):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, 'sw', group, **kwargs)


class EndTile(Tile):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, group, **kwargs)
        self.image = const.load_sprite('end')


class BackwardPusher(Tile):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, group, **kwargs)
        self.image = const.load_sprite('backward_jumper')


class InfoBlock(Tile):
    def __init__(self, screen_x, screen_y, world_x, world_y, group, text, **kwargs):
        super().__init__(screen_x, screen_y, world_x, world_y, group, **kwargs)
        self.image = const.load_sprite('info_block')
        self.text = text


# key must match the name of its sprite in Background_Sprites/
building_tiles = {"tile": Tile, 'jumper': Jumper, 'spike_n': Spike_N, 'spike_w': Spike_W, 'spike_e': Spike_E,
                  'spike_s': Spike_S, 'spike_ne': Spike_NE, 'spike_nw': Spike_NW, 'spike_se': Spike_SE, 'spike_sw': Spike_SW,
                  'end': EndTile, "backward_jumper": BackwardPusher, 'info_block': InfoBlock}
