[=== Something awesome's coming === working on this! ===]

# algorithms-and-complexity-client
Matricola VR457811 - Progetto d'esame AA 2022/2023

## Obiettivo
L'obiettivo è creare un client in js che possa gestire tanti giochi diversi tra loro [TODO finire]

## Idea di base
L'idea di base per l'implementazione è di gestire il rendering lato client principalmente tramite un elemento che consenta di visualizzare tutti gli oggetti legati al gioco ed i relativi eventi, inizialmente di tipo canvas ma poi sostituito con uno di tipo svg (vedi paragrafo dedicato).

## Canvas vs SVG

Nell progetto è stata inizialmente implementata una gestione che verteva su un elemento `<canvas>` ma è stato convertito per l'utilizzo di un elemento `<svg>`. La valutazione che ha portato a questa scelta si basa sulle caratteristiche dei giochi da implementare. Il canvas è una sorta di lavagna su cui disegnare liberamente: questo è comodo per i giochi che richiedono un framerate elevato e per effetti grafici e scene molto dinamiche. L'svg, invece, permette di avere un DOM strutturato in cui le entità grafiche sono degli oggetti del DOM, di cui è possibile manipolare le caratteristiche come posizione e dimensioni e su cui è possibile catturare gli eventi senza alcuna necessità di effettuare calcoli per comprendere se un click all'interno dell'area di disegno ricade o meno, da un punto di vista logico, all'interno di un certo oggetto. Questo calcolo, inoltre, è semplice da implementare per oggetti quadrati o circolari ma può diventare molto complesso per oggetti dalla forma irregolare. L'utilizzo di un svg permette di preservare l'oggetto grafico come entità, con i vantaggi che ne derivano, mentre il canvas è una superficie piatta su cui tutti gli oggetti grafici diventano un tutt'uno.

Ricapitolando, questi sono vantaggi e svantaggi delle due soluzioni:

Canvas (la prima soluzione implementata):\
✅ Alto framerate \
✅ Possibilità di implementare effetti grafici\
❌ Appiattimento degli oggetti durante il rendering\
❌ Individuazione manuale degli oggetti che ricevono un evento di click\
❌ Gestione complessa di un eventuale aggiornamento parziale della schermata di gioco

SVG (l'attuale soluzione implementata):\
✅ Mantenimento degli oggetti di gioco come entità\
✅ Facilità di agganciamento dei listener sui singoli elementi di gioco\
✅ Facilità di mantenimento degli oggetti che non mutano durante un aggiornamento\
❌ Minori prestazioni durante un aggiornamento dell'intero campo di gioco\
❌ Difficoltà di implementazione di effetti grafici, in particolare particellari o legati ai colori


## Stateful vs stateless

Nell'implementazione della comunicazione tra server e client si è dovuto scegliere tra due filosofie differenti, che possiamo indicare, dal punto di vista del server, con i seguenti nomi:
- Stateful
- Stateless

### Stateful

Seguendo questa filosofia, il server può tenere traccia dello stato del gioco per ogni giocatore attualmente attivo. I vantaggi di questa strategia sono principalmente due:
- Le comunicazioni tra client e server riguardano i soli cambiamenti da applicare al gioco in quando lo stato del gioco è conosciuto da entrambi in ogni momento
- I giochi possono essere multigiocatore, in quanto il server fa da coordinatore, raccoglie ed applica gli input degli utenti ad un unico stato di gioco che distribuisce a tutti i client coinvolti in una partita

Di contro, con questa filosofia si hanno i seguenti svantaggi:
- Il server deve mantenere in memoria dei dati per ciascun giocatore connesso, con conseguente occupazione di memoria
- Il server deve capire quando un giocatore interrompe la partita chiudendo il proprio browser ed implementare dei meccanismi per la liberazione della memoria da partite rimaste in sospeso
- Minore resistenza a bug di comunicazione o implementazione: client e server potrebbero divergere nell'applicazione dei cambiamenti di stato alla partita a causa di bug

### Stateless

Seguendo questa filosofia, il server non tiene traccia in alcun modo dello stato della partita. Al momento della creazione di una nuova partita esso invia al client un oggetto contenente sia gli oggetti grafici per il gioco sia eventuali informazioni legate allo stato della partita stessa. Ad ogni mossa del giocatore, il client reinvia al server lo stato completo e quest'ultimo, dopo aver applicato sullo stato appena ricevuto le logiche di gioco, reinvia al client uno stato di gioco aggiornato.

I vantaggi di questa filosofia sono i seguenti:
- Il server non ha alcuna occupazione di memoria al di fuori del momento in cui sta elaborando una risposta per un client. Non servono logiche di pulizia per eventuali partite sospese, non è necessario limitare il numero di partite contemporanee
- Server e client sono sempre ben allineati sullo stato del gioco in quanto esso viaggia avanti ed indietro in maniera completa ad ogni passaggio

Gli svantaggi sono i seguenti:
- Il client riceve uno stato di gioco che contiene anche informazioni nascoste al giocatore, giocatore che potrebbe analizzare le comunicazioni ed accedere a tali informazioni
- Maggiore payload nelle comunicazioni, in quanto non viaggiano solo gli aggiornamenti ma ogni informazione legata al gioco ed alla sua UI


## Oggetti grafici del gioco

Per quanto riguarda la rappresentazione degli oggetti del gioco, come per la scelta tra canvas e svg, il progetto è stato inizialmente implementato in un modo ma col procedere degli sviluppi si è proceduto ad un refactoring per aumentare l'elasticità della soluzione.

L'implementazione iniziale vedeva gli oggetti rappresentati tramite delle coordinate all'interno di un tavolo considerato a scacchiera: il server inviava quindi la definizione del tavolo di gioco come una coppia di valori pari al numero di righe ed al numero di colonne in cui dividere il tavolo ed ogni oggetto aveva, tra le proprie caratteristiche, una posizione definita come coppia di coordinate che rappresentassero la cella di destinazione.

Nell'implementazione corrente gli oggetti vengono descritti tramite liste di coordinate dei vertici, questo consente di avere forme irregolari se necessario.
L'eventuale testo dell'oggetto viene visualizzato al centro del rettangolo che si ottiene con la funzione `HTMLelement.getBBox()`, che restituisce un rettangolo che circoscrive l'intero poligono. Questa logica funziona bene per poligoni regolari, come quadrati o rettangoli, ma anche per poligoni irregolari che mantengono una forma convessa e con vertici che hanno distanze dal baricentro non troppo differenti. È possibile, come evolutiva, implementare un algoritmo più complesso e costruire una funzione di calcolo del baricentro della figura.
Si è comunque mantenuta la presenza delle coordinate `x` ed `y` per gli oggetti in quei giochi che hanno un tavolo di gioco a scacchiera, non ai fini del rendering ma come supporto per i calcoli di vicinanza tra le celle. Queste coordinate non sono quindi più coordinate grafiche, legate alla dimensione del tavolo di gioco in pixel, ma indici di riga e colonna.


## Posizionamento delle eventuali scritte all'interno dei poligoni

Anche qui durante lo sviluppo sono stati effettuati dei cambiamenti. Una prima versione utilizzava il centro del rettangolo contenente il poligono. Tale rettangolo può essere ottenuto dal DOM tramite la funzione `getBBox` definita per qualunque `SVGGraphicsElement`, cioé qualunque elemento facente parte di un `svg`.
Una prima miglioria è stata implementare il calcolo del centro geometrico, calcolato come la media delle coordinate di tutti i vertici. Questo metodo è semplice e veloce da applicare e funziona bene per oggetti dalla forma regolare o quasi regolare, non é però ottimale per oggetti che hanno vertici a distanze molto diverse tra loro dal centro, ad esempio in presenza di un vertice "sparato lontano" od un poligono concavo con un vertice molto vicino al centro. L'ultima evoluzione è stata quindi il calcolo del centroide, cioé il centro geometrico. Si tratta di un calcolo un poco più complesso, che tiene in considerazione anche il concetto di area e che consente di ottenere un buon posizionamento del testo anche con poligoni dalla forma molto irregolare.

# Minesweeper
## Funzionamento generale [TODO]
## Algoritmo di espansione [TODO]

# Flip
# Funzionamento generale [TODO]

# Map
## Funzionamento generale [TODO]
## Vonoroi [TODO]
### Fortune's algorithm [TODO]
### Completamento tassellamento [TODO]







# Screenshots from the games
![minesweeper lose](./screenshots/minesweeper_end.png)
![minesweeper running](./screenshots/minesweeper_running.png)
![flip lose](./screenshots/flip_running.png)
![map lose](./screenshots/map_running.png)












```

## Site where to see games
https://www.chiark.greenend.org.uk/~sgtatham/puzzles/

## TODOs
- [x] IMPL: Define a struct for json data
- [x] IMPL: load and draw json data
- [x] IMPL: method to get a clicked object
- [x] IMPL: add local events to json
- [x] GAME: Flip game
- [x] GAME: Minesweeper game
- [/] GAME: map game
- [ ] GAME: flood game

```