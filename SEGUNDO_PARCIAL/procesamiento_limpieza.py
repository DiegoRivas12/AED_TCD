import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from shapely.geometry import Point
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import ast
#USOS DEL SUELO
hilucs_dict = {
    110: "1_1_Agriculture",
    120: "1_2_Forestry",
    130: "1_3_MiningAndQuarrying",
    140: "1_4_AquacultureAndFishing",
    200: "2_SecondaryProduction",
    310: "3_1_CommercialServices",
    330: "3_3_CommunityServices",
    340: "3_4_CulturalEntertainmentAndRecreationalServices",
    410: "4_1_TransportNetworks",
    430: "4_3_Utilities",
    500: "5_ResidentialUse",
    610: "6_1_TransitionalAreas",
    620: "6_2_AbandonedAreas",
    631: "6_3_1_LandAreasNotInOtherEconomicUse",
    632: "6_3_2_WaterAreasNotInOtherEconomicUse",
    660: "6_6_NotKnownUse"
}
#CUBIERTAS DEL SUELO
codiige_dict = {
    111: "Casco",
    112: "Ensanche",
    113: "Discontinuo",
    114: "Zona verde urbana",
    121: "Instalación agrícola y/o ganadera",
    122: "Instalación forestal",
    123: "Extracción minera",
    130: "Industrial",
    140: "Servicio dotacional",
    150: "Asentamiento agrícola y huerta",
    161: "Red viaria o ferroviaria",
    162: "Puerto",
    163: "Aeropuerto",
    171: "Infraestructura de suministro",
    172: "Infraestructura de residuos",
    210: "Cultivo herbáceo",
    220: "Invernadero",
    231: "Frutal cítrico",
    232: "Frutal no cítrico",
    233: "Viñedo",
    234: "Olivar",
    235: "Otros cultivos leñosos",
    236: "Combinación de cultivos leñosos",
    240: "Prado",
    250: "Combinación de cultivos",
    260: "Combinación de cultivos con vegetación",
    311: "Bosque de frondosas",
    312: "Bosque de coníferas",
    313: "Bosque mixto",
    320: "Pastizal o herbazal",
    330: "Matorral",
    340: "Combinación de vegetación",
    351: "Playa, duna o arenal",
    352: "Roquedo",
    353: "Temporalmente desarbolado por incendios",
    354: "Suelo desnudo",
    411: "Zona húmeda y pantanosa",
    412: "Turbera",
    413: "Marisma",
    414: "Salina",
    511: "Curso de agua",
    512: "Lago o laguna",
    513: "Embalse",
    514: "Lámina de agua artificial",
    515: "Mar",
    516: "Glaciar y/o nieve perpetua"
}
COBERTURAS = {
    "EDF": "Edificación",
    "ZAU": "Zona verde artificial y arbolado urbano",
    "VAP": "Vial, aparcamiento o zona peatonal sin vegetación",
    "OCT": "Otras construcciones",
    "SNE": "Suelo no edificado",
    "ZEV": "Zonas de extracción o vertido",
    "CHL": "Cultivos herbáceos distintos de arroz",
    "CHA": "Arroz",
    "LFC": "Frutales cítricos",
    "LFN": "Frutales no cítricos",
    "LVI": "Viñedo",
    "LOL": "Olivo",
    "LAL": "Otros cultivos leñosos",
    "PRD": "Prado",
    "PST": "Pastizal",
    "FDC": "Frondosas caducifolias",
    "FDP": "Frondosas perennifolias",
    "CNF": "Coníferas",
    "MTR": "Matorral",
    "SDN": "Playas, dunas y arenales",
    "RMB": "Roquedos",
    "ACM": "Acantilado marino",
    "ARR": "Afloramientos rocosos",
    "ACH": "Canchales",
    "CLC": "Coladas lávicas",
    "HTU": "Zonas pantanosas",
    "HPA": "Humedales interiores",
    "HSA": "Humedales marinos",
    "HMA": "Marismas",
    "HSM": "Salinas",
    "AUC": "Aguas continentales",
    "LAA": "Láminas de agua artificial",
    "ALG": "Lagos y lagunas",
    "AEM": "Embalses",
    "ALC": "Aguas litorales",
    "AMO": "Mares y océanos",
    "GMP": "Glaciares"
}
CODIGOS_COBERTURAS = {
    "EDF": 101,
    "ZAU": 102,
    "LAA": 103,
    "VAP": 104,
    "OCT": 111,
    "SNE": 121,
    "ZEV": 131,
    "CHA": 211,
    "CHL": 212,
    "LFC": 222,
    "LFN": 223,
    "LVI": 231,
    "LOL": 232,
    "LAL": 241,
    "PRD": 290,
    "PST": 300,
    "FDC": 312,
    "FDP": 313,
    "CNF": 316,
    "MTR": 320,
    "PDA": 331,
    "SDN": 333,
    "ZQM": 334,
    "GMP": 335,
    "RMB": 336,
    "ACM": 351,
    "ARR": 352,
    "ACH": 353,
    "CLC": 354,
    "HPA": 411,
    "HTU": 412,
    "HSA": 413,
    "HMA": 421,
    "HSM": 422,
    "AUC": 511,
    "ALG": 513,
    "AEM": 514,
    "ALC": 521,
    "AMO": 523
}
COBERTURAS_COMPUESTAS = {
    "DHS": "Dehesas",
    "OVD": "Olivar - Viñedo",
    "AAR": "Asentamiento Agrícola Residencial",
    "UER": "Huerta Familiar",
    "UCS": "Urbano Mixto",
    "UEN": "Ensanche Urbano",
    "UDS": "Urbano Discontinuo",
    "IPO": "Polígono Industrial Ordenado",
    "IPS": "Polígono Industrial Sin Ordenar",
    "IAS": "Industria Aislada",
    "PAG": "Primario Agrícola / Ganadero",
    "PFT": "Primario Forestal",
    "PMX": "Primario Minero Extractivo",
    "PPS": "Piscifactoría",
    "TCO": "Comercial y Oficinas",
    "TCH": "Complejo Hotelero",
    "TPR": "Parque Recreativo",
    "TCG": "Camping",
    "EAI": "Administrativo Institucional",
    "ESN": "Sanitario",
    "ECM": "Cementerio",
    "EDU": "Educación",
    "EPN": "Penitenciario",
    "ERG": "Religioso",
    "ECL": "Cultural",
    "EDP": "Deportivo",
    "ECG": "Campo de Golf",
    "EPU": "Parque Urbano",
    "NRV": "Red Viaria",
    "NRF": "Red Ferroviaria",
    "NPO": "Puerto",
    "NAP": "Aeropuerto",
    "NEO": "Energía Eólica",
    "NSL": "Energía Solar",
    "NCL": "Energía Nuclear",
    "NEL": "Energía Eléctrica",
    "NTM": "Energía Térmica",
    "NHD": "Energía Hidroeléctrica",
    "NGO": "Gaseoducto / Oleoducto",
    "NTC": "Telecomunicaciones",
    "NDP": "Depuradoras y Potabilizadoras",
    "NCC": "Conducciones y Canales",
    "NDS": "Desalinizadoras",
    "NVE": "Vertederos y Escombreras",
    "NPT": "Plantas de Tratamiento"
}
CODIGOS_COBERTURAS_COMPUESTAS = {
    "DHS": 701,
    "OVD": 702,
    "AAR": 703,
    "UER": 704,
    "UCS": 810,
    "UEN": 812,
    "UDS": 813,
    "IPO": 821,
    "IPS": 822,
    "IAS": 823,
    "PAG": 831,
    "PFT": 832,
    "PMX": 833,
    "PPS": 834,
    "TCO": 841,
    "TCH": 842,
    "TPR": 843,
    "TCG": 844,
    "EAI": 851,
    "ESN": 852,
    "ECM": 853,
    "EDU": 854,
    "EPN": 855,
    "ERG": 856,
    "ECL": 857,
    "EDP": 858,
    "ECG": 859,
    "EPU": 860,
    "NRV": 881,
    "NRF": 882,
    "NPO": 883,
    "NAP": 884,
    "NEO": 891,
    "NSL": 892,
    "NCL": 893,
    "NEL": 894,
    "NTM": 895,
    "NHD": 896,
    "NGO": 897,
    "NTC": 900,
    "NDP": 911,
    "NCC": 912,
    "NDS": 913,
    "NVE": 921,
    "NPT": 922
}
ATRIBUTOS = {
    "ea": "edificio aislado",
    "em": "edificio entre medianeras",
    "va": "vivienda unifamiliar aislada",
    "vd": "vivienda unifamiliar adosada",
    "nv": "nave",
    "ec": "en construcción",
    "sc": "secano",
    "rr": "regadío regado",
    "rn": "regadío no regado",
    "ab": "abancalado",
    "fz": "forzado",
    "pl": "plantación",
    "fr": "formación de ribera",
    "fc": "función cortafuegos",
    "ct": "cortas",
    "pc": "procedencia de cultivos",
    "am": "alta montaña",
    "ra": "roturados no agrícolas",
    "ze": "zonas erosionadas",
    "cu": "cuaternarias"
}
import re
def clasificar_viaje(row):
    unlock = pd.notnull(row['station_unlock'])
    lock = pd.notnull(row['station_lock'])

    if unlock and lock:
        return "Estación inicio y fin"
    elif unlock or lock:
        return "Solo una estación"
    else:
        return "Sin estaciones"
