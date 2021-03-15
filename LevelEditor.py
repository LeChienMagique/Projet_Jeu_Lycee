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
        self.grid_square_side = const.tile_side  # + 1 pour laisser la place aux lignes de la grille
        self.level_number = -1

        self.background_group = pg.sprite.LayeredUpdates(const.background)
        self.buttons = pg.sprite.Group()
        self.tiles = pg.sprite.LayeredDirty()
        self.info_block_editor = pg.sprite.Group()
        self.info_block_editor_text_input_dims = [3 * self.grid_square_side, 2 * self.grid_square_side, 19 * self.grid_square_side, 9 * self.grid_square_side]
        self.confirm_delete_level_menu = pg.sprite.Group()

        self.running = True
        self.building_tiles = ent.building_tiles
        self.building_tiles_names = list(self.building_tiles.keys())
        self.selected_building_tile = "tile"
        self.selected_building_tile_facing = 0
        self.placing_area = pg.Surface((25 * self.grid_square_side, 21 * self.grid_square_side))
        self.make_gui()
        self.level = {}  # Dictionnaire contenant les données du niveau quand il est chargé en mémoire
        self.info_block_editor_active = False
        self.input_text = ['']

        self.confirm_delete_level_active = False
        self.make_delete_confirm_menu()

    def create_button(self, x: int, y: int, w: int, h: int, rectColor: pg.Color, onHoverRectColor: pg.Color, callback, group: pg.sprite.Group = None, **kwargs):
        """
        Permet de créer un bouton avec des dimensions en fonction de la taille des carreaux de la grille.
        :param x:
        :param y:
        :param w:
        :param h:
        :param rectColor:
        :param onHoverRectColor:
        :param callback:
        :param group:
        :param kwargs:
        :return:
        """
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
        """
        Update les boutons dans le group self.buttons
        :param mouse_pressed:
        :return:
        """
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
        if square_screeny < self.placing_area.get_rect().bottom:
            self.place_block_at(world_x, world_y, self.selected_building_tile)

    def make_info_block_editor_menu(self, block_x, block_y):
        """
        Créé tous les boutons du menu pop up d'édtion de texte pour le block info_block
        :param block_x:
        :param block_y:
        :return:
        """
        self.info_block_editor.empty()

        rect_x, rect_y, rect_w, rect_h = self.info_block_editor_text_input_dims
        gray_rectangle = pg.Surface((rect_w, rect_h))
        gray_rectangle.fill(pg.Color(150, 150, 150))

        border_width = 15
        pg.draw.line(gray_rectangle, (0, 0, 0), (0, 0), (rect_w, 0), width=border_width)
        pg.draw.line(gray_rectangle, (0, 0, 0), (0, 0), (0, rect_h), width=border_width)
        pg.draw.line(gray_rectangle, (0, 0, 0), (0, rect_h - 1), (rect_w - 1, rect_h - 1), width=border_width)
        pg.draw.line(gray_rectangle, (0, 0, 0), (rect_w - 1, 0), (rect_w - 1, rect_h), width=border_width)

        input_box = pg.sprite.Sprite()
        input_box.image = gray_rectangle
        input_box.rect = input_box.image.get_rect()
        input_box.rect.left = rect_x
        input_box.rect.top = rect_y

        self.info_block_editor.add(input_box)
        self.create_button(6, 12, 5, 3, pg.Color(0, 200, 0), pg.Color(0, 150, 0), lambda x=block_x, y=block_y: self.validate_text_input_info_block(x, y),
                           image=const.get_sprite('checkmark', icon=True), group=self.info_block_editor)
        self.create_button(14, 12, 5, 3, pg.Color(200, 0, 0), pg.Color(150, 0, 0),
                           lambda x=block_x, y=block_y: self.validate_text_input_info_block(x, y, canceled=True),
                           image=const.get_sprite('cross', icon=True), group=self.info_block_editor)

    def draw_info_block_editor(self):
        """
        Dessine à l'écran le menu pop up d'édtion de texte pour le block info_block
        :return:
        """
        self.info_block_editor.draw(self.sc)
        border_width = 15
        for line in range(len(self.input_text)):
            txt_surf = const.myFont.render(self.input_text[line], True, (255, 255, 255))
            self.sc.blit(txt_surf, (self.info_block_editor_text_input_dims[0] + 5 + border_width,
                                    self.info_block_editor_text_input_dims[1] + 5 + line * 25 + border_width))

    def prompt_info_block_editor(self):
        """
        Affiche le menu pop up d'édtion de texte pour le block info_block à l'écran
        :return:
        """
        self.info_block_editor_active = True
        pg.key.set_repeat(150, 10)

    def validate_text_input_info_block(self, block_x, block_y, canceled=False):
        """
        Méthode mappée aux boutons du menu pop up d'édtion de texte pour le block info_block pour sauvegarder le texte
        de l'éditeur dans le block ou annuler l'action.
        :param block_x:
        :param block_y:
        :param canceled:
        :return:
        """
        self.info_block_editor_active = False
        pg.key.set_repeat(100, 50)
        if not canceled:
            self.place_block_at(block_x, block_y, 'info_block', self.input_text)
        self.input_text = ['']

    def place_player_spawn_at(self, world_x: int, world_y: int):
        spawnpoint = self.level['misc']['spawnpoint']
        self.delete_block_at(spawnpoint, overwrite_spawn_delete_protection=True)
        self.level['misc']['spawnpoint'] = [world_x, world_y]

    def place_block_at(self, world_x: int, world_y: int, tile_type: str, info_block_text: list = None, loading_level=False):
        """
        Place un bloc au coord données
        :param loading_level:
        :param info_block_text:
        :param world_x:
        :param world_y:
        :param tile_type:
        :return:
        """
        if str(world_y) in self.level and not loading_level:
            if str(world_x) in self.level[str(world_y)]:
                if self.level[str(world_y)][str(world_x)] == 'player_spawn':
                    return

        if tile_type == 'info_block' and info_block_text is None:
            self.make_info_block_editor_menu(world_x, world_y)
            self.prompt_info_block_editor()
            return

        screen_x, screen_y = ((world_x - self.worldx) * self.grid_square_side + 1), ((world_y + self.worldy) * self.grid_square_side + 1)
        new_tile = self.building_tiles[tile_type](screen_x, screen_y, world_x, world_y, group=self.tiles, facing=self.selected_building_tile_facing,
                                                  editing=True, text=info_block_text)

        for collidingS in pg.sprite.spritecollide(new_tile, self.tiles, False):  # Empêche que plusieures tiles soit à la même position.
            if collidingS != new_tile:
                collidingS.kill()

        tile_name = tile_type if tile_type in ent.non_rotating_tiles else tile_type + str(self.selected_building_tile_facing)
        if not str(world_y) in self.level:
            self.level[str(world_y)] = {str(world_x): tile_name}
        else:
            self.level[str(world_y)][str(world_x)] = tile_name

        if tile_type == 'player_spawn' and not loading_level:
            self.place_player_spawn_at(world_x, world_y)

        elif tile_type == 'info_block':
            if 'info_block_text' not in self.level['misc']:
                self.level['misc']['info_block_text'] = {str(world_y): {str(world_x): info_block_text}}
            if str(world_y) not in self.level['misc']['info_block_text']:
                self.level['misc']['info_block_text'][str(world_y)] = {str(world_x): info_block_text}

    def delete_block_at(self, position, overwrite_spawn_delete_protection=False):
        """
        Supprime un bloc a la position donnée
        :param overwrite_spawn_delete_protection:
        :param position:
        :return:
        """
        sprite: ent.Tile
        x, y = position[0], position[1]
        if str(y) in self.level:
            if str(x) in self.level[str(y)]:

                if self.level[str(y)][str(x)] == 'info_block':
                    del self.level['misc']['info_block_text'][str(y)][str(x)]
                    if len(self.level['misc']['info_block_text'][str(y)]) == 0:
                        del self.level['misc']['info_block_text'][str(y)]

                elif self.level[str(y)][str(x)] == 'player_spawn' and not overwrite_spawn_delete_protection:
                    return

                for sprite in self.tiles:
                    if sprite.x == x and sprite.y == y:
                        sprite.kill()
                        del self.level[str(y)][str(x)]
                        if len(self.level[str(y)]) == 0:
                            del self.level[str(y)]

                        break

    def add_character_to_input_text(self, key: pg.event.Event):
        """
        Gère l'édition de texte en fonction de la touche appuyée
        :param key:
        :return:
        """
        if key.key == pg.K_BACKSPACE:
            if self.input_text[-1] == '' and len(self.input_text) > 1:
                self.input_text.pop()
            self.input_text[-1] = self.input_text[-1][:-1]

        elif key.key == pg.K_RETURN:
            if len(self.input_text) < 17:
                self.input_text.append('')
        else:
            if len(self.input_text[-1]) >= 40:
                if len(self.input_text) < 17:
                    self.input_text.append('')
            else:
                self.input_text[-1] += key.unicode

    def handle_keys(self):
        """
        Gère les touches pressées par l'utilisateur
        :return:
        """
        for e in pg.event.get():

            if e.type == pg.WINDOWEVENT:
                if e.event == 14:  # Quand l'utilisateur clique sur la X de la fenêtre de jeu
                    sys.exit()

            if self.confirm_delete_level_active:  # Quand le menu pop up de confirmation de suppression du niveau est à l'écran
                if e.type == pg.MOUSEBUTTONDOWN:
                    self.confirm_delete_level_menu.update(pg.mouse.get_pos(), True)
                elif e.type == pg.MOUSEMOTION:
                    self.confirm_delete_level_menu.update(pg.mouse.get_pos(), False)
                return

            if self.info_block_editor_active:  # Quand le menu pop up d'édtion de texte pour le block info_block est à l'écran
                if e.type == pg.KEYDOWN:  # Quand une touche est pressée essaye d'ajouter son unicode au texte
                    self.add_character_to_input_text(e)
                elif e.type == pg.MOUSEMOTION:
                    self.info_block_editor.update(pg.mouse.get_pos(), False)
                elif e.type == pg.MOUSEBUTTONDOWN:
                    self.info_block_editor.update(pg.mouse.get_pos(), True)
                return

            mouse_buttons = pg.mouse.get_pressed(3)
            if mouse_buttons[0]:
                self.try_place_block_at_mouse(pg.mouse.get_pos())  # Essaye de placer le bloc seléctionné à l'emplacement de la souris
                if self.running:
                    self.check_buttons(True)
                else:
                    return
            elif mouse_buttons[2]:
                self.delete_block_at(self.get_square_on_pos(pg.mouse.get_pos())[2:])  # Supprime le bloc à l'emplacement de la souris

            if e.type == pg.MOUSEMOTION:
                self.check_buttons(False)  # Pour limiter les appels à la méthode update des boutons, le fait que quand la souris bouge
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_z:
                    self.scroll_level(0, 1)  # Bouge la caméra de 1 bloc vers le haut
                elif e.key == pg.K_d:
                    self.scroll_level(-1, 0)  # Bouge la caméra de 1 bloc vers la droite
                elif e.key == pg.K_s:
                    self.scroll_level(0, -1)  # Bouge la caméra de 1 bloc vers le bas
                elif e.key == pg.K_q:
                    self.scroll_level(1, 0)  # Bouge la caméra de 1 bloc vers la gauche
                elif e.key == pg.K_p:
                    self.change_mode('playing')  # Raccourci pour jouer au niveau en cours d'édition
                elif e.key == pg.K_ESCAPE:
                    self.change_mode('level_selection')  # Raccourci pour revenir au menu principal
                elif e.key == pg.K_r:
                    self.rotate_selected_building_tile()

                # Raccourci clavier pour changer de bloc rapidement
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

    def ghost_selected_tile_on_cursor(self, mousepos):
        """
        Affiche sous la souris le bloc seléctionné mais ne le place pas
        :param mousepos:
        :return:
        """
        squarex, squarey = self.get_square_on_pos(mousepos)[0:2]
        if squarey < self.placing_area.get_rect().bottom:
            sprite = const.get_sprite(self.selected_building_tile, facing=self.selected_building_tile_facing)
            self.sc.blit(sprite, (squarex, squarey))

    def rotate_selected_building_tile(self):
        """
        Tourne le bloc seléctionné
        :return:
        """
        if self.selected_building_tile in ent.non_rotating_tiles:
            return
        if self.selected_building_tile == 'spike':
            self.selected_building_tile_facing += 1
        else:
            self.selected_building_tile_facing += 4
        self.selected_building_tile_facing %= 8

    def change_selected_building_tile(self, tile_name):
        """
        Change le bloc seléctionné
        :param tile_name:
        :return:
        """
        self.selected_building_tile = tile_name
        self.selected_building_tile_facing = 0

    def make_gui(self):
        """
        Crée tous les boutons du gui et les ajoute au group des boutons
        :return:
        """
        tiles_sprites = self.building_tiles_names
        ind = 0
        # Crée un bouton pour chaque tile existante et map self.change_selected_building_tile à chacun d'eux avec la tile correspondante
        for y in range(21, 25, 2):
            for x in range(5, 20, 2):
                if ind >= len(tiles_sprites):
                    break
                sprite = const.get_sprite(tiles_sprites[ind])
                self.create_button(x, y, 2, 2, pg.Color(0, 0, 0), pg.Color(50, 50, 50), lambda i=ind: self.change_selected_building_tile(tiles_sprites[i]),
                                   image=sprite)
                ind += 1

        self.create_button(21, 23, 4, 2, pg.Color(0, 255, 0), pg.Color(0, 255, 255), lambda: self.save_level(), image=const.get_sprite('save', icon=True))

        self.create_button(21, 21, 4, 2, pg.Color(0, 0, 255), pg.Color(255, 0, 255), lambda: self.change_mode('playing'),
                           image=const.get_sprite('right', icon=True))

        self.create_button(0, 21, 4, 2, pg.Color(150, 0, 255), pg.Color(50, 0, 175), lambda: self.change_mode('level_selection'),
                           image=const.get_sprite('home', icon=True))

        self.create_button(0, 23, 4, 2, pg.Color(255, 0, 0), pg.Color(255, 75, 0), lambda: self.prompt_confirm_delete_level(),
                           image=const.get_sprite('trashcan', icon=True))

    def make_delete_confirm_menu(self):
        """
        Crée les boutons du menu de confirmation de suppression du niveau et les ajoute au groupe correspondant
        :return:
        """
        self.create_button(6, 8, 5, 3, pg.Color(255, 0, 0), pg.Color(150, 0, 0), lambda: self.delete_level(),
                           image=const.get_sprite('checkmark', icon=True), group=self.confirm_delete_level_menu)
        self.create_button(14, 8, 5, 3, pg.Color(0, 255, 0), pg.Color(0, 150, 0), lambda: self.delete_level(cancel=True),
                           image=const.get_sprite('cross', icon=True), group=self.confirm_delete_level_menu)

    def prompt_confirm_delete_level(self):
        """
        Affiche le menu de confirmation de suppression du niveau
        :return:
        """
        self.confirm_delete_level_active = True
        const.display_infos(self.sc, "Voulez-vous vraiment supprimer le niveau ?", font=const.bigFont, center=True, y=const.sc_height // 5)

    def delete_level(self, cancel=False):
        """
        Supprime le niveau (son .json dans Edited_Levels/)
        :param cancel:
        :return:
        """
        if not cancel:
            const.delete_edited_level()
            self.change_mode('level_selection', save=False)
            self.confirm_delete_level_active = False
        else:
            self.confirm_delete_level_active = False

    def change_mode(self, mode: str, save=True):
        """
        Permet de changer de mode (playing, level_selection)
        :param mode:
        :param save:
        :return:
        """
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
            self.background_group.update(7, dx < 0)

    def save_level(self):
        """
        Sauvegarde le niveau dans un fichier .json dans Edited_Levels/
        :return:
        """
        with open(f'Edited_Levels/level_{const.level}.json', 'w') as j:
            json.dump(self.level, j, indent=0)

    def load_level(self, n):
        """
        Charge un niveau en mémoire depuis Edited_Levels/
        :param n:
        :return:
        """
        if n == self.level_number and const.previous_mode != 'level_selection':  # Ne recharge pas le niveau si le niveau est le même qu'avant
            return

        self.level_number = n

        self.worldx = 0
        self.worldy = 0

        self.tiles.empty()
        self.level = {}

        with open(f"Edited_Levels/level_{n}.json", "r") as lvl:
            lvl_design: dict = json.load(lvl)
            self.level = lvl_design.copy()

        x: str
        row: dict
        y: str
        tile_type: str

        for y, row in lvl_design.items():
            if y == 'misc':
                continue
            for x, tile_type in row.items():
                if tile_type == 'info_block':
                    self.place_block_at(int(x), int(y), tile_type, info_block_text=lvl_design['misc']['info_block_text'][str(y)][str(x)])
                else:
                    if tile_type in ent.non_rotating_tiles:
                        self.selected_building_tile_facing = 0
                        self.place_block_at(int(x), int(y), tile_type, loading_level=True)
                    else:
                        self.selected_building_tile_facing = int(tile_type[-1])
                        self.place_block_at(int(x), int(y), tile_type[:-1], loading_level=True)
        self.selected_building_tile_facing = 0

    def main(self, framerate: int):
        """
        Méthode principale
        :param framerate:
        :return:
        """
        clock = pg.time.Clock()
        while self.running:
            clock.tick(framerate)
            self.handle_keys()

            if self.info_block_editor_active:  # Quand le menu pop up d'édtion de texte pour le block info_block est actif
                self.draw_info_block_editor()

            elif self.confirm_delete_level_active:  # Quand le menu de confirmation de suppression du niveau est actif
                self.confirm_delete_level_menu.draw(self.sc)

            else:
                self.background_group.draw(self.placing_area)  # Dessine le fond d'écran
                # self.sc.blit(self.placing_area, (0, 0), pg.rect.Rect(0, 0, self.sc.get_width(), 18 * self.grid_square_side))  # Dessine la grille
                self.sc.blit(self.placing_area, (0, 1))
                self.ghost_selected_tile_on_cursor(pg.mouse.get_pos())

                self.tiles.update()
                self.tiles.draw(self.sc)  # Dessine les blocs
                self.buttons.draw(self.sc)  # Dessine les boutons
                hovered_square_pos = self.get_square_on_pos(pg.mouse.get_pos())[2:]
                const.display_infos(self.sc, f"x : {hovered_square_pos[0]}, y : {hovered_square_pos[1]}", x=15,
                                    y=15)  # Affiche des informations sur la position
                # du curseur

            pg.display.flip()
