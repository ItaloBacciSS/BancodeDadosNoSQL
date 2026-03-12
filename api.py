from fastapi import FastAPI
from pymongo import MongoClient
from datetime import datetime
from neo4j import GraphDatabase
import redis
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
REDIS_URI = os.getenv("REDIS_URI")


app = FastAPI(title="MusicHub API")

neo4j_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "12345678"))
# ================= CONEXÃO MONGO =================
client = MongoClient("mongodb+srv://admin:vyy8cUpAegI8mdNx@cluster0.zswlvtl.mongodb.net/?appName=Cluster0")
db = client["musichub"]
musicas = db["musicas"]

# ================= CONEXÃO REDIS =================
redis_client = redis.Redis(host="localhost", port=6379, db=0)

# ================= ÍNDICES =================
musicas.create_index("artista")
musicas.create_index("tipo")
musicas.create_index("publico")

musicas.create_index([
    ("titulo", "text"),
    ("artista", "text"),
    ("instrumento", "text")
])

musicas.create_index([("localizacao", "2dsphere")])



# ================= CRUD =================
@app.post("/musicas")
def criar_musica(musica: dict):
    try:
        musica["data_upload"] = datetime.now().strftime("%Y-%m-%d")
        musica["vendida"] = False
        musica["localizacao"] = {"type": "Point", "coordinates": [-46.63, -23.55]}

        musicas.insert_one(musica)

        titulo = musica.get("titulo", "sem título")
        redis_client.set("ultima_musica", titulo)
        redis_client.publish("musicas", f"Nova música cadastrada: {titulo}")

        return {"mensagem": "Música cadastrada com sucesso"}
    except Exception as e:
        return {"erro": str(e)}

# ================= NOVO ENDPOINT: Última música =================
@app.get("/musicas/ultima")
def ultima_musica():
    ultima = redis_client.get("ultima_musica")
    if ultima:
        return {"ultima_musica": ultima.decode()}
    return {"mensagem": "Nenhuma música cadastrada ainda"}

# ================= ANALYTICS =================
@app.get("/analytics/artistas")
def artistas_com_mais_musicas():
    pipeline = [
        {"$group": {"_id": "$artista", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}}
    ]
    return list(musicas.aggregate(pipeline))

@app.get("/analytics/tipos")
def distribuicao_tipos():
    pipeline = [
        {"$group": {"_id": "$tipo", "quantidade": {"$sum": 1}}}
    ]
    return list(musicas.aggregate(pipeline))

# ================= ÍNDICES – TESTES =================
# Índice simples + contador de acessos
@app.get("/musicas/artista/{nome}")
def buscar_por_artista(nome: str):
    # Incrementa contador no Redis
    redis_client.incr(f"contador:artista:{nome}")

    return list(musicas.find({"artista": nome}, {"_id": 0}))

# NOVO ENDPOINT: Consultar contador
@app.get("/analytics/contador/{nome}")
def contador_artista(nome: str):
    contador = redis_client.get(f"contador:artista:{nome}")
    if contador:
        return {"artista": nome, "buscas": int(contador)}
    return {"artista": nome, "buscas": 0}

# Índice texto
@app.get("/musicas/busca")
def busca_textual(q: str):
    return list(
        musicas.find(
            {"$text": {"$search": q}},
            {"_id": 0}
        )
    )

# Índice geoespacial
@app.get("/musicas/proximas")
def musicas_proximas(lat: float, lon: float):
    return list(
        musicas.find(
            {
                "localizacao": {
                    "$near": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": [lon, lat]
                        },
                        "$maxDistance": 50000
                    }
                }
            },
            {"_id": 0}
        )
    )

@app.get("/musicas/eventos")
def listar_eventos(limit: int = 10):
    eventos = redis_client.lrange("eventos_musicas", 0, limit - 1)
    return {"eventos": [e.decode() for e in eventos]}

@app.post("/analytics/bitmap/acesso")
def registrar_acesso(usuario_id: int):
    chave = f"acessos:{datetime.now().strftime('%Y-%m-%d')}"
    redis_client.setbit(chave, usuario_id, 1)
    return {"mensagem": f"Acesso registrado para usuário {usuario_id}"}

@app.get("/analytics/bitmap/total")
def total_acessos(data: str = datetime.now().strftime("%Y-%m-%d")):
    chave = f"acessos:{data}"
    total = redis_client.bitcount(chave)
    return {"data": data, "total_acessos": total}

@app.get("/analytics/bloom/verificar")
def verificar_artista(nome: str):
    existe = redis_client.execute_command("BF.EXISTS", "filtro_artistas", nome)
    return {"artista": nome, "existe": bool(existe)}

@app.post("/analytics/hll/adicionar")
def adicionar_busca(artista: str):
    redis_client.pfadd("buscas_artistas", artista)
    return {"mensagem": f"Busca registrada para artista {artista}"}

@app.get("/analytics/hll/contar")
def contar_buscas():
    total = redis_client.pfcount("buscas_artistas")
    return {"total_artistas_distintos": total}

@app.get("/neo4j/artistas")
def artistas_com_musicas():
    with neo4j_driver.session() as session:
        result = session.run("""
            MATCH (a:Artista)-[:COMPÔS]->(m:Musica)
            RETURN a.nome AS artista, count(m) AS total
            ORDER BY total DESC
        """)
        return [{"artista": r["artista"], "total": r["total"]} for r in result]

@app.get("/neo4j/instrumentos")
def instrumentos_usados():
    with neo4j_driver.session() as session:
        result = session.run("""
            MATCH (m:Musica)-[:USA]->(i:Instrumento)
            RETURN i.nome AS instrumento, count(m) AS total
            ORDER BY total DESC
        """)
        return [{"instrumento": r["instrumento"], "total": r["total"]} for r in result]
