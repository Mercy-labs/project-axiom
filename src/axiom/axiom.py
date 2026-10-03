from .research import (
    ResearchQuestion,
    ResearchState,
    Evidence,
)

from .model import LocalReasoningModel

from .experiment import (
    SimulationEngine,
    design_experiment,
)

from .evaluator import EvidenceEvaluator
from .memory import ResearchMemory
from .planner import ResearchPlanner


MAX_CYCLES = 6


def run_research(question_text):

    print("=" * 60)
    print("AXIOM")
    print("Adaptive Scientific Discovery Engine")
    print("=" * 60)
    print()

    question = ResearchQuestion(
        question_text
    )

    state = ResearchState(
        question=question
    )

    model = LocalReasoningModel()
    simulator = SimulationEngine()
    evaluator = EvidenceEvaluator()
    memory = ResearchMemory()
    planner = ResearchPlanner()

    print("RESEARCH QUESTION")
    print(question.question)
    print()

    print("GENERATING INITIAL HYPOTHESES")
    print()

    hypotheses = model.generate_hypotheses(
        question
    )

    for hypothesis in hypotheses:

        state.add_hypothesis(
            hypothesis
        )

        print(
            f"- {hypothesis.statement}"
        )

        print(
            f"  confidence="
            f"{hypothesis.confidence:.2f}"
        )

    print()

    completed_inputs = []

    for cycle in range(
        1,
        MAX_CYCLES + 1,
    ):

        state.next_cycle()

        print("=" * 60)
        print(
            f"RESEARCH CYCLE {cycle}"
        )
        print("=" * 60)
        print()

        hypothesis = (
            planner.choose_next_direction(
                hypotheses
            )
        )

        if hypothesis is None:
            print(
                "No research direction available."
            )
            break

        input_value = (
            planner.choose_next_input(
                hypothesis,
                completed_inputs,
            )
        )

        if input_value is None:
            print(
                "No unused experimental inputs remain."
            )
            break

        experiment = design_experiment(
            hypothesis,
            input_value,
        )

        state.add_experiment(
            experiment
        )

        print("SELECTED HYPOTHESIS")
        print(
            hypothesis.statement
        )

        print(
            f"Current confidence: "
            f"{hypothesis.confidence:.2f}"
        )

        print()

        print("EXPERIMENT")
        print(
            f"Name: {experiment.name}"
        )

        print(
            f"Input: {input_value}"
        )

        print(
            f"Purpose: "
            f"{experiment.purpose}"
        )

        print()

        result = simulator.run(
            experiment
        )

        completed_inputs.append(
            input_value
        )

        print("OBSERVATION")
        print(
            f"Input: {result['input']}"
        )

        print(
            f"Output: {result['output']}"
        )

        print()

        # Analyse the new observation together
        # with previous observations.
        previous_results = []

        for old_experiment in state.experiments:

            old_result = simulator.run(
                old_experiment
            )

            previous_results.append(
                old_result
            )

        analysis = evaluator.analyse(
            previous_results
        )

        evaluation = (
            evaluator.evaluate_hypothesis(
                hypothesis,
                analysis,
            )
        )

        model.update_belief(
            hypothesis,
            evaluation,
        )

        explanation = model.explain_result(
            hypothesis,
            analysis,
        )

        evidence = Evidence(
            experiment=experiment.name,
            hypothesis=hypothesis.statement,
            observations=analysis,
            conclusion=explanation,
            strength=0.7,
        )

        state.add_evidence(
            evidence
        )

        memory.remember(
            {
                "cycle": cycle,
                "question": question.question,
                "hypothesis": hypothesis.statement,
                "confidence": hypothesis.confidence,
                "status": hypothesis.status,
                "evaluation": evaluation,
                "input": input_value,
                "output": result["output"],
                "relationship": analysis[
                    "relationship"
                ],
            }
        )

        print("EVIDENCE ANALYSIS")
        print(
            f"Relationship: "
            f"{analysis['relationship']}"
        )

        print(
            f"Average output: "
            f"{analysis['average']}"
        )

        print(
            f"Change observed: "
            f"{analysis['change']}"
        )

        print(
            f"Evaluation: "
            f"{evaluation}"
        )

        print()

        print("UPDATED BELIEF")
        print(
            f"Confidence: "
            f"{hypothesis.confidence:.2f}"
        )

        print(
            f"Status: "
            f"{hypothesis.status}"
        )

        print()

    print("=" * 60)
    print("FINAL RESEARCH STATE")
    print("=" * 60)
    print()

    for hypothesis in hypotheses:

        print(
            f"Hypothesis: "
            f"{hypothesis.statement}"
        )

        print(
            f"Confidence: "
            f"{hypothesis.confidence:.2f}"
        )

        print(
            f"Status: "
            f"{hypothesis.status}"
        )

        print(
            f"Tests: "
            f"{hypothesis.tests_run}"
        )

        print()

    best = (
        max(
            hypotheses,
            key=lambda h: h.confidence,
        )
        if hypotheses
        else None
    )

    print("=" * 60)
    print("CURRENT RESEARCH DIRECTION")
    print("=" * 60)

    if best:
        print(
            best.statement
        )

        print(
            f"Confidence: "
            f"{best.confidence:.2f}"
        )

    print()

    print(
        "MEMORY ENTRIES:",
        len(memory.all()),
    )

    print()

    print("=" * 60)
    print("RESEARCH CYCLE COMPLETE")
    print("=" * 60)


def main():

    research_question = (
        "How does changing an input variable "
        "affect a measurable outcome?"
    )

    run_research(
        research_question
    )


if __name__ == "__main__":
    main()