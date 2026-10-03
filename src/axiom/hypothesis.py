from dataclasses import dataclass


@dataclass
class Hypothesis:
    statement: str
    predicted_direction: str
    confidence: float


class HypothesisEngine:
    def generate(
        self,
        question: str,
        knowledge_context: str = "",
    ) -> list[Hypothesis]:

        context_signal = "available literature"

        if not knowledge_context.strip():
            context_signal = "limited prior evidence"

        return [
            Hypothesis(
                statement=(
                    f"{question} may increase as the experimental input increases."
                ),
                predicted_direction="positive",
                confidence=0.50,
            ),
            Hypothesis(
                statement=(
                    f"{question} may decrease as the experimental input increases."
                ),
                predicted_direction="negative",
                confidence=0.30,
            ),
            Hypothesis(
                statement=(
                    f"{question} may remain relatively stable across the tested range."
                ),
                predicted_direction="neutral",
                confidence=0.20,
            ),
        ]