import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from shapely.geometry import Point
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import ast

import csv
import sys
csv.field_size_limit(10_000_000)    # <- Solución al error
suelo = gpd.read_file("datos_procesados/suelo_procesado.gpkg", layer="suelo")
trips = pd.read_csv("datos_procesados/trips_procesado.csv", sep=",", engine="python")
trips["duration"] = pd.to_timedelta(trips["duration"])

##Cuestiones necesarias
#trips[['lat_unlock', 'lon_unlock']] = trips['geolocation_unlock'].apply(extraer_coords)
#trips[['lat_lock', 'lon_lock']] = trips['geolocation_lock'].apply(extraer_coords)
    
#Reemplazar datos
#suelo["HILUCS"] = suelo["HILUCS"].replace(hilucs_dict)
#suelo["CODIIGE"] = suelo["CODIIGE"].replace(codiige_dict)
#suelo["SIOSE_DESC"] = suelo["SIOSE_CODE"].apply(decodificar_siose_code)
#Convertir fechas
trips['unlock_date'] = pd.to_datetime(trips['unlock_date'])
trips['lock_date'] = pd.to_datetime(trips['lock_date'])
trips['fecha'] = pd.to_datetime(trips["fecha"])


# ---------------------------
# 3. Entrada dinámica de ubicación
# ---------------------------

# Filtro por fecha
fecha_min = trips['fecha'].min()
fecha_max = trips['fecha'].max()

st.sidebar.title("Parámetros del Mapa")
lat_center = st.sidebar.number_input("Latitud central", value=40.4168, format="%.6f")
lon_center = st.sidebar.number_input("Longitud central", value=-3.7038, format="%.6f")
numero_de_viajes = st.sidebar.number_input("Numero de viajes", value=500)
zoom = st.sidebar.slider("Zoom inicial", 12, 17, 14)
fecha_sel = st.sidebar.date_input("Selecciona fecha", [fecha_min, fecha_max], min_value=fecha_min, max_value=fecha_max)
# Definir bounding box dinámico
dx, dy = 0.02, 0.02
xmin, xmax = lon_center - dx, lon_center + dx
ymin, ymax = lat_center - dy, lat_center + dy

# ---------------------------
# 4. Procesamiento del suelo
# ---------------------------
suelo_wgs84 = suelo.to_crs(epsg=4326)
suelo_zona = suelo_wgs84.cx[xmin:xmax, ymin:ymax]

# Asignar color por CODIIGE
categorias = suelo_zona['CODIIGE'].unique()
colores = plt.cm.tab20.colors
color_map = {cat: mcolors.to_hex(colores[i % len(colores)]) for i, cat in enumerate(categorias)}

def estilo_por_cobertura(feature):
    codiige = feature['properties']['CODIIGE']
    color = color_map.get(codiige, '#cccccc')
    return {
        'fillColor': color,
        'color': 'black',
        'weight': 0.3,
        'fillOpacity': 0.4
    }

# ---------------------------
# 5. Crear mapa base con Folium
# ---------------------------
m_comb = folium.Map(location=[lat_center, lon_center], zoom_start=zoom)

# Añadir suelo
folium.GeoJson(
    suelo_zona,
    name='Coberturas del Suelo',
    style_function=estilo_por_cobertura,
    tooltip=folium.GeoJsonTooltip(fields=['SIOSE_CODE', 'CODIIGE', 'HILUCS','SIOSE_DESC'])
).add_to(m_comb)

# ---------------------------
# 6. Añadir viajes al mapa
# ---------------------------
subset = trips.dropna(subset=['lat_unlock', 'lon_unlock', 'lat_lock', 'lon_lock']).head(numero_de_viajes)

for _, row in subset.iterrows():
    # Punto de inicio (verde)
    folium.CircleMarker(
        location=[row['lat_unlock'], row['lon_unlock']],
        radius=3,
        color='green',
        fill=True,
        fill_opacity=0.7
    ).add_to(m_comb)

    # Punto de fin (rojo)
    folium.CircleMarker(
        location=[row['lat_lock'], row['lon_lock']],
        radius=3,
        color='red',
        fill=True,
        fill_opacity=0.7
    ).add_to(m_comb)

    # Línea (azul)
    folium.PolyLine(
        locations=[[row['lat_unlock'], row['lon_unlock']], [row['lat_lock'], row['lon_lock']]],
        color='blue',
        weight=1,
        opacity=0.3
    ).add_to(m_comb)

