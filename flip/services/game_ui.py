#!/usr/bin/env python3

import sys, os
import json
import select
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsPolygonItem, QPushButton, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtGui import QPolygonF, QBrush, QColor, QPainter
from PyQt5.QtCore import QPointF, QTimer

from game_ui_common import print_now, ClickablePolygon, read_stdin_line, get_from_env, GameUI

from time import sleep

# polygons = []
colors = [QColor("#666666"), QColor("#ff7799")] # , QColor("#99ff99"), QColor("#cccccc"), QColor("#ffcc77")]
app = None

flog = open(os.path.join(get_from_env("TAL_META_OUTPUT_FILES", ""), "ui_log.txt"), "w")
print_now(f'GAME: flip', file=flog)
currentPlayer = None

m = int(get_from_env("TAL_m", "5"))
n = int(get_from_env("TAL_n" ,"5"))

def process_server_message(line):
    try:
        cmd, _, data = line.partition(':')
        print_now(f'cmd:{cmd}   data:{data}', file=flog)
        #if cmd == 'field':
        #    msg = json.loads(data)
        #    # print_now(f"Received: {msg}")
        #    app.draw(msg)
        if cmd == 'game':
            game = json.loads(data)
            currentPlayer = game["currentPlayer"]
            app.draw(game["board"], game["row"])
            if currentPlayer == 1:
                app.update_label(f"Playing: player")
            else:
                app.update_label(f"Playing: computer")
        elif cmd == 'hint':
            msg = json.loads(data)
            # We get the full solution from the "server" but we show only the first cell to be pressed
            first_hint = msg.index(1)
            app.polygons[first_hint].update_color(QColor('#ffdd44')) #! Change me!
    # except json.JSONDecodeError:
    #     print_now("Invalid JSON")
    except Exception as e:
        print(e)

class Flip(GameUI):
    def __init__(self):

        super().__init__('Flip')
        # UI buttons
        btn_exit = QPushButton("Exit")
        btn_exit.clicked.connect(self.exit)

        btn_hint = QPushButton("Hint")
        btn_hint.clicked.connect(lambda: print_now("hint:"))

        self.add_buttons([btn_exit, btn_hint])

        self.polygons = []

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

    def onclick (self, id):
        print_now(f'Clicked {id}', file=flog)
        print_now(f'click:{id}')
    
    def exit (self):
        print_now("exit:")
        sleep(.1)
        sys.exit(0)

def main(blocking=True):

    #back_coo = (-150, -150)
    #back_points = [
    #    (back_coo[0]-50, back_coo[1]-10),
    #    (back_coo[0]+50, back_coo[1]-10),
    #    (back_coo[0]+50, back_coo[1]+10),
    #    (back_coo[0]-50, back_coo[1]+10)
    #]
    #back = ClickablePolygon(-1, back_points, QColor("#ff8855"), text="Exit")
    #scene.addItem(back)

    #polygons = [
        #[(50, 50), (150, 60), (120, 150), (60, 140)],
        #[(200, 80), (300, 100), (280, 180), (210, 160)],
        #[(100, 200), (180, 220), (160, 300), (90, 280)],
        #[(250, 250), (320, 270), (310, 340), (260, 320)]
    #]

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
    main(blocking=False)
