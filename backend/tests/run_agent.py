import asyncio
import json
import time
import sys

from pydantic import BaseModel
from app.world.manager import world as world_mgr
from app.vision.capture import ScreenCapture
from app.vision.llm import analyze
from app.vision.analyzer import build_world
from app.executor.executor import Executor
from app.services.reasoner import next_action

capture = ScreenCapture()
executor = Executor()

MAX_STEPS = 10


async def run_agent(goal_str):
    history = []
    print(f"\n{'='*60}")
    print(f"GOAL: {goal_str}")
    print(f"{'='*60}")

    for step_num in range(MAX_STEPS):
        print(f"\n  [Step {step_num + 1}] Observing screen...")
        image = capture.capture()
        vision = analyze(image)
        state = build_world(vision)
        world_mgr.update(state)
        w = world_mgr.get()
        print(f"           active_window : {w.active_window}")
        print(f"           applications  : {w.applications}")

        print(f"  [Step {step_num + 1}] Thinking...")
        action = next_action(goal_str, w.model_dump(), history, image)
        act = action.get("action", "?")
        params = action.get("parameters", {})
        thought = action.get("thought", "")
        print(f"           action  : {act}")
        print(f"           params  : {params}")
        print(f"           thought : {thought}")

        if history and action == history[-1]:
            print("  !! Repeated action detected — breaking loop.")
            break

        if act == "DONE":
            print("  => Agent signalled DONE.")
            break

        print(f"  [Step {step_num + 1}] Executing...")
        try:
            executor.execute(action)
        except Exception as e:
            print(f"  !! Execution error: {e}")
            break

        history.append(action)
        time.sleep(2)

    print(f"\n  Total steps executed: {len(history)}")
    return {
        "goal": goal_str,
        "steps_executed": len(history),
        "history": history
    }


if __name__ == "__main__":
    goal = sys.argv[1] if len(sys.argv) > 1 else "Open YouTube"
    result = asyncio.run(run_agent(goal))
    print("\nFINAL RESULT:")
    print(json.dumps(result, indent=2, default=str))
