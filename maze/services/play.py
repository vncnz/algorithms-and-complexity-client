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

def state_as_str(board):
    return "\n".join(map(lambda row: " ".join(map(str, row)), board))

# def state_as_arr (m, n, board):
#     return [el for row in board for el in row]

def solved(m,n, board, tab=0):
    for i in range(m):
        for j in range(n):
            if board[i][j] != 0:
                return False
    return True

def apply_move (r, c, board):
    for rr in {r-1,r,r+1}:
        if 0 <= rr < m:
            board[rr][c] = 1 - board[rr][c]
    for cc in {c-1,c+1}:
        if 0 <= cc < n:
            board[r][cc] = 1 - board[r][cc]

class MazeGameStatus:
    def __init__(self, board, row, status='running'):
        self.board = board
        self.row = row
        self.status = status

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__, 
            sort_keys=True,
            indent=None)

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

    game = MazeGameStatus(board, n)
    send(f"game:{game.toJSON()}")

    log(state_as_str(board))
    num_moves = 0
    still_playing = True
    while still_playing:
        log("waiting input")
        try:
            inp = input()
        except Exception as ex:
            print(ex)
        log(f"input {inp}")
        cmd, _, i = inp.partition(':')
        if cmd == 'exit':
            log("Received exit cmd")
            break
        if cmd == 'click':
            log(f"Received click cmd with param {i}")

            row,col = map(int, i.split('_'))
            
            num_moves += 1
            apply_move(row, col, game.board)

            log(f"\n\n\n\nMove {num_moves}: {row} {col}")
            log(state_as_str(board))
            if solved(m,n, game.board):
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
    
