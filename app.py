import streamlit as st
import pandas as pd
import geopandas as gpd
import numpy as np
from pathlib import Path

# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="EV Charging Spain",
    page_icon="⚡",
    layout="wide"
)

DATA_DIR = Path("data")


# ============================================================
# FUNCIONES
# ============================================================

def haversine(lat1, lon1, lat2, lon2):
    """Calcula distancia Haversine en kilómetros."""

    R = 6371.0

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1)
        * np.cos(lat2)
        * np.sin(dlon / 2) ** 2
    )

    c = 2 * np.arcsin(np.sqrt(a))

    return R * c


# ============================================================
# NAVEGACIÓN
# ============================================================

with st.sidebar:

    st.title("⚡ EV Charging")

    page = st.radio(
        "Navegación",
        [
            "🏠 Inicio",
            "🔌 Buscar estación",
            "📊 Déficit territorial",
            "📍 Nuevas localizaciones"
        ]
    )

    st.divider()

    st.caption(
        "TFM · Data Science, Big Data & Business Analytics"
    )


# ============================================================
# CARGA DE DATOS
# ============================================================

@st.cache_data
def load_data():

    stations = gpd.read_parquet(
        DATA_DIR / "ev_charging_station_features.parquet"
    )

    deficit = gpd.read_parquet(
        DATA_DIR / "app_municipal_deficit.parquet"
    )

    proposals = gpd.read_parquet(
        DATA_DIR / "ev_charging_location_proposals.parquet"
    )

    ml = gpd.read_parquet(
        DATA_DIR / "app_ml_predictions.parquet"
    )

    clusters = gpd.read_parquet(
        DATA_DIR / "app_municipal_clusters.parquet"
    )

    return stations, deficit, proposals, ml, clusters


stations, deficit, proposals, ml, clusters = load_data()


# ============================================================
# INICIO
# ============================================================

if page == "🏠 Inicio":

    st.title("⚡ EV Charging Spain")

    st.markdown(
        """
        ### Plataforma Inteligente para la Optimización de
        Infraestructuras de Recarga de Vehículos Eléctricos en España

        Análisis geoespacial, Machine Learning y sistemas de recomendación
        para analizar la infraestructura pública de recarga en España.
        """
    )

    st.divider()

    total_stations = len(stations)
    total_municipalities = len(deficit)

    municipalities_with_station = int(
        (deficit["num_stations"] > 0).sum()
    )

    coverage = (
        municipalities_with_station
        / total_municipalities
        * 100
    )

    total_proposals = len(proposals)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Estaciones",
        f"{total_stations:,}".replace(",", ".")
    )

    col2.metric(
        "Municipios analizados",
        f"{total_municipalities:,}".replace(",", ".")
    )

    col3.metric(
        "Municipios con estación",
        f"{coverage:.1f} %"
    )

    col4.metric(
        "Nuevas localizaciones propuestas",
        total_proposals
    )

    st.divider()

    st.subheader("🗺️ Infraestructura de recarga en España")

    st.caption(
        "Distribución geográfica de las estaciones de recarga "
        "incluidas en Open Charge Map."
    )

    map_data = stations[
        ["latitude", "longitude"]
    ].dropna()

    st.map(
        map_data,
        latitude="latitude",
        longitude="longitude",
        size=5
    )


# ============================================================
# BUSCAR ESTACIÓN
# ============================================================

