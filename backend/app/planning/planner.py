import json
from app.core.llm import client, MODEL
from app.planning.models import ExecutionPlan, PlanStep, PlanStepStatus

PLANNER_PROMPT = """
You are the Planner Agent of IntentOS.

You receive:
1. User Goal
2. Current World State (Objective desktop state)
3. Current Context (Semantic desktop state)

Your job is to convert the User Goal into a structured ExecutionPlan.
Focus on HIGH-LEVEL objectives. Do NOT generate click coordinates or low-level UI actions.
Break the task down into logical, sequential steps.

Return ONLY valid JSON.

Schema:
{
    "goal": "...",
    "steps": [
        {
            "title": "...",
            "description": "...",
            "objective": "...",
            "expected_result": "...",
            "completion_condition": "..."
        }
    ]
}
"""

REPLAN_PROMPT = """
You are the Planner Agent of IntentOS.

A specific step in the current plan has FAILED permanently.
Your job is to generate an ALTERNATIVE step to replace it.
Do NOT regenerate the entire plan. Only return the alternative step.

You receive:
1. User Goal
2. Failed Step Details
3. Current World State
4. Current Context

Return ONLY valid JSON.

Schema:
{
    "title": "...",
    "description": "...",
    "objective": "...",
    "expected_result": "...",
    "completion_condition": "..."
}
"""

class Planner:
    """
    LLM-driven Planner.
    """
    
    def create_plan(self, goal: str, world: dict, context: dict) -> ExecutionPlan:
        response = client.models.generate_content(
            model=MODEL,
            contents=[
                PLANNER_PROMPT,
                f"Goal:\n{goal}",
                f"World:\n{json.dumps(world, indent=2, default=str)}",
                f"Context:\n{json.dumps(context, indent=2, default=str)}"
            ]
        )
        
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            
        data = json.loads(text)
        
        steps = []
        for s in data.get("steps", []):
            steps.append(PlanStep(
                title=s.get("title", ""),
                description=s.get("description", ""),
                objective=s.get("objective", ""),
                expected_result=s.get("expected_result", ""),
                completion_condition=s.get("completion_condition", "")
            ))
            
        return ExecutionPlan(goal=data.get("goal", goal), steps=steps)
        
    def replan(self, goal: str, failed_step: PlanStep, world: dict, context: dict) -> PlanStep:
        response = client.models.generate_content(
            model=MODEL,
            contents=[
                REPLAN_PROMPT,
                f"Goal:\n{goal}",
                f"Failed Step:\n{failed_step.model_dump_json(indent=2)}",
                f"World:\n{json.dumps(world, indent=2, default=str)}",
                f"Context:\n{json.dumps(context, indent=2, default=str)}"
            ]
        )
        
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            
        s = json.loads(text)
        return PlanStep(
            title=s.get("title", ""),
            description=s.get("description", ""),
            objective=s.get("objective", ""),
            expected_result=s.get("expected_result", ""),
            completion_condition=s.get("completion_condition", "")
        )
