from fastapi import HTTPException


class StateTokenException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=401, 
            detail=detail
        )

class OpenIDConnectException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=401, 
            detail=detail
        )

        
