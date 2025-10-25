import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="Traders_Trade_Diary", version="0.1.0")

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

# Импорты роутеров
from .routers import trades, positions, notes, calculations, importer

# Подключение роутеров
app.include_router(trades.router, prefix="/api/v1", tags=["trades"])
app.include_router(positions.router, prefix="/api/v1", tags=["positions"])
app.include_router(notes.router, prefix="/api/v1", tags=["notes"])
app.include_router(calculations.router, prefix="/api/v1", tags=["calculations"])
app.include_router(importer.router, prefix="/api/v1", tags=["import"])

@app.get("/")
def read_root():
    return FileResponse("backend/static/index.html")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)