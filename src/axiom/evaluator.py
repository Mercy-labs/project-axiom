from dataclasses import dataclass
from .experiment import Observation
from .hypothesis import Hypothesis


@dataclass
class Evaluation:
    hypothesis: str
    observations: list[Observation]
    conclusion: str
    strength: float


class EvidenceEvaluator:
    def evaluate(
        self,
        hypothesis: Hypothesis,
        observations: list[Observation],
    ) -> Evaluation:

        if len(observations) < 2:
            return Evaluation(
                hypothesis=hypothesis.statement,
                observations=observations,
                conclusion="Insufficient observations.",
                strength=0.0,
            )

        first = observations[0].output_value
        last = observations[-1].output_value

        delta = last - first

        if abs(delta) < 0.5:
            conclusion = "The observed change is small."
            agreement = 0.5

        elif delta > 0:
            conclusion = "The observations show an increasing trend."
            agreement = (
                0.8 if hypothesis.predicted_direction == "positive"
                else 0.2
            )

        else:
            conclusion = "The observations show a decreasing trend."
            agreement = (
                0.8 if hypothesis.predicted_direction == "negative"
                else 0.2
            )

        strength = min(
            1.0,
            agreement * (0.5 + 0.1 * len(observations)),
        )

        return Evaluation(
            hypothesis=hypothesis.statement,
            observations=observations,
            conclusion=conclusion,
            strength=strength,
        )