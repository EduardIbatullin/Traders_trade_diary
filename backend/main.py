import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI

app = FastAPI(title="Traders_Trade_Diary", version="0.1.0")

@app.get("/")
def read_root():
    return {"message": "Welcome to Traders_Trade_Diary API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Здесь будут добавлены маршруты
# from .routers import trades, positions, notes
# app.include_router(trades.router, prefix="/api/v1")
# app.include_router(positions.router, prefix="/api/v1")
# app.include_router(notes.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)