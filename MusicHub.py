from pymongo import MongoClient
import shutil
import os

# ================= CONEXÃO =================
uri = "mongodb+srv://admin:vyy8cUpAegI8mdNx@cluster0.zswlvtl.mongodb.net/?appName=Cluster0"
client = MongoClient(uri)

db = client["musichub"]
musicas = db["musicas"]

# ================= ÍNDICES =================
def criar_indices():
    musicas.create_index("artista")
    musicas.create_index("tipo")
    musicas.create_index("publico")

    musicas.create_index([
        ("titulo", "text"),
        ("artista", "text"),
        ("instrumento", "text")
    ])

    musicas.create_index([("localizacao", "2dsphere")])

    print("Índices criados com sucesso!\n")

# criar_indices()

# ================= FUNÇÕES =================

def cadastrar_musica():
    titulo = input("Título: ")
    artista = input("Artista: ")
    tipo = input("Tipo (Tablatura/Partitura): ")
    instrumento = input("Instrumento: ")
    autor = input("Autor do upload: ")
    dono = input("Dono do material: ")
    publico = input("Público? (s/n): ").lower() == "s"
    preco = float(input("Preço: "))

    caminho_arquivo = input("Caminho do arquivo: ")

    nome_arquivo = os.path.basename(caminho_arquivo)
    destino = os.path.join("uploads", nome_arquivo)

    os.makedirs("uploads", exist_ok=True)
    shutil.copy(caminho_arquivo, destino)

    musica = {
        "titulo": titulo,
        "artista": artista,
        "tipo": tipo,
        "instrumento": instrumento,
        "arquivo": destino,
        "autor": autor,
        "dono": dono,
        "publico": publico,
        "preco": preco,
        "vendida": False,

        # 📍 LOCALIZAÇÃO (exemplo fixo)
        "localizacao": {
            "type": "Point",
            "coordinates": [-46.63, -23.55]
        }
    }

    musicas.insert_one(musica)
    print("Música cadastrada com sucesso!\n")

def listar_musicas():
    print("\n--- Músicas cadastradas ---")
    for m in musicas.find({}, {"_id": 0}):
        print(m)
    print()

def remover_musica():
    titulo = input("Título da música a remover: ")
    musicas.delete_one({"titulo": titulo})
    print("Música removida!\n")

# ================= MENU =================
def menu():
    while True:
        print("=== MusicHub ===")
        print("1 - Cadastrar música")
        print("2 - Listar músicas")
        print("3 - Remover música")
        print("0 - Sair")

        opcao = input("Escolha: ")

        if opcao == "1":
            cadastrar_musica()
        elif opcao == "2":
            listar_musicas()
        elif opcao == "3":
            remover_musica()
        elif opcao == "0":
            print("Encerrando aplicação.")
            break
        else:
            print("Opção inválida.\n")

menu()