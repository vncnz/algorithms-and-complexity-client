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

    while walls:
        # scegli un muro a caso
        cell, next_cell, direction = random.choice(walls)
        walls.remove((cell, next_cell, direction))

        if next_cell not in visited:
            # rimuoviamo il muro tra cella e next_cell
            maze[cell][direction] = False
            maze[next_cell][opposite[direction]] = False

            visited.add(next_cell)
            # aggiungi i nuovi muri candidati
            for d, n in neighbors(next_cell):
                if n not in visited:
                    walls.append((next_cell, n, d))

    return maze

PRINT_IDX = True
def draw_maze_ascii(width, height, maze):
    """
    Disegna il labirinto in ASCII.
    - width, height: dimensioni
    - maze: dict {cell_index: set(direzioni_aperte)} 
      dove direzioni_aperte è un set con 'N','S','E','W'
    """
    output = ""

    # prima riga (tetto)
    output += "+" + "---+" * width + "\n"

    for y in range(height):
        # Riga con muri verticali
        row = "|"
        for x in range(width):
            idx = y * width + x
            p = idx if PRINT_IDX else ''
            if maze[idx]['E'] or ((idx+1) % width == 0):
                row += f" {p:2}|"  # nessun muro a destra
            else:
                row += f" {p:2} "
        output += row + "\n"

        # Riga con muri orizzontali
        row = "+"
        for x in range(width):
            idx = y * width + x
            if maze[idx]['S']:
                row += "---+"  # nessun muro sotto
            else:
                row += "   +"
        output += row + "\n"

    return output


w,h = 14,4
maze = prim_maze(w,h)
for idx, cell in enumerate(maze):
    print(idx, cell)
print(draw_maze_ascii(w,h, maze))
