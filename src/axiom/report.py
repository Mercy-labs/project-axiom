from dataclasses import dataclass

from .verification import VerificationResult
from .reasoner import ReasoningResult


@dataclass
class ResearchReport:
    question: str
    hypothesis: str
    observations: list[float]
    conclusion: str
    verification: VerificationResult
    papers_found: int = 0
    sources: list[str] | None = None
    reasoning: ReasoningResult | None = None

    def render(self) -> str:

        verification = (
            "VERIFIED"
            if self.verification.verified
            else "NOT VERIFIED"
        )

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
                lines.append(
                    f"  {source}"
                )

        if self.reasoning:

            lines.extend(
                [
                    "",
                    "=== AXIOM LITERATURE REASONING ===",
                    "",
                    (
                        "Question type: "
                        f"{self.reasoning.question_type}"
                    ),
                    "",
                    "Claims:",
                ]
            )

            for claim in self.reasoning.claims:
                lines.append(
                    f"  - {claim}"
                )

            lines.append("")
            lines.append(
                "Supported claims:"
            )

            if self.reasoning.supported_claims:

                for claim in self.reasoning.supported_claims:
                    lines.append(
                        f"  - {claim}"
                    )

            else:

                lines.append(
                    "  - None identified."
                )

            lines.append("")
            lines.append(
                "Uncertain claims:"
            )

            if self.reasoning.uncertain_claims:

                for claim in self.reasoning.uncertain_claims:
                    lines.append(
                        f"  - {claim}"
                    )

            else:

                lines.append(
                    "  - None identified."
                )

            lines.append("")
            lines.append(
                "Conflicting claims:"
            )

            if self.reasoning.conflicting_claims:

                for claim in self.reasoning.conflicting_claims:
                    lines.append(
                        f"  - {claim}"
                    )

            else:

                lines.append(
                    "  - None identified."
                )

            lines.append("")
            lines.append(
                "Research gaps:"
            )

            if self.reasoning.research_gaps:

                for gap in self.reasoning.research_gaps:
                    lines.append(
                        f"  - {gap}"
                    )

            else:

                lines.append(
                    "  - None identified."
                )

            lines.append("")
            lines.append(
                "Reasoning hypotheses:"
            )

            if self.reasoning.hypotheses:

                for hypothesis in self.reasoning.hypotheses:
                    lines.append(
                        f"  - {hypothesis}"
                    )

            else:

                lines.append(
                    "  - None generated."
                )

            lines.extend(
                [
                    "",
                    (
                        "Reasoning confidence: "
                        f"{self.reasoning.confidence:.3f}"
                    ),
                    (
                        "Reasoning conclusion: "
                        f"{self.reasoning.conclusion}"
                    ),
                ]
            )

        lines.extend(
            [
                "",
                "=== COMPUTATIONAL EXPERIMENT ===",
                "",
                "Experiment hypothesis:",
                f"  {self.hypothesis}",
                "",
                "Observations:",
            ]
        )

        for index, value in enumerate(
            self.observations,
            start=1,
        ):
            lines.append(
                f"  {index}. {value:.4f}"
            )

        lines.extend(
            [
                "",
                "Experiment conclusion:",
                f"  {self.conclusion}",
                "",
                (
                    "Experiment verification: "
                    f"{verification}"
                ),
                "",
                (
                    "Note: Experiment verification only "
                    "indicates that the computational "
                    "experiment passed Axiom's current "
                    "verification rules. It does not establish "
                    "that the real-world research question "
                    "has been scientifically proven."
                ),
            ]
        )

        if self.verification.reasons:

            lines.append("")
            lines.append(
                "Verification notes:"
            )

            for reason in self.verification.reasons:
                lines.append(
                    f"  - {reason}"
                )

        return "\n".join(lines)