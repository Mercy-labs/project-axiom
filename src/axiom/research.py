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


@dataclass
class Experiment:
    name: str
    hypothesis: Hypothesis
    parameters: dict[str, Any]
    purpose: str


@dataclass
class Evidence:
    experiment: str
    observations: dict[str, Any]
    conclusion: str
    strength: float


@dataclass
class ResearchState:
    question: ResearchQuestion
    hypotheses: list[Hypothesis] = field(default_factory=list)
    experiments: list[Experiment] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)

    def add_hypothesis(self, hypothesis: Hypothesis):
        self.hypotheses.append(hypothesis)

    def add_experiment(self, experiment: Experiment):
        self.experiments.append(experiment)

    def add_evidence(self, evidence: Evidence):
        self.evidence.append(evidence)