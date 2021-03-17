import sys
import pygame as pg
import const
from const import Button
from random import choice


class LevelSelection:
    def __init__(self, screen: pg.Surface):
        self.sc = screen
        self.running = True
        self.gui_buttons = pg.sprite.Group()
        self.play_buttons = pg.sprite.Group()
        self.edit_buttons = pg.sprite.Group()
        self.background = pg.sprite.LayeredUpdates(const.make_background_group(choice(const.background_group_names)))
        self.mode = 'play'

    def create_button(self, group: str, x: int, y: int, w: int, h: int, callback, **kwargs):
        """
        Permet de créer un bouton.
        :param group:
        :param x:
        :param y:
        :param w:
        :param h:
        :param rectColor:
        :param onHoverRectColor:
        :param callback:
        :param kwargs:
        :return:
        """
        new_button = Button(x, y, w, h, callback, **kwargs)
        if group == 'play':
            self.play_buttons.add(new_button)
        elif group == 'edit':
            self.edit_buttons.add(new_button)
        elif group == 'gui':
            self.gui_buttons.add(new_button)

    def make_gui(self):
        """
        Créé tous les boutons du menu
        :return:
        """
        self.gui_buttons.empty()
        self.play_buttons.empty()
        self.edit_buttons.empty()

        button_width = const.sc_width // 4
        button_height = const.sc_height // 10

        self.create_button('gui', 2 * const.sc_width // 8, button_height // 2, button_width, button_height, lambda: self.change_mode('play'),
                           image=const.get_sprite('right', icon=True))

        self.create_button('gui', 4 * const.sc_width // 8, button_height // 2, button_width, button_height, lambda: self.change_mode('edit'),
                           image=const.get_sprite('wrench', icon=True))

        self.create_button('gui', 6 * const.sc_width // 8, button_height // 2, button_width, button_height, lambda: self.create_level_to_edit(),
                           image=const.get_sprite('plus', icon=True))

        power_button_width = button_width // 4
        power_button_height = button_height // 2
        self.create_button('gui', const.sc_width - power_button_width, const.sc_height - power_button_height, power_button_width, power_button_height,
                           lambda: sys.exit(), image=const.get_sprite('power', icon=True))

        self.make_buttons()

    def make_buttons(self):
        """
        Créé tous les boutons de seléction de niveau
        :return:
        """
        const.refresh_number_of_levels()
        for text, group, mode in [('Custom', 'edit', 'editing'), ('Level', 'play', 'playing')]:
            button_width = const.sc_width // 4
            button_height = const.sc_height // 10
            left_column_x = const.sc_width // 10
            mid_column_x = 3 * const.sc_width // 8
            right_column_x = const.sc_width - left_column_x - button_width
            x_to_draw = left_column_x
            level_number = const.number_of_levels if mode == 'playing' else const.number_of_edited_levels
            for level in range(0, level_number):
                if level == 7:
                    x_to_draw = mid_column_x
                elif level == 14:
                    x_to_draw = right_column_x
                self.create_button(group, x_to_draw, button_height // 2 + (button_height + 10) * (level % 7 + 1), button_width,
                                   button_height, lambda n=level + 1, m=mode: self.select_level(n, m), text=f'{text} {level + 1}', textColor=pg.Color(0, 0, 0))

    def create_level_to_edit(self):
        """
        Créé un nouveau niveau éditable dans Edited_Levels/
        :return:
        """
        if const.number_of_edited_levels >= 21:
            return
        f = open(f'Edited_Levels/level_{const.number_of_edited_levels + 1}.json', 'x')
        f.write(const.blank_level_data)
        self.change_mode('edit')
        self.select_level(const.number_of_edited_levels + 1, 'editing')

    def change_mode(self, mode: str):
        """
        Permet de changer de mode (editing, playing)
        :param mode:
        :return:
        """
        self.mode = mode

    def select_level(self, n: int, mode: str):
        """
        Joue ou édite le niveau seléctionné.
        :param n:
        :param mode:
        :return:
        """
        const.level = n
        self.running = False
        const.change_mode(mode)

    def update_buttons_group(self, *args):
        """
        Update tous les boutons du menu
        :param args:
        :return:
        """
        self.gui_buttons.update(*args)
        if self.mode == 'play':
            self.play_buttons.update(*args)
        elif self.mode == 'edit':
            self.edit_buttons.update(*args)

    def handle_keys(self):
        """
        Gère les touches pressées par l'utilisateur
        :return:
        """
        for e in pg.event.get():
            if e.type == pg.QUIT:  # Quand l'utilisateur clique sur la X de la fenêtre de jeu
                sys.exit()
            elif e.type == pg.MOUSEBUTTONDOWN:  # Pour limiter les appels à la méthode update des boutons, update que quand la souris bouge ou que le bouton de
                # la souris est appuyée
                if e.button == 1:
                    self.update_buttons_group(pg.mouse.get_pos(), True)
                    pg.event.clear(pg.MOUSEBUTTONDOWN)
            elif e.type == pg.MOUSEMOTION or e.type == pg.MOUSEBUTTONUP:
                self.update_buttons_group(pg.mouse.get_pos(), False)

    def main(self, framerate: int):
        """
        Méthode principale
        :param framerate:
        :return:
        """
        clock = pg.time.Clock()
        self.make_gui()
        self.background.empty()
        self.background.add(const.make_background_group(choice(const.background_group_names)))
        while self.running:
            clock.tick(framerate)
            self.handle_keys()

            self.background.update()
            self.background.draw(self.sc)

            # Dessine les boutons
            self.gui_buttons.draw(self.sc)
            if self.mode == 'play':
                self.play_buttons.draw(self.sc)
            elif self.mode == 'edit':
                self.edit_buttons.draw(self.sc)

            pg.display.flip()
