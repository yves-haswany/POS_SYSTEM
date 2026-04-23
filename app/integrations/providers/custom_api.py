import requests
from app.integrations.base import IntegrationProvider

class CustomAPIProvider(IntegrationProvider):

    def push_order(self, order):
        config = self.tenant.integration_config

        url = config.get("api_url")
        api_key = config.get("api_key")

        payload = {
            "order_id": order.id,
            "total": order.total
        }

        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        requests.post(url, json=payload, headers=headers)