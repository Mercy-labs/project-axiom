from dataclasses import dataclass


@dataclass
class VerificationResult:
    verified: bool
    reasons: list[str]


class Verifier:
    def verify(
        self,
        observation_count: int,
        evidence_strength: float,
    ) -> VerificationResult:

        reasons = []

        if observation_count < 2:
            reasons.append(
                "Too few observations for verification."
            )

        if evidence_strength < 0.6:
            reasons.append(
                "Evidence strength is below the verification threshold."
            )

        return VerificationResult(
            verified=len(reasons) == 0,
            reasons=reasons,
        )