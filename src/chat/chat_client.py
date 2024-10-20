import base64

from fastapi import HTTPException

from common.http_client import HttpClient


class ChatClient:
    async def send_message(self, message: str):
        client = HttpClient()
        session = await client.get_session()
        auth_str = "pmd-fnt-1:OIr%gn`0L|T03D7=;S#{"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Authorization": f"Basic {base64.b64encode(bytes(auth_str, 'utf-8')).decode('utf-8')}"}
        payload = "{\"message\":\"" + message + "\"}"
        async with session.post(url="https://bck.mymedgpt.com/get_answer",
                                data=payload,
                                headers=headers
                                ) as client_response:
            if client_response.status != 200:
                raise HTTPException(status_code=client_response.status)
            return client_response.json()
