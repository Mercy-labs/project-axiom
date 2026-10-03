from dataclasses import dataclass


@dataclass
class ResearchState:
    question: str
    cycle: int
    observations: list[float]
    best_hypothesis: str | None = None
    confidence: float = 0.0


class ReasoningModel:
    def choose_hypothesis(self, hypotheses):
        if not hypotheses:
            raise ValueError("No hypotheses available.")

        return max(
            hypotheses,
            key=lambda hypothesis: hypothesis.confidence,
        )