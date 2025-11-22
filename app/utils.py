# app/utils.py
from fastapi import HTTPException

def handle_http_error(e: Exception):
    # You can map http errors to friendly messages
    raise HTTPException(status_code=502, detail=str(e))
