from .config import Config
from .literature import SafeLiteratureSearcher
from .knowledge import KnowledgeBase
from .hypothesis import HypothesisEngine
from .research import ScientificResearcher
from .report import ResearchReport


def _build_researcher(config: Config) -> ScientificResearcher:
    knowledge = KnowledgeBase()

    literature = SafeLiteratureSearcher(
        openalex_url=config.openalex_url,
        crossref_url=config.crossref_url,
    )

    return ScientificResearcher(
        literature_searcher=literature,
        knowledge_base=knowledge,
        hypothesis_engine=HypothesisEngine(),
    )


def _source_lines(source_status) -> list[str]:
    lines = []

    for result in source_status:
        if result.error:
            lines.append(
                f"{result.source}: unavailable"
            )
        else:
            lines.append(
                f"{result.source}: "
                f"{len(result.papers)} results"
            )

    return lines


def run_research(question: str) -> ResearchReport:
    """
    Run Axiom's real literature-based research pipeline.

    This path does not run the computational simulation.
    """

    config = Config.from_environment()

    researcher = _build_researcher(config)

    research_context = researcher.investigate(
        question
    )

    return ResearchReport(
        question=question,
        hypothesis=None,
        observations=[],
        conclusion=None,
        verification=None,
        papers_found=research_context.papers_found,
        sources=_source_lines(
            research_context.source_status
        ),
        reasoning=research_context.reasoning,
    )


def run_axiom(question: str) -> ResearchReport:
    """
    Run the original full Axiom experiment pipeline.

    This remains separate from the real literature-only
    research path while the research architecture is built.
    """

    from .experiment import SimulationEngine
    from .evaluator import EvidenceEvaluator
    from .planner import ResearchPlanner
    from .memory import ResearchMemory, MemoryEntry
    from .verification import Verifier
    from .ml.dataset import build_dataset
    from .ml.predictor import MLPredictor
    from .ml.selector import ExperimentSelector
    from .model import ReasoningModel

    config = Config.from_environment()

    researcher = _build_researcher(config)

    research_context = researcher.investigate(
        question
    )

    reasoning = ReasoningModel()

    hypothesis = reasoning.choose_hypothesis(
        research_context.hypotheses
    )

    simulator = SimulationEngine()
    evaluator = EvidenceEvaluator()
    verifier = Verifier()

    selector = ExperimentSelector(
        minimum=config.candidate_min,
        maximum=config.candidate_max,
    )

    planner = ResearchPlanner(
        selector=selector,
    )

    memory = ResearchMemory()

    observations = []
    tested = set()

    initial_values = [
        1.0,
        3.0,
    ]

    for value in initial_values:

        experiment = type(
            "InitialExperiment",
            (),
            {
                "input_value": value,
                "name": (
                    f"initial_experiment_{int(value)}"
                ),
            },
        )()

        observation = simulator.run(
            experiment
        )

        observations.append(
            observation
        )

        tested.add(value)

    for cycle in range(
        1,
        config.max_cycles + 1,
    ):

        if len(observations) >= 2:

            dataset = build_dataset(
                inputs=[
                    item.input_value
                    for item in observations
                ],
                outputs=[
                    item.output_value
                    for item in observations
                ],
            )

            predictor = MLPredictor()

            predictor.fit(
                dataset.features(),
                dataset.targets(),
            )

            experiment = planner.choose(
                predictor=predictor,
                tested=tested,
            )

        else:

            experiment = type(
                "FallbackExperiment",
                (),
                {
                    "input_value": 1.0,
                    "name": "fallback_experiment",
                },
            )()

        if experiment.input_value in tested:
            break

        observation = simulator.run(
            experiment
        )

        observations.append(
            observation
        )

        tested.add(
            experiment.input_value
        )

        evaluation = evaluator.evaluate(
            hypothesis=hypothesis,
            observations=observations,
        )

        memory.remember(
            MemoryEntry(
                cycle=cycle,
                hypothesis=hypothesis.statement,
                experiment=experiment.name,
                observation=(
                    observation.output_value
                ),
                conclusion=evaluation.conclusion,
                confidence=evaluation.strength,
            )
        )

    final_evaluation = evaluator.evaluate(
        hypothesis=hypothesis,
        observations=observations,
    )

    verification = verifier.verify(
        observation_count=len(observations),
        evidence_strength=(
            final_evaluation.strength
        ),
    )

    memory.save()

    return ResearchReport(
        question=question,
        hypothesis=hypothesis.statement,
        observations=[
            observation.output_value
            for observation in observations
        ],
        conclusion=final_evaluation.conclusion,
        verification=verification,
        papers_found=research_context.papers_found,
        sources=_source_lines(
            research_context.source_status
        ),
        reasoning=research_context.reasoning,
    )


def main() -> None:

    question = (
        "How does the experimental input affect "
        "the measured output in our computational "
        "research environment?"
    )

    report = run_axiom(question)

    print(
        report.render()
    )


if __name__ == "__main__":
    main()