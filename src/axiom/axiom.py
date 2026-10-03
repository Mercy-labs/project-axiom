from .config import Config
from .evaluator import Evaluator
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

    # 1. Research the question using available literature sources.
    researcher.investigate(question)

    # 2. Generate competing hypotheses.
    hypothesis_engine = HypothesisEngine()
    hypotheses = hypothesis_engine.generate(question)

    # 3. Create the experimental environment.
    simulator = SimulationEngine()
    evaluator = Evaluator()
    verifier = Verifier()

    selector = ExperimentSelector(
        min_value=config.min_candidate,
        max_value=config.max_candidate,
    )

    planner = ExperimentPlanner(selector)
    memory = ResearchMemory()

    observations: list[Observation] = []

    # Initial experiments provide the first evidence.
    initial_inputs = [1, 3]

    for value in initial_inputs:
        result = simulator.run(value)

        observation = Observation(
            input_value=value,
            output_value=result.output,
        )

        observations.append(observation)

    # 4. Let the ML selector choose subsequent experiments.
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

    # 5. Evaluate the experimental evidence.
    evaluation = evaluator.evaluate(observations)

    # 6. Score every competing hypothesis against the observed direction.
    ranked_hypotheses = hypothesis_engine.rank(
        hypotheses,
        evaluation.direction,
    )

    selected_hypothesis = ranked_hypotheses[0]

    # 7. Verify the evidence