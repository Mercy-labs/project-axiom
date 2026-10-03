from dataclasses import dataclass

from .experiment import Experiment
from .ml.selector import ExperimentSelector


@dataclass
class ResearchPlanner:
    selector: ExperimentSelector

    def choose(
        self,
        predictor,
        tested: set[float],
    ) -> Experiment:

        candidate = self.selector.select(
            predictor=predictor,
            tested=tested,
        )

        return Experiment(
            input_value=candidate.input_value,
            name=f"adaptive_experiment_{int(candidate.input_value)}",
        )