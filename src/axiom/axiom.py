from .config import Config
from .evaluator import Evaluation
from .experiment import Observation, SimulationEngine
from .hypothesis import HypothesisEngine
from .knowledge import KnowledgeBase
from .literature import SafeLiteratureSearcher
from .memory import ResearchMemory
from .planner import ExperimentPlanner
from .report import render_report
from .research import ScientificResearcher
from .verification import Verifier
from .ml.selector import ExperimentSelector


def run_axiom() -> str:
    config = Config()

    knowledge = KnowledgeBase()

    literature = SafeLiteratureSearcher(
        openalex_url=config.openalex_url,
        crossref_url=config.crossref_url,
    )

    researcher = ScientificResearcher(
        literature=literature,
        knowledge=knowledge,
    )

    question = (
        "How does the experimental input affect the measured output "
        "in our computational research environment?"
    )

    # Research the question using available literature sources.
    researcher.investigate(question)

    # Generate competing hypotheses.
    hypothesis_engine = HypothesisEngine()
    hypotheses = hypothesis_engine.generate(question)

    # Create the experimental environment.
    simulator = SimulationEngine()
    verifier = Verifier()

    selector = ExperimentSelector(
        min_value=config.min_candidate,
        max_value=config.max_candidate,
    )

    planner = ExperimentPlanner(selector)
    memory = ResearchMemory()

    observations: list[Observation] = []

    # Initial experiments provide the first evidence.
    for value in [1, 3]:
        result = simulator.run(value)

        observations.append(
            Observation(
                input_value=value,
                output_value=result.output,
            )
        )

    # Let the ML selector choose subsequent experiments.
    for _ in range(config.max_cycles):
        inputs = [observation.input_value for observation in observations]
        outputs = [observation.output_value for observation in observations]

        experiment = planner.next_experiment(inputs, outputs)

        result = simulator.run(experiment.input_value)

        observation = Observation(
            input_value=experiment.input_value,
            output_value=result.output,
        )

        observations.append(observation)

        memory.record(
            input_value=observation.input_value,
            output_value=observation.output_value,
        )

    # Evaluate the experimental evidence.
    evaluation = Evaluation.from_observations(observations)

    # Compare the competing hypotheses against the evidence.
    ranked_hypotheses = hypothesis_engine.rank(
        hypotheses,
        evaluation.direction,
    )

    selected_hypothesis = ranked_hypotheses[0]

    # Verify the evidence.
    verification = verifier.verify(
        observations=observations,
        evidence_strength=evaluation.evidence_strength,
    )

    report = render_report(
        question=question,
        hypothesis=selected_hypothesis.statement,
        observations=observations,
        conclusion=evaluation.conclusion,
        verification=verification,
    )

    print("=== PROJECT AXIOM HYPOTHESIS COMPETITION ===")
    print()
    print(f"Candidate hypotheses: {len(ranked_hypotheses)}")
    print()

    for index, hypothesis in enumerate(ranked_hypotheses, start=1):
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

    print(report)

    return report


def main() -> None:
    run_axiom()


if __name__ == "__main__":
    main()