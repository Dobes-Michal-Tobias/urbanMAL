import pandas as pd
from pathlib import Path


def load_czech_cities(path: str | Path) -> pd.DataFrame:
    """
    Načte tabulku českých obcí z ČSÚ / RÚIAN.

    Očekávané sloupce: nazev, populace, rozloha_km2, typ_sidla
    typ_sidla: 'obec' | 'mestys' | 'mesto' | 'statutarni_mesto'
    """
    path = Path(path)
    if path.suffix in {".xlsx", ".xls"}:
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)
    return df


def filter_cities(df: pd.DataFrame, min_population: int = 0, types: list[str] | None = None) -> pd.DataFrame:
    """Filtruje DataFrame obcí podle minimální populace a/nebo typu sídla."""
    mask = df["populace"] >= min_population
    if types:
        mask &= df["typ_sidla"].isin(types)
    return df[mask].reset_index(drop=True)
