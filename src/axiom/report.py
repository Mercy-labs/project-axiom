from dataclasses import dataclass

from .verification import VerificationResult


@dataclass
class ResearchReport:
    question: str
    hypothesis: str
    observations: list[float]
    conclusion: str
    verification: VerificationResult
    papers_found: int = 0
    sources: list[str] | None = None

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
            f"Hypothesis: {self.hypothesis}",
            "",
            "Literature:",
            f"  Papers found: {self.papers_found}",
        ]

        if self.sources:

            for source in self.sources:
                lines.append(
                    f"  {source}"
                )

        lines.extend(
            [
                "",
                "Computational observations:",
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
                f"Conclusion: {self.conclusion}",
                f"Verification: {verification}",
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