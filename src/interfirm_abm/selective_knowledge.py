"""Selective knowledge disclosure for Game 3C."""


class SelectiveKnowledgePool:
    """Store successful experiments voluntarily shared by firms."""

    def __init__(self):
        self.records = []

    def publish(self, experiment, shared):
        """Publish only successful experiments marked for sharing."""
        if not shared:
            return False

        if not experiment["accepted"]:
            return False

        self.records.append(dict(experiment))
        return True

    def observe(self, observer_id, round_number):
        """Return previously published knowledge from other firms."""
        return [
            dict(record)
            for record in self.records
            if record["firm_id"] != observer_id
            and record["round"] < round_number
        ]