# ---------------------------
# ---------------------------
# 6.1 Filtrar trips por fecha
# ---------------------------
trips_filtrado = trips[
    (trips["fecha"] >= pd.to_datetime(fecha_sel[0])) &
    (trips["fecha"] <= pd.to_datetime(fecha_sel[1]))
]
# Agrupar por fecha y calcular duración promedio en minutos
duracion_por_dia = trips_filtrado.groupby(trips_filtrado["fecha"].dt.date)["duration"].mean()
duracion_por_dia = duracion_por_dia.dt.total_seconds() / 60  # convertir a minutos

# 7. Mostrar mapa en la app
# ---------------------------
st.title("Visualizador de viajes y uso del suelo")
st.markdown("Explora el uso de bicicletas en relación con el tipo de suelo urbano.")
st_data = st_folium(m_comb, width=800, height=400)

# ---------------------------
# 8. Gráfico de duración promedio
# ---------------------------
st.markdown("### Duración promedio de viajes por día")

if not duracion_por_dia.empty:
    fig, ax = plt.subplots(figsize=(8, 4))
    duracion_por_dia.plot(ax=ax, marker="o", linestyle="-", color="orange")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Duración promedio (minutos)")
    ax.set_title("Duración promedio de viajes por día")
    ax.grid(True)
    st.pyplot(fig)
else:
    st.info("No hay viajes en el rango de fechas seleccionado.")

#Histogramas boxplo de duracion
st.markdown("### Distribución de duración de viajes (minutos)")
duraciones = trips_filtrado["duration"].dt.total_seconds() / 60

fig2, ax2 = plt.subplots()
ax2.hist(duraciones, bins=30, color="skyblue", edgecolor="black")
ax2.set_xlabel("Duración (minutos)")
ax2.set_ylabel("Frecuencia")
ax2.set_title("Histograma de duración de viajes")
st.pyplot(fig2)



#Mapa de calorpuntos de inici9o y fyn
from folium.plugins import HeatMap

puntos_inicio = subset[["lat_unlock", "lon_unlock"]].dropna().values.tolist()

HeatMap(puntos_inicio, radius=10).add_to(m_comb)


# ---------------------------
# 6.2 Calcular uso del suelo más frecuente (HILUCS) por día
# ---------------------------

# Crear GeoDataFrame con los puntos de desbloqueo
gdf_trips = gpd.GeoDataFrame(
    trips_filtrado,
    geometry=gpd.points_from_xy(trips_filtrado["lon_unlock"], trips_filtrado["lat_unlock"]),
    crs="EPSG:4326"
)

# Unir puntos con polígonos (uso del suelo)
gdf_union = gpd.sjoin(gdf_trips, suelo_wgs84, how="left", predicate="within")

# Agrupar por día y obtener el HILUCS más frecuente
hilucs_por_dia = (
    gdf_union.groupby(gdf_union["fecha"].dt.date)["HILUCS"]
    .agg(lambda x: x.mode().iloc[0] if not x.mode().empty else None)
)

# ---------------------------
# 9. Mostrar gráfico de uso del suelo más común
# ---------------------------
st.markdown("### Uso del suelo más frecuente por día (según ubicación de desbloqueo)")

if not hilucs_por_dia.empty:
    fig, ax = plt.subplots(figsize=(10, 4))
    hilucs_por_dia.value_counts().plot(kind="bar", ax=ax, color="purple")
    ax.set_ylabel("Número de días como más frecuente")
    ax.set_title("Usos del suelo más frecuentes en desbloqueos diarios")
    st.pyplot(fig)

    st.dataframe(hilucs_por_dia.reset_index().rename(columns={"fecha": "Fecha", "HILUCS": "Uso del suelo más frecuente"}))
else:
    st.info("No se encontraron usos del suelo en el rango de fechas seleccionado.")
