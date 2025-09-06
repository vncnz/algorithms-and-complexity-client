#!/usr/bin/env python3

import sys, os
import json
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QTimer

from game_ui_common import ClickablePolygon, read_stdin_line, get_from_env, GameUI

from functools import partial
log = print # Rewritten later in __main__
send = partial(print, flush=True)

from time import sleep

# polygons = []
colors = [QColor("#99cc99"), QColor("#bbddbb"), QColor("#999999")] # , QColor("#99ff99"), QColor("#cccccc"), QColor("#ffcc77")]
app = None

def process_server_message(line):
    try:
        cmd, _, data = line.partition(':')
        log(f'cmd:{cmd}   data:{data}')
        if cmd == 'game':
            game = json.loads(data)
            log("proceeding with drawing game board")
            app.draw(game["board"], game["row"])
            if game['status'] != 'running':
                app.update_label(game['status'])
        #elif cmd == 'hint':
        #    msg = json.loads(data)
        #    # We get the full solution from the "server" but we show only the first cell to be pressed
        #    first_hint = msg.index(1)
        #    polygons[first_hint].update_color(QColor('#ffdd44'))
    # except json.JSONDecodeError:
    #     log("Invalid JSON")
    except Exception as e:
        print(e)

class Maze(GameUI):
    def __init__(self):

        super().__init__('Maze')
        # UI buttons
        btn_exit = QPushButton("Exit")
        btn_exit.clicked.connect(self.exit)

        # btn_hint = QPushButton("Hint")
        # btn_hint.clicked.connect(lambda: send("hint:"))

        self.add_buttons([btn_exit])

        self.polygons = []

    def draw (self, data, ncols):
        log(f"Drawing game board")
        # (update_draw if len(polygons) > 0 else first_draw)(data)
        if len(self.polygons) > 0:
            self.update_draw(data, ncols)
        else:
            self.first_draw(data, ncols)
    
    def draw_maze_cell (self, row, column, sz, cell, polygon_defs):
        cell_half_size = 2

        x = column * sz * 2
        y = row * sz * 2
        polygon_defs.append((
            [(x-sz, y-sz), (x+sz, y-sz), (x+sz, y+sz), (x-sz, y+sz)],
            QColor("#bbddbb") if (row % 2 - column % 2) else QColor("#b0ddbb"),
            f"{row}_{column}"
        ))
        if cell['N']:
            polygon_defs.append((
                [(x-sz, y-sz-cell_half_size), (x+sz, y-sz-cell_half_size), (x+sz, y-sz+cell_half_size), (x-sz, y-sz+cell_half_size)],
                QColor("#333333"),
                f"{row}_{column}_N"
            ))
        if cell['E']:
            polygon_defs.append((
                [(x+sz-cell_half_size, y-sz), (x+sz+cell_half_size, y-sz), (x+sz+cell_half_size, y+sz), (x+sz-cell_half_size, y+sz)],
                QColor("#333333"),
                f"{row}_{column}_E"
            ))
        if cell['S']:
            polygon_defs.append((
                [(x-sz, y+sz-cell_half_size), (x+sz, y+sz-cell_half_size), (x+sz, y+sz+cell_half_size), (x-sz, y+sz+cell_half_size)],
                QColor("#333333"),
                f"{row}_{column}_S"
            ))
        if cell['W']:
            polygon_defs.append((
                [(x-sz-cell_half_size, y-sz), (x-sz+cell_half_size, y-sz), (x-sz+cell_half_size, y+sz), (x-sz-cell_half_size, y+sz)],
                QColor("#333333"),
                f"{row}_{column}_W"
            ))

    def first_draw (self, board, ncols):
        sz = min(30, int((self.drawWidth - 4)/ ncols / 2))
        log(f'sz:{sz} drawWidth:{self.drawWidth} ncols:{ncols}')
        polygon_defs = []
        for idx, cell in enumerate(board):
            row = int(idx / ncols)
            column = idx % ncols
            log(f'drawing {idx} at {column},{row}')
            self.draw_maze_cell(row, column, sz, cell, polygon_defs)

        for (points, color, id) in polygon_defs:
            poly = ClickablePolygon(id, points, color, onclick=self.onclick)
            self.scene.addItem(poly)
            self.polygons.append(poly)

    def update_draw (self, board, _):
        for row in range(len(board)):
            for column in range(len(board[row])):
                c = colors[board[row][column]]
                poly = next(filter(lambda x: x.id == f'{row}_{column}', self.polygons))
                poly.update_color(c)
    
    def onclick (self, id):
        log(f'Clicked {id}')
        send(f'click:{id}')
    
    def exit (self):
        log("Exiting")
        send("exit:")
        sleep(.1)
        sys.exit(0)

def main(blocking=True):
    global app
    app = Maze()
    app.show()

    # Timer for checking stdin
    timer = QTimer()
    timer.timeout.connect(lambda: (
        (line := read_stdin_line(blocking)) and process_server_message(line)
    ))
    timer.start(100) # ms

    sys.exit(app.run())

if __name__ == "__main__":
    flog = open(os.path.join(get_from_env("TAL_META_OUTPUT_FILES", ""), "ui_log.txt"), "w")
    log = partial(print, file=flog, flush=True)
    log(f'GAME: Maze')
    main(blocking=False)
