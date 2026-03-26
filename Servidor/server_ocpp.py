import asyncio
import websockets
import json
import os
import http
from datetime import datetime

# Porta dinâmica do Render
PORT = int(os.environ.get("PORT", 9000))
HOST = "0.0.0.0"

async def health_check(path, request_headers):
    """ Responde ao ping do Render para evitar erro 502 e InvalidMessage """
    # Se não for um pedido de upgrade para WebSocket (ou seja, é um ping do Render)
    if "upgrade" not in request_headers.get("Upgrade", "").lower():
        return http.HTTPStatus.OK, [], b"OK\n"
    return None

async def ocpp_handler(websocket):
    path = websocket.request.path
    charger_id = path.strip("/") or "Desconhecido"
    print(f"\n⚡ [CONEXÃO] Carregador: {charger_id}")

    try:
        async for message in websocket:
            print(f"📥 [{charger_id}]: {message}")
            # Lógica simples de resposta (BootNotification/Authorize)
            try:
                msg = json.loads(message)
                if isinstance(msg, list) and len(msg) >= 3:
                    await websocket.send(json.dumps([3, msg[1], {}]))
            except: pass
    except websockets.ConnectionClosed:
        print(f"🔌 [SAIU] {charger_id}")

async def main():
    print(f"🚀 SERVIDOR ONLINE NA PORTA {PORT}")
    # O segredo é o process_request para aceitar o ping do Render
    async with websockets.serve(ocpp_handler, HOST, PORT, process_request=health_check):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
