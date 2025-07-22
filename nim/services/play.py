#!/usr/bin/env python3
from sys import stdin, stdout, stderr
import os
from time import sleep
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

def game_is_ended(board):
    for in_pile, _ in board:
        if in_pile > 0:
            return False
    return True

# def apply_move_OLD (i, board):
#     half = int(len(board) / 2)
#     cursor = 0
#     for el in range(half):
#         next = cursor + board[el]
#         log(f"el:{el} i:{i} cursor:{cursor} next:{next} board:{board} - cycle 1")
#         if next > i:
#             # We are on the right element
#             log(f"el:{el} i:{i} cursor:{cursor} next:{next} board:{board} - return board")
#             new_v = i - cursor
#             old_v = board[el]
#             board[el] = new_v
#             board[el + half] += (old_v - new_v)
#             log(f"board to be returned: {board}")
#             return board
#         else:
#             cursor = next
#             next = cursor + board[el + half]
#             log(f"el:{el} i:{i} cursor:{cursor} next:{next} board:{board} - cycle 2")
#             if next > i:
#                 log(f"el:{el} i:{i} cursor:{cursor} next:{next} board:{board} - return False")
#                 return False
#     log(f"i:{i} cursor:{cursor} next:{next} board:{board} - end of function")

# Exists two variants of the game:
# - standard: winner-takes-last
# - misère: loser-takes-last

MISERE_MODE = False
def compute_move (board):
    game_sum = 0
    for in_pile, _ in board:
        game_sum = game_sum ^ in_pile
    
    if MISERE_MODE:
        non_trivial = len(filter(lambda pile: pile[0] > 1, board))
        if non_trivial <= 1:
            ones = len(filter(lambda pile: pile[0] == 1, board))
            if ones % 2 == 0:
                # Leave odd number of 1s, opponent is forced to lose
                for idx, (count, _) in enumerate(board):
                    if count > 1:
                        return idx, count
            else:
                # Leave even number of 1s
                for idx, (count, _) in enumerate(board):
                    if count == 1:
                        return idx, 1
    
    if game_sum != 0: # find pile to reduce, we are in a good position
        for row, (in_pile, _) in enumerate(board):
            target = in_pile ^ game_sum
            if target < in_pile:
                # to_remove = in_pile - target
                # return (row, to_remove)
                return (row, target)
    else: # reduce the longest pile, we are in a losing position
        row = min(range(len(board)), lambda x: board[x])
        # return (row, 1)
        return (row, board[row][0] - 1)

def apply_move (row, el, board):
    in_pile, removed = board[row]

    if el >= in_pile:
        log(f"i:{i} board:{board} - return False (invalid move)")
        return False


    log(f"i:{i} board:{board} - (pre-move)")
    full_pile = in_pile + removed
    new_couple = (el, full_pile - el)
    board[row] = new_couple
    log(f"i:{i} board:{board} - (post-move)")
    return board

if __name__ == "__main__":
    flog = open(os.path.join(get_from_env("TAL_META_OUTPUT_FILES", ""), "log.txt"), "w")

    log = partial(print, file=flog, flush=True)

    log(f"TALight evaluation manager service called for problem:\n   {os.path.split(get_from_env('TAL_META_DIR', ""))[-1]}")

    # board = list(map(int, get_from_env("TAL_board", "3 3 3").split(' ')))
    # board += [0 for _ in board]
    board = [(el, 0) for el in map(int, get_from_env("TAL_board", "3 3 3").split(' '))]

    log(board)
    send(f'field:{board}')
    num_moves = 0
    still_playing = True
    # player = 1
    while still_playing:
        log("waiting input")
        try:
            inp = input()
        except Exception as ex:
            print(ex, file=stderr)
        log(f"input {inp}")
        cmd, _, i = inp.partition(':')
        if cmd == 'exit':
            log("Received exit cmd")
            break
        if cmd == 'click':
            log(f"Received click cmd with param {i}")
            if i == '-1':
                still_playing = False
                continue
            # other special requests ...

            row,el = map(int, i.split('_'))
            new_board = apply_move(row, el, board)
            if new_board:
                board = new_board
                send(f'field:{board}')
            
            # Example for "async" reply
            sleep(2)
            # new_board = apply_move("2_1", board)
            suggested_move = compute_move(board)
            if suggested_move:
                row,idx = suggested_move
                new_board = apply_move(row, idx, board)
                board = new_board
                send(f'field:{board}')

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
    
