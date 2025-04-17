from flask import Flask, Response, render_template, jsonify, request
import pandas as pd
from sqlalchemy import create_engine
from keplergl import KeplerGl
import matplotlib.pyplot as plt
import io
import base64
import json
import plotly
import plotly.express as px


# === Flask app ===
app = Flask(__name__, static_folder='static', template_folder='templates')

# === DB Config ===
DB_USER = "testing1_415q_user"
DB_PASSWORD = "syezjh72qciEKZUCBIcR4LF6YkiH7aXK"
DB_HOST = "dpg-cvr1u8ngi27c738j3acg-a.singapore-postgres.render.com"
DB_PORT = "5432"
DB_NAME = "testing1_415q"
engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
query = "SELECT name, amenity, addr_city, state, latitude, longitude FROM health_facilities;"

# === Load GeoJSON for polygon ===
with open("data/geoBoundaries-MYS-ADM1_simplified.geojson", "r", encoding="utf-8") as f:
    geojson = json.load(f)

# # === Kepler Config (Point Map) ===
# point_map_config = {
#     'version': 'v1',
#     'config': {
#         'mapState': {
#             'latitude': 3.944035,
#             'longitude': 102.638624,
#             'zoom': 4.70
#         },
#         'visState': {
#             'layers': [{
#                 'id': 'poi_layer',
#                 'type': 'point',
#                 'config': {
#                     'dataId': 'health_facilities',
#                     'label': 'Health Facilities',
#                     'color': [0, 197, 255],
#                     'columns': {
#                         'lat': 'latitude',
#                         'lng': 'longitude',
#                         'altitude': None
#                     },
#                     'isVisible': True,
#                     'visConfig': {
#                         'radius': 10,
#                         'opacity': 0.8,
#                         'filled': True,
#                         'colorRange': {
#                             'name': 'Custom Amenity Colors',
#                             'type': 'custom',
#                             'category': 'Custom',
#                             'colors': ['#28a745', '#007bff']
#                         },
#                         'radiusRange': [0, 50]
#                     },
#                     'colorField': {
#                         'name': 'amenity',
#                         'type': 'string'
#                     },
#                     'colorScale': 'ordinal'
#                 }
#             }]
#         },
#         'interactionConfig': {
#             'tooltip': {
#                 'fieldsToShow': {
#                     'health_facilities': [
#                         'name', 'amenity', 'addr_city', 'latitude', 'longitude', 'state'
#                     ]
#                 },
#                 'enabled': True
#             }
#         }
#     }
# }


# # === Kepler Config (Polygon Map) ===
# polygon_map_config = {
#     'version': 'v1',
#     'config': {
#         'mapState': {
#             'latitude': 3.944035,
#             'longitude': 102.638624,
#             'zoom': 5
#         },
#         'visState': {
#             'layers': [
#                 {
#                     'id': 'polygon_layer',
#                     'type': 'geojson',
#                     'config': {
#                         'dataId': 'Malaysia_States',
#                         'label': 'State Polygons',
#                         'color': [255, 153, 31],
#                         'isVisible': True,
#                         'visConfig': {
#                             'opacity': 0.5,
#                             'thickness': 1,
#                             'strokeOpacity': 0.8,
#                             'strokeColor': [255, 255, 255],
#                             'colorRange': {
#                                 'name': 'ColorBrewer YlOrRd-6',
#                                 'type': 'sequential',
#                                 'category': 'ColorBrewer',
#                                 'colors': [
#                                     '#ffffb2', '#fed976', '#feb24c',
#                                     '#fd8d3c', '#f03b20', '#bd0026'
#                                 ]
#                             }
#                         }
#                     }
#                 }
#             ]
#         },
#         'interactionConfig': {
#             'tooltip': {
#                 'fieldsToShow': {
#                     'Malaysia_States': [
#                         'shapeName',
#                         'clinic_count',
#                         'pharmacy_count'
#                     ]
#                 },
#                 'enabled': True
#             }
#         }
#     }
# }

# === Kepler Config (Point Map) ===
point_map_config = {
    'version': 'v1',
    'config': {
        'mapState': {
            'latitude': 3.944035,
            'longitude': 102.638624,
            'zoom': 4.70
        },
        'interactionConfig': {
            'tooltip': {
                'fieldsToShow': {
                    'health_facilities': ['name', 'amenity', 'addr_city', 'latitude', 'longitude', 'state']
                },
                'enabled': True
            }
        }
    }
}

# === Kepler Config (Polygon Map) ===
polygon_map_config = {
    'version': 'v1',
    'config': {
        'mapState': {
            'latitude': 4.2105,
            'longitude': 101.9758,
            'zoom': 4.5
        },
        'visState': {
            'layers': [{
                'id': 'polygon_layer',
                'type': 'geojson',
                'config': {
                    'dataId': 'Malaysia_States',
                    'label': 'State Polygon',
                    'color': [255, 203, 153],
                    'highlightColor': [252, 242, 26, 255],
                    'columns': {
                        'geojson': '_geojson'
                    },
                    'isVisible': True,
                    'visConfig': {
                        'opacity': 0.5,
                        'thickness': 1,
                        'colorRange': {
                            'name': 'ColorBrewer YlOrRd-6',
                            'type': 'sequential',
                            'category': 'ColorBrewer',
                            'colors': ['#ffffb2', '#fecc5c', '#fd8d3c', '#f03b20', '#bd0026']
                        },
                        'filled': True
                    }
                }
            }],
            'interactionConfig': {
                'tooltip': {
                    'fieldsToShow': {
                        'Malaysia_States': ['shapeName', 'clinic_count', 'pharmacy_count']
                    },
                    'enabled': True
                }
            }
        }
    }
}



