from dataclasses import dataclass

from .verification import VerificationResult


@dataclass
class ResearchReport:
    question: str
    hypothesis: str
    observations: list[float]
    conclusion: str
    verification: VerificationResult

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
            "Observations:",
        ]

        for index, value in enumerate(self.observations, start=1):
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
            lines.append("Verification notes:")

            for reason in self.verification.reasons:
                lines.append(f"  - {reason}")

        return "\n".join(lines)