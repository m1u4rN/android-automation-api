import logging
import uvicorn
from fastapi import FastAPI
from routers import emulators, infrastructure, actions


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

app = FastAPI(title="API для автоматизации мобильного эмулятора")

app.include_router(emulators.router)
app.include_router(infrastructure.router)
app.include_router(actions.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
