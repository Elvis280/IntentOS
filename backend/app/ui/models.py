"""
UI Element models.

Every detected desktop element is represented as a structured UIElement object,
replacing reliance on raw OCR strings. The model is designed so future integrations
(Windows UI Automation, Accessibility APIs, browser a11y trees, Office object models,
VS Code extensions) can enrich elements without changing the schema.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import uuid


class UIElementType(str, Enum):
    """Supported UI element types. Unknown elements are handled gracefully."""
    BUTTON = "Button"
    TEXTBOX = "TextBox"
    INPUT = "Input"
    IMAGE = "Image"
    MENU = "Menu"
    MENU_ITEM = "MenuItem"
    DIALOG = "Dialog"
    WINDOW = "Window"
    TAB = "Tab"
    RIBBON = "Ribbon"
    TOOLBAR = "Toolbar"
    CHECKBOX = "Checkbox"
    RADIO_BUTTON = "RadioButton"
    SLIDER = "Slider"
    TABLE = "Table"
    TREE = "Tree"
    LINK = "Link"
    ICON = "Icon"
    LABEL = "Label"
    UNKNOWN = "Unknown"


class Bounds(BaseModel):
    """Pixel-space bounding box for a UI element."""
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0

    @property
    def center(self) -> tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)


class UIElement(BaseModel):
    """
    A single detected interface element on the desktop.

    Fields are intentionally broad so that future enrichment sources
    (UI Automation, a11y APIs, browser trees, Office OMs) can populate them
    without schema changes.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    type: UIElementType = UIElementType.UNKNOWN
    text: str = ""
    description: str = ""
    bounds: Bounds = Field(default_factory=Bounds)
    center: tuple[int, int] = (0, 0)
    enabled: bool = True
    visible: bool = True
    selected: bool = False
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        """Auto-compute center from bounds if not explicitly set."""
        if self.center == (0, 0) and (self.bounds.width > 0 or self.bounds.height > 0):
            self.center = self.bounds.center
