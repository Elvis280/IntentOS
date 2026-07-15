from datetime import datetime
from app.world.models import WorldState

def build_world(data):
    return WorldState(
        timestamp=datetime.now(),
        summary=data["summary"],
        active_window=data["active_window"],
        applications=data["applications"],
        buttons=data["buttons"],
        text=data["text"]
    )