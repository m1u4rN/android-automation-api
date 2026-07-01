from fastapi import APIRouter, Body
import subprocess
from appium import webdriver
from appium.options.android import UiAutomator2Options
import time
from appium.webdriver.common.appiumby import AppiumBy

router = APIRouter(tags=["Задание скриптов для UI приложения"])

@router.post("/run-scripts")
def run_scripts(command: dict = Body(
        ...,
        examples=[
        {
            "device_id": "emulator-5554",
            "app_package": "org.wikipedia",
            "app_activity": "org.wikipedia.main.MainActivity",
            "steps": [
                # Внимание: если эмулятор на английском, замени 'Поиск по Википедии' на 'Search Wikipedia'
                {"action": "click", "locator": "//android.widget.TextView[@text='Поиск по Википедии']"},
                {"action": "change_focus"},
                {"action": "type", "locator": "//android.widget.AutoCompleteTextView", "text": "Skoda Octavia"},
                {"action": "click", "locator": "//android.widget.TextView[@text='Škoda Octavia']"},
                {"action": "swipe", "start_x": 500, "start_y": 1800, "end_x": 500, "end_y": 400, "duration": 1000},
                {"action": "back"},
                {"action": "clear", "locator": "//android.widget.AutoCompleteTextView"}
            ]
        }
    ]
)
):
    command_transcript = {
        "click": lambda driver, el, step: el.click(),
        "type": lambda driver, el, step: el.send_keys(step['text']),
        "clear": lambda driver, el, step: el.clear(),
        "back": lambda driver, el, step: driver.back(),
        "change_focus": lambda driver, el, step: driver.press_keycode(61),
        "swipe": lambda driver, el, step: driver.swipe(
                start_x=step['start_x'],
                start_y=step['start_y'],
                end_x=step['end_x'],
                end_y=step['end_y'],
                duration=step.get('duration', 800)
            )
        }

    options = UiAutomator2Options()
    options.platform_name = 'Android'
    options.automation_name = 'UIAutomator2'
    options.device_name = command['device_id']
    options.no_reset = True
    options.new_command_timeout = 300
    options.app_package = command['app_package']
    options.app_activity = command['app_activity']

    try:
        driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
        driver.implicitly_wait(10)


        for step in command['steps']:
            locator = step.get('locator')
            element = driver.find_element(AppiumBy.XPATH, locator) if locator else None
            func = command_transcript.get(step['action'])
            if func:
                func(driver, element, step)
                time.sleep(4)
            else:
                print(f"Неизвестное действие: {step['action']}")
        return {"status": "success", "message": "Скрипт успешно выполнен"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        driver.quit()