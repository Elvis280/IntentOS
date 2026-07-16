import time
import base64
import io
from PIL import Image as PILImage

from app.services.verifier import verifier
from app.world.manager import world
from app.vision.capture import ScreenCapture
from app.vision.llm import analyze
from app.vision.analyzer import build_world
from app.executor.executor import Executor
from app.services.reasoner import next_action
from app.services.policy import policy
from app.runtime.job_manager import Job, JobStatus
from app.context.manager import ContextManager
from app.ui.manager import UIManager
from app.memory.manager import WorkingMemoryManager
from app.reflection.manager import ReflectionManager
from app.recovery.manager import RecoveryManager
from app.planning.manager import PlanManager
from app.core.logger import logger
import json
from pathlib import Path

capture = ScreenCapture()
executor = Executor()

def save_session(job: Job):
    """Save the job state to disk for session persistence."""
    session_dir = Path.home() / ".intentos" / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)
    session_file = session_dir / f"{job.job_id}.json"
    try:
        with open(session_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(job.to_dict(), indent=2, default=str))
    except Exception as e:
        logger.error(f"Failed to save session: {e}")

def fuzzy_duplicate(a: dict, b: dict) -> bool:
    """Return True if two actions are considered equivalent.

    For CLICK actions, coordinates within ±15 px on both axes are treated
    as the same action — catches retry loops where the reasoner varies
    coordinates slightly but repeats the same failed strategy.
    """
    if a["action"] != b["action"]:
        return False
    if a["action"] == "CLICK":
        ap = a.get("parameters", {})
        bp = b.get("parameters", {})
        return (
            abs(ap.get("x", 0) - bp.get("x", 0)) <= 15
            and abs(ap.get("y", 0) - bp.get("y", 0)) <= 15
        )
    return a.get("parameters") == b.get("parameters")

