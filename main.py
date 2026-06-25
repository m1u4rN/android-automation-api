import subprocess
import uvicorn
import time
from fastapi import FastAPI

app = FastAPI()


@app.get("/emulators")
def get_emulators():
    try:

        result = subprocess.run(["adb", "devices"], capture_output=True, text=True, check=True)
        device_ids = [line.split()[0] for line in result.stdout.splitlines()[1:] if line.strip()]

        return {
            "status": "success",
            "raw_output": result.stdout,
            "device_ids": device_ids
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/emulators/available")
def get_available_emulators():
    try:

        result = subprocess.run(["emulator", "-list-avds"], capture_output=True, text=True, check=True)
        avds = [line for line in result.stdout.splitlines() if line.strip()]

        return {
            "status": "success",
            "available_emulators": avds
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/emulator/start")
def start_emulator(emulator_name: str):
    try:

        subprocess.Popen(["emulator", "-avd", emulator_name])

        return {
            "status": "success",
            "emulator": f'Эмулятор {emulator_name} - запускается'
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.delete("/emulator/stop")
def stop_emulator(device_id: str):
    try:

        subprocess.run(["adb", "-s", device_id, "emu", "kill"], check=True)

        return {
            "status": "success",
            "message": f"Эмулятор {device_id} - выключен"
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/app/install")
def app_install(device_id: str, apk_path: str):
    try:

        result = subprocess.run(["adb", "-s", device_id, "install", apk_path], capture_output=True, text=True, check=True)

        return {
            "status": "success",
            "message": f"Приложение с путем {apk_path}, установлено на устройство {device_id}",
            "text": result.stdout
        }

    except Exception as e:
       return {"status": "error", "message": str(e)}


@app.post("/appium/start")
def appium_start():
    try:

        subprocess.Popen(["appium"], shell = True)

        return {
            "status": "success",
            "message": f"Appium сервер запущен",
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
