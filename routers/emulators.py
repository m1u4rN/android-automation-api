from fastapi import APIRouter
import subprocess


router = APIRouter(prefix="/emulators", tags=["Управление эмуляторами"])

@router.get("")
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


@router.get("/available")
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


@router.post("/start")
def start_emulator(emulator_name: str):
    try:

        subprocess.Popen(["emulator", "-avd", emulator_name])

        return {
            "status": "success",
            "emulator": f'Эмулятор {emulator_name} - запускается'
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.delete("/stop")
def stop_emulator(device_id: str, save_state: bool = True):
    try:

        if not save_state:
            subprocess.run(["adb", "-s", device_id, "emu", "avd", "snapshot", "delete", "default_boot"])

        subprocess.run(["adb", "-s", device_id, "emu", "kill"], check=True)

        state_msg = "СОХРАНЕНО" if save_state else "СБРОШЕНО"
        return {
            "status": "success",
            "message": f"Эмулятор {device_id} выключен (состояние {state_msg})"
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}