from pathlib import Path

import networkx as nx
import geopandas as gpd
import pandas as pd
import osmnx as ox

from src.urbanmal.metrics._batch import run_resumable_batch

SEGMENT_STAT_KEYS = ["mean_m", "median_m", "std_m", "count"]


def compute_segment_stats(G: nx.MultiDiGraph) -> dict:
    """
    Vypočítá statistiky délek uličních segmentů z grafu.

    Vrací slovník s klíči: mean_m, median_m, std_m, count.
    """
    _, edges = ox.graph_to_gdfs(G)
    lengths = edges["length"].dropna()
    return {
        "mean_m": lengths.mean(),
        "median_m": lengths.median(),
        "std_m": lengths.std(),
        "count": len(lengths),
    }


def batch_segment_stats(
    cities: pd.DataFrame,
    checkpoint_path: str | Path,
    name_col: str = "nazev",
    key_col: str = "kod",
    network_type: str = "drive",
) -> pd.DataFrame:
    """
    Iteruje přes DataFrame měst, pro každé stáhne síť a spočítá metriky segmentů.

    Průběžně zapisuje do `checkpoint_path` (CSV) – při přerušení lze bezpečně
    spustit znovu, dokončená města se přeskočí. Zobrazuje progress bar (tqdm).
    """
    from src.urbanmal.data.osm import download_street_network

    def process_row(row: pd.Series) -> dict:
        try:
            G = download_street_network(row[name_col], network_type=network_type)
            stats = compute_segment_stats(G)
            stats["error"] = None
            return stats
        except Exception as e:
            return {**{k: None for k in SEGMENT_STAT_KEYS}, "error": str(e)}

    return run_resumable_batch(
        cities, checkpoint_path, process_row, SEGMENT_STAT_KEYS,
        key_col=key_col, desc=f"OSMnx segmenty ({network_type})",
    )
