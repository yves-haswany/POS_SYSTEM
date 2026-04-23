from app.integrations.providers.null_provider import NullProvider
from app.integrations.providers.custom_api import CustomAPIProvider

def get_provider(tenant):
    if tenant.integration_type == "custom_api":
        return CustomAPIProvider(tenant)

    return NullProvider(tenant)