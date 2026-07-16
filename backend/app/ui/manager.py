"""
UI Manager.

The sole public interface for the Runtime to interact with UI Intelligence.
The Runtime should never access the detector internals directly.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.ui.models import UIElement, UIElementType
from app.ui.detector import UIDetector
from app.world.models import WorldState


class UIManager:
    """
    Manages the current set of detected UI elements for a single job execution.
    Instantiated per-job (same scope as ContextManager).
    """

    def __init__(self) -> None:
        self._detector = UIDetector()
        self._elements: List[UIElement] = []

    # ── Public API ────────────────────────────────────────────────────────────

    def update(self, vision_data: Dict[str, Any], world_state: WorldState) -> List[UIElement]:
        """Re-detect elements from the latest Vision + World snapshot."""
        self._elements = self._detector.detect(vision_data, world_state)
        return self._elements

    def get_elements(self) -> List[UIElement]:
        """Return all currently detected elements."""
        return list(self._elements)

    def get_selected(self) -> Optional[UIElement]:
        """Return the element currently marked as selected, if any."""
        for elem in self._elements:
            if elem.selected:
                return elem
        return None

    def find_by_text(self, text: str, case_sensitive: bool = False) -> List[UIElement]:
        """Find elements whose text contains the query string."""
        if not case_sensitive:
            text = text.lower()
        return [
            e for e in self._elements
            if (text in (e.text if case_sensitive else e.text.lower()))
        ]

    def find_by_type(self, element_type: UIElementType) -> List[UIElement]:
        """Find all elements of a specific type."""
        return [e for e in self._elements if e.type == element_type]

    def find_by_id(self, element_id: str) -> Optional[UIElement]:
        """Find a single element by its unique ID."""
        for elem in self._elements:
            if elem.id == element_id:
                return elem
        return None

    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Serialize the current element set for passing to the Reasoner."""
        return [e.model_dump() for e in self._elements]
