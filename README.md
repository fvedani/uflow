# Energia Simulator — Flask

Simulatore margini per offerte luce e gas.
Stack: Python + Flask + SQLite (zero configurazione).

## Avvio

### 1. Installa Python
https://www.python.org/downloads/ — versione 3.10 o superiore.
Su Windows spunta "Add Python to PATH" durante l'installazione.

### 2. Installa le dipendenze
Apri il terminale nella cartella del progetto:

    pip install -r requirements.txt

### 3. Avvia

    python app.py

Apri il browser su: http://127.0.0.1:5000

Il file database.db viene creato automaticamente al primo avvio.

## Struttura
    app.py              — logica Flask, routes, calcoli, DB
    database.db         — SQLite (creato automaticamente)
    templates/
      base.html         — layout + CSS
      login.html        — login / registrazione
      offerte.html      — gestione offerte CTE
      fornitori.html    — gestione fornitori
      provvigioni.html  — gestione piani provvigionali
      simulatore.html   — simulatore margini + storico

## Export
Dal simulatore: "Esporta Excel" per simulazioni e offerte.
Per vedere il DB direttamente: https://sqlitebrowser.org/
