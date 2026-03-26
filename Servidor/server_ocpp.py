import asyncio
import websockets
import json
import os
from datetime import datetime

PORT = int(os.environ.get("PORT", 9000))
HOST = "0.0.0.0"

async def ocpp_handler(websocket):
    path = websocket.path
    charger_id = path.strip("/") or "Desconhecido"

    print(f"\n⚡ [CONEXÃO] Carregador: {charger_id}")

    try:
        async for message in websocket:
            print(f"📥 [{charger_id}]: {message}")
            await websocket.send(json.dumps([3, "123", {}]))
    except Exception as e:
        print(f"🔌 [SAIU] {charger_id}: {e}")

async def main():
    print(f"🚀 INICIANDO SERVIDOR NA PORTA {PORT}...")

    async with websockets.serve(
        ocpp_handler,
        HOST,
        PORT
    ):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
