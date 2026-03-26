import asyncio
import websockets
import json
from datetime import datetime

# Configurações de Rede
HOST = "0.0.0.0" 
PORT = 9000

async def ocpp_handler(websocket):
    """
    Função que gerencia a conexão com o carregador.
    Nas versões novas do websockets, ela recebe apenas o objeto 'websocket'.
    """
    # Obtendo o ID do carregador a partir da URL (path)
    path = websocket.request.path
    charger_id = path.strip("/") or "Carregador_Desconhecido"
    
    print(f"\n⚡ [CONEXÃO] Carregador conectado! ID: {charger_id}")

    try:
        async for message in websocket:
            print(f"\n📥 [RECEBIDO de {charger_id}]: {message}")
            
            try:
                # O OCPP envia um array: [MessageTypeId, MessageId, Action, Payload]
                msg = json.loads(message)
                
                # Verifica se é um formato de lista válido do OCPP
                if isinstance(msg, list) and len(msg) >= 3:
                    msg_type = msg[0]
                    msg_id = msg[1]
                    action = msg[2]
                    payload = msg[3] if len(msg) > 3 else {}

                    now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

                    # --- RESPOSTA PARA BOOT NOTIFICATION ---
                    if action == "BootNotification":
                        response = [3, msg_id, {
                            "status": "Accepted",
                            "currentTime": now,
                            "interval": 60
                        }]
                        await websocket.send(json.dumps(response))
                        print(f"📤 [RESPOSTA]: BootNotification Aceito para {charger_id}")

                    # --- RESPOSTA PARA AUTHORIZE ---
                    elif action == "Authorize":
                        # Aceita qualquer TAG para teste
                        response = [3, msg_id, {
                            "idTagInfo": {"status": "Accepted"}
                        }]
                        await websocket.send(json.dumps(response))
                        print(f"📤 [RESPOSTA]: Autorização Aceita para a Tag: {payload.get('idTag')}")

                    # --- RESPOSTA PARA OUTRAS AÇÕES (Heartbeat, Status, etc) ---
                    else:
                        response = [3, msg_id, {}]
                        await websocket.send(json.dumps(response))
                        print(f"📤 [RESPOSTA]: Mensagem '{action}' processada.")
                
                else:
                    print("⚠️ Mensagem não segue o padrão OCPP [ID, Tipo, Ação, Dados].")
                    await websocket.send("Erro: Formato OCPP inválido.")

            except json.JSONDecodeError:
                print("❌ Erro: O que o carregador enviou não é um JSON válido.")
            except Exception as e:
                print(f"💥 Erro interno ao processar: {e}")

    except websockets.exceptions.ConnectionClosed:
        print(f"🔌 [DESCONECTADO] O carregador {charger_id} saiu.")

async def main():
    print(f"🚀 SERVIDOR OCPP ONLINE")
    print(f"📍 Endereço para o carregador: ws://[SEU_IP]:{PORT}/NOME_DO_CARREGADOR")
    print(f"📢 Ouvindo em todas as interfaces (0.0.0.0)...")
    
    async with websockets.serve(ocpp_handler, HOST, PORT):
        await asyncio.Future()  # Mantém o servidor rodando para sempre

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário.")