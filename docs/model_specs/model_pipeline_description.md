# Jump Trading Probability Cup – Pipeline Overview

Questo file fornisce una panoramica del modello che abbiamo implementato per stimare le probabilità negli incontri della Probability Cup. Non contiene codice eseguibile, ma descrive la logica e le principali fasi della pipeline utilizzata per produrre le percentuali mostrate nei report (ad esempio per Turchia–Paraguay o Brasile–Haiti).

## 1. Classificazione delle domande

Ogni domanda del contest è etichettata in una delle seguenti categorie, perché le statistiche rilevanti e le distribuzioni da usare variano a seconda del tipo di evento:

- **Match outcome / Goals** – es. “Vittoria Turchia”, “Totale gol ≤ 2”.
- **Team stats** – es. “Più falli”, “Più cartellini”, “Fuorigioco ≥ 2”.
- **Player props** – es. “Enciso 1+ tiro in porta”.
- **Rare events** – es. “Rigore o rosso”.
- **Second‑half props** – es. “Più tiri in porta nel 2° tempo”, “Corner 2° tempo”.

L’identificazione consente di applicare la distribuzione statistica più adeguata (Poisson, Negative Binomial, ecc.) e di calibrare la stima in modo coerente.

## 2. Base rate e mercato

Per ogni categoria si ricava un **base rate**: la frequenza con cui l’evento si verifica in generale (ad esempio ~30 % di rigori/espulsioni per partita). Quando esistono **quote di mercato** credibili (1X2, over/under), se ne deduce la probabilità implicita come “ancora” di riferimento. In assenza di quote, il base rate resta l’ancora.

## 3. Modello statistico

Il cuore della pipeline sono modelli probabilistici tarati sui dati disponibili:

- **Match outcome / goals** – Modellati tramite distribuzioni di Poisson (o Dixon‑Coles quando possibile) sui goal attesi delle squadre. Le lambda sono stimate a partire dagli xG medi e da eventuali correzioni per forza attacco/difesa.
- **Team stats** – Per falli, cartellini, corner e tiri/offside si usa una **Negative Binomial**. Questa distribuzione gestisce la varianza spesso superiore alla media. I parametri μ sono calcolati combinando le medie di squadra, la differenza di forza, la strategia tattica e l’arbitro.
- **Player props** – Le probabilità di “1+ tiro in porta” sono calcolate con un **Poisson** basato su (minuti previsti/90) × (tiri per 90) × (percentuale di tiri nello specchio), aggiustato per ruolo e difficoltà dell’avversario.
- **Rare events** – Eventi come rigore o rosso sono derivati da un modello di base‑rate con aggiustamenti per l’arbitro (se severo), lo stile di gioco e l’importanza della partita. Viene usata una combinazione di base rate e regressione logistica.
- **Second‑half props** – Si usa ancora una Negative Binomial, ma con dispersione più alta per riflettere la maggiore varianza dovuta allo stato del match.

## 4. Aggiustamenti contestuali

Le stime grezze vengono modificate in base a:

- **Line‑up previste** – Presenza o meno di titolari chiave, moduli tattici e minutaggi attesi.
- **Arbitro** – Numero medio di cartellini e rigori concessi.
- **Importanza della partita** – Necessità di vittoria, match da dentro/fuori, potenziale gestione del risultato.
- **Meteo/condizioni** – Quando disponibili, elementi come vento o pioggia possono influenzare il numero di corner o tiri.

## 5. Stima del bias del field

Poiché la classifica del contest dipende dal **Brier score relativo** (la differenza tra il proprio errore e la media del field), stimiamo come la massa di partecipanti potrebbe sovra‑ o sottovalutare certi mercati. Ad esempio, i partecipanti tendono a sovrastimare la probabilità di rigori e rossi o a sottostimare i falli delle squadre sfavorite. Le nostre previsioni sono leggermente spostate per sfruttare questi bias.

## 6. Calibrazione e shrinkage

Per evitare over‑confidence (che penalizza fortemente nel Brier score) applichiamo uno **shrinkage**: la probabilità grezza viene compressa verso l’ancora (base rate o mercato) in funzione della qualità dei dati (evidence score). Se l’evidenza è forte (più fonti concordi, dati solidi), la compressione è minima; se i dati sono scarsi o la varianza dell’evento è alta, la compressione aumenta.

## 7. Red team e rischio correlato

Prima di fissare la probabilità definitiva, la pipeline prevede un controllo “red team” che si interroga su cosa potrebbe invalidare la previsione: infortuni dell’ultimo minuto, risultati parziali (1‑0 veloce) che alterano corner e falli, condizioni meteo, ecc. Inoltre si osservano le correlazioni: se si scommette contemporaneamente su “più corner” e “più tiri nel secondo tempo” per la stessa squadra, si riconosce che le due props dipendono dallo stesso copione di gara e si evita di spingere entrambe agli estremi.

## 8. Produzione della probabilità finale

Le componenti precedenti (modello, base rate, mercato, contesto, bias e shrinkage) vengono combinate in una media pesata. Il risultato è la percentuale da inviare alla piattaforma del contest. Le stime sono calibrate per essere competitive (più vicine alla verità del field) ma senza rischiare penalizzazioni eccessive in caso di eventi rari.

## Utilizzo del modello

Questa pipeline è stata usata per generare le percentuali riportate nei nostri report, come quello per Turchia–Paraguay. Ogni riga di quel report deriva da una combinazione di dati reali (tiri, falli, xG, line‑up) e di una valutazione contestuale. Le soglie (es. 46 % per Enciso 1+ tiro in porta) non sono fisse ma cambiano in base ai parametri di input.

Per condividere questa spiegazione con un’altra persona (ad esempio Claude), puoi scaricare questo file e allegarlo alla conversazione. Se desideri avere anche gli script completi della pipeline (come Python o workbook), dovrai recuperare l’archivio ZIP generato nella sessione precedente o chiederne la rigenerazione.
