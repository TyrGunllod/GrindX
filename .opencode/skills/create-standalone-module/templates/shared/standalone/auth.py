from fastapi import Header, HTTPException


def verify_api_key(x_api_key: str = Header(...)) -> str:
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    return x_api_key
