from .research import ResearchQuestion, Hypothesis


class ReasoningModel:
    """
    Interface for Axiom's reasoning system.

    A real language model can be connected here later.
    """

    def generate_hypotheses(
        self,
        question: ResearchQuestion,
    ) -> list[Hypothesis]:

        return [
            Hypothesis(
                statement=(
                    "The proposed variable has a positive effect "
                    "on the measured outcome."
                ),
                confidence=0.34,
            ),
            Hypothesis(
                statement=(
                    "The proposed variable has a negative effect "
                    "on the measured outcome."
                ),
                confidence=0.33,
            ),
            Hypothesis(
                statement=(
                    "The proposed variable has little or no effect "
                    "on the measured outcome."
                ),
                confidence=0.33,
            ),
        ]

    def explain_result(self, question, hypothesis, evidence):
        return (
            f"Evidence was collected to test: "
            f"{hypothesis.statement}"
        )


class LocalReasoningModel(ReasoningModel):
    """
    Safe local reasoning engine used until a real model is connected.
    """

    pass