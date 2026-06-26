from fastapi import APIRouter
import subprocess
from appium import webdriver
from appium.options.android import UiAutomator2Options
import time
from appium.webdriver.common.appiumby import AppiumBy

router = APIRouter(tags=["Задание скриптов для UI приложения"])

@router.post("/run-scripts")
def run_scripts(command: dict):
    command_transcript = {
        "click": lambda driver, el, step: el.click(),
        "type": lambda driver, el, step: el.send_keys(step['text']),
        "clear": lambda driver, el, step: el.clear(),
        "back": lambda driver, el, step: driver.back(),
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
                time.sleep(2)
            else:
                print(f"Неизвестное действие: {step['action']}")
        return {"status": "success", "message": "Скрипт успешно выполнен"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        driver.quit()