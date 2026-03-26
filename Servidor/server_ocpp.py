import asyncio
import websockets
import json
from datetime import datetime

HOST = "0.0.0.0"
PORT = 9000

async def ocpp_handler(websocket):
    # ✅ compatível com Render
    path = websocket.path
    charger_id = path.strip("/") or "Carregador_Desconhecido"
    
    print(f"\n⚡ [CONEXÃO] ID: {charger_id}")

    try:
        async for message in websocket:
            print(f"\n📥 [{charger_id}]: {message}")
            
            try:
                msg = json.loads(message)

                if isinstance(msg, list) and len(msg) >= 3:
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

                    elif action == "Authorize":
                        response = [3, msg_id, {
                            "idTagInfo": {"status": "Accepted"}
                        }]

                    else:
                        response = [3, msg_id, {}]

                    await websocket.send(json.dumps(response))
                    print(f"📤 Resposta enviada ({action})")

            except Exception as e:
                print(f"💥 Erro ao processar: {e}")

    except Exception as e:
        print(f"🔌 Desconectado: {e}")

async def main():
    print("🚀 Servidor online (Render ready)")

    async with websockets.serve(
        ocpp_handler,
        HOST,
        PORT
    ):
        await asyncio.Future()

asyncio.run(main())
