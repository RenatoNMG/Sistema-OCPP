import asyncio
import websockets
import json
import os
import http
from datetime import datetime

# Configurações de Rede
PORT = int(os.environ.get("PORT", 9000))
HOST = "0.0.0.0"

# Função de Health Check compatível com versões novas e antigas
async def health_check(path, request_headers):
    if "upgrade" not in request_headers.get("Upgrade", "").lower():
        return http.HTTPStatus.OK, [], b"OK\n"
    return None

async def ocpp_handler(websocket):
    # Pega o ID do carregador do path (ex: /carregador1)
    path = websocket.request.path
    charger_id = path.strip("/") or "Desconhecido"
    print(f"\n⚡ [CONEXÃO] Carregador: {charger_id}")

    try:
        async for message in websocket:
            print(f"📥 [{charger_id}]: {message}")
            # Resposta básica para manter a conexão
            await websocket.send(json.dumps([3, "123", {}]))
    except Exception as e:
        print(f"🔌 [SAIU] {charger_id}: {e}")

async def main():
    print(f"🚀 INICIANDO SERVIDOR NA PORTA {PORT}...")
    # Tenta iniciar com o health_check
    async with websockets.serve(
        ocpp_handler, 
        HOST, 
        PORT, 
        process_request=health_check
    ):
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"💥 ERRO CRÍTICO NO SERVIDOR: {e}")
