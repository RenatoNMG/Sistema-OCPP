import asyncio
import websockets
import json
import os
import http
from datetime import datetime

# Configurações de Rede (Render usa a variável de ambiente PORT)
HOST = "0.0.0.0" 
PORT = int(os.environ.get("PORT", 9000))

async def health_check(connection, request):
    """
    Responde a requisições HTTP comuns (como as do Render) para evitar erros no log.
    """
    if "upgrade" not in request.headers.get("Upgrade", "").lower():
        return http.HTTPStatus.OK, [], b"OK\n"
    return None

async def ocpp_handler(websocket):
    # Obtendo o ID do carregador a partir da URL
    path = websocket.request.path
    charger_id = path.strip("/") or "Carregador_Desconhecido"
    
    print(f"\n⚡ [CONEXÃO] Carregador conectado! ID: {charger_id}")

    try:
        async for message in websocket:
            print(f"\n📥 [RECEBIDO de {charger_id}]: {message}")
            try:
                msg = json.loads(message)
                if isinstance(msg, list) and len(msg) >= 3:
                    msg_id = msg[1]
                    action = msg[2]
                    payload = msg[3] if len(msg) > 3 else {}
                    now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

                    if action == "BootNotification":
                        response = [3, msg_id, {"status": "Accepted", "currentTime": now, "interval": 60}]
                    elif action == "Authorize":
                        response = [3, msg_id, {"idTagInfo": {"status": "Accepted"}}]
                    else:
                        response = [3, msg_id, {}]
                    
                    await websocket.send(json.dumps(response))
                    print(f"📤 [RESPOSTA]: {action} enviada para {charger_id}")
            except Exception as e:
                print(f"💥 Erro ao processar: {e}")

    except websockets.exceptions.ConnectionClosed:
        print(f"🔌 [DESCONECTADO] O carregador {charger_id} saiu.")

async def main():
    print(f"🚀 SERVIDOR OCPP ONLINE NA PORTA {PORT}")
    # O segredo está no 'process_request=health_check'
    async with websockets.serve(ocpp_handler, HOST, PORT, process_request=health_check):
        await asyncio.Future() 

if __name__ == "__main__":
    asyncio.run(main())
