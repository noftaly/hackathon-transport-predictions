import streamlit as st
import pandas as pd

@st.cache_data
def load_data_validations():
    df = pd.read_csv('validations-2023-S1.csv')
    df_nb = pd.read_csv('validations-nombre-2023-S1.csv', sep=";")

    return df, df_nb

@st.cache_data
def load_data_velib():
    df = pd.read_csv('https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/exports/csv?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B', sep=';')

    df = df.dropna(subset=['Coordonnées géographiques'])

    df['latitude'] = df['Coordonnées géographiques'].apply(lambda x: float(x.split(',')[0]))
    df['longitude'] = df['Coordonnées géographiques'].apply(lambda x: float(x.split(',')[1]))

    df['Filling ratio'] = df['Nombre total vélos disponibles'] / df['Capacité de la station']
    df['Filling ratio'] = df['Filling ratio'].apply(lambda x: min(x, 1))

    # df_history = pd.read_csv('historique_stations.csv', names=['date', 'capacity', 'mechanical', 'ebike', 'station_name', 'position', 'unkown'])
    # df_history['date'] = pd.to_datetime(df_history['date'])
    # df_history['hour'] = df_history['date'].dt.hour
    # df_history['day_of_week'] = df_history['date'].dt.dayofweek
    # df_history['day_of_week'] = df_history['day_of_week'].map({0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'})
    # df_history['bikes_available'] = df_history['mechanical'] + df_history['ebike']
    # df_history['bikes_ratio'] = df_history['bikes_available'] / df_history['capacity']
    # df_history['available_docks'] = df_history['capacity'] - df_history['bikes_available']

    # df_history['less_than_3_bikes'] = (df_history['bikes_available'] <= 3).astype(int)
    # df_history['less_than_3_docks'] = (df_history['available_docks'] <= 3).astype(int)

    return df

def st_graph_title(name):
    st.markdown(f'#### <center style="margin-top: 50px">{name}</center>', unsafe_allow_html=True)
