class Verifier:

    # Fields that change every observation cycle regardless of actions taken.
    # Excluding them prevents false negatives where the verifier rejects a
    # perfectly good step just because the clock ticked forward.
    IGNORED_FIELDS = {"timestamp"}

    def _comparable(self, state: dict) -> dict:
        """Return state dict with volatile fields stripped out."""
        return {k: v for k, v in state.items() if k not in self.IGNORED_FIELDS}

    def verify(self, before, after, action):

        before_cmp = self._comparable(before)
        after_cmp = self._comparable(after)

        if action["action"] == "OPEN_URL":
            # Window title should change when a new page loads
            return before_cmp["active_window"] != after_cmp["active_window"]

        if action["action"] == "OPEN_APPLICATION":
            # A new app should appear in the applications list
            before_apps = set(before_cmp["applications"])
            after_apps = set(after_cmp["applications"])
            return len(after_apps - before_apps) > 0

        if action["action"] == "CLICK":
            # Any meaningful change in the observable world counts as success
            return before_cmp != after_cmp

        if action["action"] == "TYPE":
            # Text state or active window should change after typing
            return before_cmp != after_cmp

        # PRESS_KEY, WAIT, SCROLL — assume success unless we have a
        # specific check; the agent loop handles retries
        return True


verifier = Verifier()