from pathlib import Path

import networkx as nx
import geopandas as gpd
import pandas as pd
import osmnx as ox

from src.urbanmal.metrics._batch import run_resumable_batch

SEGMENT_STAT_KEYS = ["mean_m", "median_m", "std_m", "count"]


def compute_segment_stats_from_lengths(lengths: pd.Series) -> dict:
    """
    Vypočítá statistiky z již známých délek segmentů (v metrech).

    Vrací slovník s klíči: mean_m, median_m, std_m, count.
    """
    lengths = lengths.dropna()
    return {
        "mean_m": lengths.mean(),
        "median_m": lengths.median(),
        "std_m": lengths.std(),
        "count": len(lengths),
    }


def compute_segment_stats(G: nx.MultiDiGraph) -> dict:
    """Vypočítá statistiky délek uličních segmentů z OSMnx grafu (viz data/osm.py)."""
    _, edges = ox.graph_to_gdfs(G)
    return compute_segment_stats_from_lengths(edges["length"])


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


def batch_segment_stats_local(
    cities: pd.DataFrame,
    checkpoint_path: str | Path,
    all_streets: gpd.GeoDataFrame,
    boundaries: gpd.GeoDataFrame,
    name_col: str = "nazev",
    key_col: str = "kod",
) -> pd.DataFrame:
    """
    Jako batch_segment_stats, ale čte data z předem načtené tabulky všech ulic ČR
    (osm_local.load_all_streets / cache_all_streets) místo Overpass API nebo
    opakovaného čtení .pbf souboru. Per-město filtrování je čistě in-memory
    operace (spatial index) – řádově rychlejší než dotazy na .pbf nebo Overpass.

    `all_streets` je výsledek osm_local.load_all_streets / cache_all_streets.
    `boundaries` je výsledek osm_local.load_admin_boundaries / cache_admin_boundaries.
    """
    from src.urbanmal.data.osm_local import match_city_boundary, clip_streets_for_city

    def process_row(row: pd.Series) -> dict:
        try:
            boundary = match_city_boundary(boundaries, row[name_col])
            if boundary is None:
                return {**{k: None for k in SEGMENT_STAT_KEYS}, "error": "boundary_not_found"}
            edges = clip_streets_for_city(all_streets, boundary.geometry)
            if edges.empty:
                return {**{k: None for k in SEGMENT_STAT_KEYS}, "error": "no_edges_found"}
            stats = compute_segment_stats_from_lengths(edges["length"])
            stats["error"] = None
            return stats
        except Exception as e:
            return {**{k: None for k in SEGMENT_STAT_KEYS}, "error": str(e)}

    return run_resumable_batch(
        cities, checkpoint_path, process_row, SEGMENT_STAT_KEYS,
        key_col=key_col, desc="Lokální PBF segmenty",
    )
