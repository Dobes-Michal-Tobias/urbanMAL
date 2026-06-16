import pandas as pd
from pathlib import Path


# Mapování STATUS_KOD (RÚIAN UI_OBEC.csv) na čitelné typy sídel
_STATUS_MAP = {
    "1": "vojensky_ujezd",
    "2": "obec",
    "3": "mesto",
    "4": "statutarni_mesto",
    "5": "hlavni_mesto",
    "6": "mestys",
}


def load_ruian_obce(path: str | Path) -> pd.DataFrame:
    """
    Načte rejstřík obcí z RÚIAN (UI_OBEC.csv).

    Vrací DataFrame s aktivními záznamy (PLATI_DO prázdné):
    kod, nazev, status_kod, typ_sidla, okres_kod
    """
    df = pd.read_csv(
        path,
        sep=";",
        encoding="cp1250",
        dtype=str,
    )
    # Jen aktuálně platné záznamy (PLATI_DO = NaN znamená bez data ukončení)
    df = df[df["PLATI_DO"].isna()].copy()
    df = df.rename(columns={
        "KOD": "kod",
        "NAZEV": "nazev",
        "STATUS_KOD": "status_kod",
        "OKRES_KOD": "okres_kod",
    })
    df["typ_sidla"] = df["status_kod"].map(_STATUS_MAP).fillna("neznamy")
    return df[["kod", "nazev", "status_kod", "typ_sidla", "okres_kod"]].reset_index(drop=True)


def load_csu_population(path: str | Path) -> pd.DataFrame:
    """
    Načte počty obyvatel obcí z ČSÚ (soubor 1300722503.xlsx, k 1. 1. 2025).

    Vrací DataFrame: kod_obce (str), nazev, populace_celkem, populace_muzi, populace_zeny
    Data začínají na řádku 6 (index 5), každý kraj má vloženou hlavičkovou řádku.
    """
    raw = pd.read_excel(path, header=None, dtype=str)

    records = []
    for _, row in raw.iterrows():
        okres_val = str(row[0]).strip() if pd.notna(row[0]) else ""
        kod_val   = str(row[1]).strip() if pd.notna(row[1]) else ""
        nazev_val = str(row[2]).strip() if pd.notna(row[2]) else ""
        pop_val   = str(row[3]).strip() if pd.notna(row[3]) else ""
        pop_m     = str(row[4]).strip() if pd.notna(row[4]) else ""
        pop_z     = str(row[5]).strip() if pd.notna(row[5]) else ""

        # Přeskočit řádky bez číselného kódu obce
        if not kod_val.isdigit():
            continue

        try:
            records.append({
                "kod":               kod_val,
                "nazev":             nazev_val,
                "populace_celkem":   int(pop_val.replace("\xa0", "").replace(" ", "")),
                "populace_muzi":     int(pop_m.replace("\xa0", "").replace(" ", "")),
                "populace_zeny":     int(pop_z.replace("\xa0", "").replace(" ", "")),
            })
        except ValueError:
            continue

    return pd.DataFrame(records)


def build_municipalities(
    ruian_path: str | Path,
    population_path: str | Path,
) -> pd.DataFrame:
    """
    Spojí RÚIAN rejstřík s populačními daty ČSÚ.

    Výsledný DataFrame: kod, nazev, typ_sidla, status_kod, okres_kod,
                        populace_celkem, populace_muzi, populace_zeny
    """
    ruian = load_ruian_obce(ruian_path)
    pop   = load_csu_population(population_path)

    df = ruian.merge(pop[["kod", "populace_celkem", "populace_muzi", "populace_zeny"]],
                     on="kod", how="left")
    return df


def filter_urban(
    df: pd.DataFrame,
    types: list[str] | None = None,
    min_population: int = 0,
) -> pd.DataFrame:
    """
    Filtruje pouze urbánní sídla vhodná pro analýzu.

    Výchozí výběr: město, statutarni_mesto, hlavni_mesto, mestys
    """
    if types is None:
        types = ["mesto", "statutarni_mesto", "hlavni_mesto", "mestys"]
    mask = df["typ_sidla"].isin(types) & (df["populace_celkem"] >= min_population)
    return df[mask].reset_index(drop=True)
