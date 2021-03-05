import pygame as pg
import os

pg.init()

customSizeFont = lambda n: pg.font.SysFont('Alef', n)
myFont = pg.font.SysFont('Alef', 25)
bigFont = pg.font.SysFont('Alef', 40)

sc_width = 1200
sc_height = 1200

bg = None

level = 1

number_of_levels = len(os.listdir('Levels/'))
number_of_edited_levels = len(os.listdir('Edited_Levels/'))

startx = sc_width // 10
starty = 0

tile_side = sc_width // 25
player_side = sc_width // 35

scrolling_speed = sc_width // 140
jump_height = -(tile_side / 2)
gravity_intensity = 0.026 * tile_side

previous_mode = 'level_selection'
mode = 'level_selection'

scrolling_forward = True


def next_level():
    global level
    if number_of_levels <= level + 1:
        level += 1
        return True
    return False


def refresh_number_of_levels():
    global number_of_levels, number_of_edited_levels
    number_of_levels = len(os.listdir('Levels/'))
    number_of_edited_levels = len(os.listdir('Edited_Levels/'))


def load_sprite(sprite_name):
    if sprite_name == 'player':
        side = tile_side
    else:
        side = tile_side
    return pg.transform.scale(pg.image.load('Blocks_Sprites/' + sprite_name + '.png'), (side, side))


def load_background():
    return pg.transform.scale(pg.image.load('background.png'), (sc_width, sc_height))


background = load_background()


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
