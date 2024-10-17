from google_auth.utils.security_handler import OpenIDConnectHandler
from google_auth.utils.state_storage import StateStorage
from settings import settings

security_scheme = OpenIDConnectHandler(settings)
state_storage = StateStorage() # TODO(weldonfe): refactor somehow later, maybe to Redis storage?





