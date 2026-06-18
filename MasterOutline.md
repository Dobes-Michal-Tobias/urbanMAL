# MasterOutline: Menzerath-Altmannův zákon v urbánní morfologii

> Pracovní dokument k experimentálnímu designu. Živý dokument – aktualizovat průběžně.

---

## 1. Výzkumná otázka

**Platí Menzerath-Altmannův zákon v morfologii měst?**

MA zákon: `y = a · x^b · e^(−cx)`
- `x` = velikost konstruktu (město)
- `y` = průměrná velikost konstituentu
- Predikce: `b < 0` (záporný exponent → negativní vztah)

---

## 2. Definice konstruktu a konstituentu

### 2.1 Velikost konstruktu (nezávislá proměnná)

Testujeme **dvě alternativní míry** velikosti města – obě jsou v literatuře legitimní a dávají různé interpretace:

| Míra | Zdroj | Výhody | Rizika |
|---|---|---|---|
| **Populace** (počet obyvatel) | ČSÚ / RÚIAN | Přímá vazba na intenzitu lidské aktivity | Nezahrnuje fyzickou rozlohu |
| **Rozloha** (km²) | ČSÚ / RÚIAN | Přímá prostorová míra | Může zahrnovat pole/lesy mimo zástavbu |

→ Testovat obě, porovnat sílu vztahu (R², AIC). Pokud oba vedou ke stejnému závěru, výsledek je robustnější.

**Bonus:** Přidat binární proměnnou `typ_sidla` (vesnice / město / statutární město) z ČSÚ jako kategorický moderátor.

### 2.2 Konstituent (závislá proměnná)

Testujeme **dvě hypotézy nezávisle**:

#### H1 – Uliční segmenty
- **Konstituent:** průměrná délka uličního segmentu = vzdálenost mezi dvěma křižovatkami (v metrech)
- **Zdroj:** OSMnx, `network_type="drive"` nebo `"all"` (viz rozhodnutí níže)
- **Logika:** Větší město → hustší síť křižovatek → kratší segmenty

#### H2 – Městské bloky
- **Konstituent:** průměrná plocha městského bloku (m² nebo ha)
- **Zdroj:** OSMnx (`ox.graph_to_gdfs` + morfometrická analýza bloků), případně RÚIAN parcely
- **Logika:** Větší město → vyšší tlak na parcelaci → menší bloky

---

## 3. Fáze sběru dat a analýzy

### FÁZE 0 – Pilot: jedno město (Praha)

**Cíl:** Ověřit technický pipeline, rozhodnout parametry, porozumět datům.

**Úkoly:**
- [ ] Stáhnout uliční síť Prahy přes OSMnx
- [ ] Vizualizovat distribuci délek segmentů (histogram)
- [ ] Srovnat **historické centrum** (Praha 1) vs. **suburb** (např. Letňany, Zličín)
  - Klíčová otázka: jsou segmenty v centru kratší? Jak moc?
  - Rozhodnutí: bereme celé admin. území, nebo jen zastavěnou plochu (urban footprint)?
- [ ] Totéž pro bloky (H2)
- [ ] Rozhodnout `network_type`: `"drive"` vs `"all"`

**Výstup:** Notebook `notebooks/00_pilot_praha.ipynb`

---

### FÁZE 1 – Česká republika (~100–300 měst)

**Cíl:** První test MA zákona na homogenním vzorku (stejný kontext, právní systém, datový zdroj).

**Výběr vzorku:**
- Zdroj seznamu: **ČSÚ** – číselník obcí, filtr: obce se statusem „město" nebo „městys"
- Cílový rozsah: ~200 sídel, pokrývající populaci od ~1 000 do ~1 300 000 (Praha)
- Přidat sloupce: populace, rozloha, typ_sídla (vesnice/město/statutární město)

**Postup:**
- [ ] Načíst tabulku měst z ČSÚ / RÚIAN → DataFrame
- [ ] Iterovat přes města, pro každé stáhnout OSMnx graf a extrahovat metriky
- [ ] Ošetřit chyby (město nenalezeno v OSM, timeout, prázdný graf)
- [ ] Uložit výsledný dataset do `data/processed/czdata.csv`
- [ ] Fitovat MA zákon (scipy curve_fit / statsmodels OLS na log-log)
- [ ] Vizualizovat scatter plot + fit křivka

**Výstup:** Notebook `notebooks/01_czech_cities.ipynb`

---

### FÁZE 2 – Evropská/mezinárodní škála

**Cíl:** Ověřit, zda zákon platí napříč různými urbanistickými tradicemi.

**Výběr vzorku:**
- Velká evropská města: Berlín, Vídeň, Paříž, Londýn, Amsterdam, Barcelona, Řím, Varšava...
- Různé morfologické tradice: organické (středověké), plánované (haussmannské), postsovětské
- Případně: databáze jako **GHS Urban Centre Database** (JRC) pro globální záběr

**Klíčové otázky:**
- Je zákon specifický pro ČR, nebo je universální?
- Liší se koeficienty `a`, `b`, `c` mezi morfologickými typy měst?

