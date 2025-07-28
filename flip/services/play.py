#!/usr/bin/env python3
from sys import stdin, stdout, stderr
import os
import json
import random

# from utilities import download_files
from flip_solver import solve_lights_out, unflatten_grid, flatten_grid

#from functools import partial
#print_now = partial(print, flush=True)
from functools import partial

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

def random_gen(m,n):
    board = [ [0 for __ in range(n)] for _ in range(m) ]
    # for i in range(m):
    #     for j in range(n):
    #        board[i].append(random.randrange(2))
    for _ in range(int(n * m / 2)):
        i = random.randrange(n*m)
        r = int(i / n)
        c = i % n
        apply_move(r, c, board)
    return board

def state_as_str(m,n, board, tab_cols=0,tab_rows=0):
    ans = "\n" * tab_rows
    ans += f"{m} {n}"
    for i in range(m):
        ans += "\n" + " "*tab_cols + " ".join(map(str, board[i]))
    return ans

def state_as_arr (m, n, board):
    return [el for row in board for el in row]

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

class FlipGameStatus:
    def __init__(self, board, row, currentPlayer=None, status='running'):
        self.board = board
        self.row = row
        self.currentPlayer = currentPlayer
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

    log(f"TALight evaluation manager service called for problem FLIP:\n   {os.path.split(get_from_env('TAL_META_DIR', ""))[-1]}")
    errfs_list = [flog, stderr]

    m = get_from_env("TAL_m", 5, int)
    n = get_from_env("TAL_n", 5, int)
    seed = get_from_env("TAL_seed", random.randint(100000,999999), int)
    random.seed(seed)
    #if "TAL_seed" in os.environ and os.environ["TAL_seed"] != "random":
    #    seed = int(os.environ["TAL_seed"] or "")
    log(f"Seed for this call to the service: {seed}.\n{m=}, {n=}")

    board = random_gen(m,n)

    game = FlipGameStatus(board, n)
    send(f"game:{game.toJSON()}")

    log(state_as_str(m,n, board, tab_cols=3, tab_rows=1))
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
            # i = int(i) # map(int, input().strip().split())
            # r = int(i / n)
            # c = i % n
            # if i == -1:
            #     still_playing = False
            #     continue
            # other special requests ...

            row,col = map(int, i.split('_'))
            
            num_moves += 1
            apply_move(row, col, game.board)

            log(f"\n\n\n\nMove {num_moves}: {row} {col}")
            log(state_as_str(m,n, board, tab_cols=3, tab_rows=1))
            if solved(m,n, game.board):
                # still_playing = False
                # continue
                game.status = 'win'
            
            send(f"game:{game.toJSON()}")

        elif cmd == 'hint':
            log(f'HINT CALLED m={m} n={n} board={board}')
            # unflatten = unflatten_grid(board, n, m)
            # log(f'unflatten:{unflatten} m={m} n={n}')
            solution = solve_lights_out(game.board)
            if solution:
                send(f'hint:{flatten_grid(solution)}')
            else:
                send(f'hint:')
    flog.close()
    
