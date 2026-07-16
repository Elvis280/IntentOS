import pyautogui
import subprocess
import webbrowser
import time


from app.core.logger import logger

class Executor:

    def execute(self, step):

        logger.info("[Executor] NEW EXECUTOR LOADED")

        action = step["action"]
        params = step.get("parameters", {})

        if action == "USE_SKILL":
            self.execute_skill(
                params.get("skill"),
                params.get("function"),
                params.get("args", {})
            )


        if action == "OPEN_APPLICATION":
            self.open_application(params.get("target"))

        elif action == "OPEN_URL":
            self.open_url(params.get("url"))

        elif action == "CLICK":
            x = params.get("x")
            y = params.get("y")

            if x is None or y is None:
                raise Exception("Missing click coordinates.")

            pyautogui.click(x, y)

        elif action == "TYPE":
            pyautogui.write(
                params.get("text", ""),
                interval=0.05
            )

        elif action == "PRESS_KEY":
            # Accept both "key" (schema) and "text" (reasoner fallback) for
            # backward compatibility. Raise clearly if neither is present.
            key = params.get("key") or params.get("text")
            if not key:
                raise Exception(
                    "PRESS_KEY requires a 'key' parameter (e.g. {'key': 'enter'}). "
                    "Got: " + str(params)
                )
            pyautogui.press(key)

        elif action == "WAIT":
            seconds = params.get("seconds")
            if seconds is None:
                logger.warning("[WAIT] 'seconds' not specified in params — defaulting to 1s.")
                seconds = 1
            time.sleep(float(seconds))

        elif action == "DONE":
            return

        else:
            raise Exception(f"Unknown action: {action}")

    def execute_skill(self, skill_name, function_name, args):
        import importlib
        if not skill_name or not function_name:
            raise Exception("USE_SKILL requires both 'skill' and 'function' parameters.")
        
        try:
            module = importlib.import_module(f"app.skills.{skill_name}")
            func = getattr(module, function_name)
            func(**args)
        except ImportError:
            raise Exception(f"Skill module '{skill_name}' not found.")
        except AttributeError:
            raise Exception(f"Function '{function_name}' not found in skill '{skill_name}'.")
        except Exception as e:
            raise Exception(f"Failed to execute skill '{skill_name}.{function_name}': {e}")

    def open_application(self, app):

        if not app:
            raise Exception("Application name missing.")

        try:
            subprocess.Popen(app)
        except Exception as e:
            raise Exception(f"Failed to open application: {e}")

    def open_url(self, url):

        if not url:
            raise Exception("URL missing.")

        webbrowser.open(url)