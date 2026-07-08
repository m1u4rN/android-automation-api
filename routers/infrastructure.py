import logging
import subprocess
from typing import Dict, Any
from fastapi import APIRouter, Query

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Инфраструктура"])

SAFE_REGEX = r"^[a-zA-Z0-9_.-]+$"
PATH_REGEX = r"^[a-zA-Z0-9_./\\:-]+$"

@router.post("/app/install")
def install_app(
    device_id: str = Query(..., pattern=SAFE_REGEX),
    apk_path: str = Query(..., pattern=PATH_REGEX)
) -> Dict[str, Any]:
    logger.info(f"Установка APK из {apk_path} на устройство {device_id}")
    try:
        result = subprocess.run(
            ["adb", "-s", device_id, "install", "-r", apk_path],
            capture_output=True,
            text=True,
            check=True,
            timeout=60
        )
        logger.info(f"Приложение успешно установлено на {device_id}")
        return {
            "status": "success",
            "message": f"APK успешно установлен на устройство {device_id}",
            "output": result.stdout.strip()
        }
    except subprocess.TimeoutExpired:
        logger.error(f"Таймаут установки APK на {device_id}")
        return {"status": "error", "message": "Превышено время ожидания установки APK"}
    except Exception as e:
        logger.error(f"Ошибка установки APK на {device_id}: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.delete("/app/uninstall")
def uninstall_app(
    device_id: str = Query(..., pattern=SAFE_REGEX),
    app_package: str = Query(..., pattern=SAFE_REGEX)
) -> Dict[str, Any]:
    logger.info(f"Удаление пакета {app_package} с устройства {device_id}")
    try:
        result = subprocess.run(
            ["adb", "-s", device_id, "uninstall", app_package],
            capture_output=True,
            text=True,
            check=True,
            timeout=20
        )
        logger.info(f"Пакет {app_package} успешно удален")
        return {
            "status": "success",
            "message": f"Приложение {app_package} удалено с устройства {device_id}",
            "output": result.stdout.strip()
        }
    except subprocess.TimeoutExpired:
        logger.error(f"Таймаут удаления пакета {app_package}")
        return {"status": "error", "message": "Превышено время ожидания удаления приложения"}
    except Exception as e:
        logger.error(f"Ошибка удаления пакета {app_package}: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.post("/appium/start")
def start_appium(
    port: int = Query(4723, ge=1024, le=65535)
) -> Dict[str, Any]:
    logger.info(f"Запуск сервера Appium на порту {port}")
    try:
        subprocess.Popen(["appium", "-p", str(port)])
        logger.info(f"Сервер Appium запущен в фоне на порту {port}")
        return {
            "status": "success",
            "message": f"Appium сервер запускается на порту {port}",
            "port": port
        }
    except Exception as e:
        logger.error(f"Ошибка при запуске Appium сервера: {str(e)}")
        return {"status": "error", "message": str(e)}