def decodificar_etiqueta(etiqueta):
    # Separar porcentaje (si existe) + cobertura + atributos
    match = re.match(r"(\d{2})?([A-Z]{3})([a-z]*)", etiqueta)
    if not match:
        return etiqueta  # Retornar sin cambios si no es reconocible

    porcentaje, cobertura, attrs = match.groups()
    descripcion = COBERTURAS.get(cobertura, cobertura)
    atributos = [ATRIBUTOS.get(a, a) for a in re.findall(r'[a-z]{2}', attrs)]

    texto = f"{porcentaje + '% ' if porcentaje else ''}{descripcion}"
    if atributos:
        texto += f" con {' y '.join(atributos)}"
    return texto

def decodificar_siose_code(code):
    # Coberturas compuestas (A, M, I, o predefinidas tipo UER, DHS, etc.)
    if re.match(r"^[A-Z]{1,3}\(.*\)$", code):
        tipo = code[:code.index("(")]
        contenido = code[code.index("(")+1:-1]
        partes = contenido.split("_")
        descripcion = [decodificar_etiqueta(p) for p in partes]
        return f"{tipo}: " + ", ".join(descripcion)
    else:
        return decodificar_etiqueta(code)
    
# ---------------------------
# 1. Función para extraer coordenadas
# ---------------------------
def extraer_coords(punto_str):
    try:
        punto = ast.literal_eval(punto_str)
        lon, lat = punto['coordinates']
        return pd.Series([lat, lon])
    except:
        return pd.Series([None, None])

