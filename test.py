'''
L'idea è che possiamo definire i seguenti elementi:
A è la matrice delle mosse
b è un vettore rappresentante lo stato attuale del gioco
x è un vettore rappresentante le celle da cliccare per risolvere il gioco
Si vuole risolvere il sistema A·x = b mod 2

La dimensione della matrice A è di NxN con N=n*m
La dimensione di b è un vettore lungo n*m
La dimensione di x è un vettore lungo n*m

Com'è la matrice A? Vediamo un esempio, con una griglia 2x2 con soli 0:
0 0
0 0
La rappresentazione lineare è 0,0,0,0.
Se premiamo la cella in alto a sinistra, diventa
1 1
1 0
La rappresentazione lineare è 1,1,1,0.

Ogni riga della matrice A contiene degli 1 nelle celle che cambiano valore alla pressione della cella corrispondente a tale riga, rimanendo sull'esempio per una griglia 2x2:
1, 1, 1, 0    -> le celle che cambiano premendo quella in posizione 0
1, 1, 0, 1    -> le celle che cambiano premendo quella in posizione 1
1, 0, 1, 1    -> le celle che cambiano premendo quella in posizione 2
0, 1, 1, 1    -> le celle che cambiano premendo quella in posizione 3

Se la situazione iniziale del gioco è
1 0
0 0
Abbiamo che il vettore b è 1,0,0,0. Affiancando la matrice A di prima con questo vettore b otteniamo
1, 1, 1, 0, 1
1, 1, 0, 1, 0
1, 0, 1, 1, 0
0, 1, 1, 1, 0

'''

def build_flip_matrix(n, m):
    size = n * m
    A = [[0 for _ in range(size)] for _ in range(size)]

    def idx(i, j):
        return i * m + j

    for i in range(n):
        for j in range(m):
            index = idx(i, j)
            A[index][index] = 1  # se premi questa casella, si inverte
            for ni, nj in [(i-1,j), (i+1,j), (i,j-1), (i,j+1)]:
                if 0 <= ni < n and 0 <= nj < m:
                    A[idx(ni, nj)][index] = 1
    return A

def flatten_grid(grid):
    ''' Convert from matrix-style to list-style '''
    return [cell for row in grid for cell in row]

def unflatten_grid(vec, n, m):
    ''' Convert from list-style to matrix-style '''
    return [vec[i*m:(i+1)*m] for i in range(n)]

def gauss_mod2(A, b):
    N = len(b)
    M = [A[i][:] + [b[i]] for i in range(N)] # Ab matrix

    row = 0
    for col in range(N):
        pivot = None
        for r in range(row, N):
            if M[r][col] == 1:
                pivot = r
                break
        if pivot is None:
            continue
        if pivot != row:
            M[row], M[pivot] = M[pivot], M[row]
        for r in range(N):
            if r != row and M[r][col] == 1:
                M[r] = [(x ^ y) for x, y in zip(M[r], M[row])]
        row += 1

    # Verifica inconsistenza
    for r in range(N):
        if all(M[r][c] == 0 for c in range(N)) and M[r][N] == 1:
            return None  # sistema incompatibile

    # Soluzione particolare (non necessariamente unica)
    x = [0] * N
    for i in range(N):
        for j in range(N):
            if M[i][j] == 1:
                x[j] = M[i][N]
                break
    return x

def solve_lights_out(grid):
    n, m = len(grid), len(grid[0])
    A = build_flip_matrix(n, m)
    print(A)
    b = flatten_grid(grid)
    x = gauss_mod2(A, b)
    if x is None:
        print("Nessuna soluzione trovata.")
        return None
    return unflatten_grid(x, n, m)




def print_field (m, n, lst):
    print('Field:')
    for idx, el in enumerate(lst):
        print(f' {el} ', end='')
        if idx % n == n - 1:
            print()

def apply_move (m, n, lst, i):
    i = int(i)
    r = int(i / n)
    c = i % n

    if r > 0: lst[i-n] = 1 - lst[i-n]
    if r < m - 1: lst[i+n] = 1 - lst[i+n]
    if c > 0: lst[i-1] = 1 - lst[i-1]
    if c < m - 1: lst[i+1] = 1 - lst[i+1]

    lst[i] = 1 - lst[i]
    
    return lst


#n = 3 # numero colonne
#m = 3 # numero righe
#field = [0 for _ in range(n*m)]
#field[3] = 1

#print_field(m, n, field)
# field = apply_move(m, n, field.copy(), 8)
#print_field(m, n, field)

grid = [
    [1, 1, 1],
    [0, 1, 0],
    [0, 1, 0]
]

solution = solve_lights_out(grid)
if solution:
    print("Lights to be clicked:")
    for row in solution:
        print(row)
    # print_field(len(grid), len(grid[0]), solution)