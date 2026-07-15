from pydantic import BaseModel
from typing import List
from datetime import datetime

class WorldState(BaseModel):
    timestamp:datetime
    summary:str
    active_window:str
    applications: List[str]
    buttons: List[str]
    text:List[str]
    
    mouse_position:tuple[int,int] | None=None
    screen_width:int | None=None
    screen_height:int | None=None