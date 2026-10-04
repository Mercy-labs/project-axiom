from dataclasses import dataclass

from .verification import VerificationResult
from .reasoner import ReasoningResult
from .evidence import Evidence


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
    evidence: list[Evidence] | None = None

    def render(self) -> str:

        lines = [
            "=== PROJECT AXIOM RESEARCH REPORT ===",
            "",
            f"Question: {self.question}",
            "",
            "Literature:",
            f"  Unique papers found: "
            f"{self.papers_found}",
        ]

        if self.sources:
            lines.append("")
            lines.append("Sources:")

            for source in self.sources:
                lines.append(
                    f"  - {source}"
                )

        if self.reasoning:

            lines.extend(
                [
                    "",
                    "=== AXIOM EVIDENCE-BACKED ANSWER ===",
                    "",
                    self.reasoning.answer,
                ]
            )

            lines.extend(
                [
                    "",
                    "=== REASONING SUMMARY ===",
                    "",
                    f"Question type: "
                    f"{self.reasoning.question_type}",
                    "",
                    f"Heuristic confidence: "
                    f"{self.reasoning.confidence:.3f}",
                    "",
                    "Conclusion:",
                    self.reasoning.conclusion,
                ]
            )

            lines.extend(
                [
                    "",
                    "Supported claims:",
                ]
            )

            if self.reasoning.supported_claims:
                for claim in (
                    self.reasoning.supported_claims
                ):
                    lines.append(
                        f"  - {claim}"
                    )
            else:
                lines.append(
                    "  - None strongly identified."
                )

            lines.extend(
                [
                    "",
                    "Research gaps:",
                ]
            )

            if self.reasoning.research_gaps:
                for gap in (
                    self.reasoning.research_gaps
                ):
                    lines.append(
                        f"  - {gap}"
                    )
            else:
                lines.append(
                    "  - None identified."
                )

        if self.evidence:

            lines.extend(
                [
                    "",
                    "=== TOP EVIDENCE ===",
                    "",
                ]
            )

            for index, item in enumerate(
                self.evidence[:8],
                start=1,
            ):

                year = (
                    str(item.year)
                    if item.year
                    else "year unknown"
                )

                lines.extend(
                    [
                        (
                            f"{index}. "
                            f"[{item.source}, {year}]"
                        ),
                        (
                            f"   {item.source_title}"
                        ),
                        (
                            f"   Relevance: "
                            f"{item.relevance:.3f} | "
                            f"Strength: "
                            f"{item.strength:.3f}"
                        ),
                        (
                            f"   {item.statement}"
                        ),
                        "",
                    ]
                )

        if (
            self.hypothesis is not None
            and self.verification is not None
        ):

            lines.extend(
                [
                    "=== COMPUTATIONAL EXPERIMENT ===",
                    "",
                    f"Experiment hypothesis: "
                    f"{self.hypothesis}",
                    "",
                    "Observations:",
                ]
            )

            if self.observations:
                for index, observation in enumerate(
                    self.observations,
                    start=1,
                ):
                    lines.append(
                        f"  {index}. "
                        f"{observation:.4f}"
                    )
            else:
                lines.append(
                    "  - None recorded."
                )

            lines.extend(
                [
                    "",
                    f"Experiment conclusion: "
                    f"{self.conclusion}",
                    (
                        "Experiment verification: "
                        f"{'VERIFIED' if self.verification.verified else 'NOT VERIFIED'}"
                    ),
                    "",
                    (
                        "Note: experiment verification "
                        "does not prove the real-world "
                        "research question."
                    ),
                ]
            )

            if self.verification.reasons:
                lines.extend(
                    [
                        "",
                        "Verification notes:",
                    ]
                )

                for reason in (
                    self.verification.reasons
                ):
                    lines.append(
                        f"  - {reason}"
                    )

        return "\n".join(
            lines
        )