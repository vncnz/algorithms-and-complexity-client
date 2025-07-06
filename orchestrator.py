import subprocess
import threading
import sys

def pipe(src, dst, tag=""):
    for line in src:
        dst.write(line)
        dst.flush()
        print(f"{tag}{line.strip()}", file=sys.stderr)

# Avvia i due processi
gui = subprocess.Popen(
    [sys.executable, "game-ui.py"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
    text=True, bufsize=1
)
sim = subprocess.Popen(
    [sys.executable, "flip/services/play.py"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
    text=True, bufsize=1
)

# Thread per collegare simulatore → gui
t1 = threading.Thread(target=pipe, args=(sim.stdout, gui.stdin, "[SIM→GUI] "))
# Thread per collegare gui → simulatore
t2 = threading.Thread(target=pipe, args=(gui.stdout, sim.stdin, "[GUI→SIM] "))

t1.daemon = t2.daemon = True
t1.start()
t2.start()

# attendi fino a quando uno non finisce
gui.wait()
sim.terminate()
