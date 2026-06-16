# Menzerath-Altmannův zákon v urbánní morfologii

**[English version below / Anglická verze níže]**

---

## O projektu

Tento projekt testuje, zda **Menzerath-Altmannův (MA) zákon** – dobře ověřený princip kvantitativní lingvistiky – platí také v morfologii měst.

MA zákon říká: **čím větší je celek (konstrukt), tím menší jsou jeho průměrné stavební jednotky (konstituenty)**. V lingvistice platí např. pro vztah délky slova a délky slabik, nebo délky věty a délky slov. Projekt testuje, zda analogický princip funguje v prostorové organizaci měst, a to na datech OpenStreetMap zpracovaných přes knihovnu OSMnx.

### Testované hypotézy

**H1 – Uliční segmenty:**
Čím větší je město (populace / rozloha), tím kratší je průměrná délka uličního segmentu (vzdálenost mezi dvěma křižovatkami). Větší sídelní celek → hustší síť → kratší konstituenty.

**H2 – Městské bloky:**
Čím větší je město, tím menší je průměrná plocha jeho městských bloků. Efekt parcelačního tlaku při růstu hustoty.

### Matematická forma

Altmannův zákon se typicky fituje mocninnou funkcí s korekčním faktorem:

$$y = a \cdot x^b \cdot e^{-cx}$$

kde *x* je velikost konstruktu (město) a *y* průměrná velikost konstituentu (segment, blok). Predikce: *b* < 0.

---

## Struktura projektu

```
urbanMAL/
├── data/
│   ├── raw/          # Původní stažená data (OSM, ČSÚ, RÚIAN) – neupravená
│   ├── interim/      # Mezivýsledky čištění a transformací
│   └── processed/    # Finální analytické datasety
├── notebooks/        # Jupyter notebooky (orchestrátory analýzy)
├── src/urbanmal/     # Python balíček (veškerá analytická logika)
│   ├── data/         # Stahování a načítání dat
│   ├── metrics/      # Výpočet metrik segmentů a bloků
│   ├── fitting.py    # Fitting MA zákona
│   └── viz.py        # Vizualizační funkce (Seaborn)
├── reports/
│   └── figures/      # Exportované grafy
└── references/       # Relevantní literatura
```

---

## Instalace

```bash
git clone https://github.com/<username>/urbanMAL.git
cd urbanMAL

# Aktivovat venv
venv\Scripts\activate        # Windows
# nebo: source venv/bin/activate  # Linux/macOS

pip install -r requirements.txt
```

---

## Postup analýzy (fáze)

| Fáze | Obsah | Notebook |
|---|---|---|
| **0 – Pilot** | Praha: centrum vs. suburb, výběr parametrů | `00_pilot_praha.ipynb` |
| **1 – ČR** | ~200 českých měst, data z ČSÚ/RÚIAN | `01_czech_cities.ipynb` |
| **2 – Evropa** | Velká města, různé morfologické tradice | `02_european_cities.ipynb` |
| **3 – Globál** | GHS Urban Centre DB, tisíce měst | `03_global_scale.ipynb` |

---

## Literatura

### Menzerath-Altmannův zákon a kvantitativní lingvistika

Altmann, G. (1980). Prolegomena to Menzerath's law. *Glottometrika*, *2*, 1–10.

Hřebíček, L. (1995). *Vyprávění o lingvistických experimentech s textem*. Academia.

Hřebíček, L. (1997). Lectures on text theory. *Oriental Institute, Academy of Sciences of the Czech Republic*.

Köhler, R. (1984). Zur Interpretation des Menzerath'schen Gesetzes. *Glottometrika*, *6*, 177–183.

Menzerath, P. (1954). *Die Architektonik des deutschen Wortschatzes*. Dümmler.

### Urbánní věda a morfologie měst

Barthelemy, M. (2016). *The structure and dynamics of cities: Urban data analysis and theoretical modeling*. Cambridge University Press.

Batty, M. (2013). *The new science of cities*. MIT Press.

Batty, M., & Longley, P. A. (1994). *Fractal cities: A geometry of form and function*. Academic Press.

