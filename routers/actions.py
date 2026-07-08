import logging
import time
from typing import List, Optional, Any, Dict
from fastapi import APIRouter
from pydantic import BaseModel, Field
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Задание скриптов для UI приложения"])

SAFE_REGEX = r"^[a-zA-Z0-9_.-]+$"


class StepModel(BaseModel):
    action: str
    locator: Optional[str] = None
    text: Optional[str] = None
    start_x: Optional[int] = None
    start_y: Optional[int] = None
    end_x: Optional[int] = None
    end_y: Optional[int] = None
    duration: Optional[int] = Field(default=800, ge=100, le=5000)


class ScriptCommand(BaseModel):
    device_id: str = Field(..., pattern=SAFE_REGEX)
    app_package: str = Field(..., pattern=SAFE_REGEX)
    app_activity: str = Field(..., pattern=SAFE_REGEX)
    steps: List[StepModel]

    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "emulator-5554",
                "app_package": "org.wikipedia",
                "app_activity": "org.wikipedia.main.MainActivity",
                "steps": [
                    {"action": "click", "locator": "//android.widget.TextView[@text='Search Wikipedia']"},
                    {"action": "change_focus"},
                    {"action": "type", "locator": "//android.widget.AutoCompleteTextView", "text": "Skoda Octavia"},
                    {"action": "click", "locator": "//android.widget.TextView[@text='Škoda Octavia']"},
                    {"action": "swipe", "start_x": 500, "start_y": 1800, "end_x": 500, "end_y": 400, "duration": 1000},
                    {"action": "back"},
                    {"action": "clear", "locator": "//android.widget.AutoCompleteTextView"}
                ]
            }
        }


@router.post("/run-scripts")
def run_scripts(command: ScriptCommand) -> Dict[str, Any]:
    logger.info(f"Запуск скрипта для {command.app_package} на {command.device_id}. Шагов: {len(command.steps)}")

    command_transcript = {
        "click": lambda driver, el, step: el.click(),
        "type": lambda driver, el, step: el.send_keys(step.text),
        "clear": lambda driver, el, step: el.clear(),
        "back": lambda driver, el, step: driver.back(),
        "change_focus": lambda driver, el, step: driver.press_keycode(61),
        "swipe": lambda driver, el, step: driver.swipe(
            start_x=step.start_x,
            start_y=step.start_y,
            end_x=step.end_x,
            end_y=step.end_y,
            duration=step.duration
        )
    }

    options = UiAutomator2Options()
    options.platform_name = 'Android'
    options.automation_name = 'UIAutomator2'
    options.device_name = command.device_id
    options.no_reset = True
    options.app_package = command.app_package
    options.app_activity = command.app_activity
    options.new_command_timeout = 30
    options.adb_exec_timeout = 20000

    driver = None
    try:
        logger.info("Подключение к Appium серверу")
        driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
        driver.implicitly_wait(10)

        for idx, step in enumerate(command.steps, 1):
            logger.info(f"[Шаг {idx}/{len(command.steps)}] Выполнение действия: {step.action}")
            element = None
            if step.locator:
                element = driver.find_element(AppiumBy.XPATH, step.locator)

            func = command_transcript.get(step.action)
            if func:
                func(driver, element, step)
                time.sleep(1.5)
            else:
                logger.warning(f"Неизвестное действие в скрипте: {step.action}")

        logger.info("Скрипт успешно завершен")
        return {"status": "success", "message": "Скрипт успешно выполнен"}

    except Exception as e:
        logger.error(f"Ошибка во время выполнения скрипта: {str(e)}")
        return {"status": "error", "message": str(e)}

    finally:
        if driver:
            logger.info("Закрытие сессии драйвера")
            driver.quit()