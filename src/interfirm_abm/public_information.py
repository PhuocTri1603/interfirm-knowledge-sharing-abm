"""
Public information available to competing firms.

Snapshots expose observable firm performance but
never expose private allocations or experiment histories.
"""


def create_public_snapshot(firms, round_number):
    """Capture public information at a given round."""

    if not isinstance(round_number, int) or round_number < 0:
        raise ValueError("round_number must be non-negative.")

    snapshot = []

    for firm in firms:
        snapshot.append({
            "round": round_number,
            "firm_id": firm.firm_id,
            "technology": firm.technology,
            "output": float(firm.current_output),
        })

    return snapshot


def observe_competitors(snapshot, observer_id):
    """Return public records belonging to rival firms."""

    return [
        record.copy()
        for record in snapshot
        if record["firm_id"] != observer_id
    ]


class PublicInformationTimeline:
    """
    Store immutable-by-copy public snapshots.

    At the beginning of round t, agents may observe
    only the snapshot recorded at the end of t-1.
    """

    def __init__(self, firms):
        self._snapshots = {
            0: create_public_snapshot(firms, round_number=0)
        }

    def record_round(self, firms, round_number):
        if not isinstance(round_number, int) or round_number <= 0:
            raise ValueError("round_number must be positive.")

        if round_number in self._snapshots:
            raise ValueError("Snapshot already exists.")

        if round_number - 1 not in self._snapshots:
            raise ValueError("Previous round snapshot is missing.")

        self._snapshots[round_number] = (
            create_public_snapshot(firms, round_number)
        )

    def observe(self, observer_id, round_number):
        if not isinstance(round_number, int) or round_number <= 0:
            raise ValueError("round_number must be positive.")

        previous_round = round_number - 1

        if previous_round not in self._snapshots:
            raise ValueError(
                "Previous round public information unavailable."
            )

        return observe_competitors(
            self._snapshots[previous_round],
            observer_id,
        )

    def get_snapshot(self, round_number):
        if round_number not in self._snapshots:
            raise ValueError("Snapshot not available.")

        return [
            record.copy()
            for record in self._snapshots[round_number]
        ]
