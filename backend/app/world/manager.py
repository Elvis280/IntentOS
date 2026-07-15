from .models import WorldState

class WorldManager:
    def __init__(self):
        self.current_state = None
    def update(self,state:WorldState):
        self.current_state = state
    def get(self):
        return self.current_state
world=WorldManager()