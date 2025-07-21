#!/usr/bin/env python3
from sys import stdin, stdout, stderr
import os
import random

# from utilities import download_files
from flip_solver import solve_lights_out, unflatten_grid, flatten_grid

log = print



def get_from_env (key, default, transformer=lambda x: x):
    # return os.environ.get(key, default)
    if key in os.environ:
        v = os.environ[key]
        try:
            return transformer(v)
        except:
            pass
    return default

def state_as_str(m,n, field, tab_cols=0,tab_rows=0):
    ans = "\n" * tab_rows
    ans += f"{m} {n}"
    for i in range(m):
        ans += "\n" + " "*tab_cols + " ".join(map(str, field[i]))
    return ans

def state_as_arr (m, n, field):
    return [el for row in field for el in row]

def solved(m,n, field, tab=0):
    for i in range(m):
        for j in range(n):
            if field[i][j] != 0:
                return False
    return True

def apply_move (i, board):
    half = int(len(board) / 2)
    cursor = 0
    for el in range(half):
        next = cursor + board[el]
        log(f"el:{el} i:{i} cursor:{cursor} next:{next} board:{board} - cycle 1")
        if next > i:
            # We are on the right element
            log(f"el:{el} i:{i} cursor:{cursor} next:{next} board:{board} - return board")
            new_v = i - cursor
            old_v = board[el]
            board[el] = new_v
            board[el + half] += (old_v - new_v)
            log(f"board to be returned: {board}")
            return board
        else:
            cursor = next
            next = cursor + board[el + half]
            log(f"el:{el} i:{i} cursor:{cursor} next:{next} board:{board} - cycle 2")
            if next > i:
                log(f"el:{el} i:{i} cursor:{cursor} next:{next} board:{board} - return False")
                return False
    log(f"i:{i} cursor:{cursor} next:{next} board:{board} - end of function")
        


if __name__ == "__main__":
    flog = open(os.path.join(get_from_env("TAL_META_OUTPUT_FILES", ""), "log.txt"), "w")

    from functools import partial
    log = partial(print, file=flog, flush=True)

    log(f"TALight evaluation manager service called for problem:\n   {os.path.split(get_from_env('TAL_META_DIR', ""))[-1]}")
    errfs_list = [flog, stderr]

    board = list(map(int, get_from_env("TAL_board", "3 3 3").split(' ')))
    board += [0 for _ in board]

    log(board)
    print(f'field:{board}')
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
            i = int(i) # map(int, input().strip().split())
            if i == -1:
                still_playing = False
                continue
            # other special requests ...

            new_board = apply_move(i, board)
            print(f'field:{new_board}')

            #print(f"\n\n\n\nMove {num_moves}: {r} {c}", file=flog)
            #print(state_as_str(m,n, field, tab_cols=3, tab_rows=1), file=flog)
            #if solved(m,n, field):
            #    still_playing = False
            #    continue
        elif cmd == 'hint':
            log(f'HINT CALLED field={board}')
            #solution = solve_lights_out(field)
            #if solution:
            #    print(f'hint:{flatten_grid(solution)}')
            #else:
            #    print(f'hint:')
    flog.close()
    
