"""
UI Element detector.

Converts Vision output and WorldState into structured UIElement objects.
This is intentionally lightweight — no additional LLM calls, no expensive processing.
It reuses the data that the Vision module already produced.

Future enrichment sources (Windows UI Automation, Accessibility APIs,
browser a11y trees) would be added as additional detector methods or
as a separate enrichment pass that supplements these base elements.
"""
from __future__ import annotations

from typing import Any, Dict, List

from app.ui.models import UIElement, UIElementType, Bounds
from app.world.models import WorldState


# ── Heuristic type classification ─────────────────────────────────────────────
# Maps common substrings found in button/text labels to element types.
# This is a lightweight MVP — future versions can use UI Automation instead.

_TYPE_KEYWORDS: Dict[str, UIElementType] = {
    "button":     UIElementType.BUTTON,
    "btn":        UIElementType.BUTTON,
    "submit":     UIElementType.BUTTON,
    "ok":         UIElementType.BUTTON,
    "cancel":     UIElementType.BUTTON,
    "close":      UIElementType.BUTTON,
    "save":       UIElementType.BUTTON,
    "open":       UIElementType.BUTTON,
    "menu":       UIElementType.MENU,
    "file":       UIElementType.MENU_ITEM,
    "edit":       UIElementType.MENU_ITEM,
    "view":       UIElementType.MENU_ITEM,
    "help":       UIElementType.MENU_ITEM,
    "tab":        UIElementType.TAB,
    "checkbox":   UIElementType.CHECKBOX,
    "check":      UIElementType.CHECKBOX,
    "radio":      UIElementType.RADIO_BUTTON,
    "link":       UIElementType.LINK,
    "http":       UIElementType.LINK,
    "https":      UIElementType.LINK,
    "input":      UIElementType.INPUT,
    "search":     UIElementType.INPUT,
    "textbox":    UIElementType.TEXTBOX,
    "slider":     UIElementType.SLIDER,
    "image":      UIElementType.IMAGE,
    "icon":       UIElementType.ICON,
    "dialog":     UIElementType.DIALOG,
    "toolbar":    UIElementType.TOOLBAR,
    "ribbon":     UIElementType.RIBBON,
}


def _classify_text(text: str) -> UIElementType:
    """Heuristically classify an element by its label text."""
    lower = text.lower().strip()
    for keyword, elem_type in _TYPE_KEYWORDS.items():
        if keyword in lower:
            return elem_type
    return UIElementType.UNKNOWN


class UIDetector:
    """
    Extracts structured UIElement objects from Vision output + WorldState.

    No LLM calls. No expensive processing. Reuses existing data.
    """

    def detect(self, vision_data: Dict[str, Any], world_state: WorldState) -> List[UIElement]:
        """
        Build a list of UIElement objects from the raw Vision output dict
        and the parsed WorldState.
        """
        elements: List[UIElement] = []

        # 1. Buttons detected by Vision
        for btn_text in (vision_data.get("buttons") or world_state.buttons):
            elements.append(UIElement(
                type=UIElementType.BUTTON,
                text=btn_text,
                description=f"Button: {btn_text}",
                confidence=0.75,
            ))

        # 2. Text regions detected by Vision — classify heuristically
        for txt in (vision_data.get("text") or world_state.text):
            inferred_type = _classify_text(txt)
            # Avoid duplicating items already captured as buttons
            if inferred_type == UIElementType.BUTTON:
                continue
            elements.append(UIElement(
                type=inferred_type if inferred_type != UIElementType.UNKNOWN else UIElementType.LABEL,
                text=txt,
                description=txt,
                confidence=0.60,
            ))

        # 3. Applications listed in WorldState → Window elements
        for app_name in world_state.applications:
            elements.append(UIElement(
                type=UIElementType.WINDOW,
                text=app_name,
                description=f"Application window: {app_name}",
                confidence=0.70,
            ))

        # 4. Active window → mark as selected
        if world_state.active_window:
            for elem in elements:
                if elem.type == UIElementType.WINDOW and elem.text == world_state.active_window:
                    elem.selected = True
                    elem.confidence = 0.90

        return elements
