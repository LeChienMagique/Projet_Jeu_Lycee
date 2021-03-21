import pygame as pg
import tkinter as tk
import os
import sys
from configparser import ConfigParser

pg.init()

sc_width = sc_height = 1400


def define_window_size(size: int, root: tk.Tk):
    """
    Change la taille de la fenêtre du jeu
    :param size:
    :param root:
    :return:
    """
    global sc_width, sc_height
    sc_width = sc_height = int(size)
    settings['Window']['window_size'] = str(size)
    settings.write(open('settings.ini', 'w'))
    root.destroy()


def ask_window_size():
    """
    Créé un pop-up permettant de choisir la taille de la fenêtre du jeu
    """
    root = tk.Tk()
    root.title('Soup Slime')
    root.iconbitmap(os.path.join('assets', 'Icons', 'game_icon.ico'))
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()

    if w < 600 or h < 600:
        raise Exception("Votre écran est trop petit pour le jeu.")

    root.geometry(f'{int(w * 0.3)}x{int(h * 0.3)}')

    infos = tk.Label(root, text="Sélectionnez la taille de la fenêtre")
    infos.pack(anchor=tk.N)

    size_options = [s for s in range(600, h + 1, 100)]
    size_var = tk.StringVar()
    size_var.set(size_options[0])
    for item in size_options:
        button = tk.Radiobutton(root, text=f'{item}x{item}', variable=size_var, value=item)
        button.pack(anchor=tk.N)
    button = tk.Button(root, text='Valider', command=lambda: define_window_size(size_var.get(), root))
    button.pack(anchor=tk.N)
    root.protocol("WM_DELETE_WINDOW", sys.exit)
    root.mainloop()


settings = ConfigParser()
settings.read_file(open('settings.ini'))
settings.read('settings.ini')

if settings['Window'].getboolean('ask_window_size'):
    ask_window_size()
else:
    sc_width = sc_height = int(settings['Window']['window_size'])

screen = pg.display.set_mode((sc_width, sc_height))
window_icon = pg.image.load(os.path.join('assets', 'Icons', 'game_icon.ico'))
pg.display.set_icon(window_icon)
pg.display.set_caption('Soup Slime')

font_size = sc_width // 40
myFont = pg.font.Font('assets/PixelCountdown-Yaj4.ttf', font_size)
boldFont = pg.font.Font('assets/PixelCountdown-Yaj4.ttf', font_size)
boldFont.set_bold(True)

level = 1

number_of_levels = len(os.listdir('Levels/'))
number_of_edited_levels = len(os.listdir('Edited_Levels/'))

tile_side = sc_width / 25
normal_player_side = sc_width // 28
smol_player_side = normal_player_side // 2
player_side = normal_player_side

start_worldx = 3
startx = start_worldx * tile_side

scrolling_speed_modifier = int(settings['Physics']['scrolling_speed']) / 100
jump_height_modifier = int(settings['Physics']['jump_height']) / 100
gravity_modifier = int(settings['Physics']['gravity']) / 100

scrolling_speed = int(tile_side * 0.25 * scrolling_speed_modifier)
normal_jump_height = -(tile_side * 0.5) * jump_height_modifier
smol_jump_height = normal_jump_height * 1.2
jump_height = normal_jump_height
normal_gravity = (0.026 * tile_side) * gravity_modifier
space_gravity = normal_gravity * 0.65
gravity = normal_gravity

tile_side = int(tile_side)

previous_mode = 'level_selection'
mode = 'level_selection'

scrolling_forward = True

blank_level_data = '''{"misc": {"background_name": "industrial_layers", "spawnpoint": [0,0]}, "0":{"0":"player_spawn"}}'''

show_fps = settings['Game'].getboolean('show_fps')


def delete_edited_level():
    """
    Supprime le niveau éditable en cours d'utilisation
    """
    global number_of_edited_levels
    n = level
    print(f'Level {n} va être supprimé')
    if os.path.exists(f'Edited_Levels/level_{n}.json'):
        os.remove(f'Edited_Levels/level_{n}.json')
        print('Le niveau a été supprimé')
    for i in range(n + 1, number_of_edited_levels + 1):
        path = os.path.join('Edited_Levels', 'level_' + str(i) + '.json')
        print(path)
        if os.path.exists(path):
            os.rename(path, os.path.join('Edited_Levels', 'level_' + str(i - 1) + '.json'))
    refresh_number_of_levels()


def next_level():
    """
    Passe au niveau suivant
    :return:
    """
    global level, background_pointer
    if level + 1 <= number_of_levels:
        level += 1
        return True
    return False