**Výstup:** Notebook `notebooks/02_european_cities.ipynb`

---

### FÁZE 3 – Globální škála (ambiciózní)

**Cíl:** Tisíce měst → vysoká statistická síla, publikovatelné výsledky.

**Zdroje:**
- **GHS Urban Centre Database** (EU JRC) – ~10 000 městských center světa s populací
- **OSMnx** – stahování v dávkách (nutný výpočetní čas, případně cloud)

**Výstup:** Notebook `notebooks/03_global_scale.ipynb`

---

## 4. Pozorování z pilotu (Fáze 0 – Praha)

> Nezávazné poznámky pro informování dalšího designu. Finální rozhodnutí až po větším vzorku.

### H1 – Uliční segmenty (`network_type="drive"`)

| Oblast | Průměr (m) | Medián (m) | n segmentů |
|---|---|---|---|
| Praha 1 (historické centrum) | 82 | 58 | ~ |
| Letňany (panelákový suburb) | 104 | 74 | ~ |
| Zličín (okrajová zástavba) | 116 | 92 | ~ |
| Praha celá (`drive`) | 116 | 81 | ~ |
| Praha celá (`all`) | 44 | 23 | ~ |

**Pozorování:**
- Gradient centrum → periferie jde správným směrem pro MA zákon (kratší segmenty ve větší/hustší části).
- `all` zahrnuje chodníky, cyklostezky a krátké spojky, které dramaticky snižují průměr (44 vs 116 m) — tato varianta pravděpodobně měří jiný fenomén. Bude nutné porovnat systematicky na větším vzorku.
- Distribuce jsou silně pravostranně zešikmené (long tail) — otázka mean vs. median zůstává otevřená, budeme reportovat obojí + kvantily + popisné statistiky.

### H2 – Bloky

| Oblast | Průměr (m²) | Medián (m²) | n bloků |
|---|---|---|---|
| Praha 1 (centrum) | 1 407 | 698 | ~ |
| Letňany (suburb) | 3 043 | 371 | ~ |

**Pozorování:**
- Průměr v Letňanech je více než dvojnásobný oproti centru — táhnou ho velké panelové plochy a parkoviště.
- Medián je naopak v Letňanech nižší → distribuce je bimodální (hodně malých plošek + pár obřích).
- Toto ukazuje, že pro H2 bude výběr agregační statistiky kritičtější než pro H1. Budeme reportovat obě + kvantily.

### Otevřená rozhodnutí (průběžně aktualizovat)

| Rozhodnutí | Možnosti | Status |
|---|---|---|
| `network_type` pro OSMnx | `"drive"` / `"all"` | → testovat obě paralelně, reportovat obě |
| Definice hranice města | admin. boundary / urban footprint | → admin. boundary (konzistentní, OSM má pro všechna ČR města) |
| Míra velikosti | populace / rozloha / obojí | → testovat obojí |
| Agregace konstituentu | mean / median / kvantily | → reportovat vše, jako primární medián |
| Minimální počet segmentů | ? | → rozhodnout po průzkumu distribuce n v ČR vzorku |

### Architektonické rozhodnutí: lokální PBF extrakt místo Overpass API

Při běhu fáze 1 (843 měst) se po ~60 dotazech veřejný Overpass server (`overpass-api.de`)
začal chovat patologicky – odmítal navazovat spojení (connect timeout 180s opakovaně),
průměrná doba na město vzrostla na ~56 minut. Při tomto tempu by stažení ČR trvalo týdny
a fáze 2/3 (tisíce měst) by byly fakticky neproveditelné.

**Řešení:** Stáhnout jednorázově celostátní `.osm.pbf` extrakt z Geofabriku (~550 MB pro ČR)
a číst z něj lokálně přes GDAL OSM driver (`geopandas.read_file(..., layer=...)`), bez
jakéhokoliv API volání. `pyrosm` byl zvažován, ale nešlo ho nainstalovat (chybí Visual C++
Build Tools pro kompilaci `cykhash`, navíc žádné předkompilované wheely pro Python 3.14).
GDAL/pyogrio už je součástí `geopandas` závislostí a OSM driver podporuje čtení `.pbf` přímo.

**Klíčové vrstvy GDAL OSM driveru:**
- `lines` – cesty (`highway` jako přímý sloupec) → uliční segmenty (H1)
- `multipolygons` – budovy/landuse (H2) i administrativní hranice (`boundary='administrative'`, `admin_level`, `name`)

**Postup:** hranice obcí se extrahují z PBF jednou pro celou zemi (`admin_level=8` = obce
v ČR) a cachují do GeoJSON. Pro každé město se pak ulice/bloky vyřezávají bbox + spatial
filtrem z lokálního souboru – řádově rychlejší a bez závislosti na vnější službě.

Tento přístup nahradí Overpass i pro fáze 2/3 – stačí stáhnout odpovídající
celostátní/kontinentální extrakty z Geofabriku.

---

## 5. Statistická analýza

### 5.1 Fitting MA zákona

