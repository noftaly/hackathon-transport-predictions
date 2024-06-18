import datetime
import plotly.express as px
import streamlit as st
import pandas as pd
import requests
import urllib.parse
import pickle
import geopy.distance
from utils import *

df_validations, df_nb_validations = load_data_validations()
df_realtime_velib = load_data_velib()

@st.cache_data
def get_model():
    model = pickle.load(open('./model.pkl', 'rb'))
    preprocessor = pickle.load(open('./preprocessor.pkl', 'rb'))

    return model, preprocessor

def predict(input_data):
    categorical_features = ['VACANCES', 'JOUR_OUVRE', 'SAMEDI', 'DIMANCHE_JOUR_FERIE']
    numeric_features = ['lda', 'HEURE', 'LATITUDE', 'LONGITUDE']

    model, preprocessor = get_model()

    new_data = input_data
    new_data = new_data.dropna()

    X = new_data[categorical_features + numeric_features]

    X_preprocessed = preprocessor.transform(X)

    return model.predict(X_preprocessed)

def get_position(address, zipcode):
    url = f"https://api.geoapify.com/v1/geocode/search?name={urllib.parse.quote(address)}&postcode={urllib.parse.quote(zipcode)}&lang=fr&limit=5&format=json&apiKey=a8e69276e81648a9b95891d004a69241&bias=circle:2.341142027832575,48.8610069348303,30000|countrycode:fr"
    response = requests.get(url, headers={"Accept": "application/json"})
    return response.json()

st.title("🗺️ Autour de chez vous")

with st.form('address'):
    col1, col2 = st.columns(2)
    address = col1.text_input("Donnez votre adresse")
    zipcode = col2.text_input("Donnez votre code postal")
    chosen_hour = st.select_slider("Dans combien d'heures partez-vous ?", options=range(0, 10))

    submit = st.form_submit_button('Rechercher')

if submit:
    data = get_position(address, zipcode)

    if "results" not in data:
        st.write("Rien ne correspond à votre recherche.")
    else:
        user_pos = data["results"][0]

        st.write(f"Votre position: {user_pos['formatted']}")

        with st.spinner('Calcul...'):
            SEARCH_RADIUS = 0.05

            df_validations_user = df_validations.copy()
            # Keep only values within ±SEARCH_RADIUS latitude/longitude
            df_validations_user = df_validations_user[(df_validations_user['LATITUDE'] >= user_pos['lat'] - SEARCH_RADIUS) & (df_validations_user['LATITUDE'] <= user_pos['lat'] + SEARCH_RADIUS)]
            df_validations_user = df_validations_user[(df_validations_user['LONGITUDE'] >= user_pos['lon'] - SEARCH_RADIUS) & (df_validations_user['LONGITUDE'] <= user_pos['lon'] + SEARCH_RADIUS)]

            df_validations_user['distance'] = df_validations_user.apply(lambda x: geopy.distance.distance((x['LATITUDE'], x['LONGITUDE']), (user_pos['lat'], user_pos['lon'])).m, axis=1)
            df_validations_user = df_validations_user.drop_duplicates(subset=['LIBELLE_ARRET'])
            df_validations_user = df_validations_user.sort_values('distance', ascending=True).head(5)

            # Keep only values within ±SEARCH_RADIUS latitude/longitude
            df_realtime_velib = df_realtime_velib[(df_realtime_velib['latitude'] >= user_pos['lat'] - SEARCH_RADIUS) & (df_realtime_velib['latitude'] <= user_pos['lat'] + SEARCH_RADIUS)]
            df_realtime_velib = df_realtime_velib[(df_realtime_velib['longitude'] >= user_pos['lon'] - SEARCH_RADIUS) & (df_realtime_velib['longitude'] <= user_pos['lon'] + SEARCH_RADIUS)]
            df_realtime_velib['distance'] = df_realtime_velib.apply(lambda x: geopy.distance.distance((x['latitude'], x['longitude']), (user_pos['lat'], user_pos['lon'])).m, axis=1)
            df_realtime_velib = df_realtime_velib.sort_values('distance', ascending=True).head(5)

        poi_user = {
            "latitude": user_pos['lat'],
            "longitude": user_pos['lon'],
            "type": "Votre position"
        }
        poi_user = pd.DataFrame([poi_user])

        poi_transports = df_validations_user[['LATITUDE', 'LONGITUDE']]
        poi_transports['type'] = 'Gare'
        poi_transports = poi_transports.rename(columns={'LATITUDE': 'latitude', 'LONGITUDE': 'longitude'})

        poi_velib = df_realtime_velib[['latitude', 'longitude']]
        poi_velib['type'] = 'Vélib\''

        poi = pd.concat([poi_user, poi_transports, poi_velib])

        fig = px.scatter_mapbox(poi,
                                lat="latitude",
                                lon="longitude",
                                zoom=13,
                                mapbox_style="carto-positron",
                                color="type",
                                hover_name='type',
                                hover_data=['type'],
                                height=700)

        fig.update_traces(marker=dict(size=12))

        st.plotly_chart(fig)

        current_hour = datetime.datetime.now().hour
        target_hour = (current_hour + chosen_hour) % 24
        st.write(f"Vous partez à {target_hour}h.")

        input_data = df_validations_user[['lda', 'LATITUDE', 'LONGITUDE']].copy()
        input_data['HEURE'] = target_hour
        input_data['VACANCES'] = 0
        input_data['JOUR_OUVRE'] = 1
        input_data['SAMEDI'] = 0
        input_data['DIMANCHE_JOUR_FERIE'] = 0


        predictions = predict(input_data)

        data = df_validations_user[['LIBELLE_ARRET', 'distance']]
        data['distance'] = data['distance'].apply(lambda x: round(x, 0))
        data['predictions'] = predictions
        data['predictions'] = data['predictions'].apply(lambda x: round(x, 0))

        data = data.rename({
            'LIBELLE_ARRET': 'Nom station',
            'distance': 'Distance (m)',
            'predictions': 'Nombre de validations horaires prévues'
        }, axis=1)

        st.write("🚇 Les stations de métro les plus proches")
        st.dataframe(data, hide_index=True)

        data = df_realtime_velib[['Nom station', 'distance', 'Nombre total vélos disponibles']]
        data['distance'] = data['distance'].apply(lambda x: round(x, 0))

        data = data.rename({
            'Nom station': 'Nom station',
            'distance': 'Distance (m)',
            'Nombre total vélos disponibles': 'Nombre total de vélos disponibles'
        }, axis=1)

        st.write("🚲 Les stations de vélib les plus proches")
        st.dataframe(data, hide_index=True)

else:
    st.write("Choisissez une adresse pour trouver les gares et stations de Vélib' à proximité !")
