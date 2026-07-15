import pyautogui
import subprocess
import webbrowser
import time


class Executor:

    def execute(self, step):

        action = step["action"]

        if action == "OPEN_APPLICATION":
            self.open_application(step["target"])

        elif action == "OPEN_URL":
            self.open_url(step["target"])

        elif action == "TYPE":
            pyautogui.write(step["target"], interval=0.05)

        elif action == "PRESS_KEY":
            pyautogui.press(step["target"])

        elif action == "WAIT":
            time.sleep(float(step["target"]))

        else:
            raise Exception(f"Unknown action {action}")

    def open_application(self, app):

        try:
            subprocess.Popen(app)
        except Exception as e:
            print(e)

    def open_url(self, url):

        webbrowser.open(url)