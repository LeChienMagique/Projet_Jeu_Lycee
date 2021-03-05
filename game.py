import pygame as pg
import entities as ent
import const
import sys
import json


class Game:
    def __init__(self, screen: pg.Surface):
        self.running = True
        self.sc = screen
        self.background = const.background
        self.player = Player(self)
        self.player.rect.x = const.startx
        self.player.rect.y = const.starty

        self.player_group = pg.sprite.GroupSingle(self.player)
        self.tile_group = pg.sprite.LayeredDirty()
        self.pause_menu = pg.sprite.Group()

        self.paused = False
        self.level_ended = False
        self.time_since_level_completion = 0

    def handle_keys(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                sys.exit()
            if self.paused and e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    self.pause_menu.update(pg.mouse.get_pos(), True)
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_UP:
                    self.player.jump()
                elif e.key == pg.K_r:
                    self.reset_level()
                elif e.key == pg.K_e and const.previous_mode == 'editing':
                    self.change_mode('editing')
            elif e.type == pg.KEYUP:
                if e.key == pg.K_ESCAPE:
                    self.toggle_pause()
                elif e.key == pg.K_f:
                    self.advance_frame()

    def toggle_pause(self):
        self.paused = not self.paused

    def make_pause_menu(self):
        button_w = const.sc_width // 3
        button_h = const.sc_height // 6
        button_x = const.sc_width // 2 - button_w // 2
        self.pause_menu.add(const.Button(button_x, button_h + 10, button_w, button_h, pg.Color(0, 0, 255), pg.Color(0, 255, 0), lambda: self.toggle_pause(),
                                         text='Reprendre', textColor=pg.Color(0, 0, 0)),
                            const.Button(button_x, button_h * 2 + 20, button_w, button_h, pg.Color(0, 0, 255), pg.Color(0, 255, 0), lambda: self.reset_level(),
                                         text='Recommencer', textColor=pg.Color(0, 0, 0)),
                            const.Button(button_x, button_h * 3 + 30, button_w, button_h, pg.Color(0, 0, 255), pg.Color(0, 255, 0),
                                         lambda: self.change_mode('level_selection'), text='Quitter', textColor=pg.Color(0, 0, 0)))
        if const.previous_mode == 'editing':
            self.pause_menu.add(const.Button(button_x, button_h * 4 + 40, button_w, button_h, pg.Color(0, 0, 255), pg.Color(0, 255, 0),
                                             lambda: self.change_mode('editing'), text='Editer', textColor=pg.Color(0, 0, 0)))

    def scroll_level(self, forward: bool):
        if forward:
            for tile in self.tile_group:
                tile.rect.x -= const.scrolling_speed
        else:
            for tile in self.tile_group:
                tile.rect.x += const.scrolling_speed

    def align_cam_on_player_y(self):
        """
        Aligne le champ de vision avec la hauteur du joueur dans le repère
        :return:
        """
        player_y = self.player.rect.centery
        up_limit = const.sc_height // 2
        bottom_limit = const.sc_height - (const.sc_height // 3.4)
        if player_y < up_limit:
            offset = up_limit - player_y
            self.player.rect.centery += offset
            for tile in self.tile_group:
                tile.rect.y += offset
        elif player_y > bottom_limit:
            offset = player_y - bottom_limit
            self.player.rect.centery -= offset
            for tile in self.tile_group:
                tile.rect.y -= offset

    def end_level(self):
        self.level_ended = True

    def reset_level(self):
        self.reset_all_vars()
        self.load_level(const.level)

    def reset_all_vars(self):
        self.paused = False
        self.level_ended = False
        self.time_since_level_completion = 0
        const.scrolling_forward = True
        self.player.rect.x = const.startx
        self.player.rect.y = const.starty
        self.player.dy = 0

    def next_level(self):
        self.reset_all_vars()
        if const.previous_mode == 'playing' or const.previous_mode == 'level_selection':
            if const.next_level():
                self.load_level(const.level)
                print(f'next level : {const.level}')
            else:
                self.change_mode('level_selection')
        elif const.previous_mode == 'editing':
            self.change_mode('editing')

    def load_level(self, n: int):
        self.reset_all_vars()

        if const.previous_mode == 'editing':
            path = f"Edited_Levels/level_{n}.json"
        else:
            path = f"Levels/level_{n}.json"

        self.tile_group.empty()

        with open(path, "r") as lvl:
            lvl_design: dict = json.load(lvl)

        x: str
        col: dict
        y: str
        tile_type: str

        for x, col in lvl_design.items():
            for y, tile_type in col.items():
                ent.building_tiles[tile_type](int(x) * const.tile_side, int(y) * const.tile_side, int(x), int(y),
                                              self.tile_group)

    def change_mode(self, mode: str):
        self.reset_all_vars()
        const.change_mode(mode)
        self.running = False

    def advance_frame(self):
        self.player.handle_gravity()
        self.align_cam_on_player_y()
        self.player.tick_movement()
        self.player.handle_y_axis_collisions()
        self.scroll_level(const.scrolling_forward)
        self.tile_group.update()
        self.player.handle_x_axis_collisions()
        self.player.handle_x_offset()

        self.sc.fill((0, 0, 0))
        const.display_infos(self.sc, 15, 15,
                            f"x : {self.player.rect.x}, y : {self.player.rect.y}, dy : {round(self.player.dy, 1)}, dx : {self.player.dx}, onGround : {self.player.onGround}")
        self.player_group.draw(self.sc)
        self.tile_group.draw(self.sc)
        pg.display.flip()

    def main(self, framerate: int):
        clock = pg.time.Clock()
        self.reset_all_vars()
        self.make_pause_menu()
        while self.running:
            if self.level_ended:
                self.time_since_level_completion += clock.tick(framerate)
                if self.time_since_level_completion > 1000:
                    self.next_level()
            else:
                clock.tick(framerate)
                self.handle_keys()

            if not self.paused:
                self.player.handle_gravity()
                self.align_cam_on_player_y()
                self.player.tick_movement()
                self.player.handle_y_axis_collisions()
                self.scroll_level(const.scrolling_forward)
                self.tile_group.update()
                self.player.handle_x_axis_collisions()
                self.player.handle_x_offset()
            else:
                self.pause_menu.update(pg.mouse.get_pos(), False)

            # self.sc.fill((0, 0, 0))
            self.sc.blit(self.background, (0, 0))
            const.display_infos(self.sc, 15, 15,
                                f"x : {self.player.rect.x}, y : {self.player.rect.y}, dy : {round(self.player.dy, 1)}, dx : {self.player.dx}, onGround : {self.player.onGround}")
            self.player_group.draw(self.sc)
            self.tile_group.draw(self.sc)
            if self.paused:
                self.pause_menu.draw(self.sc)
                textsurf = const.bigFont.render('Pause', True, pg.Color(255, 255, 255), pg.Color(0, 0, 0))
                self.sc.blit(textsurf, (const.sc_width // 2 - textsurf.get_rect().width // 2, const.sc_height // 10))
            pg.display.flip()


class Player(pg.sprite.DirtySprite):
    def __init__(self, game: Game):
        super().__init__()
        self.game = game
        self.image_side = const.player_side
        # self.image = pg.Surface([self.image_side, self.image_side])
        # self.image.fill(pg.Color(255, 255, 255))
        self.image = const.load_sprite('player')
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        self.dx = 0
        self.dy = 0
        self.onGround = False
        self.colliding_right_flag = False

    def kill(self):
        if not self.game.level_ended:
            self.game.reset_level()
        else:
            self.game.next_level()

    def handle_gravity(self):
        """
        Gère l'accélération verticale du player
        :return:
        """
        self.dy += const.gravity_intensity
        if self.dy > const.player_side:
            self.dy = const.player_side

    def jump(self):
        """
        Donne de l'accélération verticale au joueur pour simuler un saut.
        :return:
        """
        if self.onGround:
            self.dy = const.jump_height
            self.onGround = False

    def tick_movement(self):
        """
        Update la position du joueur.
        :return:
        """
        self.rect.x += self.dx
        self.rect.y += self.dy

        if self.rect.y > const.sc_height:
            self.rect.y = 0
        if self.rect.x < 0:
            self.kill()

    def handle_y_axis_collisions(self):
        """
        Gère les collisions sur l'axe y du joueur avec les Tiles
        :return:
        """
        collidedS = pg.sprite.spritecollideany(self, self.game.tile_group)
        if collidedS is not None:
            if isinstance(collidedS, ent.EndTile):
                self.game.end_level()
                return

            self.dy = 0

            if not const.scrolling_forward:
                const.scrolling_forward = True

            if collidedS.rect.top < self.rect.top < collidedS.rect.bottom:  # Quand le joueur tape sa tête sur une Tile
                self.rect.top = collidedS.rect.bottom
                if isinstance(collidedS, ent.Spike):
                    if not 'n' in collidedS.side:
                        self.kill()

            elif collidedS.rect.top < self.rect.bottom < collidedS.rect.bottom:  # Quand le joueur aterri sur une Tile
                self.rect.bottom = collidedS.rect.top
                self.onGround = True
                if isinstance(collidedS, ent.Spike):
                    if not 's' in collidedS.side:
                        self.kill()



                elif isinstance(collidedS, ent.Jumper):
                    self.dy = const.jump_height * 1.4
                elif isinstance(collidedS, ent.BackwardPusher):
                    self.dy = const.jump_height * 1.4
                    const.scrolling_forward = False

    def handle_x_axis_collisions(self):
        """
        Gère les collisions sur l'axe x du joueur avec les Tiles
        :return:
        """
        collidedS = pg.sprite.spritecollideany(self, self.game.tile_group)
        if collidedS is not None:
            if isinstance(collidedS, ent.EndTile):
                self.game.end_level()
                return

            if const.scrolling_forward:
                if self.rect.right > collidedS.rect.left:  # Quand le joueur entre en collision avec un mur
                    self.rect.right = collidedS.rect.left
                    self.colliding_right_flag = True
            else:
                if self.rect.left < collidedS.rect.right:
                    self.rect.left = collidedS.rect.right

            if isinstance(collidedS, ent.Spike):
                if 'e' not in collidedS.side and const.scrolling_forward:
                    self.kill()
                elif 'w' not in collidedS.side and not const.scrolling_forward:
                    self.kill()

            if not const.scrolling_forward:
                const.scrolling_forward = True

        else:
            self.colliding_right_flag = False

    def handle_x_offset(self):
        """
        Gère l'accélération horizontale quand le joueur est derrière le point x de départ de manière à le replacer
        :return:
        """
        if self.rect.x < const.startx and not self.colliding_right_flag:
            self.dx = 1
        else:
            self.dx = 0
