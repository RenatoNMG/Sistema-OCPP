import asyncio
import logging
import os
from datetime import datetime
from websockets import serve

# Importamos a versão 1.6 que é mais simples para testes manuais
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call_result
from ocpp.v16.enums import RegistrationStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ocpp')

class ChargePoint(cp):
    @on('BootNotification')
    async def on_boot_notification(self, charge_point_model, charge_point_vendor, **kwargs):
        logger.info(f"Sucesso! Recebido Boot de: {charge_point_model}")
        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status=RegistrationStatus.accepted
        )

async def on_connect(websocket, path):
    charge_point_id = path.strip('/') or "Carregador_Teste"
    logger.info(f"Conectado: {charge_point_id}")
    
    cp_instance = ChargePoint(charge_point_id, websocket)
    try:
        await cp_instance.start()
    except Exception as e:
        logger.error(f"Erro: {e}")

async def main():
    port = int(os.environ.get("PORT", 9000))
    # Importante: Mantemos o subprotocolo que o app espera
    async with serve(on_connect, "0.0.0.0", port, subprotocols=['ocpp1.6']):
        logger.info(f"Servidor pronto na porta {port}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
