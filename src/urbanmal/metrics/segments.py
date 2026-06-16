import networkx as nx
import geopandas as gpd
import pandas as pd
import osmnx as ox


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


def batch_segment_stats(cities: pd.DataFrame, name_col: str = "nazev", network_type: str = "drive") -> pd.DataFrame:
    """
    Iteruje přes DataFrame měst, pro každé stáhne síť a spočítá metriky segmentů.

    Vrací rozšířený DataFrame s novými sloupci: mean_m, median_m, std_m, count, error.
    """
    from src.urbanmal.data.osm import download_street_network

    records = []
    for _, row in cities.iterrows():
        entry = row.to_dict()
        try:
            G = download_street_network(row[name_col], network_type=network_type)
            stats = compute_segment_stats(G)
            entry.update(stats)
            entry["error"] = None
        except Exception as e:
            entry.update({"mean_m": None, "median_m": None, "std_m": None, "count": None})
            entry["error"] = str(e)
        records.append(entry)
    return pd.DataFrame(records)
