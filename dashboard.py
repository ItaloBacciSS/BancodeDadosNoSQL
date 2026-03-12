import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="MusicHub Dashboard",
    layout="wide"
)

st.title("🎵 MusicHub — Dashboard Analítico")
st.markdown("Sistema didático de gerenciamento e análise de partituras e tablaturas")

# ======================================================
# MENU LATERAL
# ======================================================
st.sidebar.title("📌 Funcionalidades")
opcao = st.sidebar.radio(
    "Selecione:",
    [
        "Visão Geral",
        "Analytics - Artistas",
        "Analytics - Tipos",
        "Busca por Artista",
        "Busca Textual",
        "Busca por Localização",
        "Última Música Cadastrada",
        "Contador de Acessos",
        "Eventos em Tempo Real",
        "Analytics - Bitmap",
        "Analytics - Bloom Filter",
        "Analytics - HyperLogLog",
        "Neo4j - Grafo"   # <-- NOVO
    ]
)

# ======================================================
# VISÃO GERAL
# ======================================================
if opcao == "Visão Geral":
    st.header("📊 Visão Geral do Projeto")
    st.markdown("""
    **MusicHub** é um projeto acadêmico que utiliza **MongoDB NoSQL** com:

    - CRUD completo
    - API REST com FastAPI
    - Aggregation Pipeline
    - Índices:
        - Simples
        - Texto
        - Geoespacial (2dsphere)
    - Dashboard interativo com Streamlit
    - Integração com Redis (variáveis, cache e estruturas avançadas)
    - Integração com Neo4j (grafo de artistas, músicas e instrumentos)
    """)

# ======================================================
# ANALYTICS - ARTISTAS
# ======================================================
elif opcao == "Analytics - Artistas":
    st.header("🎤 Artistas com mais músicas")
    if st.button("Carregar dados"):
        response = requests.get(f"{API_URL}/analytics/artistas")
        if response.status_code == 200:
            dados = response.json()
            df = pd.DataFrame(dados).rename(columns={"_id": "Artista", "total": "Total de músicas"})
            st.dataframe(df, use_container_width=True)
            st.bar_chart(df.set_index("Artista"))
        else:
            st.error("Erro ao buscar dados")

# ======================================================
# ANALYTICS - TIPOS
# ======================================================
elif opcao == "Analytics - Tipos":
    st.header("🎼 Distribuição: Tablaturas x Partituras")
    if st.button("Carregar dados"):
        response = requests.get(f"{API_URL}/analytics/tipos")
        if response.status_code == 200:
            dados = response.json()
            df = pd.DataFrame(dados).rename(columns={"_id": "Tipo", "quantidade": "Quantidade"})
            st.dataframe(df, use_container_width=True)
            st.bar_chart(df.set_index("Tipo"))
        else:
            st.error("Erro ao buscar dados")

# ======================================================
# BUSCA POR ARTISTA
# ======================================================
elif opcao == "Busca por Artista":
    st.header("🔍 Buscar músicas por artista")
    artista = st.text_input("Nome do artista")
    if st.button("Buscar"):
        response = requests.get(f"{API_URL}/musicas/artista/{artista}")
        if response.status_code == 200:
            dados = response.json()
            if dados:
                st.dataframe(pd.DataFrame(dados), use_container_width=True)
            else:
                st.warning("Nenhuma música encontrada")
        else:
            st.error("Erro na requisição")

# ======================================================
# BUSCA TEXTUAL
# ======================================================
elif opcao == "Busca Textual":
    st.header("📝 Busca textual (título, artista ou instrumento)")
    termo = st.text_input("Digite um termo de busca")
    if st.button("Buscar"):
        response = requests.get(f"{API_URL}/musicas/busca", params={"q": termo})
        if response.status_code == 200:
            dados = response.json()
            if dados:
                st.dataframe(pd.DataFrame(dados), use_container_width=True)
            else:
                st.warning("Nenhum resultado encontrado")
        else:
            st.error("Erro na busca")

# ======================================================
# BUSCA POR LOCALIZAÇÃO
# ======================================================
elif opcao == "Busca por Localização":
    st.header("📍 Buscar músicas por proximidade")
    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input("Latitude", value=-23.55, format="%.5f")
    with col2:
        lon = st.number_input("Longitude", value=-46.63, format="%.5f")
    if st.button("Buscar músicas próximas"):
        response = requests.get(f"{API_URL}/musicas/proximas", params={"lat": lat, "lon": lon})
        if response.status_code == 200:
            dados = response.json()
            if dados:
                st.dataframe(pd.DataFrame(dados), use_container_width=True)
            else:
                st.warning("Nenhuma música encontrada na região")
        else:
            st.error("Erro na busca geoespacial")

