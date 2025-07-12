#!/usr/bin/env python3
from sys import stdin, stdout, stderr
import os
import random

# from utilities import download_files
from flip_solver import solve_lights_out, unflatten_grid, flatten_grid

#from functools import partial
#print_now = partial(print, flush=True)



def get_from_env (key, default):
    if key in os.environ:
        return os.environ[key]
    return default

def random_gen(m,n):
    field = [ [0 for __ in range(n)] for _ in range(m) ]
    # for i in range(m):
    #     for j in range(n):
    #        field[i].append(random.randrange(2))
    for _ in range(int(n * m / 2)):
        i = random.randrange(n*m)
        r = int(i / n)
        c = i % n
        apply_move(r, c, field)
    return field

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

def apply_move (r, c, field):
    for rr in {r-1,r,r+1}:
        if 0 <= rr < m:
            field[rr][c] = 1 - field[rr][c]
    for cc in {c-1,c+1}:
        if 0 <= cc < n:
            field[r][cc] = 1 - field[r][cc]


if __name__ == "__main__":
    flog = open(os.path.join(get_from_env("TAL_META_OUTPUT_FILES", ""), "log.txt"), "w")
    print(f"TALight evaluation manager service called for problem:\n   {os.path.split(get_from_env('TAL_META_DIR', ""))[-1]}", file=flog)
    errfs_list = [flog, stderr]

    m = int(get_from_env("TAL_m", "5"))
    n = int(get_from_env("TAL_n", "5"))
    seed_str = get_from_env("TAL_seed", "")
    seed = int(seed_str) if seed_str else random.randint(100000,999999)
    random.seed(seed)
    #if "TAL_seed" in os.environ and os.environ["TAL_seed"] != "random":
    #    seed = int(os.environ["TAL_seed"] or "")
    print(f"Seed for this call to the service: {seed}.\n{m=}, {n=}", file=flog)
    field = random_gen(m,n)
    print(state_as_str(m,n, field, tab_cols=3, tab_rows=1), file=flog)
    print(f'field:{state_as_arr(m,n, field)}')
    num_moves = 0
    still_playing = True
    while still_playing:
        print("waiting input", file=flog)
        try:
            inp = input()
        except Exception as ex:
            print(ex)
        print(f"input {inp}", file=flog)
        cmd, _, i = inp.partition(':')
        if cmd == 'exit':
            print("Received exit cmd", file=flog)
            break
        if cmd == 'click':
            print(f"Received click cmd with param {i}", file=flog)
            i = int(i) # map(int, input().strip().split())
            r = int(i / n)
            c = i % n
            if i == -1:
                still_playing = False
                continue
            # other special requests ...
            
            num_moves += 1
            apply_move(r, c, field)
            
            print(f'field:{state_as_arr(m,n, field)}')

            print(f"\n\n\n\nMove {num_moves}: {r} {c}", file=flog)
            print(state_as_str(m,n, field, tab_cols=3, tab_rows=1), file=flog)
            if solved(m,n, field):
                still_playing = False
                continue
        elif cmd == 'hint':
            print(f'HINT CALLED m={m} n={n} field={field}', file=flog)
            # unflatten = unflatten_grid(field, n, m)
            # print(f'unflatten:{unflatten} m={m} n={n}', file=flog)
            solution = solve_lights_out(field)
            if solution:
                print(f'hint:{flatten_grid(solution)}')
            else:
                print(f'hint:')
    flog.close()
    
