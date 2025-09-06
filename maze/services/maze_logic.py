import random

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
        # print(f'neighbors of {index}: {result}')
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