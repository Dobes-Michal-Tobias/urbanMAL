Menzerath-Altmannův zákon v urbanistice
MAL (čím větší je celek, tím menší jsou jeho složky) se v lingvistice ověřuje běžně, ale jeho aplikace na fyzický prostor je velmi neprobádaná.
Ptáš se, co jsou konstituenty. Zde se nabízí přímo propojení s Geoffem Boeingem a jeho knihovnou OSMnx. Město můžeš chápat jako síť (graf).

Hypotéza 1 (Ulice): Celek = ulice (od začátku do konce), Konstituent = segment ulice (vzdálenost mezi dvěma křižovatkami). Platí, že čím delší je celková ulice, tím kratší jsou její průměrné segmenty?

Hypotéza 2 (Městské bloky): Celek = Město (definované přes administrative boundaries nebo urban footprint), Konstituent = polygon městského bloku. Mají větší města plošně menší průměrné bloky (vlivem vyšší hustoty a tlaku na parcelaci)?
Tohle by šlo masivně škálovat na tisících městech z OpenStreetMap a publikovat ve špičkových časopisech jako Computers, Environment and Urban Systems.

---
---

# Altmann-Menzarathův zákon v urbanistice

Tohle je přesně ten typ uvažování, ze kterého vznikají průlomové (a vysoce citované) články v Computational Social Science. Vzít robustní zákon z jedné disciplíny a otestovat ho v jiné.

Abychom si nalili čistého vína: **Menzerath-Altmannův (MA) zákon v urbanistice v současnosti neexistuje jako zavedený standard.** Zatímco Zipf (rank-size) nebo West (115% scaling) jsou učebnicové základy urbánní geografie, MA zákon zůstává primárně doménou kvantitativní lingvistiky (čím delší slovo, tím kratší slabiky) a v poslední době molekulární biologie (čím delší genom, tím kratší chromozomy; čím delší protein, tím kratší aminokyselinové struktury).

Ale to vůbec neznamená, že neplatí! Jen ho tam pravděpodobně ještě nikdo pořádně a systematicky neotestoval.

Základní premisa MA zákona zní: **Čím větší je celek (konstrukt), tím menší jsou jeho průměrné stavební jednotky (konstituenty).**

Pokud bychom to chtěli aplikovat na města, musíme si definovat, co je *konstrukt* a co *konstituent*. Nabízí se dvě fascinující hypotézy, které bys mohl ve svém projektu snadno otestovat:

### 1. Město jako konstrukt, uliční síť jako konstituent

Toto je z hlediska fyziky města nejlogičtější aplikace.

* **Hypotéza:** Čím je město větší (rozlohou nebo populací), tím hustší je jeho vnitřní zástavba, a proto je průměrná délka jednoho uličního segmentu (vzdálenost mezi dvěma křižovatkami) **kratší**.
* Zatímco malá vesnice má pár dlouhých, nepřerušených silnic (dlouhé konstituenty), velkoměsto jako Praha se musí dělit do husté sítě křižovatek, bloků a uliček, aby zajistilo prostupnost (krátké konstituenty).

### 2. Město jako konstrukt, administrativní členění jako konstituent

* **Hypotéza:** Čím větší je město, tím **menší** je průměrná fyzická rozloha jeho katastrálních území (nebo městských částí).
* Vysvětlení se opět opírá o efektivitu a hustotu. Okrajové vesnice nebo malá města mají často obří, rozlehlé katastry zahrnující lesy a pole. Jakmile ale město roste do podoby metropole, jeho vnitřní prostor se zahušťuje a administrativní (či historické) celky v centru jsou prostorově titěrné (např. Praha 1, Praha 2), protože musí obsloužit obrovské množství obyvatel na malém prostoru.

---

### Jak by se to dalo technicky otestovat v Pythonu

Pokud tě láká ten první přístup (uliční síť), doporučuji opustit Wikipedii a sáhnout po knihovně **OSMnx**. Je to Python knihovna postavená nad OpenStreetMap, kterou vytvořil americký urbanista Geoff Boeing přesně pro účely CSS a analýzy měst.

Umožní ti to jedním řádkem kódu stáhnout kompletní uliční síť jakéhokoliv města a rovnou ti to spočítá metriky (včetně průměrné délky uličního segmentu):

```python
import osmnx as ox

# Stáhne uliční síť (graf) pro dané město
G_mohelnice = ox.graph_from_place("Mohelnice, Czech Republic", network_type="drive")
G_praha = ox.graph_from_place("Prague, Czech Republic", network_type="drive")

# Automaticky spočítá základní urbanistické metriky
stats_mohelnice = ox.basic_stats(G_mohelnice)
stats_praha = ox.basic_stats(G_praha)

# Získáme průměrnou délku uličního segmentu (v metrech)
print(stats_mohelnice['street_length_avg'])
print(stats_praha['street_length_avg'])

```

Pokud bys přes API ČSÚ (nebo RÚIAN) získal seznam třeba 100 českých měst s jejich populací/rozlohou a přes `osmnx` k nim v cyklu dosadil průměrnou délku jejich ulic, stačí tyto dva sloupečky vynést do grafu.

Pokud uvidíš klesající křivku odpovídající rovnici $y = a \cdot x^b$ (případně s korekčním faktorem $e^{-cx}$), našel jsi platnost Menzerath-Altmannova zákona v morfologii měst. A to je materiál na regulérní (a velmi originální) paper! Znělo by ti to jako smysluplný směr zkoumání?