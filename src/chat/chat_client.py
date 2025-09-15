import base64

from aiohttp import FormData
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
            "Authorization": f"Basic {base64.b64encode(bytes(auth_str, 'utf-8')).decode('utf-8')}"
        }
        payload = "{\"message\":\"" + message + "\"}"
        async with session.post(url=f"{settings.llm_api_url}/get_answer",
                                data=payload,
                                headers=headers
                                ) as client_response:
            if client_response.status != 200:
                raise HTTPException(status_code=client_response.status)
            return await client_response.json()

    async def send_file(self, file_content, file_name, file_type):
        client = HttpClient()
        session = await client.get_session()
        auth_str = f"{settings.llm_api_login}:{settings.llm_api_password}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Authorization": f"Basic {base64.b64encode(bytes(auth_str, 'utf-8')).decode('utf-8')}"
        }
        data = FormData()
        data.add_field(
            "file",
            file_content,
            filename=file_name,
            content_type=file_type
        )
        async with session.post(url=f"{settings.llm_api_url}/uploadfile",
                                data=data,
                                headers=headers
                                ) as client_response:
            if client_response.status != 200:
                raise HTTPException(status_code=client_response.status)
