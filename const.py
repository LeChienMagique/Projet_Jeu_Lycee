import pygame as pg
import tkinter as tk
import os
import sys
import json

pg.init()

sc_width = sc_height = 1400


def define_window_size(size: int, root: tk.Tk):
    global sc_width, sc_height
    print(size)
    sc_width = sc_height = int(size)
    settings = json.load(open('settings.json', 'r'))
    settings['window_size'] = int(size)
    json.dump(settings, open('settings.json', 'w'), indent=4)
    root.destroy()


def ask_window_size():
    root = tk.Tk()
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f'{int(w * 0.3)}x{int(h * 0.3)}')

    infos = tk.Label(root, text="Sélectionnez la taille de la fenêtre")
    infos.pack(anchor=tk.N)

    size_options = [s for s in range(400, h + 1, 100)]
    size_var = tk.StringVar()
    size_var.set(size_options[0])
    for item in size_options:
        button = tk.Radiobutton(root, text=f'{item}x{item}', variable=size_var, value=item)
        button.pack(anchor=tk.N)
    button = tk.Button(root, text='Valider', command=lambda: define_window_size(size_var.get(), root))
    button.pack(anchor=tk.N)
    root.protocol("WM_DELETE_WINDOW", sys.exit)
    root.mainloop()


settings = json.load(open("settings.json", 'r'))

if settings['ask_window_size']:
    ask_window_size()
else:
    sc_width = sc_height = settings['window_size']

screen = pg.display.set_mode((sc_width, sc_height))

customSizeFont = lambda n: pg.font.SysFont('Alef', n)
myFont = pg.font.SysFont('Alef', 25)
bigFont = pg.font.SysFont('Alef', 60)

level = 1

number_of_levels = len(os.listdir('Levels/'))
number_of_edited_levels = len(os.listdir('Edited_Levels/'))

tile_side = sc_width / 25
normal_player_side = sc_width // 28
smol_player_side = normal_player_side // 2
player_side = normal_player_side

start_worldx = 2
startx = start_worldx * tile_side

scrolling_speed_modifier = int(settings['scrolling_speed'][:-1]) / 100
jump_height_modifier = int(settings['jump_height'][:-1]) / 100
gravity_modifier = int(settings['gravity'][:-1]) / 100

scrolling_speed = int(tile_side * 0.25 * scrolling_speed_modifier)
normal_jump_height = -(tile_side * 0.5) * jump_height_modifier
smol_jump_height = normal_jump_height * 1.2
jump_height = normal_jump_height
gravity = (0.026 * tile_side) * gravity_modifier

tile_side = int(tile_side)

previous_mode = 'level_selection'
mode = 'level_selection'

scrolling_forward = True

blank_level_data = '''{"misc": {"spawnpoint": [0,0]}, "0":{"0":"player_spawn"}}'''


def delete_edited_level():
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
    global level
    if level + 1 <= number_of_levels:
        level += 1
        return True
    return False


def refresh_number_of_levels():
    global number_of_levels, number_of_edited_levels
    number_of_levels = len(os.listdir('Levels/'))
    number_of_edited_levels = len(os.listdir('Edited_Levels/'))


def load_sprite(sprite_name, custom_side: int = -1):
    if sprite_name == 'player':
        side = player_side
    else:
        side = tile_side
    side = int(side) if custom_side == -1 else custom_side
    path = os.path.join('Blocks_Sprites', sprite_name + '.png')
    return pg.transform.scale(pg.image.load(path), (side, side))


def display_infos(screen: pg.Surface, x: int, y: int, *args):
    infos = "".join(args)
    textsurf = myFont.render(infos, True, (255, 255, 255))
    screen.blit(textsurf, (x, y))


def change_mode(mode_name: str):
    global mode, previous_mode
    previous_mode = mode
    if mode_name == 'editing':
        mode = 'editing'
    elif mode_name == 'playing':
        mode = 'playing'
    elif mode_name == 'level_selection':
        mode = 'level_selection'


class BackgroundLayer(pg.sprite.Sprite):
    def __init__(self, layer: int, number: int, image: pg.Surface):
        super().__init__()
        self.image = image
        self.number = number
        self.rect = self.image.get_rect()
        self.rect.left = self.rect.width * self.number
        self.rect.bottom = sc_height
        self._layer = layer
        self.scrolling_speed = int(layer * (scrolling_speed / 4))

    def update(self, ntimes=1, forward=True) -> None:
        if scrolling_forward and forward:
            self.rect.x -= self.scrolling_speed * ntimes
            if self.rect.right < 0:
                self.rect.left = self.rect.width
        else:
            self.rect.x += self.scrolling_speed * ntimes
            if self.rect.left > self.rect.width:
                self.rect.right = 0


def make_background_group():
    # return pg.transform.scale(pg.image.load('city.png'), (sc_width, sc_height))
    sprites = []
    path = os.path.join('Backgrounds', 'space_layers')
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

        sprites.extend([BackgroundLayer(image[1], 0, scaled_img), BackgroundLayer(image[1], 1, scaled_img)])
    return sprites


background = make_background_group()


class Button(pg.sprite.Sprite):
    def __init__(self, x: int, y: int, w: int, h: int, rectColor: pg.Color, onHoverRectColor: pg.Color, callback,
                 text=None, textColor=pg.Color(0, 0, 0), image=None, font=myFont):
        super().__init__()
        self.onHoverRectColor = onHoverRectColor
        self.rectColor = rectColor
        self.callback = callback
        self.width = w
        self.height = h
        self.font = font
        self.text = text
        self.textColor = textColor
        self.spriteImg = image
        self.image = pg.Surface((w, h))
        self.image.fill(rectColor)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.blit_content()
        self.hovered = False

    def blit_content(self):
        if self.text is not None:
            self.textsurf = self.font.render(self.text, True, self.textColor)
            self.image.blit(self.textsurf, (self.width // 2 - self.textsurf.get_rect().width // 2,
                                            self.height // 2 - self.textsurf.get_rect().height // 2))

        elif self.spriteImg is not None:
            self.image.blit(self.spriteImg, (self.width // 2 - self.spriteImg.get_rect().width // 2,
                                             self.height // 2 - self.spriteImg.get_rect().height // 2))

    def change_rect_color(self, hovered: bool):
        """
        Change la couleur du bouton
        :param hovered:
        :return:
        """
        if hovered != self.hovered:  # Optimisation des appels de dessin
            self.image.fill(self.onHoverRectColor if hovered else self.rectColor)
            self.blit_content()
            # Pour aligner le texte au milieu du bouton

    def update(self, mouse_pos, mouse_pressed: bool) -> None:
        if self.rect.left < mouse_pos[0] < self.rect.right and self.rect.top < mouse_pos[1] < self.rect.bottom:
            self.change_rect_color(True)
            self.hovered = True
            if mouse_pressed:
                self.on_click()
        else:
            self.change_rect_color(False)
            self.hovered = False

    def on_click(self):
        if callable(self.callback):
            self.callback()
