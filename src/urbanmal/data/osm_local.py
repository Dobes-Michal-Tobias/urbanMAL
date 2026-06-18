from pathlib import Path

import geopandas as gpd
import pandas as pd


# Sloupce, které GDAL OSM driver zachovává jako přímé atributy (ne v other_tags)
_BOUNDARY_COLS = ["name", "boundary", "admin_level", "geometry"]
_STREET_COLS = ["name", "highway", "geometry"]
_BLOCK_COLS = ["name", "building", "landuse", "geometry"]


# GDAL OSM driver neumí prostorový index a `bbox`/`where` filtr při čtení .pbf
# stejně provede plný lineární průchod celým souborem (~190 s pro celou ČR,
# nezávisle na velikosti výřezu). Proto se data čtou JEDNOU pro celou zemi
# (load_all_*) a kešují; per-město filtrování (clip_*_for_city) je pak čistě
# in-memory operace s prostorovým indexem (geopandas .sindex) – řádově rychlejší.


def load_admin_boundaries(pbf_path: str | Path, admin_level: str | None = "8") -> gpd.GeoDataFrame:
    """Načte administrativní hranice z .osm.pbf (vrstva 'multipolygons'). admin_level='8' = obce v ČR."""
    gdf = gpd.read_file(pbf_path, layer="multipolygons", columns=_BOUNDARY_COLS,
                        where="boundary = 'administrative'")
    if admin_level is not None:
        gdf = gdf[gdf["admin_level"] == admin_level]
    return gdf.reset_index(drop=True)


def cache_admin_boundaries(pbf_path: str | Path, cache_path: str | Path, admin_level: str | None = "8") -> gpd.GeoDataFrame:
    """Načte hranice (load_admin_boundaries) a uloží do GeoJSON cache; při opakovaném volání cache jen načte."""
    cache_path = Path(cache_path)
    if cache_path.exists():
        return gpd.read_file(cache_path)
    gdf = load_admin_boundaries(pbf_path, admin_level=admin_level)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(cache_path, driver="GeoJSON")
    return gdf


def match_city_boundary(boundaries: gpd.GeoDataFrame, city_name: str, fallback_nominatim: bool = True):
    """
    Najde polygon hranice pro dané jméno města. Při více shodách (stejný název
    ve více okresech) vrátí největší polygon (typicky správné město, ne malá osada).

    Některé velmi komplexní hranice (např. Praha – desítky dílčích částí) nemusí
    GDAL OSM driver správně sestavit a v `multipolygons` vrstvě chybí. Pro takové
    případy je k dispozici fallback přes OSMnx/Nominatim (lehký, jednorázový dotaz,
    odlišný server než Overpass – nehrozí stejné rate-limit blokování).
    """
    matches = boundaries[boundaries["name"] == city_name]
    if not matches.empty:
        if len(matches) > 1:
            areas = matches.geometry.to_crs(3857).area
            matches = matches.loc[[areas.idxmax()]]
        return matches.iloc[0]

    if fallback_nominatim:
        import osmnx as ox
        try:
            gdf = ox.geocode_to_gdf(f"{city_name}, Czech Republic")
            row = gdf.iloc[0].copy()
            row["name"] = city_name
            return row
        except Exception:
            return None
    return None


def load_all_streets(pbf_path: str | Path, crs_projected: str = "EPSG:3857") -> gpd.GeoDataFrame:
    """
    Načte VŠECHNY ways s tagem `highway` z .osm.pbf najednou (jeden průchod souborem).

    Vrací GeoDataFrame se sloupcem 'length' (m, po reprojekci do metrického CRS).
    """
    edges = gpd.read_file(pbf_path, layer="lines", columns=_STREET_COLS, where="highway IS NOT NULL")
    edges = edges.to_crs(crs_projected)
    edges["length"] = edges.geometry.length
    return edges


def cache_all_streets(pbf_path: str | Path, cache_path: str | Path) -> gpd.GeoDataFrame:
    """Načte (load_all_streets) a uloží do Parquet cache; při opakovaném volání cache jen načte."""
    cache_path = Path(cache_path)
    if cache_path.exists():
        return gpd.read_parquet(cache_path)
    gdf = load_all_streets(pbf_path)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_parquet(cache_path)
    return gdf


def load_all_blocks(pbf_path: str | Path, crs_projected: str = "EPSG:3857") -> gpd.GeoDataFrame:
    """
    Načte VŠECHNY polygony s tagem `building` nebo `landuse` z .osm.pbf najednou.

    Vrací GeoDataFrame reprojektovaný do metrického CRS (plochy se počítají později).
    """
    blocks = gpd.read_file(
        pbf_path, layer="multipolygons", columns=_BLOCK_COLS,
        where="building IS NOT NULL OR landuse IS NOT NULL",
    )
    return blocks.to_crs(crs_projected)


def cache_all_blocks(pbf_path: str | Path, cache_path: str | Path) -> gpd.GeoDataFrame:
    """Načte (load_all_blocks) a uloží do Parquet cache; při opakovaném volání cache jen načte."""
    cache_path = Path(cache_path)
    if cache_path.exists():
        return gpd.read_parquet(cache_path)
    gdf = load_all_blocks(pbf_path)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_parquet(cache_path)
    return gdf


def _to_projected(boundary_geom, crs_projected: str = "EPSG:3857"):
    """Hranice z load_admin_boundaries / Nominatim jsou v EPSG:4326 – převede na metrický CRS."""
    return gpd.GeoSeries([boundary_geom], crs="EPSG:4326").to_crs(crs_projected).iloc[0]


def clip_streets_for_city(all_streets: gpd.GeoDataFrame, boundary_geom, crs_projected: str = "EPSG:3857") -> gpd.GeoDataFrame:
    """Vyfiltruje z předem načtených ulic (load_all_streets) jen ty uvnitř hranice města."""
    boundary_proj = _to_projected(boundary_geom, crs_projected)
    minx, miny, maxx, maxy = boundary_proj.bounds
    candidates = all_streets.cx[minx:maxx, miny:maxy]
    if candidates.empty:
        return candidates
    return candidates[candidates.intersects(boundary_proj)]


def clip_blocks_for_city(all_blocks: gpd.GeoDataFrame, boundary_geom, crs_projected: str = "EPSG:3857") -> gpd.GeoDataFrame:
    """Vyfiltruje z předem načtených bloků (load_all_blocks) jen ty uvnitř hranice města."""
    boundary_proj = _to_projected(boundary_geom, crs_projected)
    minx, miny, maxx, maxy = boundary_proj.bounds
    candidates = all_blocks.cx[minx:maxx, miny:maxy]
    if candidates.empty:
        return candidates
    return candidates[candidates.intersects(boundary_proj)]
