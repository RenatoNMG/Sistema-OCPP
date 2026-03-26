import asyncio
import websockets
import json
import os
from datetime import datetime

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 9000))  # ✅ ESSENCIAL

async def ocpp_handler(websocket):
    path = websocket.request.path
    charger_id = path.strip("/") or "Carregador_Desconhecido"
    
    print(f"\n⚡ [CONEXÃO] ID: {charger_id}")

    try:
        async for message in websocket:
            print(f"\n📥 [{charger_id}]: {message}")
            
            msg = json.loads(message)

            msg_id = msg[1]
            action = msg[2]
            payload = msg[3] if len(msg) > 3 else {}

            now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

            if action == "BootNotification":
                response = [3, msg_id, {
                    "status": "Accepted",
                    "currentTime": now,
                    "interval": 60
                }]
            else:
                response = [3, msg_id, {}]

            await websocket.send(json.dumps(response))
            print(f"📤 Resposta enviada")

    except Exception as e:
        print(f"🔌 Erro: {e}")

async def main():
    print(f"🚀 Rodando na porta {PORT}")

    async with websockets.serve(ocpp_handler, HOST, PORT):
        await asyncio.Future()

asyncio.run(main())
