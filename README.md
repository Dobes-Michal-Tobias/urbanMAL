# Menzerath-Altmannův zákon v urbánní morfologii

> **English summary below / Anglické shrnutí níže**

---

## O projektu

Tento projekt testuje, zda **Menzerath-Altmannův (MA) zákon** – dobře ověřený princip kvantitativní lingvistiky – platí také v morfologii měst.

MA zákon říká: **čím větší je celek (konstrukt), tím menší jsou jeho průměrné stavební jednotky (konstituenty)**. V lingvistice platí např. pro vztah délky slova a délky slabik. Zde jej testujeme na prostorových datech měst stažených přes OpenStreetMap (OSMnx).

### Testované hypotézy

**H1 – Uliční segmenty:**
Čím větší je město (populace / rozloha), tím kratší je průměrná délka uličního segmentu (vzdálenost mezi dvěma křižovatkami). Větší sídelní celek → hustší síť → kratší konstituenty.

**H2 – Administrativní členění:**
Čím větší je město, tím menší je průměrná rozloha jeho administrativních dílčích celků (katastrální území, čtvrti). Efekt parcelačního tlaku při růstu hustoty.

### Matematická forma

Altmannův zákon se typicky fituje mocninnou funkcí s korekčním faktorem:

$$y = a \cdot x^b \cdot e^{-cx}$$

kde *x* je velikost konstruktu (město) a *y* průměrná velikost konstituentu (segment, čtvrť).

---

## Struktura projektu

```
urbanMAL/
├── data/
│   ├── raw/          # Původní stažená data (OSM, ČSÚ, RÚIAN) – neupravená
│   ├── interim/      # Mezivýsledky čištění a transformací
│   └── processed/    # Finální analytické datasety
├── notebooks/        # Jupyter notebooky (průzkum, analýza, vizualizace)
├── src/urbanmal/     # Balíček se zdrojovým kódem (funkce, pipelines)
├── reports/
│   └── figures/      # Exportované grafy a mapy
├── references/       # Relevantní literatura (PDF, citace)
├── requirements.txt
└── README.md
```

---

## Instalace

```bash
# Klonovat repozitář
git clone <url>
cd urbanMAL

# Aktivovat venv
venv\Scripts\activate        # Windows
# nebo: source venv/bin/activate  # Linux/macOS

# Nainstalovat závislosti
pip install -r requirements.txt
```

---

## Stav projektu

- [x] Inicializace struktury projektu
- [ ] Sběr dat: česká města (ČSÚ / RÚIAN)
- [ ] Stažení uličních sítí přes OSMnx
- [ ] Explorace a čištění dat
- [ ] Fitting MA zákona (H1 – segmenty)
- [ ] Fitting MA zákona (H2 – administrativní členění)
- [ ] Vizualizace a interpretace
- [ ] Rukopis / paper

---

## English Summary

This project investigates whether the **Menzerath-Altmann (MA) law** — a robust principle from quantitative linguistics — holds in **urban morphology**.

The MA law states: *the larger the construct, the smaller its average constituents*. Originally established for linguistic units (e.g. longer words have shorter syllables), it has since been found in molecular biology as well. Here we test it on spatial data of cities extracted from OpenStreetMap via the OSMnx library.

**Hypothesis 1 (Street segments):** Larger cities have shorter average street segment lengths (distance between two intersections), reflecting denser network topology.

**Hypothesis 2 (Administrative subdivisions):** Larger cities have smaller average areas of their administrative sub-units (cadastral areas, districts), reflecting parcelation pressure under urban growth.

The law is fit using a power function with an optional exponential correction term: *y = a · x^b · e^(−cx)*.

The study draws on Czech urban data (population, area) from ČSÚ/RÚIAN and street network metrics computed with OSMnx.

---

## Licence

MIT
