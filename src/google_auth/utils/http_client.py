import aiohttp
from common.logger import logger
from common.singleton import singleton

@singleton
class HttpClient:
    def __init__(self):
        self.session = None

    async def init_session(self):
        """Initialize the aiohttp ClientSession."""
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def close_session(self):
        """Close the aiohttp ClientSession."""
        if self.session:
            await self.session.close()
            self.session = None

    async def get_session(self) -> aiohttp.ClientSession:
        if not self.session:
            await self.init_session()
        
        return self.session
    
    def __call__(self):
        return self