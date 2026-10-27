def select_transfer_experiment(
    shared_history,
    recipient_technology,
    rng,
    transfer_policy="same_technology",
):
    """
    Select a successful peer experiment under a transfer policy.

    Policies:
      same_technology: source and recipient technologies match.
      cross_technology: source and recipient technologies differ.
      mixed: all source technologies are eligible.

    Every eligible experiment has equal selection probability.

    Source success does not imply recipient success.
    Recipient outcomes must be evaluated separately.

    Returns a shallow copy of the selected record, or None.
    """

    valid_policies = {
        "same_technology",
        "cross_technology",
        "mixed",
    }

    if transfer_policy not in valid_policies:
        raise ValueError(
            f"Unknown transfer policy: {transfer_policy}"
        )

    eligible = []

    for record in shared_history:
        if record["accepted"] is not True:
            continue

        source_technology = record["technology"]

        if (
            transfer_policy == "same_technology"
            and source_technology != recipient_technology
        ):
            continue

        if (
            transfer_policy == "cross_technology"
            and source_technology == recipient_technology
        ):
            continue

        eligible.append(record)

    if not eligible:
        return None

    index = int(rng.integers(0, len(eligible)))

    return eligible[index].copy()
