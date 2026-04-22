import logging
from datetime import datetime
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call_result
from ocpp.v16.enums import RegistrationStatus, AuthorizationStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ocpp')

class Charger(cp):
    @on('BootNotification')
    async def on_boot_notification(self, **kwargs):
        return call_result.BootNotification(
            current_time=datetime.utcnow().isoformat(),
            interval=300,
            status=RegistrationStatus.accepted
        )

    @on('Heartbeat')
    async def on_heartbeat(self):
        return call_result.Heartbeat(
            current_time=datetime.utcnow().isoformat()
        )

    @on('Authorize')
    async def on_authorize(self, id_tag):
        logger.info(f"🔑 Verificando autorização para a tag: {id_tag}")
        # Aqui você poderia consultar um banco de dados. 
        # Por enquanto, vamos aceitar tudo:
        return call_result.Authorize(
            id_tag_info={
                'status': AuthorizationStatus.accepted,
                'expiryDate': '2030-12-31T23:59:59Z',
                'parentIdTag': 'PARENT_TAG'
            }
        )

    @on('StartTransaction')
    async def on_start_transaction(self, connector_id, id_tag, meter_start, timestamp, **kwargs):
        logger.info(f"⚡ Iniciando transação no conector {connector_id} para {id_tag}")
        return call_result.StartTransaction(
            transaction_id=1,  # ID da transação que você geraria no banco
            id_tag_info={
                'status': AuthorizationStatus.accepted
            }
        )

    @on('StatusNotification')
    async def on_status_notification(self, connector_id, error_code, status, **kwargs):
        return call_result.StatusNotification()