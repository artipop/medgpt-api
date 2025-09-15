import json

from common.http_client import HttpClient

api_uri = "https://enter.tochka.com/uapi/acquiring/v1.0"


class TochkaClient:
    def __init__(self, api_token: str, customer_code: int, base_redirect_url: str):
        self.api_token = api_token
        self.customer_code = customer_code
        self.base_redirect_url = base_redirect_url

    async def send_request(self, amount: str, uuid: str):
        request_data = {
            "customerCode": str(self.customer_code),
            "amount": amount,
            "purpose": "Подписка MedGPT",  # на месяц или год
            "paymentMode": ["sbp", "card"],
            "redirectUrl": self.base_redirect_url + "/success",
            "failRedirectUrl": self.base_redirect_url + "/fail",
            "consumerId": uuid
        }

        api_request = {
            "Data": request_data
        }

        # Serialize to JSON
        request_json = json.dumps(api_request)

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        client = HttpClient()
        session = await client.get_session()
        async with session.post(f"{api_uri}/payments", data=request_json, headers=headers) as response:
            if response.status == 200:
                response_json = await response.json()
                return response_json.get("Data")
            else:
                response_text = await response.text()
                raise Exception(f"Request failed with status {response.status}: {response_text}")
