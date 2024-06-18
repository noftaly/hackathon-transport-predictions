import streamlit as st
from utils import *
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

df, df_nb = load_data_validations()

df_station = df.groupby(['LATITUDE', 'LONGITUDE'])['NB_VALD'].sum().reset_index()
df_station['LIBELLE_ARRET'] = df.groupby(['LATITUDE', 'LONGITUDE'])['LIBELLE_ARRET'].unique().reset_index()['LIBELLE_ARRET']
df_station = df_station.round({'NB_VALD': 0})
# LIBELLE_ARRET is a list of strings, we need to convert it to a single string (separated by a comma)
df_station_conc = df_station.copy()
df_station_conc['LIBELLE_ARRET'] = df_station_conc['LIBELLE_ARRET'].apply(lambda x: ', '.join(x))

st.header("Validations dans les transports en commun d'Île-de-France Mobilité (réseau ferré, 1er semestre 2023)")
st.subheader("Réseau ferré, 1er semestre 2023", divider="rainbow")


st_graph_title('Carte des validations par station')

fig = px.scatter_mapbox(df_station_conc, lat="LATITUDE", lon="LONGITUDE", color="NB_VALD", size="NB_VALD", size_max=40, hover_name='LIBELLE_ARRET', hover_data=['NB_VALD'])
fig.update_layout(mapbox_style="carto-positron", mapbox_zoom=12, mapbox_center_lat = 48.8566, mapbox_center_lon = 2.3522, height=700)
st.plotly_chart(fig, theme=None)


st_graph_title('Nombre total de validations par station')

grouped_data = df_station_conc.sort_values('NB_VALD', ascending=False)

fig = px.bar(grouped_data.head(15),
              x='LIBELLE_ARRET',
              y='NB_VALD',
              labels={
                  'LIBELLE_ARRET': 'Station',
                  'NB_VALD': 'Nombre de validations'
              })

st.plotly_chart(fig)


st_graph_title('Nombre de validations dans la journée par catégorie de jour')

col1, col2 = st.columns(2)

grouped_data = df.groupby(['CAT_JOUR', 'HEURE'])['NB_VALD'].sum().reset_index()
readable_label = {
  'DIJFP': 'Dimanche, jours fériés, ponts',
  'JOHV': 'Jours ouvrés (hors vacances)',
  'SAHV': 'Samedi (hors vacances)',
  'JOVS': 'Jours ouvrés (vacances)',
  'SAVS': 'Samedi (vacances)',
}

grouped_data['CAT_JOUR'] = grouped_data['CAT_JOUR'].map(readable_label)

fig = px.line(grouped_data,
              x='HEURE',
              y='NB_VALD',
              color='CAT_JOUR',
              markers=True,
              labels={
                  'HEURE': 'Heure',
                  'NB_VALD': 'Nombre de validations',
                  'CAT_JOUR': 'Catégorie de jour'
              })

col1.plotly_chart(fig)


heatmap_data = df.pivot_table(index='CAT_JOUR', columns='HEURE', values='NB_VALD', aggfunc='sum')

fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(heatmap_data, cmap='viridis', fmt=".0f")
ax.set_xlabel('Heure')
ax.set_ylabel('Catégorie de jour')

col2.pyplot(fig)


st_graph_title('Prédictions du nombre de validations')

st.image('predictions.png', )


st_graph_title('Nombre de validations par catégorie de titre')

grouped_data = df_nb.groupby('CATEGORIE_TITRE')['NB_VALD'].sum().reset_index()
grouped_data = grouped_data.sort_values('NB_VALD', ascending=False)
grouped_data = grouped_data.replace({'CATEGORIE_TITRE': {'?': 'NON DEFINI', 'AUTRE TITRE': 'NON DEFINI'}})

fig = px.pie(grouped_data,
              values='NB_VALD',
              names='CATEGORIE_TITRE',
              labels={
                  'CATEGORIE_TITRE': 'Catégorie de titre',
                  'NB_VALD': 'Nombre de validations'
              })

st.plotly_chart(fig)


st_graph_title('Informations sur une station en particulier')

# flatten the list of station names from "df_station"
station_names = set([item for sublist in df_station['LIBELLE_ARRET'] for item in sublist])
chosen_station = st.selectbox('Choisissez une station', station_names)

station_data = df[df['LIBELLE_ARRET'].isin([chosen_station])]

grouped_data = station_data.groupby(['CAT_JOUR', 'HEURE'])['NB_VALD'].sum().reset_index()
readable_label = {
  'DIJFP': 'Dimanche, jours fériés, ponts',
  'JOHV': 'Jours ouvrés (hors vacances)',
  'SAHV': 'Samedi (hors vacances)',
  'JOVS': 'Jours ouvrés (vacances)',
  'SAVS': 'Samedi (vacances)',
}

grouped_data['CAT_JOUR'] = grouped_data['CAT_JOUR'].map(readable_label)

fig = px.line(grouped_data,
              x='HEURE',
              y='NB_VALD',
              color='CAT_JOUR',
              markers=True,
              labels={
                  'HEURE': 'Heure',
                  'NB_VALD': 'Nombre de validations',
                  'CAT_JOUR': 'Catégorie de jour'
              })

st.plotly_chart(fig)
