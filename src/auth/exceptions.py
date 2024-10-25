from fastapi import HTTPException, status


class NativeAuthException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=detail
        )


