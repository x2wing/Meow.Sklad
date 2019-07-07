from ipyleaflet import Map, basemaps, basemap_to_tiles

def foo(p):
    print(p)

m = Map(
    layers=(basemap_to_tiles(basemaps.NASAGIBS.ModisTerraTrueColorCR, "2017-04-08"), ),
    center=(52.204793, 360.121558),
    zoom=4, 
)

m.on_interaction(foo)