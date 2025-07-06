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