# ---------------------------
# 2. Cargar datos (y caché para rendimiento)
# ---------------------------

def cargar_datos():
    suelo = gpd.read_file("SIOSE_Madrid_2014.gpkg", layer="T_POLIGONOS")
    trips = pd.read_csv("trips_febrero_2023.csv", sep=";", engine="python")

    # Extraer coordenadas
    trips[['lat_unlock', 'lon_unlock']] = trips['geolocation_unlock'].apply(extraer_coords)
    trips[['lat_lock', 'lon_lock']] = trips['geolocation_lock'].apply(extraer_coords)
    
    #Reemplazar datos
    suelo["HILUCS"] = suelo["HILUCS"].replace(hilucs_dict)
    suelo["CODIIGE"] = suelo["CODIIGE"].replace(codiige_dict)
    suelo["SIOSE_DESC"] = suelo["SIOSE_CODE"].apply(decodificar_siose_code)
    #Convertir fechas
    trips['unlock_date'] = pd.to_datetime(trips['unlock_date'])
    trips['lock_date'] = pd.to_datetime(trips['lock_date'])
    trips['fecha'] = pd.to_datetime(trips["fecha"])

    # Elimina filas donde *todas* las columnas son NaN
    trips = trips.dropna(how='all').reset_index(drop=True)
    #Borramos los nulos que faltan
    trips = trips.dropna()

    #Agregamoseltipo de viaje
    #trips_tmp=trips
    trips['tipo_viaje'] = trips.apply(clasificar_viaje, axis=1)

    #Duracion de los viajes
    trips['duration'] = trips['lock_date'] - trips['unlock_date']
    return suelo, trips

suelo, trips = cargar_datos()



# Guardar los DataFrames procesados en archivos CSV
suelo.to_file("datos_procesados/suelo_procesado.gpkg", layer="suelo", driver="GPKG")

trips.to_csv("datos_procesados/trips_procesado.csv", index=True)
