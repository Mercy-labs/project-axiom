from .research import (
    ResearchQuestion,
    ResearchState,
    Evidence,
)

from .model import LocalReasoningModel
from .experiment import (
    SimulationEngine,
    design_experiments,
)

from .evaluator import EvidenceEvaluator
from .memory import ResearchMemory
from .planner import ResearchPlanner


def run_research(question_text):

    print("=" * 60)
    print("AXIOM")
    print("Autonomous Scientific Discovery Engine")
    print("=" * 60)
    print()

    question = ResearchQuestion(question_text)

    state = ResearchState(
        question=question
    )

    model = LocalReasoningModel()
    simulator = SimulationEngine()
    evaluator = EvidenceEvaluator()
    memory = ResearchMemory()
    planner = ResearchPlanner()

    # ----------------------------------------
    # 1. RESEARCH QUESTION
    # ----------------------------------------

    print("RESEARCH QUESTION")
    print(question.question)
    print()

    # ----------------------------------------
    # 2. GENERATE COMPETING HYPOTHESES
    # ----------------------------------------

    print("GENERATING HYPOTHESES")

    hypotheses = model.generate_hypotheses(
        question
    )

    for hypothesis in hypotheses:
        state.add_hypothesis(hypothesis)

        print(
            f"- {hypothesis.statement}"
            f" | confidence={hypothesis.confidence:.2f}"
        )

    print()

    # ----------------------------------------
    # 3. TEST EACH HYPOTHESIS
    # ----------------------------------------

    evaluations = []

    for hypothesis in hypotheses:

        print("TESTING HYPOTHESIS")
        print(hypothesis.statement)
        print()

        experiments = design_experiments(
            hypothesis
        )

        results = []

        for experiment in experiments:

            state.add_experiment(
                experiment
            )

            result = simulator.run(
                experiment
            )

            results.append(result)

            print(
                f"{experiment.name}: "
                f"input={result['input']} "
                f"output={result['output']}"
            )

        print()

        # ------------------------------------
        # 4. ANALYSE EVIDENCE
        # ------------------------------------

        analysis = evaluator.analyse(
            results
        )

        evaluation = evaluator.evaluate_hypothesis(
            hypothesis,
            analysis,
        )

        evaluations.append(evaluation)

        hypothesis.status = evaluation

        conclusion = (
            f"Hypothesis is {evaluation}. "
            f"Observed relationship: "
            f"{analysis['relationship']}."
        )

        evidence = Evidence(
            experiment=experiments[0].name,
            observations=analysis,
            conclusion=conclusion,
            strength=0.7,
        )

        state.add_evidence(evidence)

        print("EVIDENCE")
        print("Average:", analysis["average"])
        print("Highest:", analysis["highest"])
        print("Lowest:", analysis["lowest"])
        print("Relationship:", analysis["relationship"])
        print("Evaluation:", evaluation)
        print()

    # ----------------------------------------
    # 5. CHOOSE NEXT DIRECTION
    # ----------------------------------------

    next_hypothesis = planner.choose_next_direction(
        hypotheses,
        evaluations,
    )

    # ----------------------------------------
    # 6. SAVE RESEARCH MEMORY
    # ----------------------------------------

    for hypothesis, evaluation in zip(
        hypotheses,
        evaluations,
    ):
        memory.remember(
            {
                "question": question.question,
                "hypothesis": hypothesis.statement,
                "confidence": hypothesis.confidence,
                "status": evaluation,
            }
        )

    # ----------------------------------------
    # 7. REPORT
    # ----------------------------------------

    print("=" * 60)
    print("RESEARCH DECISION")
    print("=" * 60)

    if next_hypothesis:
        print(
            "Next direction:",
            next_hypothesis.statement,
        )

    print()

    print("MEMORY ENTRIES:", len(memory.all()))

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