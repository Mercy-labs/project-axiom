from dataclasses import dataclass


@dataclass
class EvidenceAssessment:
    statement: str
    supports: bool
    strength: float
    reason: str


@dataclass
class ReasoningResult:
    question: str
    assessments: list[EvidenceAssessment]
    supported_claims: list[str]
    conflicting_claims: list[str]
    research_gaps: list[str]
    conclusion: str
    confidence: float


class AxiomReasoner:
    """
    Axiom's first independent reasoning engine.

    It evaluates evidence against claims and produces:
    - supporting evidence
    - conflicting evidence
    - research gaps
    - a conclusion
    - an uncertainty-aware confidence value
    """

    def reason(
        self,
        question: str,
        evidence: list[str],
        claims: list[str],
    ) -> ReasoningResult:

        if not question.strip():
            raise ValueError("Research question cannot be empty.")

        if not claims:
            raise ValueError("At least one claim is required.")

        assessments = []
        supported_claims = []
        conflicting_claims = []

        for claim in claims:
            support_score = self._calculate_support(claim, evidence)
            conflict_score = self._calculate_conflict(claim, evidence)

            if support_score >= conflict_score:
                supports = True
                strength = support_score
                reason = "The available evidence provides more support than conflict."
                supported_claims.append(claim)
            else:
                supports = False
                strength = conflict_score
                reason = "The available evidence provides more conflict than support."
                conflicting_claims.append(claim)

            assessments.append(
                EvidenceAssessment(
                    statement=claim,
                    supports=supports,
                    strength=round(strength, 3),
                    reason=reason,
                )
            )

        confidence = self._calculate_confidence(
            evidence_count=len(evidence),
            assessments=assessments,
        )

        conclusion = self._build_conclusion(
            supported_claims=supported_claims,
            conflicting_claims=conflicting_claims,
            confidence=confidence,
        )

        research_gaps = self._find_gaps(
            evidence=evidence,
            supported_claims=supported_claims,
            conflicting_claims=conflicting_claims,
        )

        return ReasoningResult(
            question=question,
            assessments=assessments,
            supported_claims=supported_claims,
            conflicting_claims=conflicting_claims,
            research_gaps=research_gaps,
            conclusion=conclusion,
            confidence=confidence,
        )

    def _calculate_support(
        self,
        claim: str,
        evidence: list[str],
    ) -> float:
        """
        Estimate how strongly the evidence supports a claim.

        This first version uses simple language overlap.
        Later we can replace this with a learned reasoning model.
        """

        claim_words = self._important_words(claim)

        if not claim_words:
            return 0.0

        best_score = 0.0

        for item in evidence:
            evidence_words = self._important_words(item)
            overlap = claim_words.intersection(evidence_words)

            score = len(overlap) / len(claim_words)

            if score > best_score:
                best_score = score

        return min(best_score, 1.0)

    def _calculate_conflict(
        self,
        claim: str,
        evidence: list[str],
    ) -> float:
        """
        Look for language that explicitly contradicts a claim.
        """

        negative_terms = {
            "not",
            "no",
            "cannot",
            "cannot",
            "fails",
            "failed",
            "limited",
            "unlikely",
            "contradicts",
            "contrary",
            "insufficient",
        }

        claim_words = self._important_words(claim)

        if not claim_words:
            return 0.0

        conflict_score = 0.0

        for item in evidence:
            words = self._important_words(item)

            overlap = claim_words.intersection(words)

            negative_overlap = words.intersection(negative_terms)

            if overlap and negative_overlap:
                score = min(
                    1.0,
                    (len(overlap) / len(claim_words))
                    * 0.75
                    + 0.25,
                )
                conflict_score = max(conflict_score, score)

        return conflict_score

    def _calculate_confidence(
        self,
        evidence_count: int,
        assessments: list[EvidenceAssessment],
    ) -> float:

        if not assessments:
            return 0.0

        evidence_factor = min(evidence_count / 10, 1.0)

        consistency = sum(
            assessment.strength
            for assessment in assessments
        ) / len(assessments)

        confidence = (
            evidence_factor * 0.4
            + consistency * 0.6
        )

        return round(min(confidence, 1.0), 3)

    def _build_conclusion(
        self,
        supported_claims: list[str],
        conflicting_claims: