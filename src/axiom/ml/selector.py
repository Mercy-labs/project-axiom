from dataclasses import dataclass
import math

from .predictor import MLPredictor


@dataclass
class CandidateScore:
    input_value: float
    predicted_value: float
    uncertainty: float
    score: float


class ExperimentSelector:
    def __init__(
        self,
        minimum: int = 1,
        maximum: int = 20,
    ):
        self.minimum = minimum
        self.maximum = maximum

    def select(
        self,
        predictor: MLPredictor,
        tested: set[float],
    ) -> CandidateScore:

        candidates = [
            float(value)
            for value in range(self.minimum, self.maximum + 1)
            if float(value) not in tested
        ]

        if not candidates:
            raise RuntimeError("No unused experiment candidates remain.")

        scored = []

        for value in candidates:
            prediction = predictor.predict(
                [[value]]
            )

            exploration_bonus = prediction.uncertainty

            score = (
                abs(prediction.value)
                + 1.5 * exploration_bonus
            )

            scored.append(
                CandidateScore(
                    input_value=value,
                    predicted_value=prediction.value,
                    uncertainty=prediction.uncertainty,
                    score=score,
                )
            )

        return max(
            scored,
            key=lambda item: item.score,
        )