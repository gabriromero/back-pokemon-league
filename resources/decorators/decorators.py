import os
from flask import request

def secret_header_required(func):
    def wrapper(*args, **kwargs):
        secret_header = request.headers.get("X-SECRET-HEADER")
        if secret_header != os.getenv("SECRET_HEADER"):
            return {"message": "Invalid or missing Secret Header"}, 401
        return func(*args, **kwargs)
    return wrapper