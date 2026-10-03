from .research import Experiment


class SimulationEngine:
    """
    Executes computational experiments.

    This is deliberately simulation-based so Axiom can experiment
    safely before interacting with real-world systems.
    """

    def run(self, experiment: Experiment) -> dict:
        input_value = experiment.parameters.get("input", 1)

        output = (
            input_value * 10
            + input_value ** 2
        )

        return {
            "input": input_value,
            "output": output,
        }


def design_experiments(hypothesis):
    experiments = []

    for value in range(1, 6):
        experiments.append(
            Experiment(
                name=f"simulation_{value}",
                hypothesis=hypothesis,
                parameters={
                    "input": value
                },
                purpose=(
                    "Measure how changing the input affects "
                    "the simulated outcome."
                ),
            )
        )

    return experiments