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

currentPlayer = None

def process_server_message(line):
    global currentPlayer
    try:
        cmd, _, data = line.partition(':')
        log(f'cmd:{cmd}   data:{data}')
        # if cmd == 'board':
        #    from ast import literal_eval
        #    msg = literal_eval(data)
        #    app.draw(msg)
        if cmd == 'game':
            game = json.loads(data)
            currentPlayer = game["currentPlayer"]
            app.draw(game["board"])
            if game['status'] != 'running':
                app.update_label(game['status'])
                currentPlayer = None
            else:
                if currentPlayer == 1:
                    app.update_label(f"Playing: player")
                else:
                    app.update_label(f"Playing: computer")
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
        # (update_draw if len(polygons) > 0 else first_draw)(data)
        if len(self.polygons) > 0:
            self.update_draw(data, ncols)
        else:
            self.first_draw(data, ncols)

    def first_draw (self, board, ncols):
        sz = 30
        polygon_defs = []
        for idx, cell in enumerate(board):
            row = int(idx / ncols)
            column = idx % ncols
            x = column * sz * 2
            y = row * sz * 2
            polygon_defs.append((
                [(x-sz, y-sz), (x+sz, y-sz), (x+sz, y+sz), (x-sz, y+sz)],
                QColor("#bbddbb") if idx % 2 else QColor("#99ddbb"),
                f"{row}_{column}"
            ))

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
