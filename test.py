import random

PRINT_IDX = True
rows, cols = 5,10
entry_cell = 1
exit_cell = 8

def prim_maze(rows, cols):
    # ogni cella avrà info sui muri: N, S, E, W
    maze = [{'N': True, 'S': True, 'E': True, 'W': True} for _ in range(rows * cols)]

    def neighbors(index):
        r, c = divmod(index, cols)
        result = []
        if r > 0: result.append(('N', index - cols))   # sopra
        if r < rows - 1: result.append(('S', index + cols))  # sotto
        if c > 0: result.append(('W', index - 1))      # sinistra
        if c < cols - 1: result.append(('E', index + 1))  # destra
        print(f'neighbors of {index}: {result}')
        return result

    # iniziamo da una cella casuale
    start = random.randrange(rows * cols)
    visited = {start}
    walls = []

    # aggiungiamo i muri iniziali
    for direction, n in neighbors(start):
        walls.append((start, n, direction))

    # mapping direzione opposta
    opposite = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}

    tree = {}

    while walls:
        # scegli un muro a caso
        cell, next_cell, direction = random.choice(walls)
        walls.remove((cell, next_cell, direction))

        if next_cell not in visited:
            tree[next_cell] = cell

            # rimuoviamo il muro tra cella e next_cell
            maze[cell][direction] = False
            maze[next_cell][opposite[direction]] = False

            visited.add(next_cell)
            # aggiungi i nuovi muri candidati
            for d, n in neighbors(next_cell):
                if n not in visited:
                    walls.append((next_cell, n, d))
    # print(tree)

    return maze, tree

def draw_maze_ascii(rows, cols, maze):
    """
    Disegna il labirinto in ASCII.
    - rows, cols: dimensioni
    - maze: dict {cell_index: set(direzioni_aperte)} 
      dove direzioni_aperte è un set con 'N','S','E','W'
    """
    output = ""

    # prima riga (tetto)
    output += "+" + "---+" * cols + "\n"

    for y in range(rows):
        # Riga con muri verticali
        row = "|"
        for x in range(cols):
            idx = y * cols + x
            p = idx if PRINT_IDX else ''
            if maze[idx]['E'] or ((idx+1) % cols == 0):
                row += f" {p:2}|"  # nessun muro a destra
            else:
                row += f" {p:2} "
        output += row + "\n"

        # Riga con muri orizzontali
        row = "+"
        for x in range(cols):
            idx = y * cols + x
            if maze[idx]['S']:
                row += "---+"  # nessun muro sotto
            else:
                row += "   +"
        output += row + "\n"

    return output

def build_path (start, end, tree):
    s_path = [start]
    while True:
        if s_path[-1] in tree and s_path[-1] != tree[s_path[-1]]:
            s_path.append(tree[s_path[-1]])
        else:
            break
    e_path = [end]
    while True:
        if e_path[-1] in tree and e_path[-1] != tree[e_path[-1]]:
            e_path.append(tree[e_path[-1]])
        else:
            break

    idx = -1
    while idx > -len(s_path) and idx > -len(e_path):
        if s_path[idx-1] == e_path[idx-1]:
            idx -= 1
        else:
            break
    print(idx)
    return s_path, e_path, s_path[0:idx] + [s_path[idx]] + list(reversed(e_path[0:idx]))

maze, tree = prim_maze(rows, cols)
print(tree)
for idx, cell in enumerate(maze):
    print(idx, cell)
print(draw_maze_ascii(rows, cols, maze))

s_path, e_path, solution = build_path(entry_cell, exit_cell, tree)
print('Path from start to root', s_path)
print('Path from end to root  ', e_path)
print('Path between nodes     ', solution)