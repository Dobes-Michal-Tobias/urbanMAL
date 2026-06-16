import geopandas as gpd
import pandas as pd


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


def batch_block_stats(cities: pd.DataFrame, name_col: str = "nazev") -> pd.DataFrame:
    """
    Iteruje přes DataFrame měst, pro každé stáhne bloky a spočítá metriky ploch.

    Vrací rozšířený DataFrame s novými sloupci: mean_m2, median_m2, std_m2, count, error.
    """
    from src.urbanmal.data.osm import download_urban_blocks

    records = []
    for _, row in cities.iterrows():
        entry = row.to_dict()
        try:
            gdf = download_urban_blocks(row[name_col])
            stats = compute_block_stats(gdf)
            entry.update(stats)
            entry["error"] = None
        except Exception as e:
            entry.update({"mean_m2": None, "median_m2": None, "std_m2": None, "count": None})
            entry["error"] = str(e)
        records.append(entry)
    return pd.DataFrame(records)