def refresh_number_of_levels():
    """
    Actualise le nombre de niveau présents dans le dossier Edited_Levels/ et Levels/
    """
    global number_of_levels, number_of_edited_levels
    number_of_levels = len(os.listdir('Levels/'))
    number_of_edited_levels = len(os.listdir('Edited_Levels/'))


def get_sprite(sprite_name, facing=0, icon=False):
    """
    Renvoie le sprite correspondant à la demande
    :param sprite_name:
    :param facing:
    :param icon:
    :return:
    """
    if icon:
        return icons[sprite_name]
    if facing != 0:
        if "spike" in sprite_name:
            return sprites['spike' + str(facing)]
        else:
            return pg.transform.rotate(sprites[sprite_name], 45 * facing)
    return sprites[sprite_name]


def load_sprite(sprite_name, facing=0, icon=False, custom_side: int = None):
    """
    Charge en mémoire le sprite demandé et le renvoie
    :param sprite_name:
    :param facing:
    :param icon:
    :param custom_side:
    :return:
    """
    if custom_side is None:
        side = tile_side
    else:
        side = custom_side

    if icon:
        path = os.path.join('assets', 'Icons', sprite_name + '.png')
    else:
        path = os.path.join('assets', 'Blocks_Sprites', sprite_name + '.png')
    image = pg.transform.scale(pg.image.load(path), (side, side))
    return pg.transform.rotate(image, 45 * facing)


def load_player_sprite(sprite_name):
    """
    Charge en mémoire le sprite du joueur et le renvoie
    :param sprite_name:
    :return:
    """
    path = os.path.join('assets', 'Player_Animations', sprite_name + '.png')
    return pg.transform.scale(pg.image.load(path), (player_side, player_side))


sprites = {'backward_jumper': load_sprite('backward_jumper'), 'checkpoint': load_sprite('checkpoint'),
           'tile': load_sprite('tile'), 'jumper': load_sprite('jumper'), 'end': load_sprite('end'),
           'info_block': load_sprite('info_block'), 'gravity_inverter': load_sprite('gravity_inverter'), 'minimizer': load_sprite('minimizer'),
           'spike0': load_sprite('spike0'), 'spike1': load_sprite('spike1'), 'spike2': load_sprite('spike2'),
           'spike3': load_sprite('spike3'), 'spike4': load_sprite('spike4'),
           'spike5': load_sprite('spike5'), 'spike6': load_sprite('spike6'), 'spike7': load_sprite('spike7'),
           'spike': load_sprite('spike'), 'player_spawn': load_sprite('player_spawn', custom_side=tile_side)}

icons = {'checkmark': load_sprite('checkmark', icon=True), 'cross': load_sprite('cross', icon=True),
         'home': load_sprite('home', icon=True), 'plus': load_sprite('plus', icon=True),
         'power': load_sprite('power', icon=True), 'return': load_sprite('return', icon=True),
         'right': load_sprite('right', icon=True), 'save': load_sprite('save', icon=True),
         'trashcan': load_sprite('trashcan', icon=True), 'warning': load_sprite('warning', icon=True),
         'wrench': load_sprite('wrench', icon=True), 'button_unpressed': load_sprite('button_unpressed', icon=True),
         'button_pressed': load_sprite('button_pressed', icon=True), 'change_background': load_sprite('contrast', icon=True),
         'information': load_sprite('information', icon=True)}

player_animations = {'jump': [load_player_sprite('jump' + str(i)) for i in range(2)], 'idle': [load_player_sprite('idle' + str(i)) for i in range(3)]}

