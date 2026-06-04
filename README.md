# 🎓 JPEG-like DCT Image Compressor
**Progetto 2 — Metodi del Calcolo Scientifico · A.A. 2025-2026**  
*Jacopo Borgato · Nicolas Chines*

---

## Indice

1. [Descrizione del progetto](#descrizione-del-progetto)
2. [Struttura del codice](#struttura-del-codice)
3. [Requisiti e installazione](#requisiti-e-installazione)
4. [Utilizzo](#utilizzo)
   - [Modalità GUI](#modalità-gui)
   - [Modalità CLI](#modalità-cli)
5. [Algoritmo di compressione](#algoritmo-di-compressione)
6. [Test e validazione](#test-e-validazione)
7. [Benchmark delle prestazioni](#benchmark-delle-prestazioni)

---

## Descrizione del progetto

Il progetto implementa un algoritmo di compressione di immagini in toni di grigio ispirato allo standard JPEG, basato sulla **Discrete Cosine Transform 2D (DCT2)**. Il cuore dell'algoritmo opera su macro-blocchi di dimensione F×F: applica la DCT2, annulla i coefficienti ad alta frequenza secondo una soglia `d`, quindi applica la DCT2 inversa per ricostruire l'immagine compressa.

Il progetto si divide in due parti:

- **Parte 1** — Implementazione manuale della DCT2 e confronto delle prestazioni con la versione fast (FFT-based) della libreria SciPy, su matrici N×N con N crescente.
- **Parte 2** — Software completo con interfaccia grafica (GUI) e interfaccia a riga di comando (CLI) per applicare la compressione a immagini `.bmp` in toni di grigio.

---

## Struttura del codice

```
.
├── main.py          # Entry point: avvia GUI (no args) o CLI (con args)
├── jpeg.py          # Logica di compressione: block_splitter, compress_block, compress_image
├── utils.py         # Implementazione manuale di DCT1, DCT2, IDCT1, IDCT2
├── gui.py           # Interfaccia grafica PyQt6 con splash screen e pannelli affiancati
├── CLI.py           # Interfaccia a riga di comando con argparse
├── styles.py        # Stile dark mode (Catppuccin Mocha) e messaggi splash
├── benchmark.py     # Confronto prestazionale DCT2 custom vs SciPy
└── tests.py         # Test di correttezza su blocco 8×8 di riferimento (consegna)
```

### `utils.py` — DCT manuale

Contiene l'implementazione **from scratch** (senza librerie FFT) della trasformata DCT-II ortonormale e della sua inversa, sia in versione monodimensionale che bidimensionale:

- `dct(v)` — DCT-II 1D con normalizzazione ortonormale
- `dct2(m)` — DCT-II 2D ottenuta applicando `dct` prima sulle colonne poi sulle righe
- `idct(Y)` — IDCT-II 1D (inversa esatta di `dct`)
- `idct2(m)` — IDCT-II 2D ottenuta applicando `idct` prima sulle righe poi sulle colonne

La formula di normalizzazione utilizzata è:

$$C_k = \begin{cases} \frac{1}{\sqrt{N}} & k = 0 \\ \sqrt{\frac{2}{N}} & k > 0 \end{cases}$$

$$y_k = C_k \sum_{i=0}^{N-1} v_i \cos\!\left(\frac{\pi k (2i+1)}{2N}\right)$$

### `jpeg.py` — Compressione

- `block_splitter(A, F)` — Suddivide l'array 2D in blocchi F×F (top-left, scarti rimossi), restituisce `(n_y, n_x, lista_blocchi)`
- `compress_block(block, d)` — Applica DCT2, azzera i coefficienti con k+l ≥ d, applica IDCT2, arrotonda e fa clipping in [0, 255]
- `compress_image(img, F, d)` — Orchestrazione completa con parallelismo multiprocesso (`ProcessPoolExecutor`) per sfruttare tutti i core CPU disponibili (lasciandone 2 liberi al sistema)
- `validate_params(img, F, d)` — Validazione dei parametri: F ≥ 1, F ≤ min(dimensioni), 0 ≤ d ≤ 2F−2
- `kept_coefficients(F, d)` — Conta i coefficienti DCT mantenuti per blocco dopo il taglio

> **Nota sul parallelismo:** la compressione usa `ProcessPoolExecutor` (multiprocessing) e non multithreading, per aggirare il GIL di Python e sfruttare effettivamente tutti i core fisici disponibili.

### `gui.py` — Interfaccia grafica

Interfaccia PyQt6 con:

- **Splash screen** animato con messaggi sequenziali
- **Header** con logo opzionale (file `bicocca_logo.png`) e nome autori
- **Barra di controllo** compatta: selezione file (browse + path editabile), campi F e d, pulsante Process
- **Pannelli affiancati** per immagine originale e immagine compressa, con ridimensionamento reattivo
- **Status bar** con feedback in tempo reale sullo stato dell'elaborazione
- **Thread separato** (`ProcessorThread`) per l'elaborazione asincrona, così la GUI rimane sempre reattiva
- Supporto scorciatoia da tastiera `Enter` / `Return` per avviare la compressione

### `CLI.py` — Interfaccia a riga di comando

Basata su `argparse`, accetta:

```
python main.py <immagine> <F> <d> [-o output.bmp] [-s]
```

Stampa a terminale: dimensioni immagine, parametri usati, numero di coefficienti mantenuti per blocco (assoluto e percentuale), dimensioni dell'immagine compressa. Opzionalmente salva il file di output con `-o`.

### `benchmark.py` — Analisi prestazionale

Genera matrici N×N casuali con N da 10 a 200 (step 10), misura i tempi di esecuzione di `utils.dct2` (custom, O(N³)) e `scipy.fftpack.dctn` (fast, O(N² log N)), e produce un grafico in scala semi-logaritmica con le curve misurate e le tendenze teoriche di riferimento, normalizzate sull'ultimo punto.

---

## Requisiti e installazione

**Python ≥ 3.10** (richiesto per la type hint `str | None`)

### Dipendenze

```bash
pip install numpy pillow pyqt6 scipy matplotlib
```

| Pacchetto | Utilizzo |
|-----------|----------|
| `numpy` | Operazioni su array, meshgrid, clip, round |
| `Pillow` | Apertura/salvataggio immagini (PIL) |
| `PyQt6` | Interfaccia grafica |
| `scipy` | DCT fast nel benchmark (non usata nella compressione) |
| `matplotlib` | Grafici nel benchmark |

### (Opzionale) Logo Bicocca

Per visualizzare il logo dell'Università Bicocca nell'header della GUI, inserire il file `bicocca_logo.png` nella stessa directory dei sorgenti.

---

## Utilizzo

### Modalità GUI

Avviare senza argomenti:

```bash
python main.py
```

1. Cliccare **Browse** per selezionare un file `.bmp` in toni di grigio (o digitare il path manualmente)
2. Inserire il valore di **F** (dimensione del blocco, ≥ 1)
3. Inserire il valore di **d** (soglia di taglio frequenze, 0 ≤ d ≤ 2F−2)
4. Cliccare **⚙ Process** (oppure premere `Enter`)

L'immagine originale e quella compressa vengono visualizzate affiancate.

### Modalità CLI

```bash
python main.py <immagine> <F> <d> [opzioni]
```

**Argomenti posizionali:**

| Argomento | Descrizione |
|-----------|-------------|
| `image` | Path del file immagine (`.bmp`, `.png`, `.jpg`) |
| `F` | Dimensione del blocco in pixel (es. `8`) |
| `d` | Soglia di taglio frequenze (`0` … `2F-2`) |

**Opzioni:**

| Flag | Descrizione |
|------|-------------|
| `-o`, `--output <path>` | Salva l'immagine compressa su file |
| `-s`, `--show` | Mostra le immagini originale e compressa a schermo |

**Esempi:**

```bash
# Compressione base con F=8, d=5
python main.py photo.bmp 8 5

# Salva il risultato e mostra le immagini
python main.py photo.bmp 16 10 --output result.bmp --show

# d=0: azzera tutti i coefficienti → immagine completamente grigia
python main.py photo.bmp 8 0
```

**Output a terminale (esempio):**

```
Avvio in modalità CLI (Terminale)...
Image   : photo.bmp  (512 x 512 px)
F = 8,  d = 5
Kept    : 10 / 64 coefficients per block  (16 %)
Output  : 512 x 512 px  (cropped to multiple of F)
Saved   : result.bmp
```

---

## Algoritmo di compressione

Per ogni blocco F×F estratto dall'immagine, l'algoritmo esegue:

```
1.  c    = DCT2(blocco)
2.  c[k,l] = 0   per tutti gli indici con k + l ≥ d
3.  ff   = IDCT2(c)
4.  ff   = clip(round(ff), 0, 255)
```

Il parametro `d` controlla quante frequenze vengono mantenute. Con d=0 tutti i coefficienti vengono azzerati (immagine uniforme grigia); con d=2F−2 viene azzerato solo il coefficiente di frequenza massima (k=F−1, l=F−1); valori intermedi producono diversi livelli di compressione/qualità.

Il numero di coefficienti mantenuti per blocco è dato dal numero di coppie (k,l) con k+l < d, ovvero il triangolo superiore sinistro della matrice dei coefficienti:

$$\text{kept}(d) = \sum_{s=0}^{d-1} \min(s+1,\ F)$$

---

## Test e validazione

Il file `tests.py` verifica la correttezza dell'implementazione DCT rispetto ai valori di riferimento forniti dalla consegna:

```bash
python tests.py
```

Output atteso:
```
Testing on Array: True
Testing on Matrix: True
```

I test confrontano (con tolleranza relativa 1%):
- La DCT-1D sulla prima riga del blocco 8×8 di riferimento
- La DCT-2D sull'intero blocco 8×8 di riferimento

---

## Benchmark delle prestazioni

```bash
python benchmark.py
```

Esegue la DCT2 su matrici N×N con N ∈ {10, 20, …, 200} e genera un grafico in scala semi-logaritmica che confronta:

- `utils.dct2` — implementazione custom, complessità **O(N³)**
- `scipy.fftpack.dctn` — implementazione FFT-based, complessità **O(N² log N)**

Le curve teoriche di riferimento (O(N³) e O(N² log N)) vengono normalizzate sull'ultimo punto misurato per confronto visivo.

> Come atteso, la versione SciPy è significativamente più rapida per N grandi, mentre per N piccoli il vantaggio è minore a causa dell'overhead di inizializzazione dell'FFT.