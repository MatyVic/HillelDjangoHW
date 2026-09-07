import os
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "bookstoreHW.asgi:application",
        host=os.environ.get("UVICORN_HOST", "127.0.0.1"),
        port=int(os.environ.get("UVICORN_PORT", 8000)),
        reload=os.environ.get("DJANGO_DEBUG", "True") == "True",
        lifespan="off",
    )