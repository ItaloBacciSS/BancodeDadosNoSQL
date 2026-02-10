import streamlit as st
import requests
import pandas as pd

st.title("🎵 MusicHub - Data Analytics")

# ======================
# Artistas com mais músicas
# ======================
st.header("Artistas com mais músicas")

if st.button("Carregar artistas"):
    response = requests.get("http://127.0.0.1:8000/analytics/artistas")
    dados = response.json()
    df = pd.DataFrame(dados)
    df = df.rename(columns={"_id": "Artista"})
    st.dataframe(df)


# ======================
# Distribuição de tipos
# ======================
st.header("Distribuição: Tablatura x Partitura")

if st.button("Carregar tipos"):
    response = requests.get("http://127.0.0.1:8000/analytics/tipos")
    dados = response.json()
    df = pd.DataFrame(dados)
    df = df.rename(columns={"_id": "Tipo"})
    st.bar_chart(df.set_index("Tipo"))
