import subprocess
import threading
import sys, os
from time import sleep

game = 'flip'
if len(sys.argv) > 1:
    game = sys.argv[1]

def pipe(src, dst, tag=""):
    for line in src:
        dst.write(line)
        dst.flush()
        print(f"{tag}{line.strip()}", file=sys.stderr)

child_env = os.environ.copy()
child_env["TAL_m"] = "3"
child_env["TAL_n"] = "3"

# Avvia i due processi
gui = subprocess.Popen(
    [sys.executable, "game-ui.py"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
    env=child_env,
    text=True, bufsize=1
)

child_env["TAL_seed"] = "37545"
sim = subprocess.Popen(
    [sys.executable, game + "/services/play.py"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
    env=child_env,
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

sim.stdin.write("exit:\n")
sleep(1)
sim.terminate()