# ======================================================
# ÚLTIMA MÚSICA CADASTRADA
# ======================================================
elif opcao == "Última Música Cadastrada":
    st.header("🎵 Última música cadastrada")
    if st.button("Ver última música"):
        response = requests.get(f"{API_URL}/musicas/ultima")
        if response.status_code == 200:
            dados = response.json()
            if "ultima_musica" in dados:
                st.success(f"A última música cadastrada foi: **{dados['ultima_musica']}**")
            else:
                st.warning(dados.get("mensagem", "Nenhum dado disponível"))
        else:
            st.error("Erro ao buscar última música")

# ======================================================
# CONTADOR DE ACESSOS
# ======================================================
elif opcao == "Contador de Acessos":
    st.header("📊 Contador de buscas por artista")
    artista = st.text_input("Digite o nome do artista")
    if st.button("Ver contador"):
        response = requests.get(f"{API_URL}/analytics/contador/{artista}")
        if response.status_code == 200:
            dados = response.json()
            st.info(f"O artista **{dados['artista']}** foi buscado **{dados['buscas']}** vezes.")
        else:
            st.error("Erro ao buscar contador")

# ======================================================
# EVENTOS EM TEMPO REAL
# ======================================================
elif opcao == "Eventos em Tempo Real":
    st.header("📡 Eventos em tempo real")
    limite = st.slider("Quantos eventos mostrar?", 5, 20, 10)
    if st.button("Carregar eventos"):
        response = requests.get(f"{API_URL}/musicas/eventos", params={"limit": limite})
        if response.status_code == 200:
            eventos = response.json()["eventos"]
            if eventos:
                for e in eventos:
                    st.info(e)
            else:
                st.warning("Nenhum evento registrado ainda")
        else:
            st.error("Erro ao buscar eventos")

# ======================================================
# ANALYTICS - BITMAP
# ======================================================
elif opcao == "Analytics - Bitmap":
    st.header("📊 Bitmap - Acessos de Usuários")
    usuario_id = st.number_input("ID do usuário", min_value=0, step=1)
    if st.button("Registrar acesso"):
        response = requests.post(f"{API_URL}/analytics/bitmap/acesso", params={"usuario_id": usuario_id})
        st.success(response.json()["mensagem"])
    if st.button("Ver total de acessos hoje"):
        response = requests.get(f"{API_URL}/analytics/bitmap/total")
        dados = response.json()
        st.info(f"Total de acessos em {dados['data']}: {dados['total_acessos']}")

# ======================================================
# ANALYTICS - BLOOM FILTER
# ======================================================
elif opcao == "Analytics - Bloom Filter":
    st.header("🌱 Bloom Filter - Artistas")
    nome = st.text_input("Nome do artista")
    if st.button("Adicionar artista"):
        response = requests.post(f"{API_URL}/analytics/bloom/adicionar", params={"nome": nome})
        st.success(response.json()["mensagem"])
    if st.button("Verificar artista"):
        response = requests.get(f"{API_URL}/analytics/bloom/verificar", params={"nome": nome})
        dados = response.json()
        if dados["existe"]:
            st.info(f"O artista {nome} provavelmente já existe.")
        else:
            st.warning(f"O artista {nome} não existe no filtro.")

# ======================================================
# ANALYTICS - HYPERLOGLOG
# ======================================================
elif opcao == "Analytics - HyperLogLog":
    st.header("📈 HyperLogLog - Buscas de Artistas")
    artista = st.text_input("Nome do artista buscado")
    if st.button("Registrar busca"):
        response = requests.post(f"{API_URL}/analytics/hll/adicionar", params={"artista": artista})
        st.success(response.json()["mensagem"])
    if st.button("Contar artistas distintos buscados"):
        response = requests.get(f"{API_URL}/analytics/hll/contar")
        dados = response.json()
        st.info(f"Total de artistas distintos buscados: {dados['total_artistas_distintos']}")

# ======================================================
# NEO4J - GRAFO
# ======================================================
elif opcao == "Neo4j - Grafo":
    st.header("🔗 Neo4j - Análise de Grafo")

    if st.button("Carregar artistas e músicas"):
        response = requests.get(f"{API_URL}/neo4j/artistas")
        if response.status_code == 200:
            dados = response.json()
            if dados:
                df = pd.DataFrame(dados)
                st.dataframe(df, use_container_width=True)
                st.bar_chart(df.set_index("artista"))
            else:
                st.warning("Nenhum dado encontrado no grafo")
        else:
            st.error("Erro ao buscar dados do Neo4j")

    if st.button("Instrumentos mais usados"):
        response = requests.get(f"{API_URL}/neo4j/instrumentos")
        if response.status_code == 200:
            dados = response.json()
            if dados:
                df = pd.DataFrame(dados)
                st.dataframe(df, use_container_width=True)
                st.bar_chart(df.set_index("instrumento"))
            else:
                st.warning("Nenhum dado encontrado")
        else:
            st.error("Erro ao buscar dados de instrumentos")