# === Donut Chart Generator ===
def create_donut_chart_data(clinic_count, pharmacy_count):
    data = pd.DataFrame({
        'amenity': ['clinic', 'pharmacy'],
        'count': [clinic_count, pharmacy_count]
    })

    fig = px.pie(
        data,
        names='amenity',
        values='count',
        hole=0.5,
        title='Amenity Distribution',
        color_discrete_sequence=px.colors.sequential.RdBu
    )

    # Separate fig into data and layout for Plotly
    return json.dumps({
        "data": fig.data,
        "layout": fig.layout
    }, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/')
def index():
    df = pd.read_sql(query, engine)
    df['amenity'] = df['amenity'].str.lower()

    clinic_count = df[df['amenity'] == 'clinic'].shape[0]
    pharmacy_count = df[df['amenity'] == 'pharmacy'].shape[0]
    total_facilities = clinic_count + pharmacy_count

    chart_json = create_donut_chart_data(clinic_count, pharmacy_count)

    print("Clinic:", clinic_count, "Pharmacy:", pharmacy_count)


    return render_template(
        'index.html',
        chart_json=chart_json,
        clinic_count=clinic_count,
        pharmacy_count=pharmacy_count,
        total_facilities=total_facilities
    )


# === Point Map Generator ===
def generate_point_map(df):
    df['amenity'] = df['amenity'].str.lower()
    df['Latitude'] = df['latitude']
    df['Longitude'] = df['longitude']

    map_ = KeplerGl(height=400)
    map_.add_data(data=df, name='health_facilities')  # Add data first
    map_.config = point_map_config                    # Then apply config

    print(json.dumps(map_.config, indent=2))          # 👈 Export actual config from Kepler

    html_bytes = map_._repr_html_()
    html = html_bytes.decode('utf-8')
    return Response(html.encode('utf-8'), mimetype='text/html')



# === Polygon Map Generator ===
def generate_polygon_map():
    df = pd.read_sql(query, engine)

    # Aggregate clinics and pharmacies by state
    counts = df.groupby('state')['amenity'].value_counts().unstack(fill_value=0).reset_index()
    counts.rename(columns={'clinic': 'clinic_count', 'pharmacy': 'pharmacy_count'}, inplace=True)

    # Merge with geojson properties
    for feature in geojson['features']:
        state_name = feature['properties'].get('shapeName', '').lower()
        match = counts[counts['state'].str.lower() == state_name]
        if not match.empty:
            feature['properties']['clinic_count'] = int(match['clinic_count'].values[0])
            feature['properties']['pharmacy_count'] = int(match['pharmacy_count'].values[0])
        else:
            feature['properties']['clinic_count'] = 0
            feature['properties']['pharmacy_count'] = 0

    # ✅ Debug print
    print("Debug GeoJSON Properties:", geojson['features'][0]['properties'])

    # ✅ Create map with proper ordering
    map_ = KeplerGl(height=400)
    map_.add_data(data=geojson, name='Malaysia_States')  # IMPORTANT: data name must match config
    map_.config = polygon_map_config  # Apply config after data is added

    # ✅ Export actual config back from Kepler if needed
    print(json.dumps(map_.config, indent=2))


    html_bytes = map_._repr_html_()
    html = html_bytes.decode('utf-8')

    return Response(html.encode('utf-8'), mimetype='text/html')



# === Map routes ===
@app.route('/map')
def map_all():
    df = pd.read_sql(query, engine)
    return generate_point_map(df)

@app.route('/map/clinic')
def map_clinic():
    df = pd.read_sql(query, engine)
    clinic_df = df[df['amenity'].str.lower() == 'clinic']
    return generate_point_map(clinic_df)

@app.route('/map/pharmacy')
def map_pharmacy():
    df = pd.read_sql(query, engine)
    pharmacy_df = df[df['amenity'].str.lower() == 'pharmacy']
    return generate_point_map(pharmacy_df)

@app.route('/map/polygon')
def map_polygon():
    return generate_polygon_map()

# === API: Table Data ===
@app.route('/api/data')
def api_data():
    filter_type = request.args.get('filter', '').lower()
    df = pd.read_sql(query, engine)

    if filter_type == 'clinic':
        df = df[df['amenity'].str.lower() == 'clinic']
    elif filter_type == 'pharmacy':
        df = df[df['amenity'].str.lower() == 'pharmacy']

    result = df[['name', 'amenity', 'state', 'latitude', 'longitude']].to_dict(orient='records')
    return jsonify(result)

# === API: KPI Data ===
@app.route('/api/kpi')
def api_kpi():
    df = pd.read_sql(query, engine)
    clinic_count = df[df['amenity'].str.lower() == 'clinic'].shape[0]
    pharmacy_count = df[df['amenity'].str.lower() == 'pharmacy'].shape[0]
    total_facilities = clinic_count + pharmacy_count

    return jsonify({
        'clinic_count': clinic_count,
        'pharmacy_count': pharmacy_count,
        'total_facilities': total_facilities
    })

# === Run Flask App ===
def run_flask():
    app.run(debug=True, port=5006, use_reloader=False)

if __name__ == "__main__":
    run_flask()

