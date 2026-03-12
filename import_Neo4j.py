from pymongo import MongoClient
from neo4j import GraphDatabase

# Conexão com Mongo Atlas
client = MongoClient("mongodb+srv://admin:vyy8cUpAegI8mdNx@cluster0.zswlvtl.mongodb.net/?appName=Cluster0")
db = client["musichub"]
musicas = db["musicas"]

# Conexão com Neo4j
neo4j_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "12345678"))

def importar_musicas():
    with neo4j_driver.session() as session:
        for musica in musicas.find():
            artista = musica.get("artista")
            titulo = musica.get("titulo")
            instrumentos = musica.get("instrumentos", [])

            session.run("MERGE (a:Artista {nome:$nome})", nome=artista)
            session.run("MERGE (m:Musica {titulo:$titulo})", titulo=titulo)
            session.run("""
                MATCH (a:Artista {nome:$nome}), (m:Musica {titulo:$titulo})
                MERGE (a)-[:COMPÔS]->(m)
            """, nome=artista, titulo=titulo)

            for inst in instrumentos:
                session.run("MERGE (i:Instrumento {nome:$nome})", nome=inst)
                session.run("""
                    MATCH (m:Musica {titulo:$titulo}), (i:Instrumento {nome:$nome})
                    MERGE (m)-[:USA]->(i)
                """, titulo=titulo, nome=inst)

importar_musicas()
