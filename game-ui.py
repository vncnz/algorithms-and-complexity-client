import sys
import json
import select
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsPolygonItem
from PyQt5.QtGui import QPolygonF, QBrush, QColor, QPainter
from PyQt5.QtCore import QPointF, QTimer

from game_ui_common import print_now, ClickablePolygon, read_stdin_line

polygons = []
colors = [QColor("#ff9999"), QColor("#99ccff")] # , QColor("#99ff99"), QColor("#cccccc"), QColor("#ffcc77")]

def process_input(line):
    try:
        msg = json.loads(line)
        # print_now(f"Received: {msg}")
        for idx,v in enumerate(msg):
            polygons[idx].update_color(colors[v])
        # Esempio: potresti modificare un poligono in base al messaggio
    # except json.JSONDecodeError:
    #     print_now("Invalid JSON")
    except Exception as e:
        print(e)

def main(blocking=True):
    app = QApplication(sys.argv)
    scene = QGraphicsScene()

    #polygons = [
        #[(50, 50), (150, 60), (120, 150), (60, 140)],
        #[(200, 80), (300, 100), (280, 180), (210, 160)],
        #[(100, 200), (180, 220), (160, 300), (90, 280)],
        #[(250, 250), (320, 270), (310, 340), (260, 320)]
    #]

    polygon_defs = []
    for idx in range(16):
        sz = 30
        x = (idx % 4) * sz * 2
        y = int(idx / 4) * sz * 2
        polygon_defs.append((
            [(x-sz, y-sz), (x+sz, y-sz), (x+sz, y+sz), (x-sz, y+sz)],
            colors[0] # [idx % len(colors)]
        ))

    for i, (points, color) in enumerate(polygon_defs):
        poly = ClickablePolygon(i, points, color)
        scene.addItem(poly)
        polygons.append(poly)

    view = QGraphicsView(scene)
    # view.setRenderHint(view.renderHints() | view.renderHints().Antialiasing)
    view.setRenderHint(QPainter.Antialiasing)
    view.setWindowTitle("Polygons with Click Events")
    view.resize(400, 400)
    view.show()

    # Timer per controllo stdin periodico
    timer = QTimer()
    timer.timeout.connect(lambda: (
        (line := read_stdin_line(blocking)) and process_input(line)
    ))
    timer.start(100)  # ogni 100ms

    sys.exit(app.exec_())

if __name__ == "__main__":
    main(blocking=False)
