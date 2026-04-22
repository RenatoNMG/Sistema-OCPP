import asyncio
import websockets
from charger_handler import Charger

connected_chargers = {}

async def handle_connection(websocket):
    path = websocket.request.path
    charger_id = path.strip("/")
    
    if not charger_id:
        print("⚠️ Tentativa de conexão sem ID no path.")
        await websocket.close()
        return

    charger = Charger(charger_id, websocket)
    connected_chargers[charger_id] = charger
    
    print(f"🔌 [Conexão Aberta] Charger ID: {charger_id}")

    try:
        await charger.start()
    except websockets.exceptions.ConnectionClosed:
        print(f"❌ [Desconectado] Charger ID: {charger_id}")
    finally:
        connected_chargers.pop(charger_id, None)

async def main():
    async with websockets.serve(
        handle_connection,
        "0.0.0.0",
        9000,
        subprotocols=['ocpp1.6']
    ):
        print("🚀 Servidor OCPP 1.6J rodando em: ws://0.0.0.0:9000")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())