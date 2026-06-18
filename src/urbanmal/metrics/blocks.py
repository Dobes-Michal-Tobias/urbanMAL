from pathlib import Path

import geopandas as gpd
import pandas as pd

from src.urbanmal.metrics._batch import run_resumable_batch

BLOCK_STAT_KEYS = ["mean_m2", "median_m2", "std_m2", "count"]


def compute_block_stats(gdf: gpd.GeoDataFrame, crs_projected: str = "EPSG:3857") -> dict:
    """
    Vypočítá statistiky ploch městských bloků z GeoDataFrame polygonů.

    Plochy jsou počítány v metrech čtverečních (po reprojekci do metrického CRS).
    Vrací slovník s klíči: mean_m2, median_m2, std_m2, count.
    """
    gdf_proj = gdf.to_crs(crs_projected)
    areas = gdf_proj.geometry.area.dropna()
    return {
        "mean_m2": areas.mean(),
        "median_m2": areas.median(),
        "std_m2": areas.std(),
        "count": len(areas),
    }


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
