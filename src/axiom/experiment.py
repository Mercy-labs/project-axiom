from .research import Experiment


class SimulationEngine:
    """
    Computational scientific simulation engine.

    The current environment is intentionally simulated.
    This gives Axiom a safe environment in which to
    develop experimental reasoning.
    """

    def run(self, experiment: Experiment) -> dict:

        input_value = experiment.parameters.get(
            "input",
            1,
        )

        # Simulated scientific relationship.
        output = (
            input_value * 10
            + input_value ** 2
        )

        return {
            "input": input_value,
            "output": output,
        }


def design_experiment(
    hypothesis,
    input_value: int,
) -> Experiment:

    return Experiment(
        name=f"experiment_input_{input_value}",
        hypothesis=hypothesis,
        parameters={
            "input": input_value,
        },
        purpose=(
            "Measure how changing the input variable "
            "affects the simulated outcome."
        ),
    )