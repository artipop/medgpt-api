import jwt
from settings import settings


def encode_jwt(
    payload,
    private_key: str = settings.native_auth_jwt.private_key_path.read_text(),
    algorithm: str = settings.native_auth_jwt.algorithm
):
    encoded = jwt.encode(
        payload,
        private_key,
        algorithm=algorithm
    )
    return encoded


def decode_jwt(
    token,
    public_key: str = settings.native_auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.native_auth_jwt.algorithm
):
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=algorithm
    )
    return decoded
