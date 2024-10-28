import base64

from fastapi import HTTPException

from common.http_client import HttpClient
from settings import settings


class ChatClient:
    async def send_message(self, message: str):
        client = HttpClient()
        session = await client.get_session()
        auth_str = f"{settings.llm_api_login}:{settings.llm_api_password}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Authorization": f"Basic {base64.b64encode(bytes(auth_str, 'utf-8')).decode('utf-8')}"}
        payload = "{\"message\":\"" + message + "\"}"
        async with session.post(url=f"{settings.llm_api_url}/get_answer",
                                data=payload,
                                headers=headers
                                ) as client_response:
            if client_response.status != 200:
                raise HTTPException(status_code=client_response.status)
            return await client_response.json()
