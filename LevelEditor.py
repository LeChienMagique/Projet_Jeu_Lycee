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
        self.background = const.background
        self.grid_square_side = const.tile_side + 1
        self.buttons = pg.sprite.Group()
        self.tiles = pg.sprite.LayeredDirty()
        self.running = True
        self.building_tiles = ent.building_tiles
        self.selected_building_tile = "tile"
        self.grid = self.create_grid_background()
        self.gui = self.make_gui()
        self.level = {}

    def create_grid_background(self) -> pg.Surface:
        back = pg.Surface((25 * self.grid_square_side, 16 * self.grid_square_side))
        # back.fill(pg.Color(0, 0, 0))
        back.blit(self.background, (0, 0))
        self.draw_grid(back)
        return back

    def draw_grid(self, surf):
        for col in range(25):
            pg.draw.line(surf, pg.Color(220, 220, 220), (col * self.grid_square_side, 0),
                         (col * self.grid_square_side, self.sc.get_height()))
        for row in range(16):
            pg.draw.line(surf, pg.Color(220, 220, 220), (0, row * self.grid_square_side),
                         (self.sc.get_width(), row * self.grid_square_side))

    def create_button(self, x: int, y: int, w: int, h: int, rectColor: pg.Color, onHoverRectColor: pg.Color, callback,
                      **kwargs):
        x *= self.grid_square_side
        y *= self.grid_square_side
        w *= self.grid_square_side
        h *= self.grid_square_side
        new_button = Button(x, y, w, h, rectColor, onHoverRectColor, callback, **kwargs)
        self.buttons.add(new_button)

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

    def place_block_at(self, world_x: int, world_y: int, tile_type: str):
        """
        Place un bloc au coord données
        :param world_x:
        :param world_y:
        :param tile_type:
        :return:
        """
        # print('Placing at :', x, y)
        screen_x, screen_y = ((world_x - self.worldx) * self.grid_square_side + 1), (
                (world_y + self.worldy) * self.grid_square_side + 1)
        new_tile = self.building_tiles[tile_type](screen_x, screen_y, world_x, world_y, group=self.tiles, editing=True)
        for collidingS in pg.sprite.spritecollide(new_tile, self.tiles,
                                                  False):  # Empêche que plusieures tiles soit à la même position.
            if collidingS != new_tile:
                collidingS.kill()
        if not str(world_x) in self.level:
            self.level[str(world_x)] = {str(world_y): tile_type}
        else:
            self.level[str(world_x)][str(world_y)] = tile_type

    def pos_in_building_area(self, x: int, y: int):
        return x < (self.worldx + 24) and y < (self.worldy + 16)

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
                        del self.level[str(x)][str(y)]
                        if len(self.level[str(x)]) == 0:
                            del self.level[str(x)]

    def handle_keys(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                sys.exit()
            mouse_buttons = pg.mouse.get_pressed(3)
            if mouse_buttons[0]:
                self.check_buttons(True)
                self.try_place_block_at_mouse(pg.mouse.get_pos())
            elif mouse_buttons[2]:
                self.delete_block_at(self.get_square_on_pos(pg.mouse.get_pos())[2:])
            elif e.type == pg.MOUSEMOTION:
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
                    sys.exit()

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
        tiles_sprites = list(self.building_tiles.keys())
        ind = 0
        # Crée un bouton pour chaque tile existente
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
        self.change_mode('level_selection')

    def change_mode(self, mode: str):
        self.save_level()
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

    def save_level(self):
        with open(f'Edited_Levels/level_{const.level}.json', 'w') as j:
            json.dump(self.level, j, indent=0)
            print('Level saved !')

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
            for y, tile_type in col.items():
                self.place_block_at(int(x), int(y), tile_type)

    def main(self, framerate: int):
        clock = pg.time.Clock()
        while self.running:
            clock.tick(framerate)
            self.handle_keys()

            self.sc.blit(self.grid, (0, 0),
                         pg.rect.Rect(0, 0, self.sc.get_width(), 16 * self.grid_square_side))
            self.ghost_selected_tile_on_cursor(pg.mouse.get_pos())

            self.tiles.update()
            self.tiles.draw(self.sc)
            self.buttons.draw(self.sc)
            const.display_infos(self.sc, 15, 15,
                                f"wx : {self.worldx}, wy : {self.worldy}, mouse : {pg.mouse.get_pos()}, selected square : "
                                f"{self.get_square_on_pos(pg.mouse.get_pos())}")
            pg.display.flip()
