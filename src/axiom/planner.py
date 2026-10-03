class ResearchPlanner:
    """
    Decides what Axiom should investigate next.

    The current strategy prioritises hypotheses with
    uncertainty and then hypotheses that have received
    contradictory evidence.
    """

    def choose_next_direction(
        self,
        hypotheses,
    ):

        if not hypotheses:
            return None

        # First investigate hypotheses that have not
        # yet received experimental evidence.
        untested = [
            hypothesis
            for hypothesis in hypotheses
            if hypothesis.tests_run == 0
        ]

        if untested:
            return max(
                untested,
                key=lambda h: h.confidence,
            )

        # Then investigate the least certain hypothesis.
        return min(
            hypotheses,
            key=lambda h: h.confidence,
        )

    def choose_next_input(
        self,
        hypothesis,
        completed_inputs,
    ):
        """
        Choose a new experimental input.

        Axiom avoids immediately repeating an experiment.
        """

        candidates = range(1, 11)

        for value in candidates:
            if value not in completed_inputs:
                return value

        return None