Batty, M., & Longley, P. A. (1994). When and where is a city fractal? *Environment and Planning B: Planning and Design*, *21*(1), 79–103.

Bettencourt, L. M. A. (2021). *Introduction to urban science: Evidence and theory of cities as complex systems*. MIT Press.

Boeing, G. (2017). OSMnx: New methods for acquiring, constructing, analyzing, and visualizing complex street networks. *Computers, Environment and Urban Systems*, *65*, 126–139.

Boeing, G. (2019). Urban spatial order: Street network orientation, configuration, and entropy. *Applied Network Science*, *4*(1), 67.

Jacobs, J. (1961). *The death and life of great American cities*. Random House.

Lynch, K. (1960). *The image of the city*. MIT Press.

West, G. B. (2017). *Scale: The universal laws of growth, innovation, sustainability, and the pace of life in organisms, cities, economies, and companies*. Penguin Press.

### Statistické metody

Clauset, A., Shalizi, C. R., & Newman, M. E. J. (2009). Power-law distributions in empirical data. *SIAM Review*, *51*(4), 661–703.

---

## Stav projektu

- [x] Inicializace struktury projektu
- [x] Pilotní analýza: Praha (centrum vs. suburb, H1 + H2)
- [ ] Sběr dat: česká města (ČSÚ / RÚIAN)
- [ ] Stažení uličních sítí přes OSMnx – ČR vzorek
- [ ] Fitting MA zákona (H1 – segmenty, ČR)
- [ ] Fitting MA zákona (H2 – bloky, ČR)
- [ ] Robustní statistické testování (model comparison, bootstrap, permutační test)
- [ ] Replikace na evropském a globálním vzorku
- [ ] Rukopis

---

## Licence

MIT

---

---

# Menzerath-Altmann Law in Urban Morphology

## About

This project investigates whether the **Menzerath-Altmann (MA) law** — a robust principle from quantitative linguistics — holds in **urban morphology**.

The MA law states: *the larger the construct, the smaller its average constituents*. Originally established for linguistic units (e.g. longer words have shorter syllables; longer sentences have shorter words), it has since been extended to molecular biology (longer genomes → shorter chromosomes). Here we test whether an analogous scaling principle governs the spatial organisation of cities, using street network and block data extracted from OpenStreetMap via OSMnx.

**Hypothesis 1 (Street segments):** Larger cities have shorter average street segment lengths (distance between two intersections), reflecting denser network topology.

**Hypothesis 2 (Urban blocks):** Larger cities have smaller average urban block areas, reflecting parcelation pressure under urban growth.

The law is fit using a power function with an optional exponential correction term: *y = a · x^b · e^(−cx)*. We test its presence rigorously — using AIC/BIC model comparison, bootstrap confidence intervals, permutation tests, and leave-one-out diagnostics — to avoid the common pitfall of reporting visually convincing log-log fits without proper statistical validation (cf. Clauset et al., 2009).

### Data sources

- **OSMnx / OpenStreetMap** — street networks and urban blocks, globally available
- **ČSÚ** (Czech Statistical Office) — population, area, settlement type for Czech municipalities
- **RÚIAN** — detailed Czech cadastral and administrative spatial data
- **GHS Urban Centre Database** (EU JRC) — global urban centres for large-scale replication

### Phases

| Phase | Scope | Notebook |
|---|---|---|
| 0 – Pilot | Prague: centre vs. suburb | `00_pilot_praha.ipynb` |
| 1 – Czech Republic | ~200 cities, ČSÚ/RÚIAN | `01_czech_cities.ipynb` |
| 2 – Europe | Major cities, morphological traditions | `02_european_cities.ipynb` |
| 3 – Global | GHS-UC database, thousands of cities | `03_global_scale.ipynb` |

### Installation

```bash
git clone https://github.com/<username>/urbanMAL.git
cd urbanMAL
pip install -r requirements.txt
```

### Target journals

*Computers, Environment and Urban Systems* · *Environment and Planning B* · *Urban Studies*

### Licence

MIT
