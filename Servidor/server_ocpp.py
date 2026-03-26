import asyncio
import logging
import os
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

async def on_connect(websocket, path):
    """
    Gerencia novas conexões WebSocket.
    """
    # Extrai o ID do carregador da URL (ex: wss://url.com/NOME_DO_CARREGADOR)
    charge_point_id = path.strip('/')
    if not charge_point_id:
        charge_point_id = "unknown_device"

    logger.info(f"Nova conexão: {charge_point_id}")

    cp_instance = ChargePoint(charge_point_id, websocket)

    try:
        await cp_instance.start()
    except Exception as e:
        logger.error(f"Erro na sessão {charge_point_id}: {e}")
    finally:
        logger.info(f"Conexão encerrada para: {charge_point_id}")

async def main():
    # O Render exige o uso da variável de ambiente PORT
    port = int(os.environ.get("PORT", 9000))
    
    # "0.0.0.0" permite conexões externas
    async with serve(on_connect, "0.0.0.0", port, subprotocols=['ocpp2.0.1']):
        logger.info(f"Servidor OCPP 2.0.1 rodando na porta {port}")
        await asyncio.Future()  # Mantém o loop rodando infinitamente

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Servidor finalizado manualmente.")
