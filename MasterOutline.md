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

## 4. Otevřená rozhodnutí (TODO)

| Rozhodnutí | Možnosti | Status |
|---|---|---|
| `network_type` pro OSMnx | `"drive"` / `"all"` | ❓ otevřené |
| Definice hranice města | admin. boundary / urban footprint | ❓ otevřené |
| Míra velikosti | populace / rozloha / obojí | → testovat obojí |
| Jak agregovat metriku segmentů | mean / median (odolnější vůči outlierům) | ❓ otevřené |
| Minimální počet segmentů pro zařazení do vzorku | ? (filtr malých obcí) | ❓ otevřené |

---

## 5. Statistická analýza

### Fitting MA zákona
1. **Log-log OLS:** `log(y) = log(a) + b·log(x) + ε` → jednoduchá interpretace, ale ignoruje korekční faktor `e^(-cx)`
2. **Nelineární least squares** (scipy `curve_fit`): fit celé rovnice `y = a·x^b·e^(-cx)`
3. **Reportovat:** koeficienty a jejich CI, R², AIC/BIC, p-hodnota pro `b < 0`

### Validace
- Residuální analýza (heteroskedasticita?)
- Bootstrap CI pro koeficienty
- Srovnání H1 vs. H2 (které hypotézy mají silnější podporu?)

---

## 6. Datové zdroje

| Zdroj | Data | Formát | Poznámka |
|---|---|---|---|
| **ČSÚ** | Populace, rozloha, typ sídla | CSV / XLSX | Číselník obcí ČR |
| **RÚIAN** | Parcely, katastrální území | SHP / GeoJSON | Detailní prostorová data |
| **OSMnx / OpenStreetMap** | Uliční sítě, bloky | Graf (NetworkX) | Globálně dostupné |
| **GHS Urban Centre DB** | Světová města, populace | GeoPackage | JRC, fáze 3 |

---

## 7. Potenciální výstupy

- Preprint / paper: *Computers, Environment and Urban Systems* nebo *Environment and Planning B*
- Replikační balíček (data + kód na GitHub/Zenodo)
- Vizualizace pro prezentaci / poster
