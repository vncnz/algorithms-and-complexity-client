import sys, os
import json
import select
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsPolygonItem, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QPolygonF, QBrush, QColor, QPainter
from PyQt5.QtCore import QPointF, QTimer

from game_ui_common import print_now, ClickablePolygon, read_stdin_line, get_from_env

polygons = []
colors = [QColor("#666666"), QColor("#ff7799")] # , QColor("#99ff99"), QColor("#cccccc"), QColor("#ffcc77")]
scene = None

m = int(get_from_env("TAL_m", "5"))
n = int(get_from_env("TAL_n" ,"5"))

def first_draw ():
    polygon_defs = []
    for idx in range(m * n):
        sz = 30
        x = (idx % n) * sz * 2
        y = int(idx / n) * sz * 2
        polygon_defs.append((
            [(x-sz, y-sz), (x+sz, y-sz), (x+sz, y+sz), (x-sz, y+sz)],
            colors[0] # [idx % len(colors)]
        ))

    for i, (points, color) in enumerate(polygon_defs):
        poly = ClickablePolygon(i, points, color)
        scene.addItem(poly)
        polygons.append(poly)

def update_draw (data):
    for idx,v in enumerate(data):
        polygons[idx].update_color(colors[v])

def process_server_message(line):
    try:
        cmd, _, data = line.partition(':')
        if cmd == 'field':
            msg = json.loads(data)
            # print_now(f"Received: {msg}")
            update_draw(msg)
        elif cmd == 'hint':
            msg = json.loads(data)
            first_hint = msg.index(1)
            polygons[first_hint].update_color(QColor('#ffdd44'))
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

    first_draw()

    # UI buttons
    btn_exit = QPushButton("Exit")
    btn_exit.clicked.connect(lambda: print_now("exit:"))

    btn_hint = QPushButton("Hint")
    btn_hint.clicked.connect(lambda: print_now("hint:"))

    # Layout
    layout = QVBoxLayout()
    layout.addWidget(view)
    layout.addWidget(btn_exit)
    layout.addWidget(btn_hint)

    window = QWidget()
    window.setLayout(layout)
    window.setWindowTitle("Flip")
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
