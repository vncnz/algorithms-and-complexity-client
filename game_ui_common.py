import sys, os
import json
import select

from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsPolygonItem, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel
from PyQt5.QtGui import QPolygonF, QBrush, QColor, QPainter
from PyQt5.QtCore import QPointF, QTimer, Qt, QEvent, QObject

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
    def __init__(self, id, points, color, onclick):
        super().__init__(QPolygonF([QPointF(x, y) for x, y in points]))
        self.id = id
        self.setBrush(QBrush(color))
        self.setFlag(QGraphicsPolygonItem.ItemIsSelectable, True)
        self.onclick = onclick

    def mousePressEvent(self, event):
        # print_now(json.dumps({"type": "click", "polygon": self.id}))
        self.onclick(self.id)
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

class KeyFilter(QObject):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            self.callback(event)
            return True  # consumato
        return False

class GameUI:
    def __init__(self, gamename, width=400, height=400):
        app = QApplication(sys.argv)
        scene = QGraphicsScene()
        view = QGraphicsView(scene)
        label = QLabel()
        self.drawWidth = width
        self.drawHeight = height
        view.setFixedSize(self.drawWidth, self.drawHeight)

        # Layout
        layout = QVBoxLayout()
        layout_buttons = QHBoxLayout()
        self.layout_buttons = layout_buttons

        layout.addWidget(view)
        layout.addWidget(label)
        layout.addLayout(layout_buttons)

        window = QWidget()
        window.setLayout(layout)
        window.setWindowTitle(gamename)
        window.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.window = window
        self.app = app
        self.scene = scene
        self.label = label

        # self.keyFilter = KeyFilter(lambda e: print("Key pressed:", e.key()))
        # self.app.installEventFilter(self.keyFilter)
    
    def setOnKeyEvent (self, onKeyEvent):
        # self.window.keyPressEvent = onKeyEvent
        self.keyFilter = KeyFilter(onKeyEvent)
        self.app.installEventFilter(self.keyFilter)
    
    def setOnClose(self, onClose):
        def handler(event):
            try: onClose()
            except: pass
            event.accept()
        self.window.closeEvent = handler
    
    def add_buttons (self, buttons):
        for btn in buttons:
            self.layout_buttons.addWidget(btn)
    
    def update_label (self, txt):
        self.label.setText(txt)
    
    def show (self):
        self.window.show()
    
    def run (self):
        return self.app.exec_()
