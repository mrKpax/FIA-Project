# FIA-Project
# **ALAN: AI per il Blackjack**
Progetto per il corso di Fondamenti di Intelligenza Artificiale che implementa un agente intelligente in grado di apprendere e giocare al blackjack. ALAN utilizza tecniche di Reinforcement Learning per migliorare le proprie performance basandosi su esperienze di gioco e dati simulati.

---

## **Introduzione**
ALAN è un agente basato su Q-Learning che si distingue per la capacità di apprendere strategie ottimali per il blackjack. Grazie a un approccio data-driven e self-driven, l'agente è in grado di:
- Imparare a giocare da zero.
- Migliorarsi attraverso simulazioni e dataset di training.
- Ottimizzare le decisioni in un ambiente stocastico e parzialmente osservabile.

---

## **Tecnologie Utilizzate**
- **Linguaggio**: Python
- **Librerie principali**:
  - `pygame` per la GUI.
  - `pandas` per la gestione dei dataset.
  - `random` per la generazione di carte e scelte casuali.
  - `collections` per la gestione delle strutture dati (Replay Buffer).
- **Strumenti**:
  - Dataset simulati con la strategia ottima di base.
  - Grafici di performance tramite Matplotlib.

---

## **Come Utilizzare il Progetto**
1. **Requisiti**:
   - Python 3.8+.
   - Ambiente virtuale configurato con le dipendenze necessarie.
       - Possibile crearlo con `python3 -m venv myenv`.
       - Attivabile tramite `source myenv/bin/activate`.
       - Librerie installabili tramite `pip install -r pygame pandas`.

2. **Esecuzione**:
   - Per avviare il gioco manuale:
     ```bash
     python3 blackjack.py
     ```
     Poi selezionare la modalità di gioco manuale cliccando il pulsante "Start" tramite la GUI.
     
   - Per avviare il gioco controllato dall'AI:
     ```bash
     python3 main.py --mode ai
     ```
     Poi selezionare la modalità di gioco controllata dall'AI cliccando il pulsante "AI Play" tramite la GUI.

3. **Dataset**:
   - Il dataset di training si trova in `data/game_log.csv`.
   - Per generare nuovi dataset:
     ```bash
     python benchmark.py
     ```

---

## **Struttura del Codice**
- **`blackjack.py`**: Punto di ingresso del programma, implementa la logica del gioco, gestione dello stato e GUI.
- **`agent.py`**: Implementazione dell'agente RL.
- **`benchmark.py`**: Generazione del dataset con la strategia ottima di base.
- **`benchmark_bj.py`**: Implementa la logica del gioco, ne usufruisce il benchmark.
- **`game_log.csv`**: Contiene il dataset CSV per il training.

---

## **Algoritmo di Apprendimento**
ALAN utilizza il Q-Learning con Replay Buffer e Decaying Epsilon. I principali parametri sono:
- **Alpha (tasso di apprendimento)**: `0.1`
- **Gamma (fattore di sconto)**: `0.95`
- **Epsilon iniziale**: `1.0`
- **Epsilon minimo**: `0.01`
- **Epsilon decay**: `0.995`

L'agente impara a ottimizzare le decisioni (`Hit` o `Stand`) attraverso simulazioni ripetute, affinando i valori nella Q-Table.

---

## **Prestazioni**
### **Strategia Ottima di Base**
- Win Rate: ~43%
- Pareggi: ~8%
- Sconfitte: ~49%

### **Agente Self-Driven**
- Dopo 10.000 partite:
  - Win Rate: ~41%
  - Pareggi: ~6%
  - Sconfitte: ~53%

### **Agente Data-Driven**
- Win Rate dopo 10.000 partite: ~42%.
- Convergenza rapida grazie al training iniziale sul dataset.

---

## **Autore**
Francesco Passiatore - [GitHub Repository](https://github.com/mrKpax/FIA-Project)
