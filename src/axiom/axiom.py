import numpy as np

from .config import Config
from .experiment import Experiment, Observation, SimulationEngine
from .hypothesis import HypothesisEngine
from .knowledge import KnowledgeBase
from .literature import SafeLiteratureSearcher
from .memory import MemoryEntry, ResearchMemory
from .ml.predictor import MLPredictor
from .ml.selector import ExperimentSelector
from .planner import ResearchPlanner
from .report import ResearchReport
from .research import ScientificResearcher
from .verification import Verifier


def determine_direction(observations: list[Observation]) -> str:
    if len(observations) < 2:
        return "neutral"

    first = observations[0].output_value
    last = observations[-1].output_value
    delta = last - first

    if abs(delta) < 0.5:
        return "neutral"

    if delta > 0:
        return "increasing"

    return "decreasing"


def calculate_evidence_strength(
    observations: list[Observation],
) -> float:
    if len(observations) < 2:
        return 0.0

    first = observations[0].output_value
    last = observations[-1].output_value

    delta = abs(last - first)

    strength = min(
        1.0,
        0.5 + 0.1 * len(observations) + 0.05 * delta,
    )

    return strength


def run_axiom() -> str:
    config = Config()

    question = (
        "How does the experimental input affect the measured output "
        "in our computational research environment?"
    )

    # ---------------------------------------------------------
    # 1. Literature and knowledge
    # ---------------------------------------------------------

    knowledge = KnowledgeBase()

    literature = SafeLiteratureSearcher(
        openalex_url=config.openalex_url,
        crossref_url=config.crossref_url,
    )

    researcher = ScientificResearcher(
        literature=literature,
        knowledge=knowledge,
    )

    researcher.investigate(question)

    # ---------------------------------------------------------
    # 2. Generate competing hypotheses
    # ---------------------------------------------------------

    hypothesis_engine = HypothesisEngine()
    hypotheses = hypothesis_engine.generate(question)

    # ---------------------------------------------------------
    # 3. Create the computational experiment environment
    # ---------------------------------------------------------

    simulator = SimulationEngine()

    selector = ExperimentSelector(
        minimum=config.min_candidate,
        maximum=config.max_candidate,
    )

    planner = ResearchPlanner(selector)
    predictor = MLPredictor()

    memory = ResearchMemory()
    observations: list[Observation] = []

    # ---------------------------------------------------------
    # 4. Run initial experiments
    # ---------------------------------------------------------

    initial_values = [1, 3]

    for value in initial_values:
        experiment = Experiment(
            input_value=float(value),
            name=f"initial_experiment_{value}",
        )

        observation = simulator.run(experiment)
        observations.append(observation)

    # ---------------------------------------------------------
    # 5. Let the ML model choose subsequent experiments
    # ---------------------------------------------------------

    for cycle in range(config.max_cycles):
        features = np.array(
            [
                [observation.input_value]
                for observation in observations
            ],
            dtype=float,
        )

        targets = np.array(
            [
                observation.output_value
                for observation in observations
            ],
            dtype=float,
        )

        predictor.fit(features, targets)

        tested = {
            observation.input_value
            for observation in observations
        }

        experiment = planner.choose(
            predictor=predictor,
            tested=tested,
        )

        observation = simulator.run(experiment)
        observations.append(observation)

        # Store the current research state in memory.
        memory.remember(
            MemoryEntry(
                cycle=cycle + 1,
                hypothesis=hypotheses[0].statement,
                experiment=experiment.name,
                observation=observation.output_value,
                conclusion="Experiment completed.",
                confidence=hypotheses[0].confidence,
            )
        )

    # ---------------------------------------------------------
    # 6. Analyse the accumulated evidence
    # ---------------------------------------------------------

    observed_direction = determine_direction(observations)

    evidence_strength = calculate_evidence_strength(
        observations
    )

    # ---------------------------------------------------------
    # 7. Rank competing hypotheses
    # ---------------------------------------------------------

    ranked_hypotheses = hypothesis_engine.rank(
        hypotheses,
        observed_direction,
    )

    selected_hypothesis = ranked_hypotheses[0]

    # ---------------------------------------------------------
    # 8. Build the conclusion
    # ---------------------------------------------------------

    if observed_direction == "increasing":
        conclusion = "The observations show an increasing trend."
    elif observed_direction == "decreasing":
        conclusion = "The observations show a decreasing trend."
    else:
        conclusion = (
            "The observations do not show a strong consistent trend."
        )

    # ---------------------------------------------------------
    # 9. Verify the evidence
    # ---------------------------------------------------------

    verifier = Verifier()

    verification = verifier.verify(
        observation_count=len(observations),
        evidence_strength=evidence_strength,
    )

    # ---------------------------------------------------------
    # 10. Save research memory
    # ---------------------------------------------------------

    memory.save()

    # ---------------------------------------------------------
    # 11. Build the final report
    # ---------------------------------------------------------

    report = ResearchReport(
        question=question,
        hypothesis=selected_hypothesis.statement,
        observations=[
            observation.output_value
            for observation in observations
        ],
        conclusion=conclusion,
        verification=verification,
    )

    rendered_report = report.render()

    # ---------------------------------------------------------
    # 12. Display hypothesis competition
    # ---------------------------------------------------------

    print("=== PROJECT AXIOM HYPOTHESIS COMPETITION ===")
    print()
    print(f"Candidate hypotheses: {len(ranked_hypotheses)}")
    print()

    for index, hypothesis in enumerate(
        ranked_hypotheses,
        start=1,
    ):
        print(
            f"{index}. "
            f"{hypothesis.direction.capitalize()} "
            f"(confidence: {hypothesis.confidence:.2f})"
        )
        print(f"   {hypothesis.statement}")
        print()

    print("Selected hypothesis:")
    print(selected_hypothesis.statement)
    print()

    print(rendered_report)

    return rendered_report


def main() -> None:
    run_axiom()


if __name__ == "__main__":
    main()