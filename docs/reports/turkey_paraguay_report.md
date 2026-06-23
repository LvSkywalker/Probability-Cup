# Probabilità Cup – Analisi Turchia vs. Paraguay (World Cup 2026)

## Contesto e formazioni previste

- **Formazioni attese** (ESPN): la Turchia dovrebbe giocare con un 4‑2‑3‑1 composto da Çakir; Kadioglu, Bardakci, Demiral, Çelik; Çalhanoğlu, Yüksek; Barış Alper Yılmaz, Kökçü, Güler; Aktürkoğlu【927339720943185†L248-L261】.  
  Il Paraguay dovrebbe schierare un 4‑4‑2 con Gil; Alonso, Alderete, Gustavo Gómez, Cáceres; Almirón, Bobadilla, Cubas, Diego Gómez; Sanabria e Julio Enciso in attacco【927339720943185†L263-L271】.  
  L’arbitro designato è **Iván Barton**【927339720943185†L248-L252】, noto per la media di oltre cinque cartellini gialli a partita e qualche rosso (65 gialli e 2 espulsioni in 13 gare valutate in precedenza)【54766179793289†L130-L135】.

- **Statistiche di squadra**:

  | Squadra | Tiri totali/match | Tiri in porta/match | XG (Fatti – Concessi) | Fuorigioco/match | Falli commessi | Falli subiti | Note |
  |---|---:|---:|---:|---:|---:|---:|---|
  | **Turchia** | 16.4 | 5.1 | 1.81 – 1.24 | 2.2 (over 1.5 in 70 % dei match) | 9.3 | 11.3 | segna 2.2 g/match, subisce 1.3 g/match; conversione 13 %【839017757575117†L3128-L3167】【839017757575117†L1556-L1584】 |
  | **Paraguay** | 10.7 | 4.7 | 1.22 – 1.15 | 1.56 (over 1.5 in 78 %) | 12.78 | 11.67 | segna 1.3 g/match, subisce 1.3 g/match; conversione 12 %【2851657761723†L3090-L3149】【2851657761723†L1564-L1583】 |

- **Statistiche giocatori chiave**:

  - **Julio Enciso** (Paraguay) effettua 2.9 tiri/90’ e il 36 % dei suoi tiri è in porta; equivale a circa 1.05 tiri in porta per 90’【530814297521421†L2007-L2010】.  
  - **Orkun Kökçü** (Turchia) tenta 3.19 tiri/90’ con precisione del 36.36 %, per ~1.16 tiri in porta/90’【159551795661340†L2082-L2084】. Gioca però da trequartista, quindi la sua libertà al tiro dipenderà dal flusso del match.

## Valutazione dei mercati e probabilità proposte

Le percentuali sotto rappresentano la probabilità stimata che ciascun evento si verifichi. Viene utilizzato un modello basato su distribuzioni Poisson/NB per tiri, fuorigioco e falli, combinato con la calibrazione derivata dalle statistiche dei singoli giocatori, dalle medie di squadra e dalle considerazioni di contesto (arbitro, necessità di punti, ecc.).

