# see: https://fastkml.readthedocs.org/en/latest/usage_guide.html#read-a-kml-file
# and: https://github.com/python-visualization/folium

from fastkml import kml
import pandas as pd
import folium

UNCLASSIFIED = '#808080'
ALL_ABILITIES = '#00FF00'
INTERMEDIATE = '#FFFF00'
DIFFICULT = '#FF0000'

difficulties = { 'u' : UNCLASSIFIED,
                 'e' : ALL_ABILITIES,
                 'i' : INTERMEDIATE,
                 'd' : DIFFICULT }

def read_kml(filename):
    f = open(filename, 'r')
    return f.read()


def process_kml(kml):
    the_map = kml.features().next()
    print("Map: %s" % (the_map.name))
    
    layers = the_map.features()

    segment_records = { 'name' : [],
                        'description' : [],
                        'polyline': [],
                        'district' : [],
                        'difficulty' : [],
                        'difficulty_code' : []
                    }
    
    for layer in layers:
        print("Layer: %s" % (layer.name))
        try:
            segments = layer.features()
        except:
            continue
        
        for segment in segments:
            print("Segment: %s" % (segment.name))
            try:
                polyline = [(g.y, g.x) for g in segment.geometry.geoms]
                segment_records['name'].append(segment.name)
                segment_records['description'].append(segment.description)
                segment_records['polyline'].append(polyline)
                segment_records['district'].append(layer.name)
                segment_records['difficulty'].append(UNCLASSIFIED)
                segment_records['difficulty_code'].append('u')

            except:
                print("no geometry")
                
    segment_df = pd.DataFrame(segment_records)
    
    return segment_df
    

def draw_folium_lines(folium_map, segment_df):
    for (index, polyline, difficulty) in segment_df[['polyline', 'difficulty']].itertuples():
        folium.PolyLine(polyline, color=difficulty, weight=1).add_to(folium_map)

    
def segments_to_map(map_osm, segment_df, included=['e', 'i'], filename='osm.html'):
    #map_osm = folium.Map(location=coords,tiles='Stamen Toner')    
    
    # Copy this by hand to greenways_edited.csv, edit in Open Office, fill in the difficulty codes.
    # Then re-run the script.
    segment_df.to_csv('greenways.csv',
                      columns=['name', 'difficulty_code', 'district', 'difficulty', 'description', 'polyline'])

    plot_df = segment_df.loc[segment_df['difficulty_code'].isin(included)]
        
    draw_lines(map_osm, plot_df)

    map_osm.create_map(path=filename)

def kmls_to_segments(kml_files):
    first = True
    
    for kml_file in kml_files:
        k = kml.KML()
        k.from_string(read_kml(kml_file))
        
        if first:
            segment_df = process_kml(k)
            first = False
        else:
            segment_df = segment_df.append(process_kml(k)).reset_index(drop=True)
            
    return segment_df


def bike_share_docks(folium_map, csv_file):
    dock_df = pd.read_csv(csv_file)

    for (_, lattitude, longitude, name) in dock_df[['lat', 'long', 'name']].itertuples():
        folium_map.simple_marker([lattitude, longitude], popup=name)
    
    

def csv_to_map(coords, segment_df, csv_file, output_html):
    edited_segment_df = pd.read_csv(csv_file, "\t")
    edited_segment_df['difficulty'] = edited_segment_df['difficulty_code'].map(lambda d: difficulties[d.lower()])
    segment_df = segment_df.reindex()
    edited_segment_df[['polyline']] = segment_df[['polyline']]
    
    map_osm = folium.Map(location=coords, tiles='Stamen Toner')
    draw_lines(map_osm, edited_segment_df)
    bike_share_docks(map_osm, '2015_station_data.csv')
    
    map_osm.create_map(path=output_html)
    
def get_folium_map(coords):
    get_folium_map.map= folium.Map(
        location=coords,
        tiles='Stamen Watercolor'
    )

    return get_folium_map.map

if __name__ == '__main__':
    coords = [47.6131746,-122.4878834] # Seattle
    # coords = [45.5236, -122.6750] # Portland

    # from http://seattlegreenways.org/neighborhoods/
    # Download the KML for the maps
    # Copy the .kmz file to kmz/
    # unzip <neighborhood>.kmz; mv doc.kml <neighborhood>.kml
    # eastlake and montlake weren't found on the page

    segments_df = kmls_to_segments(kml_files)

    segments_to_map(coords, segments_df)
    
    csv_to_map(coords, segments_df, 'greenways_edited.csv', 'osm2.html')
