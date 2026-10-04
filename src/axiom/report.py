from dataclasses import dataclass

from .verification import VerificationResult
from .reasoner import ReasoningResult


@dataclass
class ResearchReport:
    question: str
    hypothesis: str | None
    observations: list[float]
    conclusion: str | None
    verification: VerificationResult | None
    papers_found: int = 0
    sources: list[str] | None = None
    reasoning: ReasoningResult | None = None

    def render(self) -> str:
        lines = [
            "=== PROJECT AXIOM RESEARCH REPORT ===",
            "",
            f"Question: {self.question}",
            "",
            "Literature:",
            f"  Papers found: {self.papers_found}",
        ]

        if self.sources:
            for source in self.sources:
                lines.append(f"  {source}")

        if self.reasoning:
            lines.extend(
                [
                    "",
                    "=== AXIOM LITERATURE REASONING ===",
                    "",
                    f"Question type: {self.reasoning.question_type}",
                    "",
                    "Claims:",
                ]
            )

            if self.reasoning.claims:
                for claim in self.reasoning.claims:
                    lines.append(f"  - {claim}")
            else:
                lines.append("  - None identified.")

            lines.extend(
                [
                    "",
                    "Supported claims:",
                ]
            )

            if self.reasoning.supported_claims:
                for claim in self.reasoning.supported_claims:
                    lines.append(f"  - {claim}")
            else:
                lines.append("  - None identified.")

            lines.extend(
                [
                    "",
                    "Uncertain claims:",
                ]
            )

            if self.reasoning.uncertain_claims:
                for claim in self.reasoning.uncertain_claims:
                    lines.append(f"  - {claim}")
            else:
                lines.append("  - None identified.")

            lines.extend(
                [
                    "",
                    "Conflicting claims:",
                ]
            )

            if self.reasoning.conflicting_claims:
                for claim in self.reasoning.conflicting_claims:
                    lines.append(f"  - {claim}")
            else:
                lines.append("  - None identified.")

            lines.extend(
                [
                    "",
                    "Research gaps:",
                ]
            )

            if self.reasoning.research_gaps:
                for gap in self.reasoning.research_gaps:
                    lines.append(f"  - {gap}")
            else:
                lines