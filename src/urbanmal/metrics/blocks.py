from pathlib import Path

import geopandas as gpd
import pandas as pd

from src.urbanmal.metrics._batch import run_resumable_batch

BLOCK_STAT_KEYS = ["mean_m2", "median_m2", "std_m2", "count"]


def compute_block_stats_from_areas(areas: pd.Series) -> dict:
    """
    Vypočítá statistiky z již známých ploch bloků (v m²).

    Vrací slovník s klíči: mean_m2, median_m2, std_m2, count.
    """
    areas = areas.dropna()
    return {
        "mean_m2": areas.mean(),
        "median_m2": areas.median(),
        "std_m2": areas.std(),
        "count": len(areas),
    }


def compute_block_stats(gdf: gpd.GeoDataFrame, crs_projected: str = "EPSG:3857") -> dict:
    """
    Vypočítá statistiky ploch městských bloků z GeoDataFrame polygonů.

    Plochy jsou počítány v metrech čtverečních (po reprojekci do metrického CRS).
    """
    gdf_proj = gdf.to_crs(crs_projected)
    return compute_block_stats_from_areas(gdf_proj.geometry.area)


def batch_block_stats(
    cities: pd.DataFrame,
    checkpoint_path: str | Path,
    name_col: str = "nazev",
    key_col: str = "kod",
) -> pd.DataFrame:
    """
    Iteruje přes DataFrame měst, pro každé stáhne bloky a spočítá metriky ploch.

    Průběžně zapisuje do `checkpoint_path` (CSV) – při přerušení lze bezpečně
    spustit znovu, dokončená města se přeskočí. Zobrazuje progress bar (tqdm).
    """
    from src.urbanmal.data.osm import download_urban_blocks

    def process_row(row: pd.Series) -> dict:
        try:
            gdf = download_urban_blocks(row[name_col])
            stats = compute_block_stats(gdf)
            stats["error"] = None
            return stats
        except Exception as e:
            return {**{k: None for k in BLOCK_STAT_KEYS}, "error": str(e)}

    return run_resumable_batch(
        cities, checkpoint_path, process_row, BLOCK_STAT_KEYS,
        key_col=key_col, desc="OSMnx bloky",
    )


def batch_block_stats_local(
    cities: pd.DataFrame,
    checkpoint_path: str | Path,
    all_blocks: gpd.GeoDataFrame,
    boundaries: gpd.GeoDataFrame,
    name_col: str = "nazev",
    key_col: str = "kod",
) -> pd.DataFrame:
    """
    Jako batch_block_stats, ale čte data z předem načtené tabulky všech bloků ČR
    (osm_local.load_all_blocks / cache_all_blocks) místo Overpass API.

    `all_blocks` je výsledek osm_local.load_all_blocks / cache_all_blocks.
    `boundaries` je výsledek osm_local.load_admin_boundaries / cache_admin_boundaries.
    """
    from src.urbanmal.data.osm_local import match_city_boundary, clip_blocks_for_city

    def process_row(row: pd.Series) -> dict:
        try:
            boundary = match_city_boundary(boundaries, row[name_col])
            if boundary is None:
                return {**{k: None for k in BLOCK_STAT_KEYS}, "error": "boundary_not_found"}
            blocks = clip_blocks_for_city(all_blocks, boundary.geometry)
            if blocks.empty:
                return {**{k: None for k in BLOCK_STAT_KEYS}, "error": "no_blocks_found"}
            stats = compute_block_stats_from_areas(blocks.geometry.area)
            stats["error"] = None
            return stats
        except Exception as e:
            return {**{k: None for k in BLOCK_STAT_KEYS}, "error": str(e)}

    return run_resumable_batch(
        cities, checkpoint_path, process_row, BLOCK_STAT_KEYS,
        key_col=key_col, desc="Lokální PBF bloky",
    )
