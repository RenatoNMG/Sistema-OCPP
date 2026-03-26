import asyncio
import logging
import json
from datetime import datetime
from websockets import serve

from ocpp.routing import on
from ocpp.v201 import ChargePoint as cp
from ocpp.v201 import call_result

# Ativa logs para terminal
logging.basicConfig(level=logging.INFO)

# Criação de classe para a estação de recarga
class ChargePoint(cp):
    @on('BootNotification')
    async def on_boot_notification(self, charging_station, reason, **kwargs):
        print(f"[{datetime.now()}] BootNotification recebido: {charging_station=}, {reason=}, {kwargs=}")
        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status='Accepted'
        )

    @on('Heartbeat')
    async def on_heartbeat(self):
        print(f"[{datetime.now()}] Heartbeat recebido")
        return call_result.HeartbeatPayload(
            current_time=datetime.utcnow().isoformat()
        )

async def on_connect(websocket, path):
    """
    Função chamada para cada conexão de estação de recarga.
    """
    # Extrai ID do Charge Point do path da URL
    charge_point_id = path.strip('/')
    logging.info(f"Conexão recebida de: {charge_point_id}")

    # Cria instância da estação
    cp_instance = ChargePoint(charge_point_id, websocket)

    try:
        await cp_instance.start()
    except Exception as e:
        logging.error(f"Erro na conexão com {charge_point_id}: {e}")

async def main():
    # Inicia servidor WebSocket na porta 9000
    async with serve(on_connect, "0.0.0.0", 9000):
        logging.info("Servidor OCPP iniciado na porta 9000")
        await asyncio.Future()  # Mantém o servidor rodando

if __name__ == "__main__":
    asyncio.run(main())
