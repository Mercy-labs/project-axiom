from dataclasses import dataclass


@dataclass
class Hypothesis:
    statement: str
    direction: str
    confidence: float


class HypothesisEngine:
    def generate(self, question: str) -> list[Hypothesis]:
        return [
            Hypothesis(
                statement=(
                    f"{question} may increase as the experimental input increases."
                ),
                direction="increasing",
                confidence=0.50,
            ),
            Hypothesis(
                statement=(
                    f"{question} may decrease as the experimental input increases."
                ),
                direction="decreasing",
                confidence=0.50,
            ),
            Hypothesis(
                statement=(
                    f"{question} may not have a consistent relationship with "
                    "the experimental input."
                ),
                direction="neutral",
                confidence=0.50,
            ),
        ]

    def score(
        self,
        hypothesis: Hypothesis,
        observed_direction: str,
    ) -> Hypothesis:
        if hypothesis.direction == observed_direction:
            confidence = min(hypothesis.confidence + 0.40, 1.0)
        else:
            confidence = max(hypothesis.confidence - 0.30, 0.0)

        return Hypothesis(
            statement=hypothesis.statement,
            direction=hypothesis.direction,
            confidence=confidence,
        )

    def rank(
        self,
        hypotheses: list[Hypothesis],
        observed_direction: str,
    ) -> list[Hypothesis]:
        scored = [
            self.score(hypothesis, observed_direction)
            for hypothesis in hypotheses
        ]

        return sorted(
            scored,
            key=lambda hypothesis: hypothesis.confidence,
            reverse=True,
        )