import uvicorn
from config.settings import settings

def start_server():
    print(f"Starting API Server on port 8000...")
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

if __name__ == "__main__":
    start_server()