| Prop (evento) | Analisi e ragioni principali | Probabilità stimata |
|---|---|---|
| **Julio Enciso 1+ tiro in porta** | Enciso genera ~1.05 tiri in porta ogni 90’【530814297521421†L2007-L2010】. In un 4‑4‑2 viene supportato da Almirón ma affronta una difesa turca che concede 5.1 tiri in porta a gara. Poiché potrebbe non giocare tutti i minuti, la λ per i tiri in porta è stimata a 0.9–1.0. La probabilità di almeno 1 tiro in porta (~1 – e^‑λ) è ~55–60 %, ma l’incertezza sul match spinge la stima a **≈46 %**. | **46 %** |
| **Paraguay più cartellini della Turchia** | L’arbitro Iván Barton ha una media elevata di ammonizioni (circa 5 gialli a match)【54766179793289†L130-L135】. Il Paraguay commette 12.78 falli a partita, nettamente più dei 9.3 della Turchia【2851657761723†L1564-L1583】【839017757575117†L1556-L1584】; inoltre difenderà più basso, con molti duelli. La Turchia tende a subire più falli di quanti ne faccia. Tutto questo suggerisce un vantaggio per il Paraguay nel conteggio dei cartellini. | **60 %** |
| **Turchia ≥ 2 fuorigioco** | La Turchia è registrata con una media di 2.2 fuorigioco per match (70 % delle partite sopra quota 1.5)【839017757575117†L3128-L3167】. Con attaccanti che attaccano la profondità (Aktürkoğlu, Güler, Barış Alper Yılmaz), e un Paraguay che difenderà basso ma potrebbe alzare la linea nei momenti finali, la distribuzione Poisson (λ≈2.2) dà circa 65 % di probabilità per ≥2 fuorigioco. Si applica una piccola compressione per incertezza → **≈60 %**. | **60 %** |
| **Turchia più corner del Paraguay nel 2° tempo** | Le medie dei corner non sono pubbliche, ma la Turchia produce 16.4 tiri a gara e avrà maggior possesso (72 % contro l’Australia【927339720943185†L279-L285】). È plausibile che nel secondo tempo, specie se il risultato è in bilico, la Turchia forzi molte azioni sulle fasce. Il Paraguay invece tende a essere passivo. Mercato difficile da modellare → **≈60 %**. | **60 %** |
| **Paraguay più falli della Turchia** | La Turchia commette 9.3 falli, mentre il Paraguay 12.78【2851657761723†L1564-L1583】【839017757575117†L1556-L1584】. È quindi probabile che i sudamericani superino i turchi. La differenza di medie (≈3.5) e la distribuzione NB suggeriscono circa 70–75 %; si applica un margine prudenziale → **≈72 %**. | **72 %** |
| **Turchia più tiri in porta del Paraguay nel 2° tempo** | Turchia 5.1 SOT/match, Paraguay 4.7【839017757575117†L3128-L3167】【2851657761723†L3090-L3149】. Differenza non enorme; in un solo tempo la varianza è alta. Turchia però attaccherà di più se dovesse inseguire la vittoria. Si stima un vantaggio moderato, con prudenza → **≈55 %**. | **55 %** |
| **Ci sarà un rigore o un cartellino rosso** | La frequenza base di un penalty o un’espulsione in un singolo match è intorno al 25–30 %. Con un arbitro severo come Barton【54766179793289†L130-L135】 e due squadre che giocano per restare nel torneo, la probabilità sale leggermente. Restiamo però sotto il 35 % per rispetto del base rate → **≈32 %**. | **32 %** |
| **La Turchia vince** | Poisson per i goal con xG 1.81 vs 1.22 per Paraguay【839017757575117†L3128-L3167】【2851657761723†L3090-L3149】 produce circa 50–55 % di vittoria turca; la necessità di ottenere i tre punti e la forma difensiva del Paraguay (4 gol subiti dagli USA) spinge oltre la parità. Si stimano **≈55 %** di chance di vittoria turca. | **55 %** |
| **Totale gol della partita ≤ 2** | Le due squadre sommano ~3.0 goal/match (2.2+1.3 per la Turchia e 1.3+1.3 per il Paraguay【839017757575117†L1556-L1584】【2851657761723†L1564-L1583】), ma la tensione del match e un Paraguay che cercherà di non subire possono abbassare il ritmo. Il modello Poisson dà circa 44–48 % di under 2.5; contando la cautela si arriva **≈51 %**. | **51 %** |
| **Orkun Kökçü 1+ tiro in porta** | Kökçü tenta 3.19 tiri/90’ con il 36.36 % di precisione【159551795661340†L2082-L2084】 → ~1.16 tiri in porta/90’. In un ruolo da trequartista potrebbe abbassare un po’ il volume (λ≈0.9). La probabilità di almeno un tiro in porta (1 – e^‑0.9) è ~59 %. Si considerano le incognite sulla posizione e la possibile alternanza con Yildiz, quindi la stima finale è **≈44 %**. | **44 %** |

## Conclusioni e raccomandazioni

- **Eventi “forti”**: *Paraguay più falli* (≈72 %) e *Paraguay più cartellini* (≈60 %) sono supportati da statistiche solide e dall’arbitro severo.  
- **Eventi “moderati”**: *Turchia ≥2 fuorigioco* e *Turchia più corner nel 2° tempo* sono leggermente sopra il 50 % ma con varianza alta.  
- **Eventi equilibrati**: *Turchia più SOT nel 2° tempo* (55 %), *match ≤2 gol* (51 %) e *vittoria turca* (55 %) restano vicini alla parità, per cui conviene non spingersi troppo con le percentuali.  
- **Prop su giocatori**: per Enciso (46 %) e Kökçü (44 %) la probabilità di almeno un tiro in porta è intorno alla metà; qui i minuti effettivi e il gioco del match saranno determinanti.

Queste stime mirano a essere calibrate: abbastanza aggressive dove i dati lo supportano (falli/cartellini), ma prudenti su mercati ad alta varianza. Ricorda che nella Probability Cup il punteggio è relativo al Brier score medio degli avversari, quindi è importante essere più accurati della massa senza estremizzare troppo le proprie previsioni.
