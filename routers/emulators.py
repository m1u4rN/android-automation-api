import logging
import subprocess
from typing import Dict, Any
from fastapi import APIRouter, Query

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/emulators", tags=["Управление эмуляторами"])

SAFE_REGEX = r"^[a-zA-Z0-9_.-]+$"

@router.get("/avds")
def get_available_avds() -> Dict[str, Any]:
    logger.info("Запрос списка доступных AVD")
    try:
        result = subprocess.run(
            ["emulator", "-list-avds"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        avds = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
        return {"status": "success", "avds": avds}
    except subprocess.TimeoutExpired:
        logger.error("Таймаут команды emulator -list-avds")
        return {"status": "error", "message": "Превышено время ожидания команды"}
    except Exception as e:
        logger.error(f"Ошибка получения списка AVD: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.get("/devices")
def get_running_devices() -> Dict[str, Any]:
    logger.info("Запрос списка запущенных устройств")
    try:
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        return {"status": "success", "output": result.stdout.strip()}
    except subprocess.TimeoutExpired:
        logger.error("Таймаут команды adb devices")
        return {"status": "error", "message": "Превышено время ожидания ADB"}
    except Exception as e:
        logger.error(f"Ошибка получения списка устройств: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.post("/start")
def start_emulator(
    emulator_name: str = Query(..., pattern=SAFE_REGEX),
    wipe_data: bool = Query(False)
) -> Dict[str, Any]:
    logger.info(f"Запуск эмулятора {emulator_name}, wipe_data={wipe_data}")
    try:
        command = ["emulator", "-avd", emulator_name]
        if wipe_data:
            command.append("-wipe-data")

        subprocess.Popen(command)
        logger.info(f"Команда запуска для {emulator_name} отправлена")
        return {
            "status": "success",
            "message": f"Эмулятор {emulator_name} запускается",
            "wiped": wipe_data
        }
    except Exception as e:
        logger.error(f"Ошибка запуска эмулятора {emulator_name}: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.delete("/stop")
def stop_emulator(
    device_id: str = Query(..., pattern=SAFE_REGEX),
    save_state: bool = Query(True)
) -> Dict[str, Any]:
    logger.info(f"Остановка эмулятора {device_id}, save_state={save_state}")
    try:
        if not save_state:
            logger.info(f"[{device_id}] Удаление снапшота default_boot")
            subprocess.run(
                ["adb", "-s", device_id, "emu", "avd", "snapshot", "delete", "default_boot"],
                check=True,
                timeout=15
            )

        logger.info(f"[{device_id}] Отправка команды выключения")
        subprocess.run(["adb", "-s", device_id, "emu", "kill"], check=True, timeout=15)

        state_msg = "СОХРАНЕНО" if save_state else "СБРОШЕНО"
        logger.info(f"[{device_id}] Эмулятор выключен, состояние: {state_msg}")
        return {
            "status": "success",
            "message": f"Эмулятор {device_id} выключен (состояние {state_msg})"
        }
    except subprocess.TimeoutExpired:
        logger.error(f"[{device_id}] Таймаут команды ADB")
        return {"status": "error", "message": "Превышено время ожидания команды ADB"}
    except Exception as e:
        logger.error(f"[{device_id}] Ошибка при остановке: {str(e)}")
        return {"status": "error", "message": str(e)}