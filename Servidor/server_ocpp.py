import asyncio
import websockets
import json
import os
from datetime import datetime

# ==============================
# Configurações de rede
# ==============================
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 9000))  # Render exige porta dinâmica

# ==============================
# Função que trata cada conexão
# ==============================
async def ocpp_handler(websocket):
    # Pega o ID do carregador a partir do path da URL
    path = websocket.request.path
    charger_id = path.strip("/") or "Carregador_Desconhecido"

    print(f"\n⚡ [CONEXÃO] Carregador conectado! ID: {charger_id}")

    try:
        async for message in websocket:
            print(f"\n📥 [{charger_id} RECEBIDO]: {message}")

            try:
                # Tenta interpretar como JSON
                msg = json.loads(message)

                # Valida se é uma lista OCPP mínima
                if not isinstance(msg, list) or len(msg) < 3:
                    print("⚠️ Mensagem fora do padrão OCPP")
                    await websocket.send("Erro: Formato OCPP inválido")
                    continue

                # Extrai campos principais
                msg_type = msg[0]
                msg_id = msg[1]
                action = msg[2]
                payload = msg[3] if len(msg) > 3 else {}

                now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

                # ===== RESPONDE BootNotification =====
                if action == "BootNotification":
                    response = [3, msg_id, {
                        "status": "Accepted",
                        "currentTime": now,
                        "interval": 60
                    }]
                    await websocket.send(json.dumps(response))
                    print(f"📤 [RESPOSTA] BootNotification enviada")

                # ===== RESPONDE Authorize =====
                elif action == "Authorize":
                    response = [3, msg_id, {
                        "idTagInfo": {"status": "Accepted"}
                    }]
                    await websocket.send(json.dumps(response))
                    print(f"📤 [RESPOSTA] Authorize enviada para idTag={payload.get('idTag')}")

                # ===== OUTRAS AÇÕES (Heartbeat, Status, etc) =====
                else:
                    response = [3, msg_id, {}]
                    await websocket.send(json.dumps(response))
                    print(f"📤 [RESPOSTA] Mensagem '{action}' processada")

            except json.JSONDecodeError:
                # Mensagem não é JSON
                print("❌ Mensagem recebida não é JSON")
                await websocket.send("Erro: JSON inválido")
                continue

            except Exception as e:
                # Qualquer outro erro não derruba a conexão
                print(f"💥 Erro interno ao processar mensagem: {e}")
                await websocket.send("Erro interno")
                continue

    except websockets.exceptions.ConnectionClosed:
        print(f"🔌 [DESCONECTADO] Carregador {charger_id} saiu")
    except Exception as e:
        print(f"💥 Erro de conexão: {e}")


# ==============================
# Inicia servidor
# ==============================
async def main():
    print(f"🚀 Servidor OCPP rodando na porta {PORT}")
    print(f"📢 Endereço para conexão: ws://[SEU_DOMÍNIO]/ID_DO_CARREGADOR")
    print("📍 Aguardando conexões...")

    async with websockets.serve(ocpp_handler, HOST, PORT):
        await asyncio.Future()  # Mantém o servidor rodando

# ==============================
# Entrypoint
# ==============================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
