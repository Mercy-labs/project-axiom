class ResearchPlanner:

    def choose_next_direction(
        self,
        hypotheses,
        evaluations,
    ):
        """
        Select what Axiom should investigate next.

        The first version prioritises uncertain hypotheses.
        Later versions can use information gain, Bayesian
        reasoning, optimisation and active learning.
        """

        uncertain = [
            hypothesis
            for hypothesis, evaluation
            in zip(hypotheses, evaluations)
            if evaluation == "uncertain"
        ]

        if uncertain:
            return uncertain[0]

        for hypothesis, evaluation in zip(
            hypotheses,
            evaluations,
        ):
            if evaluation == "contradicted":
                return hypothesis

        if hypotheses:
            return hypotheses[0]

        return None