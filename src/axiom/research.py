from dataclasses import dataclass, field
from typing import Any


@dataclass
class ResearchQuestion:
    question: str


@dataclass
class Hypothesis:
    statement: str
    confidence: float = 0.5
    status: str = "untested"
    tests_run: int = 0
    supporting_evidence: int = 0
    contradicting_evidence: int = 0

    def update_from_evidence(self, evaluation: str):
        self.tests_run += 1

        if evaluation == "supported":
            self.supporting_evidence += 1
            self.confidence = min(
                0.99,
                self.confidence + 0.15,
            )
            self.status = "supported"

        elif evaluation == "contradicted":
            self.contradicting_evidence += 1
            self.confidence = max(
                0.01,
                self.confidence - 0.15,
            )
            self.status = "contradicted"

        else:
            self.status = "uncertain"


@dataclass
class Experiment:
    name: str
    hypothesis: Hypothesis
    parameters: dict[str, Any]
    purpose: str


@dataclass
class Evidence:
    experiment: str
    hypothesis: str
    observations: dict[str, Any]
    conclusion: str
    strength: float


@dataclass
class ResearchState:
    question: ResearchQuestion
    hypotheses: list[Hypothesis] = field(default_factory=list)
    experiments: list[Experiment] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    cycle: int = 0

    def add_hypothesis(self, hypothesis: Hypothesis):
        self.hypotheses.append(hypothesis)

    def add_experiment(self, experiment: Experiment):
        self.experiments.append(experiment)

    def add_evidence(self, evidence: Evidence):
        self.evidence.append(evidence)

    def next_cycle(self):
        self.cycle += 1