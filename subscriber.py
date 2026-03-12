import redis

redis_client = redis.Redis(host="localhost", port=6379, db=0)
pubsub = redis_client.pubsub()
pubsub.subscribe("musicas")

print("📡 Ouvindo canal 'musicas'...")

for mensagem in pubsub.listen():
    if mensagem["type"] == "message":
        print(f"🔔 Evento recebido: {mensagem['data'].decode()}")
