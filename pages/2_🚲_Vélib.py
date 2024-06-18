import streamlit as st
from millify import millify
import plotly.express as px
from utils import *

df = load_data_velib()

df = df[df['Station en fonctionnement'] == 'OUI']

st.header("Disponibilités des Vélib en temps réel", divider="rainbow")

col_1, col_2, col_3 = st.columns(3)

col_1.metric("Available mechanicals bikes", millify(df['Vélos mécaniques disponibles'].sum()))

col_2.metric("Available electric bikes", millify(df['Vélos électriques disponibles'].sum()))

col_3.metric("Available docks", millify(df['Nombre bornettes libres'].sum()))


st_graph_title('Nombre moyen de vélos disponibles, vélos électriques disponibles et bornettes libres')

fig = px.bar(df[['Vélos mécaniques disponibles', 'Vélos électriques disponibles', 'Nombre bornettes libres']].mean(),
             color=['Vélos mécaniques disponibles', 'Vélos électriques disponibles', 'Nombre bornettes libres'],
)
st.plotly_chart(fig)


st_graph_title('Nombre total de vélos disponibles par station')

fig = px.density_mapbox(df,
                        lat='latitude',
                        lon='longitude',
                        z='Vélos mécaniques disponibles',
                        radius=10,
                        center=dict(lat=48.8566, lon=2.3522),
                        zoom=10,
                        mapbox_style="carto-positron",
                        color_continuous_scale='Agsunset')
st.plotly_chart(fig)


st_graph_title('Stations avec trop peu de vélos disponibles et trop peu de bornettes libres')

col_1, col_2 = st.columns(2)

fig = px.bar(df[df['Nombre total vélos disponibles']<=3].sort_values('Nombre total vélos disponibles', ascending=False),
             x='Nom station',
             y='Nombre total vélos disponibles',
             orientation='v')
fig.update_traces(marker_color='lightcoral')
col_1.plotly_chart(fig)

fig = px.bar(df[df['Nombre bornettes libres']<=3].sort_values('Nombre bornettes libres', ascending=True),
             x='Nom station',
             y='Nombre bornettes libres',
             orientation='v')
fig.update_traces(marker_color='lightgreen')
col_2.plotly_chart(fig)


st_graph_title('Carte des stations avec le taux de remplissage')

fig = px.scatter_mapbox(df,
                        lat='latitude',
                        lon='longitude',
                        color='Filling ratio',
                        color_continuous_scale='RdBu',
                        size_max=15,
                        zoom=10,
                        mapbox_style='carto-positron',
                        hover_name='Nom station',
                        hover_data=['Filling ratio'])
st.plotly_chart(fig)

# st.title('Historical data 🕰️')

# fig = px.imshow(df_history.pivot_table(index='day_of_week', columns='hour', values='less_than_3_bikes', aggfunc='mean'), color_continuous_scale='peach')
# fig.update_xaxes(title='Hour')
# fig.update_yaxes(title='Day of the week')
# st.plotly_chart(fig)

# fig = px.imshow(df_history.pivot_table(index='day_of_week', columns='hour', values='less_than_3_docks', aggfunc='mean'), color_continuous_scale='Blugrn')
# fig.update_xaxes(title='Hour')
# fig.update_yaxes(title='Day of the week')
# st.plotly_chart(fig)