def run_job(job: Job) -> None:
    """
    Executes the full Observe→UI→Context→Memory→Reason→Policy→Execute→Verify loop.
    Reads job.should_stop() and job.wait_if_paused() at every phase boundary
    so that pause/resume/stop work without killing the thread forcibly.
    """
    logger.info(f"Starting job {job.job_id} with goal: {job.goal}")
    job.status = JobStatus.RUNNING
    history: list = []
    context_manager = ContextManager()
    ui_manager = UIManager()
    memory_manager = WorkingMemoryManager()
    reflection_manager = ReflectionManager()
    recovery_manager = RecoveryManager()
    plan_manager = PlanManager()
    
    forced_next_action = None
    # Cache from Phase 0 to reuse in first loop iteration
    cached_image = None
    cached_vision = None
    cached_world = None

    try:
        # ── Phase 0: Planning ─────────────────────────────────────────────
        job.update(stage="Planning")
        init_image = capture.capture()
        init_vision = analyze(init_image)
        init_state = build_world(init_vision)
        world.update(init_state)
        init_context_state = context_manager.update(job.goal, 0, world.get(), history)
        
        # Cache Phase 0 so step 1 doesn't need a second screenshot
        cached_image = init_image
        cached_vision = init_vision
        cached_world = world.get().model_dump()
        
        plan_manager.initialize(job.goal, cached_world, init_context_state.model_dump())
        
        for step in range(1, job.max_steps + 1):
            if job.should_stop():
                job.status = JobStatus.STOPPED
                return

            job.wait_if_paused()
            if job.should_stop():
                job.status = JobStatus.STOPPED
                return

            if job.clarification_answer:
                memory_manager.remember("latest_clarification", job.clarification_answer)
                logger.info(f"[Agent] Received user clarification: {job.clarification_answer}")
                job.clarification_answer = ""
                job.clarification_question = ""

            # ── Phase 1: Observe ─────────────────────────────────────────────
            job.update(stage="Observing", step=step)
            if cached_image is not None:
                # Reuse Phase 0 capture for the first iteration
                image = cached_image
                vision = cached_vision
                before = cached_world
                cached_image = cached_vision = cached_world = None
            else:
                image  = capture.capture()
                vision = analyze(image)
                state  = build_world(vision)
                world.update(state)
                before = world.get().model_dump()

            buf = io.BytesIO()
            img_obj = image if hasattr(image, "save") else PILImage.fromarray(image)
            img_obj.save(buf, format="PNG")
            screenshot_b64 = base64.b64encode(buf.getvalue()).decode()

            job.update(
                stage="Observing",
                world=before,
                screenshot=screenshot_b64,
                history=history,
            )

            job.wait_if_paused()
            if job.should_stop():
                job.status = JobStatus.STOPPED
                return

            # ── Phase 1.5: UI Intelligence ───────────────────────────────────
            ui_elements = ui_manager.update(vision, world.get())
            ui_elements_dict = ui_manager.to_dict_list()

            # ── Phase 1.6: Context ───────────────────────────────────────────
            context_state = context_manager.update(job.goal, step, world.get(), history)
            context_dict = context_state.model_dump()

            # ── Phase 1.8: Plan Sync ─────────────────────────────────────────
            active_step = plan_manager.get_active_step()
            active_step_dict = active_step.model_dump() if active_step else None
            plan_dict = plan_manager.get_plan().model_dump() if plan_manager.get_plan() else None
            progress_dict = plan_manager.get_progress().model_dump()
            
            # ── Phase 1.9: Working Memory ────────────────────────────────────
            memory_manager.update(
                goal=job.goal,
                step=step,
                world_snapshot=before,
                context_snapshot=context_dict,
                ui_elements=ui_elements_dict,
                history=history,
                plan=plan_dict,
                active_plan_step=active_step_dict,
                plan_progress=progress_dict
            )
            memory_dict = memory_manager.to_dict()

            job.update(plan=plan_dict, plan_progress=progress_dict)

            # ── Phase 2: Reason ───────────────────────────────────────────────
            job.update(stage="Reasoning")
            if forced_next_action:
                action = forced_next_action
                forced_next_action = None
                logger.info(f"[Agent] Using forced action from Recovery: {action}")
            else:
                action = next_action(job.goal, active_step_dict, before, context_dict, ui_elements_dict, memory_dict, history, image)

            job.update(
                stage="Reasoning",
                thought=action.get("thought", ""),
                action=action,
            )

            # ── Phase 3: Policy ───────────────────────────────────────────────
            if history and fuzzy_duplicate(action, history[-1]["action"]):
                logger.warning("[Agent] Repeated action detected — stopping loop.")
                job.update(stage="Failed", thought="Repeated failed action detected.", error="Loop detected.")
                job.status = JobStatus.FAILED
                return

            if action["action"] == "DONE":
                is_fully_done = plan_manager.mark_step_completed()
                if is_fully_done:
                    job.update(stage="Completed", thought="All plan steps completed.")
                    job.status = JobStatus.COMPLETED
                    return
                else:
                    job.update(stage="Completed Step", thought="Plan step completed. Moving to next.")
                    recovery_manager.reset_attempts()
                    continue

            job.wait_if_paused()
            if job.should_stop():
                job.status = JobStatus.STOPPED
                return

            # ── Phase 3: Policy ───────────────────────────────────────────────
            job.update(stage="Policy")
            action = policy.apply(
                goal=job.goal,
                world=before,
                history=history,
                action=action,
            )
            job.update(action=action)

            if action["action"] == "REASON_AGAIN":
                logger.warning("[Agent] Policy returned REASON_AGAIN — skipping execution.")
                history.append({"action": action, "verified": False})
                job.update(history=history)
                continue

            job.wait_if_paused()
            if job.should_stop():
                job.status = JobStatus.STOPPED
                return

            # ── Phase 4: Execute ──────────────────────────────────────────────
            job.update(stage="Executing")
            executor.execute(action)
            time.sleep(1.5)

            job.wait_if_paused()
            if job.should_stop():
                job.status = JobStatus.STOPPED
                return

            # ── Phase 5: Verify ───────────────────────────────────────────────
            job.update(stage="Verifying")
            image_after  = capture.capture()
            vision_after = analyze(image_after)
            state_after  = build_world(vision_after)
            world.update(state_after)
            after = world.get().model_dump()

            after_ui_elements = ui_manager.update(vision_after, world.get())
            after_ui_dict = ui_manager.to_dict_list()
            
            after_context_state = context_manager.update(job.goal, step, world.get(), history)
            after_context_dict = after_context_state.model_dump()

            verification_result = verifier.verify(before, after, ui_elements_dict, after_ui_dict, context_dict, after_context_dict, action)
            
            # ── Phase 6: Reflection ───────────────────────────────────────────
            job.update(stage="Reflecting")
            reflection_result = reflection_manager.reflect(verification_result, history)
            
            for mem_update in reflection_result.memory_updates:
                if mem_update.get("action") == "remember":
                    memory_manager.remember(mem_update.get("key"), mem_update.get("value"))
                elif mem_update.get("action") == "forget":
                    memory_manager.forget(mem_update.get("key"))
                    
            history.append({
                "action": action, 
                "verified": verification_result.model_dump(),
                "reflection": reflection_result.model_dump()
            })

            buf2 = io.BytesIO()
            img_obj2 = image_after if hasattr(image_after, "save") else PILImage.fromarray(image_after)
            img_obj2.save(buf2, format="PNG")
            screenshot_b64_after = base64.b64encode(buf2.getvalue()).decode()

            job.update(
                stage="Verifying",
                world=after,
                history=history,
                screenshot=screenshot_b64_after,
            )

            if not verification_result.verified:
                logger.warning(f"[Agent] Verification failed: {verification_result.verification_reason}")
                
            # ── Phase 7: Recovery ─────────────────────────────────────────────
            if not verification_result.verified and reflection_result.recovery_required:
                job.update(stage="Recovering")
                recovery_result = recovery_manager.recover(
                    verification=verification_result,
                    reflection=reflection_result,
                    last_action=action
                )
                
                # Update history with recovery decision
                history[-1]["recovery"] = recovery_result.model_dump()
                
                if recovery_result.strategy == "Abort":
                    replanned = plan_manager.mark_step_failed_and_replan(after, after_context_dict)
                    if replanned:
                        job.update(stage="Replanning", thought="Recovery failed. Generated alternative plan step.")
                        recovery_manager.reset_attempts()
                        continue
                    else:
                        job.update(stage="Failed", thought=recovery_result.explanation)
                        job.status = JobStatus.FAILED
                        return
                
                if recovery_result.strategy == "Ask User":
                    job.update(stage="Awaiting User Clarification", thought=recovery_result.explanation)
                    job.clarification_question = recovery_result.clarification_question
                    job.pause()
                    continue
                
                # For RETRY, WAIT_AND_RETRY, MODIFY_ACTION
                if recovery_result.modified_action:
                    forced_next_action = recovery_result.modified_action
                    
                continue
            else:
                if verification_result.verified:
                    recovery_manager.reset_attempts()

            # Cache the post-execution state for the next step's Phase 1
            cached_image = image_after
            cached_vision = vision_after
            cached_world = after

        job.status = JobStatus.COMPLETED

    except Exception as exc:
        job.error  = str(exc)
        job.status = JobStatus.FAILED
        logger.error(f"[Agent] Job {job.job_id} failed with exception: {exc}")
    finally:
        memory_manager.clear()
        save_session(job)
