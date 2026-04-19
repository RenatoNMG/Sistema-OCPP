import asyncio
import websockets

connected_chargers = {}

async def handle_connection(websocket):
    # pega o path da conexão (novo formato)
    path = websocket.request.path
    charger_id = path.strip("/")

    print(f"🔌 Charger conectado: {charger_id}")

    connected_chargers[charger_id] = websocket

    try:
        while True:
            message = await websocket.recv()
            print(f"📩 Mensagem de {charger_id}: {message}")

    except websockets.exceptions.ConnectionClosed:
        print(f"❌ Charger desconectado: {charger_id}")
        connected_chargers.pop(charger_id, None)


async def main():
    server = await websockets.serve(
        handle_connection,
        "0.0.0.0",
        9000
    )

    print("🚀 Servidor OCPP rodando na porta 9000")
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())