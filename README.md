# algorithms-and-complexity-client
Matricola VR457811 - Progetto d'esame AA 2024/2025

## Obiettivo
[TODO]

## Istruzioni per l'esecuzione

### venv

| what to do      | cmd            |
|-----------------|----------------|
|Creazione venv:  | python -m venv |
|Activate: source | ./bin/activate |


### Exec

Se si può utilizzare rtald il comando dovrebbe assomigliare a questo:

```./rtal connect flip -am=2 -an=2 -- game-ui.py```

In assenza di rtald, è possibile avviare utilizzando il file orchestrator.py:

```python orchestrator.py```

Questo script si occupa di eseguire parallelamente game-ui.py e flip/play.py agganciando in maniera incrociata i rispettivi stdin ed stdout, simulando così il funzionamento di rtald.

## Flip

### Solver / richiesta suggerimento

Una ricerca per esplorazione, ad esempio A*, è tecnicamente implementabile per questo gioco ma non è indicato. Il numero di stati possibili, infatti, è 2^N con N il numero di celle del gioco. Naturalmente, con un N molto piccolo non è un problema ma concettualmente si trova di una soluzione con complessità esponenziale e quindi altamente inefficiente.

Un approccio migliore esiste ma richiede un po' di ragionamento di tipo matematico: si tratta di risolvere il seguente sistema.
A·x = b mod 2

Vediamo i diversi elementi di questo sistema:
- A è la matrice delle mosse
- b è un vettore rappresentante lo stato attuale del gioco
- x è un vettore rappresentante le celle da cliccare per risolvere il gioco

#### Matrice A

Per capirne bene la composizione, utilizziamo un esempio ed immaginiamo una griglia 2x2 con soli 0:
0 0
0 0
La rappresentazione lineare (concatenando le diverse righe) è 0,0,0,0.

Se clicchiamo sulla cella in alto a sinistra, la matrice diventa
1 1
1 0
La rappresentazione lineare ora è 1,1,1,0.

Ogni riga della matrice A contiene degli 1 nelle celle che cambiano valore alla pressione della cella corrispondente a tale riga, rimanendo sull'esempio per una griglia 2x2:
1, 1, 1, 0    -> le celle che cambiano premendo quella in posizione 0
1, 1, 0, 1    -> le celle che cambiano premendo quella in posizione 1
1, 0, 1, 1    -> le celle che cambiano premendo quella in posizione 2
0, 1, 1, 1    -> le celle che cambiano premendo quella in posizione 3

La dimensione della matrice A è quindi NxN con N=n*m

#### Vettore b

Il vettore b rappresenta la situazione attuale del campo di gioco.

Se la situazione iniziale del gioco è
1 0
0 0
Abbiamo che il vettore b è 1,0,0,0

La dimensione di b è quindi n*m.


#### Vettore x

Il vettore x rappresenta la soluzione e conterrà degli 1 in corrispondenza delle caselle che è necessario cliccare per risolvere il gioco.
Il concetto di ordine non è presente nella soluzione perché l'ordine il cui vengono cliccate le celle durante il gioco è indifferente. Lo stato di ciascuna cella viene infatti invertito ogni volta che essa o una delle celle confinanti vengono cliccate: se il numero di tali azioni è pari la cella torna nello stato iniziale, se è dispari la cella termina nello stato opposto. Questo spiega anche il ```mod 2``` visibile nella formula.
La dimensione di x è quindi n*m.

#### A·x

Completando l'esempio, affiancando la matrice A con il vettore b otteniamo
1, 1, 1, 0, 1
1, 1, 0, 1, 0
1, 0, 1, 1, 0
0, 1, 1, 1, 0

#### Risoluzione

