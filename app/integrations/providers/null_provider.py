from app.integrations.base import IntegrationProvider

class NullProvider(IntegrationProvider):
    def push_order(self, order):
        print("No integration configured")