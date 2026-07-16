"""
UI Intelligence package.

Transforms raw Vision output into structured UI element objects.
The World Model answers "What exists?"
UI Intelligence answers "What interface elements exist?"
"""
from .models import UIElement, UIElementType, Bounds
from .manager import UIManager
