import osmnx as ox
import networkx as nx
import geopandas as gpd


def download_street_network(place: str, network_type: str = "drive") -> nx.MultiDiGraph:
    """Stáhne uliční síť pro zadané místo z OpenStreetMap."""
    return ox.graph_from_place(place, network_type=network_type)


def download_urban_blocks(place: str) -> gpd.GeoDataFrame:
    """Stáhne polygony městských bloků pro zadané místo."""
    tags = {"landuse": True, "building": True}
    gdf = ox.features_from_place(place, tags=tags)
    return gdf[gdf.geometry.geom_type.isin(["Polygon", "MultiPolygon"])].copy()


def get_graph_edges(G: nx.MultiDiGraph) -> gpd.GeoDataFrame:
    """Vrátí hrany grafu jako GeoDataFrame (každá hrana = jeden uliční segment)."""
    _, edges = ox.graph_to_gdfs(G)
    return edges
