import pygame as pg
import entities as ent
import const
import sys
import json


class Game:
    """
    Instance du jeu
    """

    def __init__(self, screen: pg.Surface):
        self.running = True
        self.sc = screen
        self.player = Player(self)
        self.player.rect.x = 0
        self.player.rect.y = 0

        self.player_group = pg.sprite.GroupSingle(self.player)
        self.tile_group = pg.sprite.Group()
        self.pass_through_tiles = pg.sprite.Group()
        self.background_name = 'industrial_layers'
        self.background_group = pg.sprite.LayeredUpdates(const.make_background_group(self.background_name))
        self.pause_menu = pg.sprite.Group()

        self.paused = False
        self.info_block_pause = False
        self.info_block_text = ['']
        self.level_ended = False

        self.timer = 0
        self.timer_active = False

        self.gravity_is_inversed = False

        self.start_pos = [2, 0]
        self.last_checkpoint_pos = self.start_pos

        pg.mixer.music.load('assets/Sounds/music.mp3')
        pg.mixer.music.set_volume(0.20)

    def handle_keys(self):
        """
        Gère les touches pressées par l'utilisateur
        :return:
        """
        for e in pg.event.get():
            if e.type == pg.QUIT:  # Quand l'utilisateur clique sur la X de la fenêtre de jeu
                sys.exit()

            if self.level_ended:
                if e.type == pg.KEYUP:
                    if e.key == pg.K_ESCAPE:
                        self.next_level()

            elif self.paused:
                if e.type == pg.MOUSEMOTION or e.type == pg.MOUSEBUTTONUP:  # Pour limiter les appels à la méthode update des boutons, le fait que quand la souris bouge ou que le bouton de
                    # la souris est appuyée
                    self.pause_menu.update(pg.mouse.get_pos(), False)
                elif e.type == pg.MOUSEBUTTONDOWN:
                    if e.button == 1:
                        self.pause_menu.update(pg.mouse.get_pos(), True)
                elif e.type == pg.KEYUP:
                    if e.key == pg.K_ESCAPE:
                        self.toggle_pause()  # Arrête la pause

            elif e.type == pg.KEYDOWN:
                if self.info_block_pause:  # Quand le menu pop up du bloc info_block est affiché
                    if self.timer > 1000:  # Pour empêcher que le menu se ferme juste après s'être ouvert
                        self.quit_info_block_pause()
                elif e.key == pg.K_UP or e.key == pg.K_SPACE:
                    self.player.jump()  # Fait sauter le joueur
                elif e.key == pg.K_r:
                    self.reset_level()  # Recommence le niveau depuis le dernier checkpoint
                elif e.key == pg.K_e and const.previous_mode == 'editing':
                    self.change_mode('editing')  # Repasse en mode édition si le niveau est éditable
            elif e.type == pg.KEYUP:
                if e.key == pg.K_ESCAPE:
                    self.quit_info_block_pause()
                    self.toggle_pause()  # Met le jeu en pause et affiche le menu de pause

    def start_timer(self):
        """
        Commence un timer pour compter le temps écoulé en millisecondes
        :return:
        """
        self.timer_active = True
        self.timer = 0

    def stop_timer(self):
        """
        Arrête le timer et le réinitialise
        :return:
        """
        self.timer_active = False
        self.timer = 0

    def draw_info_block_text(self):
        """
        Dessine le menu pop up du bloc info_block avec le texte correspondant
        :return:
        """
        for line in range(len(self.info_block_text)):
            textsurf = const.myFont.render(self.info_block_text[line], True, pg.Color(255, 255, 255))
            self.sc.blit(textsurf, (const.sc_width // 2 - textsurf.get_rect().width // 2, const.sc_height // 10 + line * 25))

    def prompt_info_block_pause(self, text: str):
        """
        Affiche le menu pop up du bloc info_block avec le texte correspondant
        :return:
        """
        info_block_box_dims = [3 * const.tile_side, 2 * const.tile_side, 19 * const.tile_side, 9 * const.tile_side]
        pg.draw.rect(self.sc, pg.Color(50, 50, 50), info_block_box_dims, 15)

        self.info_block_text = text
        self.info_block_pause = True
        self.start_timer()

    def quit_info_block_pause(self):
        """
        Quitte le menu pop up du bloc info_block
        :return:
        """
        self.info_block_pause = False
        self.stop_timer()

    def toggle_pause(self):
        """
        Alterne entre met le jeu en pause et arrête la pause
        :return:
        """
        self.paused = not self.paused

    def toggle_music(self):
        """
        Alterne entre musique activée et musique désactivée
        :return:
        """
        const.music_enabled = not const.music_enabled
        if const.music_enabled:
            pg.mixer.music.play(loops=-1)
        else:
            pg.mixer.music.stop()

    def toggle_sfx(self):
        """
        Alterne entre sfx activée et sfx désactivée
        :return:
        """
        const.sound_effects_enabled = not const.sound_effects_enabled

    def make_pause_menu(self):
        """
        Créé tous les boutons du menu de pause et les ajoute au group correspondant
        :return:
        """
        self.pause_menu.empty()
        button_w = const.sc_width // 3
        button_h = const.sc_height // 6
        button_x = const.sc_width // 2 - button_w // 2
        self.pause_menu.add(const.Button(button_x, button_h + 10, button_w, button_h, lambda: self.toggle_pause(),
                                         image=const.get_sprite('right', icon=True)),
                            const.Button(button_x, button_h * 2 + 20, button_w, button_h, lambda: self.reset_level(),
                                         image=const.get_sprite('return', icon=True)),
                            const.Button(button_x, button_h * 3 + 30, button_w, button_h, lambda: self.change_mode('level_selection'),
                                         image=const.get_sprite('home', icon=True)),
                            const.Button(10, const.sc_height - button_h - 10, button_w // 2, button_h, lambda: const.toggle_music(),
                                         image=const.get_sprite('music', icon=True)),
                            const.Button(10 + button_w // 2 + 5, const.sc_height - button_h - 10, button_w // 2, button_h, lambda: const.toggle_sfx(),
                                         image=const.get_sprite('sfx', icon=True))
                            )
        if const.previous_mode == 'editing':
            self.pause_menu.add(const.Button(button_x, button_h * 4 + 40, button_w, button_h, lambda: self.change_mode('editing'), image=const.get_sprite(
                'wrench', icon=True)))

    def set_scrolling(self, forward: bool):
        """
        Défini le scrolling du niveau
        :return:
        """
        const.scrolling_forward = forward
        if not forward:
            for tile in self.pass_through_tiles:
                if isinstance(tile, ent.Minimizer):
                    tile.disabled = False

    def scroll_level(self, forward: bool):
        """
        Fait défiler le niveau pour donner l'impression d'avancer
        :param forward:
        :return:
        """
        mult = (1 - 2 * forward)
        for tile in self.tile_group:
            tile.rect.x += const.scrolling_speed * mult
        for tile in self.pass_through_tiles:
            tile.rect.x += const.scrolling_speed * mult

    def align_cam_on_player_y(self):
        """
        Aligne la caméra avec la hauteur du joueur dans le repère pour qu'il ne sorte pas de l'écran
        :return:
        """
        player_y = self.player.rect.centery
        divider = 3
        up_limit = const.sc_height // divider
        bottom_limit = const.sc_height - up_limit
        if player_y < up_limit:  # Si le joueur est trop haut
            offset = up_limit - player_y
            self.player.rect.centery = up_limit
            for tile in self.tile_group:
                tile.rect.y += offset
            for tile in self.pass_through_tiles:
                tile.rect.y += offset

        elif player_y > bottom_limit:  # Si le joueur est trop bas
            offset = player_y - bottom_limit
            self.player.rect.centery = bottom_limit
            for tile in self.tile_group:
                tile.rect.y -= offset
            for tile in self.pass_through_tiles:
                tile.rect.y -= offset

    def end_level(self):
        """
        Déclenche la séquence de fin de niveau
        :return:
        """
        if not self.level_ended:
            self.level_ended = True
            self.start_timer()

    def reset_level(self):
        """
        Recommence le niveau depuis le dernier checkpoint
        :return:
        """
        self.reset_all_vars()
        # Fait en sorte que la position en y du joueur soit le plus bas possible (voir align_cam_on_player_y.bottom_limit) pour avoir
        # une meilleure visibilité
        y_offset = (const.sc_height - (const.sc_height // 3)) - (self.last_checkpoint_pos[1] * const.tile_side)
        y_offset *= -1

        for tile in self.tile_group:
            tile: ent.Tile
            tile.rect.x = (tile.x - self.last_checkpoint_pos[0] + const.start_worldx) * const.tile_side
            tile.rect.y = tile.y * const.tile_side - y_offset
            if isinstance(tile, ent.Minimizer):
                tile.disabled = False
        for tile in self.pass_through_tiles:
            tile: ent.Tile
            tile.rect.x = (tile.x - self.last_checkpoint_pos[0] + const.start_worldx) * const.tile_side
            tile.rect.y = tile.y * const.tile_side - y_offset
            if isinstance(tile, ent.Minimizer):
                tile.disabled = False

    def reset_all_vars(self):
        """
        Réinitialise toutes les variables de la classe
        :return:
        """
        self.paused = False
        self.level_ended = False
        self.timer = 0
        self.timer_active = False
        self.set_scrolling(True)
        if self.gravity_is_inversed:
            const.gravity *= -1
            const.jump_height *= -1
        self.gravity_is_inversed = False
        self.player.reset_pos_and_vars()  # Réinitialise toutes les variables de positions etc... du joueur

    def next_level(self):
        """
        Passe au niveau d'après
        :return:
        """
        self.reset_all_vars()
        if const.previous_mode == 'playing' or const.previous_mode == 'level_selection':
            if const.next_level():
                self.load_level(const.level)
            else:
                self.change_mode('level_selection')
        elif const.previous_mode == 'editing':  # Si le niveau est un niveau éditable, revient juste au menu d'édition
            self.change_mode('editing')

    def load_level(self, n: int):
        """
        Charge le niveau en mémoire
        :param n:
        :return:
        """

        if const.previous_mode == 'editing':
            path = f"Edited_Levels/level_{n}.json"
        else:
            path = f"Levels/level_{n}.json"

        self.tile_group.empty()
        self.pass_through_tiles.empty()

        with open(path, "r", encoding='utf-8') as lvl:
            lvl_design: dict = json.load(lvl)

        self.start_pos = lvl_design['misc']['spawnpoint']
        self.last_checkpoint_pos = lvl_design['misc']['spawnpoint']

        self.reset_all_vars()

        if lvl_design['misc']['background_name'] != self.background_name:
            self.background_name = lvl_design['misc']['background_name']
            self.background_group.empty()
            self.background_group.add(const.make_background_group(self.background_name))

        if self.background_name == 'space_layers':
            const.gravity = const.space_gravity
        else:
            const.gravity = const.normal_gravity

        x: str
        row: dict
        y: str
        tile_type: str
        # Fait en sorte que la position en y du joueur soit le plus bas possible (voir align_cam_on_player_y.bottom_limit) pour avoir
        # une meilleure visibilité
        y_offset = (const.sc_height - (const.sc_height // 3)) - (self.last_checkpoint_pos[1] * const.tile_side)
        y_offset *= -1

        for y, row in lvl_design.items():
            if y == 'misc':
                continue
            for x, tile_type in row.items():
                screenx = (int(x) - self.start_pos[0] + const.start_worldx) * const.tile_side
                screeny = int(y) * const.tile_side - y_offset
                if tile_type == 'info_block':
                    ent.building_tiles[tile_type](screenx, screeny, int(x), int(y), self.tile_group,
                                                  text=lvl_design['misc']['info_block_text'][str(y)][str(x)])
                elif tile_type == 'player_spawn':
                    continue
                else:
                    if tile_type in ['minimizer', 'end', 'checkpoint']:
                        ent.building_tiles[tile_type](screenx, screeny, int(x), int(y), self.pass_through_tiles)
                    else:
                        try:
                            facing = int(tile_type[-1])
                            ent.building_tiles[tile_type[:-1]](screenx, screeny, int(x), int(y), self.tile_group, facing=facing)
                        except ValueError:
                            ent.building_tiles[tile_type](screenx, screeny, int(x), int(y), self.tile_group)

        # Détermine 2 tiles : la plus haute et la plus basse du niveau pour créer des limites où le joueur
        # meurt quand il les traverse
        self.low_dead_line: ent.Tile
        self.high_dead_line: ent.Tile
        lowest_tile = None
        highest_tile = None
        for tile in self.tile_group:
            if lowest_tile is None or tile.y > lowest_tile:
                lowest_tile = tile.y
                self.low_dead_line = tile
            if highest_tile is None or tile.y < highest_tile:
                highest_tile = tile.y
                self.high_dead_line = tile
        for tile in self.pass_through_tiles:
            if lowest_tile is None or tile.y > lowest_tile:
                lowest_tile = tile.y
                self.low_dead_line = tile
            if highest_tile is None or tile.y < highest_tile:
                highest_tile = tile.y
                self.high_dead_line = tile

    def change_mode(self, mode: str):
        """
        Permet de changer de mode (editing, level_selection)
        :param mode:
        :return:
        """
        pg.mixer.music.stop()
        self.reset_all_vars()
        const.change_mode(mode)
        self.running = False

    def invert_gravity(self):
        """
        Inverse la gravité
        :return:
        """
        self.player.image = pg.transform.flip(self.player.image, False, True)
        const.gravity *= -1
        const.jump_height *= -1
        self.gravity_is_inversed = not self.gravity_is_inversed

    def main(self, framerate: int):
        """
        Méthode principale
        :param framerate:
        :return:
        """
        self.clock = pg.time.Clock()
        self.reset_all_vars()
        self.make_pause_menu()
        self.timer_active = True
        if const.music_enabled:
            pg.mixer.music.play(loops=-1)
        while self.running:

            self.timer += self.clock.tick(framerate) * self.timer_active

            if self.level_ended:
                if self.timer > 1000:
                    self.next_level()

            self.handle_keys()

            if not self.paused and not self.info_block_pause:
                self.player.handle_gravity()
                self.align_cam_on_player_y()
                self.player.tick_movement()
                self.player.handle_y_axis_collisions()
                self.scroll_level(const.scrolling_forward)
                self.player.handle_x_axis_collisions()
                self.player.handle_x_offset()

                self.background_group.update()

            self.background_group.draw(self.sc)

            self.player_group.draw(self.sc)
            for tile in self.tile_group:
                tile: ent.Tile
                x, y = tile.rect.left, tile.rect.top
                # Ne render que les tiles visibles à l'écran pour optimiser les appels coûteux à la méthode draw/blit
                if -const.tile_side < x < const.sc_width and -const.tile_side < y < const.sc_height:
                    self.sc.blit(tile.image, (tile.rect.x, tile.rect.y))
            for tile in self.pass_through_tiles:
                tile: ent.Tile
                x, y = tile.rect.left, tile.rect.top
                # Ne render que les tiles visibles à l'écran pour optimiser les appels coûteux à la méthode draw/blit
                if -const.tile_side < x < const.sc_width and -const.tile_side < y < const.sc_height:
                    self.sc.blit(tile.image, (tile.rect.x, tile.rect.y))

            if self.paused:
                self.pause_menu.draw(self.sc)
                textsurf = const.boldFont.render('PAUSE', True, pg.Color(255, 255, 255))
                self.sc.blit(textsurf, (const.sc_width // 2 - textsurf.get_rect().width // 2, const.sc_height // 10))
            elif self.info_block_pause:
                pg.draw.rect(self.sc, pg.Color(50, 50, 50), (3 * const.tile_side, 2 * const.tile_side, 19 * const.tile_side, 15 * const.tile_side),
                             border_radius=15)
                self.draw_info_block_text()

            const.display_infos(self.sc, 'Level ' + str(const.level), x=15, y=15)

            if const.show_fps:
                const.display_infos(self.sc, str(self.clock.get_fps().__round__(2)), center=True, y=15)

            pg.display.flip()


class Player(pg.sprite.DirtySprite):
    """
    Classe du joueur
    """

    def __init__(self, game: Game):
        super().__init__()
        self.game = game  # Référence à l'instance du jeu

        self.animation_number = 0
        self.animation_name = 'idle'

        self.normal_image = const.player_animations[self.animation_name][self.animation_number]
        self.smol_image = const.smol_player_animations[self.animation_name][self.animation_number]
        self.image = self.normal_image

        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)

        self.dx = 0
        self.dy = 0
        self.onGround = False
        self.colliding_right_flag = False

        self.minimized = False

        self.frame_counter = 0

        self.collided_end_tile = None

        self.jump_sound = pg.mixer.Sound('assets/Sounds/jump.wav')
        self.jump_sound.set_volume(0.1)
        self.small_jump_sound = pg.mixer.Sound('assets/Sounds/small_jump.wav')
        self.small_jump_sound.set_volume(0.1)
        self.death_sound = pg.mixer.Sound('assets/Sounds/death.wav')
        self.death_sound.set_volume(0.15)

    def kill_player(self):
        """
        Tue le joueur, donc recommence le niveau au dernier checkpoint ou passe au niveau d'après si le joueur meurt après avoir fini le niveau
        :return:
        """
        if not self.game.level_ended:
            self.death_sound.play() if const.sound_effects_enabled else None
            self.game.reset_level()
        else:
            self.game.next_level()

    def handle_gravity(self):
        """
        Gère l'accélération verticale du player
        :return:
        """
        self.dy += const.gravity

        grav_inv = (-1 + 2 * (self.dy > const.tile_side))
        if abs(self.dy) > const.tile_side:
            self.dy = const.tile_side * grav_inv

    def jump(self, forced_dy: float = None):
        """
        Donne de l'accélération verticale au joueur pour simuler un saut.
        :return:
        """

        if forced_dy is not None:
            if const.sound_effects_enabled:
                self.jump_sound.play() if not self.minimized else self.small_jump_sound.play()
            self.dy = forced_dy

        elif self.onGround:
            if const.sound_effects_enabled:
                self.jump_sound.play() if not self.minimized else self.small_jump_sound.play()
            self.dy = const.jump_height
            self.onGround = False
        self.change_animation_to('jump')

    def change_animation_to(self, animation_name: str, tick: int = 0):
        """
        Change le cycle d'anination du sprite du joueur
        :param animation_name:
        :param tick:
        :return:
        """
        self.animation_name = animation_name
        if self.minimized:
            self.image = const.smol_player_animations[self.animation_name][tick]
        else:
            self.image = const.player_animations[self.animation_name][tick]
        if self.game.gravity_is_inversed:
            self.image = pg.transform.flip(self.image, False, True)

        self.frame_counter = 0

    def tick_animation(self, animation_number: int = None):
        """
        Update le cycle d'animation du sprite du joueur
        :param animation_number:
        :return:
        """
        if animation_number is None:
            self.animation_number += 1
            self.animation_number %= 3
        else:
            self.animation_number = animation_number

        if self.minimized:
            self.image = const.smol_player_animations[self.animation_name][self.animation_number]
        else:
            self.image = const.player_animations[self.animation_name][self.animation_number]
        if self.game.gravity_is_inversed:
            self.image = pg.transform.flip(self.image, False, True)

        self.frame_counter = 0

    def tick_movement(self):
        """
        Update la position du joueur.
        :return:
        """
        self.rect.x += self.dx
        self.rect.y += self.dy

        if (self.rect.y > self.game.low_dead_line.rect.y + const.tile_side * 20 and not self.game.gravity_is_inversed) or \
                (self.rect.y < self.game.high_dead_line.rect.y - const.tile_side * 20 and self.game.gravity_is_inversed):
            self.kill_player()
        if self.rect.x < 0:
            self.kill_player()

        if self.onGround:
            self.frame_counter += 1
            if self.frame_counter == 20:
                if self.animation_name == 'jump':
                    self.change_animation_to('idle')
                else:
                    self.tick_animation()

    def handle_y_axis_collisions(self):
        """
        Gère les collisions sur l'axe y du joueur avec les Tiles et applique l'effet des Tiles percutées
        :return:
        """
        collidedS = pg.sprite.spritecollideany(self, self.game.tile_group)
        no_collisions_S = pg.sprite.spritecollideany(self, self.game.pass_through_tiles)

        if no_collisions_S is not None:
            if isinstance(no_collisions_S, ent.EndTile):  # Quand le joueur passe dans un bloc de fin de niveau
                self.game.end_level()
            elif isinstance(no_collisions_S, ent.Minimizer):
                self.toggle_minimize() if not no_collisions_S.disabled else None
                no_collisions_S.disabled = True
            elif isinstance(no_collisions_S, ent.Checkpoint):
                self.game.last_checkpoint_pos = [no_collisions_S.x, no_collisions_S.y]

        if collidedS is not None:
            falling = self.dy > 0
            self.dy = 0

            if collidedS.rect.top <= self.rect.top <= collidedS.rect.bottom and not falling:  # Quand le joueur tape sa tête sur une Tile
                self.rect.top = collidedS.rect.bottom

                if self.game.gravity_is_inversed:  # Quand la gravité est inversée
                    if not self.onGround:
                        self.onGround = True
                        self.tick_animation(animation_number=1)
                    if not const.scrolling_forward:
                        self.game.set_scrolling(True)

                if isinstance(collidedS, ent.Spike):  # Collisions avec les spikes
                    if collidedS.facing != 0:
                        self.kill_player()
                elif isinstance(collidedS, ent.InfoBlock):  # Collisions avec les info_blocks
                    self.game.prompt_info_block_pause(collidedS.text)

                if self.game.gravity_is_inversed and collidedS.rect.left <= self.rect.centerx:  # Collisions quand la gravité est inversée
                    if collidedS.facing == 4:
                        if isinstance(collidedS, ent.Jumper):  # Collisions avec les Jumpers
                            self.jump(forced_dy=const.jump_height * 1.4)
                        elif isinstance(collidedS, ent.BackwardPusher):  # Collisions avec les Backward Jumper
                            self.jump(forced_dy=const.jump_height * 1.4)
                            self.game.set_scrolling(False)
                        elif isinstance(collidedS, ent.GravInverter):  # Collisions avec les inverseurs de gravité
                            self.game.invert_gravity()

            elif collidedS.rect.top <= self.rect.bottom <= collidedS.rect.bottom and falling:  # Quand le joueur aterri sur une Tile
                self.rect.bottom = collidedS.rect.top
                if not self.game.gravity_is_inversed:
                    if not self.onGround:
                        self.onGround = True
                        self.tick_animation(animation_number=1)
                    if not const.scrolling_forward:
                        self.game.set_scrolling(True)

                if collidedS.rect.left <= self.rect.centerx:
                    if collidedS.facing == 0:
                        if isinstance(collidedS, ent.Jumper):  # Collisions avec les Jumpers
                            self.jump(forced_dy=const.jump_height * 1.4)
                        elif isinstance(collidedS, ent.BackwardPusher):  # Collisions avec les Backward Jumper
                            self.jump(forced_dy=const.jump_height * 1.4)
                            self.game.set_scrolling(False)
                        elif isinstance(collidedS, ent.GravInverter) and not self.game.gravity_is_inversed:  # Collisions avec les inverseurs de gravité
                            self.game.invert_gravity()

                    if isinstance(collidedS, ent.Spike):  # Collisions avec les spikes
                        if collidedS.facing != 4:
                            self.kill_player()

    def handle_x_axis_collisions(self):
        """
        Gère les collisions sur l'axe x du joueur avec les Tiles et applique l'effet des Tiles percutées
        :return:
        """
        collidedS = pg.sprite.spritecollideany(self, self.game.tile_group)
        if collidedS is not None:
            if const.scrolling_forward:
                if self.rect.right > collidedS.rect.left:  # Quand le joueur entre en collision avec un mur
                    self.rect.right = collidedS.rect.left
                    self.colliding_right_flag = True
            else:
                if self.rect.left < collidedS.rect.right:
                    self.rect.left = collidedS.rect.right

            if isinstance(collidedS, ent.Spike):  # Collisions avec les spikes
                if collidedS.facing != 2 and const.scrolling_forward:
                    self.kill_player()
                elif collidedS.facing != 6 and not const.scrolling_forward:
                    self.kill_player()

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
            self.dx = 3
        else:
            self.dx = 0

    def toggle_minimize(self):
        """
        Alterne entre petit et normal
        :return:
        """
        centerx = self.rect.centerx
        floor_y = self.rect.top if self.game.gravity_is_inversed else self.rect.bottom
        if self.minimized:
            const.jump_height = const.normal_jump_height
            self.image = self.normal_image
            const.player_side = const.normal_player_side
        else:
            const.jump_height = const.smol_jump_height
            self.image = self.smol_image
            const.player_side = const.smol_player_side
        self.minimized = not self.minimized
        self.image = pg.transform.flip(self.image, False, self.game.gravity_is_inversed)
        self.rect = self.image.get_rect()
        self.rect.centerx = centerx
        if self.game.gravity_is_inversed:
            self.rect.top = floor_y
        else:
            self.rect.bottom = floor_y

    def reset_pos_and_vars(self):
        """
        Réinitialise les variables du joueur
        :return:
        """
        const.jump_height = const.normal_jump_height
        const.player_side = const.normal_player_side
        self.minimized = False
        self.image = self.normal_image
        self.rect = self.image.get_rect()
        self.rect.x = const.startx
        self.rect.y = const.sc_height - (const.sc_height // 3)
        self.dy = 0
        self.onGround = True
        self.change_animation_to('idle')
        self.colliding_right_flag = False
        self.collided_end_tile = None
