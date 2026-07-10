import logging
from typing import List
from models.dto.ai_dto import CustomerCluster

logger = logging.getLogger("wa_service")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

class WhatsAppService:
    @staticmethod
    async def send_promo_to_segment(customers: List[CustomerCluster], message_template: str) -> int:
        """
        Mensimulasikan pengiriman pesan WhatsApp promosi.
        Mendukung Mock Provider seperti yang disepakati.
        """
        success_count = 0
        for customer in customers:
            if not customer.phone:
                continue
                
            # Personalisasi pesan
            msg = message_template.replace("{name}", customer.name)
            
            # Simulasi pengiriman (Mock Provider)
            logger.info(f"Mock WA Send -> To: {customer.phone} ({customer.cluster_label}) | Message: {msg}")
            success_count += 1
            
        return success_count
