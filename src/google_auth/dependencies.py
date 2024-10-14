from google_auth.utils.security_handler import OpenIDConnectHandler
from google_auth.utils.state_storage import StateStorage
from google_auth.utils.http_client import HttpClient 
from settings import settings


http_client = HttpClient()
def get_http_client() -> HttpClient:
    return http_client

security_scheme = OpenIDConnectHandler(settings)

state_storage = StateStorage() # TODO(weldonfe): refactor somehow later, maybe to Redis storage?








