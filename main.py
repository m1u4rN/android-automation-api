import subprocess
import uvicorn
import time
from fastapi import FastAPI


app = FastAPI()


@app.get("/emulators")
def get_emulators():
    try:

        result = subprocess.run(["adb", "devices"], capture_output=True, text=True, check=True)
        words = result.stdout.split()

        if len(words) > 4:
            device_id = words[4]
        else:
            device_id = "Нет активных устройств"

        return {
            "status": "success",
            "raw_output": result.stdout,
            "device_id" : device_id
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/emulator/start")
def start_emulator(emulator_name: str):
    try:
        subprocess.Popen(["emulator", "-avd", emulator_name])

        return {
            "status": "success",
            "emulator" : f'Эмулятор {emulator_name} - запускается'
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

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)