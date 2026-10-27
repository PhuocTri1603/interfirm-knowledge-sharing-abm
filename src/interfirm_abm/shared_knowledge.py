from copy import deepcopy


class SharedKnowledgeTimeline:
    """
    Store completed experiments shared by firms.

    At the beginning of round t, a firm can observe
    experiments completed through round t-1.

    The recipient cannot mutate the stored knowledge.
    """

    def __init__(self):
        self._rounds = {}

    def record_round(self, firms, round_number):
        if not isinstance(round_number, int) or round_number <= 0:
            raise ValueError("round_number must be positive.")

        if round_number in self._rounds:
            raise ValueError("Round already recorded.")

        if round_number > 1 and round_number - 1 not in self._rounds:
            raise ValueError("Previous round is missing.")

        records = []

        for firm in firms:
            matching = [
                record
                for record in firm.history
                if record["round"] == round_number
            ]

            if len(matching) != 1:
                raise ValueError(
                    "Each firm must have one completed experiment."
                )

            records.append(deepcopy(matching[0]))

        self._rounds[round_number] = records

    def observe(self, observer_id, round_number):
        if not isinstance(round_number, int) or round_number <= 0:
            raise ValueError("round_number must be positive.")

        visible_rounds = range(1, round_number)
        knowledge = []

        for past_round in visible_rounds:
            if past_round not in self._rounds:
                raise ValueError(
                    "Required previous round is unavailable."
                )

            for record in self._rounds[past_round]:
                if record["firm_id"] != observer_id:
                    knowledge.append(deepcopy(record))

        return knowledge
