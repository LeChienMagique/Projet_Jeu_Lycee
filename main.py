import pygame as pg
import game
import const
import LevelEditor
import level_selection

if __name__ == '__main__':
    screen = const.screen
    framerate = 60
    g = game.Game(screen)
    le = LevelEditor.LevelEditor(screen)
    le_select = level_selection.LevelSelection(screen)
    while True:
        if const.mode == "playing":
            pg.key.set_repeat(1, 10)
            g.running = True
            g.load_level(const.level)
            g.main(framerate)
        elif const.mode == "editing":
            pg.key.set_repeat(75, 75)
            le.running = True
            le.load_level(const.level)
            le.main(framerate)
        elif const.mode == 'level_selection':
            pg.key.set_repeat(1, 10)
            le_select.running = True
            le_select.main(framerate)

        screen.fill((0, 0, 0))
