#!/usr/bin/env python3
from sys import stdin, stdout, stderr
import os
import json
import random

#from functools import partial
#print_now = partial(print, flush=True)
from functools import partial
from maze_logic import prim_maze

log = print # Rewritten later in __main__
send = partial(print, flush=True)

def get_from_env (key, default, transformer=lambda x: x):
    # return os.environ.get(key, default)
    if key in os.environ:
        v = os.environ[key]
        try:
            return transformer(v)
        except:
            pass
    return default
class MazeGameStatus:
    def __init__(self, board, row, start, end, status='running'):
        self.board = board
        self.row = row
        self.status = status
        self.start = start
        self.end = end
        self.path = [start]

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__, 
            sort_keys=True,
            indent=None)
    
    def apply_move(self, idx):
        new_row = int(idx / self.row)
        new_col = idx % self.row

        old_row = int(self.path[-1] / self.row)
        old_col = self.path[-1] % self.row

        if abs(new_row - old_row) + abs(new_col - old_col) != 1:
            log("No close to head")
            return False # TODO: si aggiungerà la possibilità di troncare il path
        
        last = self.board[self.path[-1]]
        if new_row == old_row+1 and last['S']: log("wall S"); return False
        elif new_row == old_row-1 and last['N']: log("wall N"); return False
        elif new_col == old_col+1 and last['E']: log("wall E"); return False
        elif new_col == old_col-1 and last['W']: log("wall W"); return False

        # ind = [i for i, val in enumerate(a) if val == x]
        if idx in self.path:
            log('Already in path')
            end = self.path.index(idx) + 1
            self.path = self.path[0:end]
        else:
            log('Appending new idx')
            self.path.append(idx)
        return True
    
    def solved (self):
        return self.path[-1] == self.end

if __name__ == "__main__":
    flog = open(os.path.join(get_from_env("TAL_META_OUTPUT_FILES", ""), "log.txt"), "w")
    log = partial(print, file=flog, flush=True)

    log(f"TALight evaluation manager service called for problem MAZE:\n   {os.path.split(get_from_env('TAL_META_DIR', ""))[-1]}")
    errfs_list = [flog, stderr]

    m = get_from_env("TAL_r", 5, int)
    n = get_from_env("TAL_c", 5, int)
    seed = get_from_env("TAL_seed", random.randint(100000,999999), int)
    random.seed(seed)
    #if "TAL_seed" in os.environ and os.environ["TAL_seed"] != "random":
    #    seed = int(os.environ["TAL_seed"] or "")
    log(f"Seed for this call to the service: {seed}.\n{m=}, {n=}")

    board, tree = prim_maze(m, n)

    game = MazeGameStatus(board, n, start=0, end=m*n-1)
    send(f"game:{game.toJSON()}")

    log(game.toJSON())
    num_moves = 0
    still_playing = True
    while still_playing:
        log("waiting input")
        try:
            inp = input()
        except Exception as ex:
            print(ex)
        log(f"\n\n\n\ninput {inp}")
        cmd, _, i = inp.partition(':')
        if cmd == 'exit':
            log("Received exit cmd")
            break
        if cmd == 'click':
            log(f"Received click cmd with param {i}")
            
            game.apply_move(int(i))
            num_moves += 1
            log(f"Move {num_moves}: {i}")
            log(game.toJSON())
            if game.solved():
                game.status = 'win'
            
            send(f"game:{game.toJSON()}")

        elif cmd == 'hint':
            log(f'HINT CALLED m={m} n={n} board={board}')
            #solution = solve_lights_out(game.board, log)
            #if solution:
            #    send(f'hint:{flatten_grid(solution)}')
            #else:
            #    send(f'hint:')
    flog.close()
    