smol_player_animations = {k: [pg.transform.scale(image, (player_side // 2, player_side // 2)) for image in v] for k, v in player_animations.items()}


def display_infos(surf: pg.Surface, *args, font: pg.font = myFont, center: bool = False, x: int = None, y: int = None,
                  textColor: pg.Color = pg.Color(255, 255, 255)):
    """
    Affiche du texte à l'endroit indiqué avec des options de customisation
    :param surf:
    :param args:
    :param font:
    :param center:
    :param x:
    :param y:
    :param textColor:
    """
    infos = "".join(args)
    textsurf = font.render(infos, True, textColor)
    if not center:
        surf.blit(textsurf, (x, y))
    else:
        x = surf.get_width() // 2 - textsurf.get_width() // 2 if x is None else x
        y = surf.get_height() // 2 - textsurf.get_height() // 2 if y is None else y
        surf.blit(textsurf, (x, y))


def change_mode(mode_name: str):
    """
    Change le 'mode de jeu'
    :param mode_name:
    """
    global mode, previous_mode
    previous_mode = mode
    if mode_name == 'editing':
        mode = 'editing'
    elif mode_name == 'playing':
        mode = 'playing'
    elif mode_name == 'level_selection':
        mode = 'level_selection'


class BackgroundLayer(pg.sprite.Sprite):
    """
    Class pour créer des layers de background
    """

    def __init__(self, layer: int, number: int, image: pg.Surface):
        super().__init__()
        self.image = image
        self.number = number
        self.rect = self.image.get_rect()
        self.rect.left = self.rect.width * self.number
        self.rect.bottom = sc_height
        self._layer = layer
        self.scrolling_speed = int(layer * (scrolling_speed / 6))

    def update(self, ntimes=1, forward=True) -> None:
        """
        Actualise la position du layer
        :param ntimes:
        :param forward:
        """
        if scrolling_forward and forward:
            self.rect.x -= self.scrolling_speed * ntimes
            if self.rect.right < 0:
                self.rect.left = self.rect.width
        else:
            self.rect.x += self.scrolling_speed * ntimes
            if self.rect.left > self.rect.width:
                self.rect.right = 0


def make_background_group(background_group_name: str):
    """
    Créé les backgrounds et les renvoie
    :return:
    """
    background_sprites = []
    path = os.path.join('assets', 'Backgrounds', background_group_name)
    images = []
    max_height = -1
    for file in os.listdir(path):
        image = pg.image.load(os.path.join(path, file)).convert_alpha(screen)
        max_height = max(image.get_height(), max_height)
        layer = int(os.path.splitext(file)[0])
        images.append((image, layer))

    ratio = sc_height / max_height
    for image in images:
        image[0]: pg.Surface
        new_width = int(image[0].get_width() * ratio)
        new_height = int(image[0].get_height() * ratio)

        scaled_img = pg.transform.scale(image[0], (new_width, new_height))

        background_sprites.extend([BackgroundLayer(image[1], 0, scaled_img), BackgroundLayer(image[1], 1, scaled_img)])
    return background_sprites


def get_background_for_level(n: int):
    """
    Retourne le background à afficher pour un niveau donné
    :param n:
    :return:
    """
    n -= 1
    n %= 16
    return make_background_group(background_group_names[n // 4])


background_group_names = ['industrial_layers', 'forest_layers', 'mountain_layers', 'space_layers']




class Button(pg.sprite.Sprite):
    """
    Class permettant de créer un bouton avec des options de customisation
    """

    def __init__(self, x: int, y: int, w: int, h: int, callback, text=None, textColor=pg.Color(0, 0, 0), image: pg.Surface = None, font=myFont):
        super().__init__()
        self.callback = callback
        self.width = w
        self.height = h
        self.font = font
        self.text = text
        self.textColor = textColor
        self.spriteImg = image

        self.pressed_image = pg.transform.scale(get_sprite('button_pressed', icon=True), (w, h))
        self.unpressed_image = pg.transform.scale(get_sprite('button_unpressed', icon=True), (w, h))
        self.hovered_image = self.unpressed_image.copy()
        self.hovered_image.fill((50, 50, 50), special_flags=pg.BLEND_RGB_ADD)

        self.image = self.unpressed_image

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.blit_content()
        self.hovered = False

    def blit_content(self):
        """
        Réaffihe le texte ou l'image sur le bouton
        """
        if self.text is not None:
            self.textsurf = self.font.render(self.text, True, self.textColor)
            self.image.blit(self.textsurf, (self.width // 2 - self.textsurf.get_rect().width // 2,
                                            self.height // 2 - self.textsurf.get_rect().height // 2))
            # Pour aligner le texte au milieu du bouton

        elif self.spriteImg is not None:
            self.image.blit(self.spriteImg, (self.width // 2 - self.spriteImg.get_rect().width // 2,
                                             self.height // 2 - self.spriteImg.get_rect().height // 2))

    def change_rect_color(self, hovered: bool):
        """
        Change la couleur du bouton
        :param hovered:
        :return:
        """
        if hovered != self.hovered:
            self.image = self.hovered_image if hovered else self.unpressed_image
            self.blit_content()

    def update(self, mouse_pos, mouse_pressed: bool) -> None:
        """
        Actualise le bouton, change sa couleur etc... si il est appuyé ou survolé
        :param mouse_pos:
        :param mouse_pressed:
        """
        if self.rect.left < mouse_pos[0] < self.rect.right and self.rect.top < mouse_pos[1] < self.rect.bottom:
            self.change_rect_color(True)
            self.hovered = True
            if mouse_pressed:
                self.on_click()
            else:
                self.image = self.hovered_image
        else:
            self.change_rect_color(False)
            self.hovered = False
            self.image = self.unpressed_image

    def on_click(self):
        """
        Appelé quand le bouton est cliqué
        """
        self.image = self.pressed_image
        self.blit_content()
        if callable(self.callback):
            self.callback()
