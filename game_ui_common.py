import sys, os
import json
import select

from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsPolygonItem, QPushButton, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtGui import QPolygonF, QBrush, QColor, QPainter
from PyQt5.QtCore import QPointF, QTimer

from functools import partial
print_now = partial(print, flush=True)
#def print_now_ (string):
#    try: print(string, flush=True)
#    except BrokenPipeError: sys.exit(32)
#    except: sys.exit(1)

def get_from_env (key, default):
    if key in os.environ:
        return os.environ[key]
    return default

class ClickablePolygon(QGraphicsPolygonItem):
    def __init__(self, id, points, color):
        super().__init__(QPolygonF([QPointF(x, y) for x, y in points]))
        self.id = id
        self.setBrush(QBrush(color))
        self.setFlag(QGraphicsPolygonItem.ItemIsSelectable, True)

    def mousePressEvent(self, event):
        # print_now(json.dumps({"type": "click", "polygon": self.id}))
        print_now(f'click:{self.id}')
        super().mousePressEvent(event)
    
    def update_color (self, color):
        self.color = color
        self.setBrush(QBrush(self.color))

def read_stdin_line(blocking):
    if blocking:
        return sys.stdin.readline()
    else:
        if select.select([sys.stdin], [], [], 0.0)[0]:
            return sys.stdin.readline()
    return None

class GameUI:
    def __init__(self):
        app = QApplication(sys.argv)
        scene = QGraphicsScene()
        view = QGraphicsView(scene)
        view.setFixedSize(400, 400)

        # Layout
        layout = QVBoxLayout()
        layout_buttons = QHBoxLayout()
        self.layout_buttons = layout_buttons

        layout.addWidget(view)
        layout.addLayout(layout_buttons)

        window = QWidget()
        window.setLayout(layout)
        window.setWindowTitle("Nim")

        self.window = window
        self.app = app
        self.scene = scene
    
    def add_buttons(self, buttons):
        for btn in buttons:
            self.layout_buttons.addWidget(btn)
    
    def show (self):
        self.window.show()
    
    def run (self):
        return self.app.exec_()
