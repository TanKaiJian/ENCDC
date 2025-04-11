from flask import Flask, Response, render_template
import threading
import pandas as pd
from sqlalchemy import create_engine
from keplergl import KeplerGl
import matplotlib.pyplot as plt
import io
import base64

# === Flask app ===
app = Flask(__name__)

# === DB Config ===
DB_USER = "testing1_415q_user"
DB_PASSWORD = "syezjh72qciEKZUCBIcR4LF6YkiH7aXK"
DB_HOST = "dpg-cvr1u8ngi27c738j3acg-a.singapore-postgres.render.com"
DB_PORT = "5432"
DB_NAME = "testing1_415q"
engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
query = "SELECT name, amenity, latitude, longitude FROM health_facilities;"

# === Map config ===
config = {
    'version': 'v1',
    'config': {
        'mapState': {
            'latitude': 3.944035,
            'longitude': 102.638624,
            'zoom': 4.32
        }
    }
}

# === Donut chart generator ===
def create_donut_chart():
    df = pd.read_sql(query, engine)
    amenities_count = df['amenity'].value_counts()

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(amenities_count, labels=amenities_count.index, autopct='%1.1f%%', startangle=90, wedgeprops={'width': 0.4})
    ax.axis('equal')

    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format='png')
    img_bytes.seek(0)
    img_base64 = base64.b64encode(img_bytes.read()).decode('utf-8')

    return img_base64

# === Routes ===
@app.route('/')
def index():
    chart_image = create_donut_chart()
    return render_template('index.html', chart_image=chart_image)

@app.route('/map')
def map_all():
    df = pd.read_sql(query, engine)
    map_ = KeplerGl(height=600)
    map_.add_data(data=df, name='All Health Facilities')
    map_.config = config
    return Response(map_._repr_html_(), mimetype='text/html')

@app.route('/map/clinic')
def map_clinic():
    df = pd.read_sql(query, engine)
    clinic_df = df[df['amenity'].str.lower() == 'clinic']
    map_ = KeplerGl(height=600)
    map_.add_data(data=clinic_df, name='Clinics Only')
    map_.config = config
    return Response(map_._repr_html_(), mimetype='text/html')

# === Run Flask ===
def run_flask():
    app.run(debug=True, port=5006, use_reloader=False)

if __name__ == "__main__":
    run_flask()
