from ipyleaflet import (
    Polyline,
    Map,
    basemaps
)


LINE_WEIGHT=1
OPACITY=1.0

UNCLASSIFIED = '#808080'
ALL_ABILITIES = '#00FF00'
INTERMEDIATE = '#FFFF00'
DIFFICULT = '#FF0000'

difficulties = { 'u' : UNCLASSIFIED,
                 'e' : ALL_ABILITIES,
                 'i' : INTERMEDIATE,
                 'd' : DIFFICULT }

#_BACKGROUND=basemaps.Stamen.Watercolor
#_BACKGROUND=basemaps.Strava.Ride
#_BACKGROUND=basemaps.CartoDB.Positron
#_BACKGROUND=basemaps.Stamen.Toner
_BACKGROUND=basemaps.Esri.NatGeoWorldMap

def get_map(coords):
    get_map.folium_map = Map(
        center=coords, zoom=10,
        basemap=_BACKGROUND)

    return get_map.folium_map

def draw_lines(folium_map, segment_df):
    for (index, poly_coords, difficulty) in segment_df[['polyline','difficulty_code']].itertuples():
        line_color = difficulties[difficulty]
        pl = Polyline(
            locations=poly_coords,
            color=line_color,
            #fill_color=line_color,
            weight=LINE_WEIGHT,
            opacity=OPACITY)
        folium_map += pl