class Verifier:

    def verify(self, world, step):

        if world is None:
            return False

        action = step["action"]

        if action == "OPEN_APPLICATION":

            target = step["target"].lower()

            return any(
                target in app.lower()
                for app in world.applications
            )

        return True


verifier = Verifier()