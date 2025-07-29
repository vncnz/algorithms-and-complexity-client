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

colors = [QColor("#666666"), QColor("#ff7799")]
app = None

currentPlayer = None
gameStatus = None

m = int(get_from_env("TAL_m", "5"))
n = int(get_from_env("TAL_n" ,"5"))

def process_server_message(line):
    try:
        cmd, _, data = line.partition(':')
        log(f'cmd:{cmd}   data:{data}')
        #if cmd == 'field':
        #    msg = json.loads(data)
        #    # send(f"Received: {msg}")
        #    app.draw(msg)
        if cmd == 'game':
            game = json.loads(data)
            currentPlayer = game["currentPlayer"]
            gameStatus = game["status"]
            app.draw(game["board"], game["row"])
            if currentPlayer == 1: # unused in flip game
                app.update_label(f"Playing: player")
            elif currentPlayer == 0: # unused in flip game
                app.update_label(f"Playing: computer")
            elif gameStatus == 'win':
                app.end_game(True)
            elif gameStatus == 'running':
                app.update_label(f"Keep trying...")
        elif cmd == 'hint':
            msg = json.loads(data)
            # We get the full solution from the "server" but we show only the first cell to be pressed
            first_hint = msg.index(1)
            app.draw_hint(first_hint)
            app.update_label(f"Click on the yellow square!")
    # except json.JSONDecodeError:
    #     send("Invalid JSON")
    except Exception as e:
        print(e)

class Flip(GameUI):
    def __init__(self):

        super().__init__('Flip')
        # UI buttons
        btn_exit = QPushButton("Exit")
        btn_exit.clicked.connect(self.exit)

        btn_hint = QPushButton("Hint")
        btn_hint.clicked.connect(lambda: send("hint:"))

        self.add_buttons([btn_exit, btn_hint])

        self.polygons = []
        self.readonly = False

    def draw (self, data, row):
        # (update_draw if len(polygons) > 0 else first_draw)(data)
        if len(self.polygons) > 0:
            self.update_draw(data, row)
        else:
            self.first_draw(data, row)

    def first_draw (self, board, _):
        sz = 30
        polygon_defs = []
        for row in range(len(board)):
            for column in range(len(board[row])):
                x = column * sz * 2
                y = row * sz * 2
                polygon_defs.append((
                    [(x-sz, y-sz), (x+sz, y-sz), (x+sz, y+sz), (x-sz, y+sz)],
                    colors[board[row][column]],
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
    
    def draw_hint (self, idx):
        self.polygons[idx].update_color(QColor('#ffdd44'))

    def onclick (self, id):
        if not self.readonly:
            log(f'Clicked {id}')
            send(f'click:{id}')
    
    def end_game (self, win):
        if win: self.update_label(f"Congratulations!")
        # No lose case in flip game
        self.readonly = True
    
    def exit (self):
        log("Exiting")
        send("exit:")
        sleep(.1)
        sys.exit(0)

def main(blocking=True):
    global app
    app = Flip()
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
    log(f'GAME: flip')
    main(blocking=False)
