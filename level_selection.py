import sys

import pygame as pg
import const
from const import Button


class LevelSelection:
    def __init__(self, screen: pg.Surface):
        self.sc = screen
        self.running = True
        self.gui_buttons = pg.sprite.Group()
        self.play_buttons = pg.sprite.Group()
        self.edit_buttons = pg.sprite.Group()
        self.mode = 'play'

    def create_button(self, group: str, x: int, y: int, w: int, h: int, rectColor: pg.Color, onHoverRectColor: pg.Color, callback,
                      **kwargs):
        new_button = Button(x, y, w, h, rectColor, onHoverRectColor, callback, **kwargs)
        if group == 'play':
            self.play_buttons.add(new_button)
        elif group == 'edit':
            self.edit_buttons.add(new_button)
        elif group == 'gui':
            self.gui_buttons.add(new_button)

    def make_gui(self):
        self.gui_buttons.empty()
        self.play_buttons.empty()
        self.edit_buttons.empty()

        button_width = const.sc_width / 4
        button_height = const.sc_height / 10

        self.create_button('gui', 2 * const.sc_width / 8, button_height / 2, button_width, button_height,
                           pg.Color(0, 100, 255), pg.Color(0, 200, 0), lambda: self.change_mode('play'), text='Play', textColor=pg.Color(0, 0, 0))

        self.create_button('gui', 4 * const.sc_width / 8, button_height / 2, button_width, button_height,
                           pg.Color(0, 100, 255), pg.Color(0, 200, 0), lambda: self.change_mode('edit'), text='Edit', textColor=pg.Color(0, 0, 0))

        self.create_button('gui', 6 * const.sc_width / 8, button_height / 2, button_width, button_height,
                            pg.Color(150,0,250), pg.Color(0,200,0), lambda: self.create_level_to_edit(), text='Creer niveau', textColor=pg.Color(0,0,0))

        self.make_buttons()

    def make_buttons(self):
        const.refresh_number_of_levels()
        for text, group, mode in [('Custom', 'edit', 'editing'),('Level','play', 'playing')]:
            button_width = const.sc_width / 4
            button_height = const.sc_height / 10
            left_column_x = const.sc_width / 10
            mid_column_x = 3 * const.sc_width / 8
            right_column_x = const.sc_width - left_column_x - button_width
            x_to_draw = left_column_x
            level_number = const.number_of_levels if mode == 'playing' else const.number_of_edited_levels
            for level in range(1, level_number + 1):
                if level == 8:
                    x_to_draw = mid_column_x
                elif level == 16:
                    x_to_draw = right_column_x
                self.create_button(group, x_to_draw, button_height / 2 + (button_height + 10) * (level % 8 if level % 8 != 0 else 1), button_width,
                                   button_height, pg.Color(255, 0, 0), pg.Color(0, 200, 0), lambda n=level, m=mode: self.select_level(n, m),
                                   text=f'{text} {level}', textColor=pg.Color(0, 0, 0))

    def create_level_to_edit(self):
        f = open(f'Edited_Levels/level_{const.number_of_edited_levels + 1}.json', 'x')
        f.write('{}')
        self.change_mode('edit')
        self.select_level(const.number_of_edited_levels + 1, 'editing')


    def change_mode(self, mode: str):
        self.mode = mode

    def select_level(self, n: int, mode: str):
        const.level = n
        self.running = False
        const.change_mode(mode)

    def update_buttons_group(self, *args):
        self.gui_buttons.update(*args)
        if self.mode == 'play':
            self.play_buttons.update(*args)
        elif self.mode == 'edit':
            self.edit_buttons.update(*args)

    def handle_keys(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                sys.exit()
            elif e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    self.update_buttons_group(pg.mouse.get_pos(), True)
                    pg.event.clear(pg.MOUSEBUTTONDOWN)
            elif e.type == pg.MOUSEMOTION:
                self.update_buttons_group(pg.mouse.get_pos(), False)

    def main(self, framerate: int):
        clock = pg.time.Clock()
        self.make_gui()
        while self.running:
            clock.tick(framerate)
            self.handle_keys()

            self.sc.fill(pg.Color(0, 0, 0))

            self.gui_buttons.draw(self.sc)
            if self.mode == 'play':
                self.play_buttons.draw(self.sc)
            elif self.mode == 'edit':
                self.edit_buttons.draw(self.sc)

            pg.display.flip()
