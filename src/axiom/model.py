from .research import ResearchQuestion, Hypothesis


class ReasoningModel:
    """
    Reasoning interface for Axiom.

    This version uses deterministic scientific reasoning.
    A more advanced reasoning model can be connected later.
    """

    def generate_hypotheses(
        self,
        question: ResearchQuestion,
    ) -> list[Hypothesis]:

        return [
            Hypothesis(
                statement=(
                    "The proposed variable has a positive "
                    "effect on the measured outcome."
                ),
                confidence=0.34,
            ),
            Hypothesis(
                statement=(
                    "The proposed variable has a negative "
                    "effect on the measured outcome."
                ),
                confidence=0.33,
            ),
            Hypothesis(
                statement=(
                    "The proposed variable has little or no "
                    "effect on the measured outcome."
                ),
                confidence=0.33,
            ),
        ]

    def update_belief(
        self,
        hypothesis: Hypothesis,
        evaluation: str,
    ):
        """
        Update the model's belief using experimental evidence.
        """

        hypothesis.update_from_evidence(
            evaluation
        )

    def explain_result(
        self,
        hypothesis: Hypothesis,
        analysis: dict,
    ) -> str:

        return (
            f"The experiment produced a "
            f"{analysis['relationship']} relationship. "
            f"This evidence makes the hypothesis "
            f"{analysis['relationship']} relative to "
            f"the observed data."
        )


class LocalReasoningModel(ReasoningModel):
    """
    Local reasoning engine.

    This provides Axiom with a safe deterministic
    reasoning layer before a larger model is connected.
    """

    pass