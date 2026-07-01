from fastapi import APIRouter
import subprocess


router = APIRouter(tags=["Инфраструктура"])

@router.post("/app/install")
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


@router.post("/appium/start")
def appium_start():
    try:

        subprocess.Popen(["appium"], shell = True)

        return {
            "status": "success",
            "message": f"Appium сервер запущен",
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.delete("/app/uninstall")
def app_uninstall(device_id: str, app_package: str):
    try:

        result = subprocess.run(
            ["adb", "-s", device_id, "uninstall", app_package], capture_output=True, text=True, check=True)

        return {
            "status": "success",
            "message": f"Приложение {app_package} удалено с устройства {device_id}",
            "text": result.stdout.strip()
        }

    except Exception as e:
       return {"status": "error", "message": str(e)}