import uvicorn
from fastapi import FastAPI
from routers import emulators, infrastructure, actions


app = FastAPI(title='API для автоматизации мобильного эмулятора')
app.include_router(emulators.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
