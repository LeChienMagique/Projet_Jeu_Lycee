import pygame as pg
import json
import const
from const import Button
import entities as ent
import sys


class LevelEditor:
    def __init__(self, screen: pg.Surface):
        self.sc = screen
        self.worldx = 0  # les coordonnées du coin en haut à gauche de l'éditeur
        self.worldy = 0
        self.grid_square_side = const.tile_side + 1

        self.background_group = pg.sprite.LayeredUpdates(const.background)
        self.buttons = pg.sprite.Group()
        self.tiles = pg.sprite.LayeredDirty()
        self.info_block_editor = pg.sprite.Group()
        self.info_block_editor_text_input_dims = [3 * self.grid_square_side, 2 * self.grid_square_side, 19 * self.grid_square_side, 9 * self.grid_square_side]

        self.running = True
        self.building_tiles = ent.building_tiles
        self.building_tiles_names = list(self.building_tiles.keys())
        self.selected_building_tile = "tile"
        self.grid = self.create_grid_background()
        self.gui = self.make_gui()
        self.level = {}
        self.info_block_editor_active = False
        self.input_text = ''

    def create_grid_background(self):
        back = pg.Surface((25 * self.grid_square_side, 16 * self.grid_square_side))
        self.draw_grid(back)
        return back

    def draw_grid(self, surf):
        for col in range(25):
            pg.draw.line(surf, pg.Color(220, 220, 220), (col * self.grid_square_side, 0),
                         (col * self.grid_square_side, self.sc.get_height()))
        for row in range(16):
            pg.draw.line(surf, pg.Color(220, 220, 220), (0, row * self.grid_square_side),
                         (self.sc.get_width(), row * self.grid_square_side))

    def create_button(self, x: int, y: int, w: int, h: int, rectColor: pg.Color, onHoverRectColor: pg.Color, callback, group: pg.sprite.Group = None, **kwargs):
        x *= self.grid_square_side
        y *= self.grid_square_side
        w *= self.grid_square_side
        h *= self.grid_square_side
        new_button = Button(x, y, w, h, rectColor, onHoverRectColor, callback, **kwargs)
        if group is None:
            self.buttons.add(new_button)
        else:
            group.add(new_button)

    def check_buttons(self, mouse_pressed: bool):
        self.buttons.update(pg.mouse.get_pos(), mouse_pressed)

    def get_square_on_pos(self, pos) -> tuple:
        """
        Renvoie la position absolue du carré, dans lequel est le curseur, sur l'écran ainsi que sa position dans le plan
        :param pos:
        :return:
        """
        square_screenx = (pos[0] // self.grid_square_side) * self.grid_square_side + 1
        square_screeny = (pos[1] // self.grid_square_side) * self.grid_square_side + 1
        square_worldx = (pos[0] // self.grid_square_side) + self.worldx
        square_worldy = (pos[1] // self.grid_square_side) - self.worldy
        return (square_screenx, square_screeny, square_worldx, square_worldy)

    def try_place_block_at_mouse(self, mousepos):
        """
        Teste si un bloc peut être placé en dessous de la souris et le place si oui
        :param mousepos:
        :return:
        """
        square_screeny, world_x, world_y = self.get_square_on_pos(mousepos)[1:]
        if square_screeny < self.grid.get_rect().bottom:
            self.place_block_at(world_x, world_y, self.selected_building_tile)

    def make_info_block_editor_menu(self, block_x, block_y):
        self.info_block_editor.empty()

        rect_x, rect_y, rect_w, rect_h = self.info_block_editor_text_input_dims
        gray_rectangle = pg.Surface((rect_w, rect_h))
        gray_rectangle.fill(pg.Color(150, 150, 150))

        input_box = pg.sprite.Sprite()
        input_box.image = gray_rectangle
        input_box.rect = input_box.image.get_rect()
        input_box.rect.left = rect_x
        input_box.rect.top = rect_y

        self.info_block_editor.add(input_box)
        self.create_button(8, 12, 5, 3, pg.Color(0, 0, 200), pg.Color(0, 200, 0), lambda x=block_x, y=block_y: self.validate_text_input_info_block(x, y),
                           text='Valider', textColor=pg.Color(0, 0, 0), group=self.info_block_editor)
        self.create_button(14, 12, 5, 3, pg.Color(0, 0, 200), pg.Color(0, 200, 0),
                           lambda x=block_x, y=block_y: self.validate_text_input_info_block(x, y, canceled=True),
                           text='Annuler', textColor=pg.Color(0, 0, 0), group=self.info_block_editor)

    def draw_info_block_editor(self):
        txt_surf = const.myFont.render(self.input_text, True, (255, 255, 255))
        self.info_block_editor.draw(self.sc)
        self.sc.blit(txt_surf, (self.info_block_editor_text_input_dims[0] + 5, self.info_block_editor_text_input_dims[1] + 5))

    def prompt_info_block_editor(self):
        self.info_block_editor_active = True
        pg.key.set_repeat(150, 100)

    def validate_text_input_info_block(self, block_x, block_y, canceled=False):
        self.info_block_editor_active = False
        pg.key.set_repeat(75, 75)
        if not canceled:
            self.place_block_at(block_x, block_y, 'info_block', self.input_text)
        self.input_text = ''

    def place_block_at(self, world_x: int, world_y: int, tile_type: str, info_block_text=''):
        """
        Place un bloc au coord données
        :param info_block_text:
        :param world_x:
        :param world_y:
        :param tile_type:
        :return:
        """
        if tile_type == 'info_block' and info_block_text == '':
            self.make_info_block_editor_menu(world_x, world_y)
            self.prompt_info_block_editor()
            return

        screen_x, screen_y = ((world_x - self.worldx) * self.grid_square_side + 1), ((world_y + self.worldy) * self.grid_square_side + 1)
        new_tile = self.building_tiles[tile_type](screen_x, screen_y, world_x, world_y, group=self.tiles, editing=True, text=info_block_text)
        for collidingS in pg.sprite.spritecollide(new_tile, self.tiles, False):  # Empêche que plusieures tiles soit à la même position.
            if collidingS != new_tile:
                collidingS.kill()
        if not str(world_x) in self.level:
            self.level[str(world_x)] = {str(world_y): tile_type}
        else:
            self.level[str(world_x)][str(world_y)] = tile_type

        if tile_type == 'info_block':
            if 'info_block_text' not in self.level:
                self.level['info_block_text'] = {str(world_x): {str(world_y): info_block_text}}
            if str(world_x) not in self.level['info_block_text']:
                self.level['info_block_text'][str(world_x)] = {str(world_y): info_block_text}

    def delete_block_at(self, position):
        """
        Supprime un bloc a la position donnée
        :param position:
        :return:
        """
        sprite: ent.Tile
        x, y = position[0], position[1]
        if str(x) in self.level:
            if str(y) in self.level[str(x)]:
                for sprite in self.tiles:
                    if sprite.x == x and sprite.y == y:
                        sprite.kill()
                        if self.level[str(x)][str(y)] == 'info_block':
                            del self.level['info_block_text'][str(x)][str(y)]
                            if len(self.level['info_block_text'][str(x)]) == 0:
                                del self.level['info_block_text'][str(x)]

                        del self.level[str(x)][str(y)]
                        if len(self.level[str(x)]) == 0:
                            del self.level[str(x)]

    def handle_keys(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                sys.exit()
            if self.info_block_editor_active:
                if e.type == pg.KEYDOWN:
                    if e.key == pg.K_ESCAPE:
                        self.info_block_editor_active = False
                        # self.input_text = ''
                    elif e.key == pg.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    elif e.key == pg.K_RETURN:
                        self.input_text += '\n'
                    else:
                        self.input_text += e.unicode
                elif e.type == pg.MOUSEMOTION:
                    self.info_block_editor.update(pg.mouse.get_pos(), False)
                elif e.type == pg.MOUSEBUTTONDOWN:
                    self.info_block_editor.update(pg.mouse.get_pos(), True)
                return

            mouse_buttons = pg.mouse.get_pressed(3)
            if mouse_buttons[0]:
                self.try_place_block_at_mouse(pg.mouse.get_pos())
                if self.running:
                    self.check_buttons(True)
                else:
                    return
            elif mouse_buttons[2]:
                self.delete_block_at(self.get_square_on_pos(pg.mouse.get_pos())[2:])

            if e.type == pg.MOUSEMOTION:
                self.check_buttons(False)
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_z:
                    self.scroll_level(0, 1)
                elif e.key == pg.K_d:
                    self.scroll_level(-1, 0)
                elif e.key == pg.K_s:
                    self.scroll_level(0, -1)
                elif e.key == pg.K_q:
                    self.scroll_level(1, 0)
                elif e.key == pg.K_p:
                    self.change_mode('playing')
                elif e.key == pg.K_ESCAPE:
                    self.change_mode('level_selection')
                elif e.key == pg.K_1:
                    self.change_selected_building_tile(self.building_tiles_names[0])
                elif e.key == pg.K_2:
                    self.change_selected_building_tile(self.building_tiles_names[1])
                elif e.key == pg.K_3:
                    self.change_selected_building_tile(self.building_tiles_names[2])
                elif e.key == pg.K_4:
                    self.change_selected_building_tile(self.building_tiles_names[3])
                elif e.key == pg.K_5:
                    self.change_selected_building_tile(self.building_tiles_names[4])
                elif e.key == pg.K_6:
                    self.change_selected_building_tile(self.building_tiles_names[5])
                elif e.key == pg.K_7:
                    self.change_selected_building_tile(self.building_tiles_names[6])
                elif e.key == pg.K_8:
                    self.change_selected_building_tile(self.building_tiles_names[7])
                elif e.key == pg.K_9:
                    self.change_selected_building_tile(self.building_tiles_names[8])
                elif e.key == pg.K_0:
                    self.change_selected_building_tile(self.building_tiles_names[9])

    def highlight_square(self, mousepos):
        squarex, squarey = self.get_square_on_pos(mousepos)[0:2]
        if squarey < self.grid.get_rect().bottom:
            pg.draw.rect(self.sc, pg.Color(200, 200, 200),
                         pg.rect.Rect(squarex, squarey, self.grid_square_side, self.grid_square_side))

    def ghost_selected_tile_on_cursor(self, mousepos):
        squarex, squarey = self.get_square_on_pos(mousepos)[0:2]
        if squarey < self.grid.get_rect().bottom:
            sprite = const.load_sprite(self.selected_building_tile)
            self.sc.blit(sprite, (squarex, squarey))

    def change_selected_building_tile(self, tile_name):
        self.selected_building_tile = tile_name

    def make_gui(self) -> pg.Surface:
        """
        Crée tous les boutons du gui.
        :return:
        """
        gui_surf = pg.Surface((self.sc.get_width(), 8 * self.grid_square_side))
        gui_surf.fill(pg.Color(255, 255, 255))
        tiles_sprites = self.building_tiles_names
        ind = 0
        # Crée un bouton pour chaque tile existante
        for y in range(16, 22, 2):
            for x in range(0, 20, 2):
                if ind >= len(tiles_sprites):
                    break
                sprite = const.load_sprite(tiles_sprites[ind])
                self.create_button(x, y, 2, 2, pg.Color(0, 0, 0), pg.Color(50, 50, 50), lambda i=ind: self.change_selected_building_tile(tiles_sprites[i]),
                                   image=sprite)
                ind += 1

        self.create_button(20, 16, 4, 2, pg.Color(0, 255, 0), pg.Color(0, 255, 255), lambda: self.save_level(), text='Save', textColor=pg.Color(0, 0, 0))

        self.create_button(20, 18, 4, 2, pg.Color(0, 0, 255), pg.Color(255, 0, 255), lambda: self.change_mode('playing'), text='Play',
                           textColor=pg.Color(0, 0, 0))

        self.create_button(20, 22, 4, 2, pg.Color(150, 0, 255), pg.Color(50, 0, 175), lambda: self.change_mode('level_selection'), text='Quitter',
                           textColor=pg.Color(0, 0, 0))

        self.create_button(20, 20, 4, 2, pg.Color(255, 0, 0), pg.Color(255, 75, 0), lambda: self.delete_level(), text='Suppr level',
                           textColor=pg.Color(0, 0, 0))

        return gui_surf

    def delete_level(self):
        const.delete_edited_level()
        self.change_mode('level_selection', save=False)

    def change_mode(self, mode: str, save=True):
        self.save_level() if save else None
        const.change_mode(mode)
        self.running = False

    def scroll_level(self, dx: int, dy: int):
        """
        Fait défiler le niveau dans l'éditeur
        :param dx: -1 -> vers la droite, 1 -> vers la gauche
        :param dy:  -1 -> vers le haut, 1 -> vers le bas
        :return:
        """
        for tile in self.tiles:
            tile.rect.x += dx * self.grid_square_side
            tile.rect.y += dy * self.grid_square_side
        self.worldx -= dx
        self.worldy += dy
        if dx != 0:
            self.background_group.update(forward=dx < 0, ntimes=7)

    def save_level(self):
        with open(f'Edited_Levels/level_{const.level}.json', 'w') as j:
            json.dump(self.level, j, indent=0)

    def load_level(self, n):
        self.tiles.empty()
        self.level = {}

        with open(f"Edited_Levels/level_{n}.json", "r") as lvl:
            lvl_design: dict = json.load(lvl)
            self.level = lvl_design.copy()

        x: str
        col: dict
        y: str
        tile_type: str

        for x, col in lvl_design.items():
            if x == 'info_block_text':
                continue
            for y, tile_type in col.items():
                if tile_type == 'info_block':
                    self.place_block_at(int(x), int(y), tile_type, info_block_text=lvl_design['info_block_text'][str(x)][str(y)])
                else:
                    self.place_block_at(int(x), int(y), tile_type)

    def main(self, framerate: int):
        clock = pg.time.Clock()
        while self.running:
            clock.tick(framerate)
            self.handle_keys()

            if not self.info_block_editor_active:
                self.background_group.draw(self.grid)
                self.sc.blit(self.grid, (0, 0), pg.rect.Rect(0, 0, self.sc.get_width(), 16 * self.grid_square_side))
                self.ghost_selected_tile_on_cursor(pg.mouse.get_pos())

                self.tiles.update()
                self.tiles.draw(self.sc)
                self.buttons.draw(self.sc)
                const.display_infos(self.sc, 15, 15, f"wx : {self.worldx}, wy : {self.worldy},"
                                                     f" mouse : {pg.mouse.get_pos()}, selected square : "
                                                     f"{self.get_square_on_pos(pg.mouse.get_pos())}")
            else:
                self.draw_info_block_editor()

            pg.display.flip()


class Grid(pg.sprite.Sprite):
    def __init__(self, layer: int, image: pg.Surface):
        super().__init__()
        self._layer = layer
        self.image = image
        self.rect = self.image.get_rect()