Budeme systematicky procházet smyčkou přes dimenze experimentu:
- `network_type` ∈ {`drive`, `all`}
- agregace ∈ {mean, median, Q25, Q75}
- míra velikosti ∈ {populace, rozloha}
- granularita ∈ {celé město, administrativní části}

Pro každou kombinaci:
1. **Log-log OLS:** `log(y) = log(a) + b·log(x) + ε` — rychlý průzkum, snadná interpretace
2. **Nelineární least squares** (scipy `curve_fit`): fit celé Altmannovy rovnice `y = a·x^b·e^(-cx)`
3. **Reportovat:** koeficienty + 95% CI, R², AIC/BIC, p-hodnota pro `b < 0`

### 5.2 Robustní testování přítomnosti MA zákona

> Analogicky k problémům u Zipfova zákona (viz Clauset et al. 2009, *SIAM Review*): pouhý vizuálně hezký fit na log-log grafu **nestačí**. Potřebujeme rigorózní testovací rámec.

**Krok 1 – Potvrzení negativního vztahu**
- OLS na log-log: je koeficient `b` statisticky signifikantně záporný? (t-test / bootstrap CI)
- Pearsonovo / Spearmanovo ρ mezi log(x) a log(y) — obě verze, Spearman je robustnější vůči outlierům.

**Krok 2 – Výběr funkční formy (model comparison)**
Nestačí ukázat, že mocninná funkce fituje — musíme ukázat, že fituje *lépe než alternativy*:
- Lineární model (žádný vztah): `y = a + b·x`
- Exponenciální pokles: `y = a·e^(-bx)`
- Mocninná funkce (jednoduchá): `y = a·x^b`
- Altmannova funkce (plná): `y = a·x^b·e^(-cx)`

Srovnání přes **AIC / BIC** — nižší = lépe, s penalizací za počet parametrů.

**Krok 3 – Diagnóza residuí**
- QQ-plot residuí (normalita?)
- Breusch-Pagan test na heteroskedasticitu
- Pokud heteroskedasticita → WLS (weighted least squares) nebo log-transformace obou stran

**Krok 4 – Robustnost vzorku**
- Bootstrap resampling koeficientů (n = 1000 iterací) → CI bez distribučních předpokladů
- Leave-one-out analýza (je výsledek tažen jedním outlierem — Prahou?)
- Permutační test: je pozorované `b` větší (v absolutní hodnotě), než bychom čekali náhodou?

**Krok 5 – Replikace napříč subvzorky**
- Rozdělit ČR dataset na poloviny náhodně → platí zákon v obou?
- Porovnat koeficienty mezi fázemi (ČR vs. Evropa vs. globál)

### 5.3 Validace

- Srovnání H1 vs. H2: které hypotézy mají silnější a konzistentnější podporu?
- Srovnání koeficientu `b` s hodnotami z lingvistiky (typicky -0.3 až -0.5) — jsou si podobné?

---

## 6. Datové zdroje

| Zdroj | Data | Formát | Poznámka |
|---|---|---|---|
| **ČSÚ** | Populace, rozloha, typ sídla | CSV / XLSX | Číselník obcí ČR |
| **RÚIAN** | Parcely, katastrální území | SHP / GeoJSON | Detailní prostorová data |
| **OSMnx / OpenStreetMap** | Uliční sítě, bloky | Graf (NetworkX) | Globálně dostupné |
| **GHS Urban Centre DB** | Světová města, populace | GeoPackage | JRC, fáze 3 |

---

## 7. Architektura kódu

### Princip
- **Notebooky** (`notebooks/`) jsou čistě orchestrátory: načtou data, zavolají funkce z `src`, zobrazí výsledky.
- **Veškerá logika** (stahování dat, čištění, výpočet metrik, fitting, vizualizace) žije v modulech v `src/urbanmal/`.
- Žádná analytická logika přímo v notebooku – jen volání funkcí a komentáře.

### Struktura `src/urbanmal/`

```
src/urbanmal/
├── __init__.py
├── data/
│   ├── osm.py        # stahování sítí přes OSMnx
│   └── census.py     # načítání dat ČSÚ / RÚIAN
├── metrics/
│   ├── segments.py   # výpočet metrik uličních segmentů (H1)
│   └── blocks.py     # výpočet metrik městských bloků (H2)
├── fitting.py        # fitting MA zákona (log-log OLS, NLS curve_fit)
└── viz.py            # všechny vizualizační funkce (Seaborn)
```

### Vizualizace
- Knihovna: **Seaborn** (+ Matplotlib jako backend)
- Dvě palety:
  - `palette_seq` – sekvenční (pro metriky na spojité škále)
  - `palette_cat` – kategorická (pro typy sídel, fáze analýzy)
- Všechny vizualizační funkce centralizovány v `src/urbanmal/viz.py`, notebooky jen volají a zobrazují.

---

## 8. Potenciální výstupy

- Preprint / paper: *Computers, Environment and Urban Systems* nebo *Environment and Planning B*
- Replikační balíček (data + kód na GitHub/Zenodo)
- Vizualizace pro prezentaci / poster
