from fastapi import FastAPI
from pymongo import MongoClient
from datetime import datetime

app = FastAPI(title="MusicHub API")

# conexão com o MongoDB Atlas
client = MongoClient("mongodb+srv://admin:vyy8cUpAegI8mdNx@cluster0.zswlvtl.mongodb.net/?appName=Cluster0")
db = client["musichub"]
musicas = db["musicas"]

@app.post("/musicas/popular")
def popular_musicas(lista_musicas: list[dict]):
    for musica in lista_musicas:
        musica["data_upload"] = datetime.now().strftime("%Y-%m-%d")
    resultado = musicas.insert_many(lista_musicas)
    return {
        "mensagem": "Músicas inseridas com sucesso",
        "quantidade": len(resultado.inserted_ids)
    }

@app.get("/analytics/artistas")
def artistas_com_mais_musicas():
    pipeline = [
        {
            "$group": {
                "_id": "$artista",
                "total_musicas": { "$sum": 1 }
            }
        },
        {
            "$sort": { "total_musicas": -1 }
        }
    ]

    resultado = list(musicas.aggregate(pipeline))
    return resultado

@app.get("/analytics/tipos")
def distribuicao_tipos():
    pipeline = [
        {
            "$group": {
                "_id": "$tipo",
                "quantidade": { "$sum": 1 }
            }
        }
    ]

    resultado = list(musicas.aggregate(pipeline))
    return resultado
