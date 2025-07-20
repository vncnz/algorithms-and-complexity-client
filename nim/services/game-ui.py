import sys, os
import json
import select
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsPolygonItem, QPushButton, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtGui import QPolygonF, QBrush, QColor, QPainter
from PyQt5.QtCore import QPointF, QTimer

from game_ui_common import print_now, ClickablePolygon, read_stdin_line, get_from_env

polygons = []
colors = [QColor("#99cc99"), QColor("#999999")] # , QColor("#99ff99"), QColor("#cccccc"), QColor("#ffcc77")]
scene = None

board = map(int, get_from_env("TAL_board", "3 3 3").split(' '))
flog = open(os.path.join(get_from_env("TAL_META_OUTPUT_FILES", ""), "ui_log.txt"), "w")

def first_draw ():
    polygon_defs = []
    for (idx, row) in enumerate(board):
        sz = 30
        print_now(f'row:{row} idx:{idx}', file=flog)
        for el in range(row):
            x = el * sz * 2
            y = idx * sz * 2
            print_now(f'{x},{y}', file=flog)
            polygon_defs.append((
                [(x-sz, y-sz), (x+sz, y-sz), (x+sz, y+sz), (x-sz, y+sz)],
                colors[0] # [idx % len(colors)]
            ))

    for i, (points, color) in enumerate(polygon_defs):
        poly = ClickablePolygon(i, points, color)
        scene.addItem(poly)
        polygons.append(poly)

#! To be changed
def update_draw (data):
    for idx,v in enumerate(data):
        polygons[idx].update_color(colors[v])

#! To be changed
def process_server_message(line):
    try:
        cmd, _, data = line.partition(':')
        if cmd == 'field':
            msg = json.loads(data)
            # print_now(f"Received: {msg}")
            update_draw(msg)
        #elif cmd == 'hint':
        #    msg = json.loads(data)
        #    # We get the full solution from the "server" but we show only the first cell to be pressed
        #    first_hint = msg.index(1)
        #    polygons[first_hint].update_color(QColor('#ffdd44'))
    # except json.JSONDecodeError:
    #     print_now("Invalid JSON")
    except Exception as e:
        print(e)

def main(blocking=True):
    global scene
    app = QApplication(sys.argv)
    scene = QGraphicsScene()
    view = QGraphicsView(scene)
    view.setFixedSize(400, 400)

    first_draw()

    # UI buttons
    btn_exit = QPushButton("Exit")
    btn_exit.clicked.connect(lambda: print_now("exit:"))

    btn_hint = QPushButton("Hint")
    btn_hint.clicked.connect(lambda: print_now("hint:"))

    # Layout
    layout = QVBoxLayout()
    layout_buttons = QHBoxLayout()
    layout_buttons.addWidget(btn_exit)
    layout_buttons.addWidget(btn_hint)

    layout.addWidget(view)
    layout.addLayout(layout_buttons)

    window = QWidget()
    window.setLayout(layout)
    window.setWindowTitle("Nim")
    window.show()

    # Timer for checking stdin
    timer = QTimer()
    timer.timeout.connect(lambda: (
        (line := read_stdin_line(blocking)) and process_server_message(line)
    ))
    timer.start(100) # ms

    sys.exit(app.exec_())

if __name__ == "__main__":
    main(blocking=False)
