from dataclasses import dataclass
import math


@dataclass
class Experiment:
    input_value: float
    name: str


@dataclass
class Observation:
    input_value: float
    output_value: float


class SimulationEngine:
    """
    Deterministic computational environment.

    This is deliberately labelled as a simulation. It is not presented
    as a real physical scientific experiment.
    """

    def run(self, experiment: Experiment) -> Observation:
        x = experiment.input_value

        output = (
            0.8 * x
            + 2.0 * math.sin(x / 2.0)
            + 0.03 * (x ** 2)
        )

        return Observation(
            input_value=x,
            output_value=output,
        )