import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import numpy as np
import random

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Large-Scale Traffic Monitoring Application",
    layout="wide"
)

st.title("🚦 Large-Scale Traffic Monitoring Application")
st.caption(
    "Traffic congestion visualization using Hyderabad GPS bottleneck data "
    "(stable, realistic, road-level clarity)"
)

# -----------------------------
# LOAD CSV
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("gps_data.csv")

    # Ensure correct types
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    # Drop invalid rows
    df = df.dropna(subset=["latitude", "longitude"])

    return df

df = load_data()

# -----------------------------
# ASSIGN VEHICLE COUNT (100–500)
# -----------------------------
random.seed(42)
df["vehicle_count"] = df["area"].apply(
    lambda _: random.randint(100, 500)
)

# -----------------------------
# TABLE VIEW
# -----------------------------
st.subheader("📍 Major Traffic Bottlenecks (CSV Input)")
st.dataframe(
    df[
        [
            "area",
            "signal_junction",
            "landmark",
            "latitude",
            "longitude",
            "vehicle_count",
        ]
    ],
    use_container_width=True,
)

# -----------------------------
# MAP SETUP
# -----------------------------
st.subheader("🗺️ City-Scale Traffic Map (5–10 km)")

center_lat = df["latitude"].mean()
center_lon = df["longitude"].mean()

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=11,
    tiles="OpenStreetMap",
    control_scale=True,
)

# -----------------------------
# BOTTLENECK ZONES + VEHICLES
# -----------------------------
for _, row in df.iterrows():

    lat = row["latitude"]
    lon = row["longitude"]
    count = row["vehicle_count"]

    # ---- Red congestion box (fixed size, no NaN)
    delta = 0.004  # ~400m box
    bounds = [
        [lat - delta, lon - delta],
        [lat + delta, lon + delta],
    ]

    folium.Rectangle(
        bounds=bounds,
        color="red",
        fill=True,
        fill_opacity=0.25,
        weight=2,
    ).add_to(m)

    # ---- Bottleneck marker
    folium.Marker(
        location=[lat, lon],
        icon=folium.Icon(color="red", icon="info-sign"),
        popup=(
            f"<b>{row['area']}</b><br>"
            f"Landmark: {row['landmark']}<br>"
            f"Vehicles: {count}"
        ),
    ).add_to(m)

    # ---- Vehicle points (tight clustering → looks like road traffic)
    vehicles_layer = MarkerCluster(disableClusteringAtZoom=15).add_to(m)

    spread = 0.0006  # VERY small spread = vehicles stay on roads
    for _ in range(count):
        v_lat = lat + np.random.normal(0, spread)
        v_lon = lon + np.random.normal(0, spread)

        folium.CircleMarker(
            location=[v_lat, v_lon],
            radius=2,
            color="blue",
            fill=True,
            fill_color="blue",
            fill_opacity=0.9,
        ).add_to(vehicles_layer)

# -----------------------------
# RENDER MAP (NO FLICKER)
# -----------------------------
st_folium(
    m,
    width=1400,
    height=650,
    returned_objects=[],
)
