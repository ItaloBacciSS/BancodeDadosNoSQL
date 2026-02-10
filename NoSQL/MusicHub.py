from pymongo import MongoClient
import shutil
import os

# ================= CONEXÃO =================
uri = "mongodb+srv://admin:vyy8cUpAegI8mdNx@cluster0.zswlvtl.mongodb.net/?appName=Cluster0"
client = MongoClient(uri)

db = client["musichub"]
musicas = db["musicas"]

# ================= FUNÇÕES =================

def cadastrar_musica():
    titulo = input("Título: ")
    artista = input("Artista: ")
    tipo = input("Tipo (Tablatura/Partitura): ")
    instrumento = input("Instrumeto: ")
    autor = input("Autor do upload: ")

    caminho_arquivo = input("Caminho do arquivo da partitura/imagem: ")

    nome_arquivo = os.path.basename(caminho_arquivo)
    destino = os.path.join("uploads", nome_arquivo)

    shutil.copy(caminho_arquivo, destino)

    musica = {
        "titulo": titulo,
        "artista": artista,
        "tipo": tipo,
        "instrumento": instrumento,
        "arquivo": destino,
        "autor": autor

    }

    musicas.insert_one(musica)
    print("Música cadastrada com arquivo!\n")


def listar_musicas():
    print("\n--- Músicas cadastradas ---")
    for m in musicas.find({}, {"_id": 0}):
        print(m)
    print()

def atualizar_musica():
    titulo = input("Título da música a atualizar: ")
    novo_conteudo = input("Novo conteúdo: ")

    musicas.update_one(
        {"titulo": titulo},
        {"$set": {"conteudo": novo_conteudo}}
    )
    print("Música atualizada!\n")

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
        print("3 - Atualizar música")
        print("4 - Remover música")
        print("0 - Sair")

        opcao = input("Escolha: ")

        if opcao == "1":
            cadastrar_musica()
        elif opcao == "2":
            listar_musicas()
        elif opcao == "3":
            atualizar_musica()
        elif opcao == "4":
            remover_musica()
        elif opcao == "0":
            print("Encerrando aplicação.")
            break
        else:
            print("Opção inválida.\n")

menu()

