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

class Nim(GameUI):
    def __init__(self):

        super().__init__('Nim')
        # UI buttons
        btn_exit = QPushButton("Exit")
        btn_exit.clicked.connect(self.exit)

        # btn_hint = QPushButton("Hint")
        # btn_hint.clicked.connect(lambda: send("hint:"))

        self.add_buttons([btn_exit])

        self.polygons = []

    def draw (self, data):
        # (update_draw if len(polygons) > 0 else first_draw)(data)
        if len(self.polygons) > 0:
            self.update_draw(data)
        else:
            self.first_draw(data)

    def first_draw (self, data):
        polygon_defs = []
        for row, couple in enumerate(data):
            sz = 30
            in_pile, removed = couple
            # log(f'couple:{couple}')
            for el in range(in_pile + removed):
                x = el * sz * 2
                y = row * sz * 2
                inpile_color = 0 if currentPlayer == 1 else 1
                polygon_defs.append((
                    [(x-sz, y-sz), (x+sz, y-sz), (x+sz, y+sz), (x-sz, y+sz)],
                    colors[inpile_color if el < in_pile else 2],
                    f"{row}_{el}"
                ))

        for (points, color, id) in polygon_defs:
            poly = ClickablePolygon(id, points, color, onclick=self.onclick)
            self.scene.addItem(poly)
            self.polygons.append(poly)

    def update_draw (self, data):

        for row, couple in enumerate(data):
            in_pile, removed = couple
            for el in range(in_pile + removed):
                inpile_color = 0 if currentPlayer == 1 else 1
                color = colors[inpile_color if el < in_pile else 2]
                poly = next(filter(lambda x: x.id == f'{row}_{el}', self.polygons))
                poly.update_color(color)
    
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
    app = Nim()
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
    log(f'GAME: nim')
    main(blocking=False)
