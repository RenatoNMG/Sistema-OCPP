import asyncio
import logging
import os
import json
from datetime import datetime
from websockets import serve

from ocpp.routing import on
from ocpp.v201 import ChargePoint as cp
from ocpp.v201 import call_result

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ocpp')

class ChargePoint(cp):
    @on('BootNotification')
    async def on_boot_notification(self, charging_station, reason, **kwargs):
        logger.info(f"BootNotification de {self.id}: {charging_station}")
        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status='Accepted'
        )

    @on('Heartbeat')
    async def on_heartbeat(self, **kwargs):
        logger.info(f"Heartbeat recebido de {self.id}")
        return call_result.HeartbeatPayload(
            current_time=datetime.utcnow().isoformat()
        )

async def send_welcome_message(websocket, cp_id):
    """
    Envia uma mensagem de teste (JSON) assim que o app conecta.
    Isso ajuda a confirmar no log do celular que o servidor respondeu.
    """
    welcome_payload = [
        3, # MessageType: CallResult (Resposta)
        "00000", # UniqueID
        {"message": f"Conectado com sucesso ao Servidor Render! ID: {cp_id}", "status": "Online"}
    ]
    await websocket.send(json.dumps(welcome_payload))
    logger.info(f"Mensagem de boas-vindas enviada para {cp_id}")

async def on_connect(websocket, path):
    # Extrai o ID do carregador da URL
    charge_point_id = path.strip('/')
    if not charge_point_id:
        charge_point_id = "Desconhecido"

    logger.info(f"Tentativa de conexão: {charge_point_id}")

    # Envia o teste inicial para o app
    try:
        await send_welcome_message(websocket, charge_point_id)
    except Exception as e:
        logger.error(f"Erro ao enviar boas-vindas: {e}")

    cp_instance = ChargePoint(charge_point_id, websocket)

    try:
        await cp_instance.start()
    except Exception as e:
        logger.error(f"Erro na sessão {charge_point_id}: {e}")
    finally:
        logger.info(f"Conexão encerrada para: {charge_point_id}")

async def main():
    port = int(os.environ.get("PORT", 9000))
    
    # ADICIONADO: ocpp1.6 na lista de subprotocols para evitar o erro 400 Bad Request
    async with serve(
        on_connect, 
        "0.0.0.0", 
        port, 
        subprotocols=['ocpp1.6', 'ocpp2.0.1']
    ):
        logger.info(f"Servidor iniciado. Escutando na porta {port}")
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Servidor finalizado.")