elif page == "🔌 Buscar estación":

    st.title("🔌 Buscar estación")

    st.write(
        """
        Selecciona un municipio y los criterios de búsqueda.
        El sistema prioriza estaciones cercanas y con mayor
        potencia disponible.
        """
    )

    st.caption(
        "El filtro por tipo de conector se incorporará cuando esté "
        "disponible el detalle estación-conector."
    )

    st.divider()

    municipalities = deficit[
        [
            "municipality_name",
            "province_name",
            "geometry"
        ]
    ].dropna(
        subset=["municipality_name", "geometry"]
    ).copy()

    municipalities["municipality_label"] = (
        municipalities["municipality_name"]
        + " · "
        + municipalities["province_name"].fillna("")
    )

    municipalities = municipalities.sort_values(
        "municipality_label"
    )

    selected_label = st.selectbox(
        "Municipio de origen",
        municipalities["municipality_label"].tolist()
    )

    selected_municipality = municipalities[
        municipalities["municipality_label"]
        == selected_label
    ].iloc[0]

    selected_geometry = selected_municipality.geometry

    if selected_geometry.geom_type == "Point":
        origin_point = selected_geometry
    else:
        origin_point = selected_geometry.representative_point()

    origin_lat = origin_point.y
    origin_lon = origin_point.x

    col1, col2 = st.columns(2)

    with col1:

        max_distance = st.slider(
            "Distancia máxima (km)",
            min_value=5,
            max_value=100,
            value=25,
            step=5
        )

    with col2:

        min_power = st.slider(
            "Potencia mínima (kW)",
            min_value=0,
            max_value=350,
            value=22,
            step=10
        )

    top_n = st.slider(
        "Número de recomendaciones",
        min_value=3,
        max_value=20,
        value=10
    )

    candidates = stations.copy()

    candidates = candidates.dropna(
        subset=["latitude", "longitude"]
    )

    candidates["distance_km"] = haversine(
        origin_lat,
        origin_lon,
        candidates["latitude"].values,
        candidates["longitude"].values
    )

    candidates = candidates[
        candidates["distance_km"] <= max_distance
    ].copy()

    if "max_power_kw" in candidates.columns:

        candidates = candidates[
            candidates["max_power_kw"].fillna(0)
            >= min_power
        ].copy()

    if len(candidates) > 0:

        distance_score = (
            1
            - np.minimum(
                candidates["distance_km"] / max_distance,
                1
            )
        )

        power_score = np.minimum(
            candidates["max_power_kw"].fillna(0) / 350,
            1
        )

        candidates["recommendation_score"] = (
            0.70 * distance_score
            + 0.30 * power_score
        )

        recommendations = (
            candidates
            .sort_values(
                ["recommendation_score", "distance_km"],
                ascending=[False, True]
            )
            .head(top_n)
            .copy()
        )

        st.divider()

        st.subheader(
            f"⚡ Mejores estaciones desde "
            f"{selected_municipality['municipality_name']}"
        )

        display_cols = []

        for col in [
            "station_name",
            "town_ocm",
            "distance_km",
            "max_power_kw",
            "price_min_eur_kwh",
            "usage_cost_clean"
        ]:
            if col in recommendations.columns:
                display_cols.append(col)

        results_table = recommendations[
            display_cols
        ].copy()

        results_table = results_table.rename(
            columns={
                "station_name": "Estación",
                "town_ocm": "Municipio",
                "distance_km": "Distancia (km)",
                "max_power_kw": "Potencia máx. (kW)",
                "price_min_eur_kwh": "Precio mín. €/kWh",
                "usage_cost_clean": "Información de precio"
            }
        )

        if "Distancia (km)" in results_table.columns:
            results_table["Distancia (km)"] = (
                results_table["Distancia (km)"].round(2)
            )

        if "Potencia máx. (kW)" in results_table.columns:
            results_table["Potencia máx. (kW)"] = (
                results_table["Potencia máx. (kW)"].round(1)
            )

        if "Precio mín. €/kWh" in results_table.columns:
            results_table["Precio mín. €/kWh"] = (
                results_table["Precio mín. €/kWh"].round(3)
            )

        st.dataframe(
            results_table,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("🗺️ Mapa de recomendaciones")

        map_results = recommendations[
            ["latitude", "longitude"]
        ].dropna()

        st.map(
            map_results,
            latitude="latitude",
            longitude="longitude",
            size=25
        )

        st.caption(
            "El ranking combina proximidad y potencia máxima disponible."
        )

    else:

        st.warning(
            "No se han encontrado estaciones que cumplan "
            "los criterios seleccionados."
        )


# ============================================================
# DÉFICIT TERRITORIAL
# ============================================================

elif page == "📊 Déficit territorial":

    st.title("📊 Déficit territorial")

    st.write(
        """
        Esta sección combina el índice territorial de necesidad
        con los resultados del modelo de Machine Learning y la
        segmentación de municipios.
        """
    )

    st.divider()

    deficit_view = deficit.merge(
        ml[
            [
                "municipality_code",
                "expected_stations_ml",
                "station_gap_ml"
            ]
        ],
        on="municipality_code",
        how="left"
    )

    deficit_view = deficit_view.merge(
        clusters[
            [
                "municipality_code",
                "cluster"
            ]
        ],
        on="municipality_code",
        how="left"
    )

    deficit_view["municipality_label"] = (
        deficit_view["municipality_name"]
        + " · "
        + deficit_view["province_name"].fillna("")
    )

    deficit_view = deficit_view.sort_values(
        "municipality_label"
    )

    selected_label = st.selectbox(
        "Selecciona un municipio",
        deficit_view["municipality_label"].tolist()
    )

    selected = deficit_view[
        deficit_view["municipality_label"]
        == selected_label
    ].iloc[0]

    st.subheader(
        f"📍 {selected['municipality_name']}"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Prioridad",
        selected["priority_class"]
    )

    col2.metric(
        "Índice de necesidad",
        f"{selected['infrastructure_need_score']:.3f}"
    )

    col3.metric(
        "Estaciones actuales",
        int(selected["num_stations"])
    )

    expected_ml = selected["expected_stations_ml"]

    if pd.notna(expected_ml):
        expected_text = f"{expected_ml:.1f}"
    else:
        expected_text = "N/D"

    col4.metric(
        "Estaciones esperadas por ML",
        expected_text
    )

    st.divider()

    st.subheader("🤖 Resultado del modelo")

    gap = selected["station_gap_ml"]

    if pd.isna(gap):

        st.info(
            "No existe una estimación ML disponible para este municipio."
        )

    elif gap < -1:

        st.warning(
            f"El municipio presenta aproximadamente "
            f"{abs(gap):.1f} estaciones menos que las esperadas "
            f"por el patrón aprendido por el modelo."
        )

    elif gap > 1:

        st.success(
            f"El municipio presenta aproximadamente "
            f"{gap:.1f} estaciones más que las esperadas "
            f"por el patrón aprendido por el modelo."
        )

    else:

        st.info(
            "La infraestructura existente se encuentra próxima "
            "al nivel estimado por el modelo."
        )

    st.caption(
        "La diferencia ML no representa directamente el número "
        "de estaciones que deberían instalarse. Indica la desviación "
        "respecto al patrón aprendido a partir de características "
        "demográficas y territoriales."
    )

    st.subheader("🧩 Perfil territorial")

    cluster_value = selected["cluster"]

    if pd.isna(cluster_value):

        st.write("Cluster no disponible.")

    elif int(cluster_value) == 0:

        st.info(
            """
            **Cluster 0 — Perfil territorial de menor escala**

            Este grupo presenta, en términos generales, menor población,
            menor densidad y menor presencia de infraestructura de recarga,
            junto con una mayor distancia a las estaciones existentes.
            """
        )

    elif int(cluster_value) == 1:

        st.info(
            """
            **Cluster 1 — Perfil territorial con mayor presencia de infraestructura**

            Este grupo presenta, en términos generales, mayor población
            y densidad, junto con una mayor disponibilidad y proximidad
            de infraestructura de recarga.
            """
        )

    st.subheader("📈 Contexto del municipio")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Población",
        f"{int(selected['population']):,}".replace(",", ".")
    )

    col2.metric(
        "Densidad",
        f"{selected['population_density_km2']:.1f} hab/km²"
    )

    col3.metric(
        "Conectores / 10.000 hab.",
        f"{selected['connectors_per_10k']:.2f}"
    )

    col4.metric(
        "Distancia estación más cercana",
        f"{selected['nearest_station_distance_km']:.1f} km"
    )

    st.divider()

    st.subheader("🏆 Municipios con mayor necesidad relativa")

    ranking = (
        deficit_view[
            [
                "municipality_name",
                "province_name",
                "population",
                "num_stations",
                "infrastructure_need_score",
                "priority_class",
                "expected_stations_ml",
                "station_gap_ml"
            ]
        ]
        .sort_values(
            "infrastructure_need_score",
            ascending=False
        )
        .head(25)
        .copy()
    )

    ranking = ranking.rename(
        columns={
            "municipality_name": "Municipio",
            "province_name": "Provincia",
            "population": "Población",
            "num_stations": "Estaciones",
            "infrastructure_need_score": "Índice necesidad",
            "priority_class": "Prioridad",
            "expected_stations_ml": "Esperadas ML",
            "station_gap_ml": "Diferencia ML"
        }
    )

    ranking["Índice necesidad"] = (
        ranking["Índice necesidad"].round(3)
    )

    ranking["Esperadas ML"] = (
        ranking["Esperadas ML"].round(1)
    )

    ranking["Diferencia ML"] = (
        ranking["Diferencia ML"].round(1)
    )

    st.dataframe(
        ranking,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("🗺️ Localización")

    geom = selected.geometry

    if geom.geom_type == "Point":
        point = geom
    else:
        point = geom.representative_point()

    municipality_map = pd.DataFrame({
        "latitude": [point.y],
        "longitude": [point.x]
    })

    st.map(
        municipality_map,
        latitude="latitude",
        longitude="longitude",
        size=40
    )


# ============================================================
# NUEVAS LOCALIZACIONES
# ============================================================

elif page == "📍 Nuevas localizaciones":

    st.title("📍 Nuevas localizaciones")

    st.write(
        """
        Esta sección muestra las localizaciones estratégicas
        priorizadas para ampliar la red pública de recarga.
        """
    )

    st.caption(
        "Las propuestas son localizaciones aproximadas obtenidas mediante "
        "un modelo multicriterio. No representan ubicaciones definitivas "
        "a nivel de parcela."
    )

    st.divider()

    # --------------------------------------------------------
    # KPIs
    # --------------------------------------------------------

    total_proposals = len(proposals)

    proposal_municipalities = (
        proposals["municipality_code"]
        .nunique()
    )

    median_gap = (
        proposals["distance_existing_station_km"]
        .median()
    )

    median_road = (
        proposals["distance_main_road_km"]
        .median()
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Propuestas",
        total_proposals
    )

    col2.metric(
        "Municipios",
        proposal_municipalities
    )

    col3.metric(
        "Distancia mediana a estación",
        f"{median_gap:.1f} km"
    )

    col4.metric(
        "Distancia mediana a vía principal",
        f"{median_road:.2f} km"
    )

    st.divider()

    # --------------------------------------------------------
    # FILTROS
    # --------------------------------------------------------

    st.subheader("🔎 Explorar propuestas")

    communities = [
        "Todas"
    ] + sorted(
        proposals[
            "autonomous_community"
        ].dropna().unique().tolist()
    )

    col1, col2 = st.columns(2)

    with col1:

        selected_community = st.selectbox(
            "Comunidad Autónoma",
            communities
        )

    with col2:

        top_proposals = st.slider(
            "Número de propuestas a mostrar",
            min_value=5,
            max_value=50,
            value=20,
            step=5
        )

    filtered_proposals = proposals.copy()

    if selected_community != "Todas":

        filtered_proposals = filtered_proposals[
            filtered_proposals[
                "autonomous_community"
            ] == selected_community
        ].copy()

    filtered_proposals = (
        filtered_proposals
        .sort_values(
            "proposal_rank"
        )
        .head(top_proposals)
        .copy()
    )

    # --------------------------------------------------------
    # MAPA
    # --------------------------------------------------------

    st.subheader("🗺️ Mapa de localizaciones propuestas")

    proposal_map = filtered_proposals[
        ["latitude", "longitude"]
    ].dropna()

    if len(proposal_map) > 0:

        st.map(
            proposal_map,
            latitude="latitude",
            longitude="longitude",
            size=35
        )

    else:

        st.warning(
            "No existen propuestas para los filtros seleccionados."
        )

    # --------------------------------------------------------
    # TABLA
    # --------------------------------------------------------

    st.subheader("🏆 Ranking de propuestas")

    proposal_table = filtered_proposals[
        [
            "proposal_rank",
            "municipality_name",
            "province_name",
            "source_type",
            "name",
            "priority_class",
            "location_score",
            "distance_existing_station_km",
            "distance_main_road_km"
        ]
    ].copy()

    proposal_table = proposal_table.rename(
        columns={
            "proposal_rank": "Ranking",
            "municipality_name": "Municipio",
            "province_name": "Provincia",
            "source_type": "Tipo de ubicación",
            "name": "Nombre",
            "priority_class": "Prioridad",
            "location_score": "Score",
            "distance_existing_station_km":
                "Distancia estación existente (km)",
            "distance_main_road_km":
                "Distancia vía principal (km)"
        }
    )

    proposal_table["Score"] = (
        proposal_table["Score"].round(3)
    )

    proposal_table[
        "Distancia estación existente (km)"
    ] = (
        proposal_table[
            "Distancia estación existente (km)"
        ].round(2)
    )

    proposal_table[
        "Distancia vía principal (km)"
    ] = (
        proposal_table[
            "Distancia vía principal (km)"
        ].round(2)
    )

    st.dataframe(
        proposal_table,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # --------------------------------------------------------
    # DETALLE DE PROPUESTA
    # --------------------------------------------------------

    st.subheader("📍 Detalle de una propuesta")

    proposals_selector = proposals.copy()

    proposals_selector["proposal_label"] = (
        "#"
        + proposals_selector["proposal_rank"].astype(str)
        + " · "
        + proposals_selector["municipality_name"].fillna("")
        + " · "
        + proposals_selector["source_type"].fillna("")
    )

    selected_proposal_label = st.selectbox(
        "Selecciona una propuesta",
        proposals_selector[
            "proposal_label"
        ].tolist()
    )

    selected_proposal = proposals_selector[
        proposals_selector[
            "proposal_label"
        ] == selected_proposal_label
    ].iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Ranking nacional",
        int(selected_proposal["proposal_rank"])
    )

    col2.metric(
        "Score",
        f"{selected_proposal['location_score']:.3f}"
    )

    col3.metric(
        "Distancia estación existente",
        f"{selected_proposal['distance_existing_station_km']:.2f} km"
    )

    col4.metric(
        "Distancia vía principal",
        f"{selected_proposal['distance_main_road_km']:.2f} km"
    )

    st.markdown(
        f"""
        **Municipio:** {selected_proposal['municipality_name']}  
        **Provincia:** {selected_proposal['province_name']}  
        **Comunidad Autónoma:** {selected_proposal['autonomous_community']}  
        **Tipo de ubicación:** {selected_proposal['source_type']}  
        **POI:** {selected_proposal['name'] if pd.notna(selected_proposal['name']) else 'Sin nombre'}  
        **Prioridad territorial:** {selected_proposal['priority_class']}
        """
    )

    selected_map = pd.DataFrame({
        "latitude": [
            selected_proposal["latitude"]
        ],
        "longitude": [
            selected_proposal["longitude"]
        ]
    })

    st.map(
        selected_map,
        latitude="latitude",
        longitude="longitude",
        size=60
    )

    st.caption(
        "El score de localización integra necesidad territorial, "
        "electrificación, distancia a infraestructura existente, "
        "accesibilidad viaria y adecuación del tipo de punto de interés."
    )

