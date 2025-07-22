import sys, os
import json
import select
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsPolygonItem, QPushButton, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtGui import QPolygonF, QBrush, QColor, QPainter
from PyQt5.QtCore import QPointF, QTimer

from game_ui_common import print_now, ClickablePolygon, read_stdin_line, get_from_env, GameUI

from ast import literal_eval
from time import sleep

polygons = []
colors = [QColor("#99cc99"), QColor("#999999")] # , QColor("#99ff99"), QColor("#cccccc"), QColor("#ffcc77")]
app = None

board = [(el, 0) for el in map(int, get_from_env("TAL_board", "3 3 3").split(' '))]
flog = open(os.path.join(get_from_env("TAL_META_OUTPUT_FILES", ""), "ui_log.txt"), "w")

def process_server_message(line):
    try:
        cmd, _, data = line.partition(':')
        if cmd == 'field':
            msg = literal_eval(data)
            # print_now(f"Received: {msg}")
            app.draw(msg)
        #elif cmd == 'hint':
        #    msg = json.loads(data)
        #    # We get the full solution from the "server" but we show only the first cell to be pressed
        #    first_hint = msg.index(1)
        #    polygons[first_hint].update_color(QColor('#ffdd44'))
    # except json.JSONDecodeError:
    #     print_now("Invalid JSON")
    except Exception as e:
        print(e)

class Nim(GameUI):
    def __init__(self):

        super().__init__()

        def exit ():
            print_now("exit:")
            sleep(.1)
            sys.exit(0)
        # UI buttons
        btn_exit = QPushButton("Exit")
        btn_exit.clicked.connect(exit)

        btn_hint = QPushButton("Hint")
        btn_hint.clicked.connect(lambda: print_now("hint:"))

        self.add_buttons([btn_exit, btn_hint])

    def draw (self, data):
        # (update_draw if len(polygons) > 0 else first_draw)(data)
        if len(polygons) > 0:
            self.update_draw(data)
        else:
            self.first_draw(data)

    def first_draw (self, data):
        polygon_defs = []
        for row, couple in enumerate(data):
            sz = 30
            in_pile, removed = couple
            # print_now(f'couple:{couple}', file=flog)
            for el in range(in_pile + removed):
                x = el * sz * 2
                y = row * sz * 2
                # print_now(f'{x},{y}', file=flog)
                polygon_defs.append((
                    [(x-sz, y-sz), (x+sz, y-sz), (x+sz, y+sz), (x-sz, y+sz)],
                    colors[0 if el < in_pile else 1],
                    f"{row}_{el}"
                ))

        for (points, color, id) in polygon_defs:
            poly = ClickablePolygon(id, points, color)
            self.scene.addItem(poly)
            polygons.append(poly)

    def update_draw (self, data):

        for row, couple in enumerate(data):
            in_pile, removed = couple
            for el in range(in_pile + removed):
                color = colors[0 if el < in_pile else 1]
                poly = next(filter(lambda x: x.id == f'{row}_{el}', polygons))
                poly.update_color(color)

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
    main(blocking=False)
