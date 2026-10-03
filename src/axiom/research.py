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
            support_score = self._calculate_support(
                claim,
                evidence,
            )

            conflict_score = self._calculate_conflict(
                claim,
                evidence,
            )

            if support_score >= conflict_score:
                supports = True
                strength = support_score
                reason = (
                    "The available evidence provides more "
                    "support than conflict."
                )
                supported_claims.append(claim)
            else:
                supports = False
                strength = conflict_score
                reason = (
                    "The available evidence provides more "
                    "conflict than support."
                )
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

        negative_terms = {
            "not",
            "no",
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
            negative_overlap = words.intersection(
                negative_terms
            )

            if overlap and negative_overlap:
                score = min(
                    1.0,
                    (len(overlap) / len(claim_words)) * 0.75
                    + 0.25,
                )

                conflict_score = max(
                    conflict_score,
                    score,
                )

        return conflict_score

    def _calculate_confidence(
        self,
        evidence_count: int,
        assessments: list[EvidenceAssessment],
    ) -> float:

        if not assessments:
            return 0.0

        evidence_factor = min(
            evidence_count / 10,
            1.0,
        )

        consistency = (
            sum(
                assessment.strength
                for assessment in assessments
            )
            / len(assessments)
        )

        confidence = (
            evidence_factor * 0.4
            + consistency * 0.6
        )

        return round(
            min(confidence, 1.0),
            3,
        )

    def _build_conclusion(
        self,
        supported_claims: list[str],
        conflicting_claims: list[str],
        confidence: float,
    ) -> str:

        if supported_claims and not conflicting_claims:
            return (
                "The available evidence supports the current "
                "claims, with an estimated reasoning confidence "
                f"of {confidence:.3f}."
            )

        if conflicting_claims and not supported_claims:
            return (
                "The available evidence conflicts with the "
                "current claims, with an estimated reasoning "
                f"confidence of {confidence:.3f}."
            )

        if supported_claims and conflicting_claims:
            return (
                "The evidence is mixed: some claims are "
                "supported while others remain conflicting "
                "or insufficiently supported."
            )

        return (
            "The available evidence is insufficient "
            "for a strong conclusion."
        )

    def _find_gaps(
        self,
        evidence: list[str],
        supported_claims: list[str],
        conflicting_claims: list[str],
    ) -> list[str]:

        gaps = []

        if len(evidence) < 3:
            gaps.append(
                "More independent evidence is needed."
            )

        if conflicting_claims:
            gaps.append(
                "Conflicting evidence needs further investigation."
            )

        if not supported_claims:
            gaps.append(
                "No claim currently has sufficient support."
            )

        return gaps

    @staticmethod
    def _important_words(text: str) -> set[str]:

        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "of",
            "to",
            "in",
            "on",
            "for",
            "with",
            "is",
            "are",
            "was",
            "were",
            "that",
            "this",
            "as",
            "by",
            "from",
        }

        words = {
            word.strip(
                ".,!?():;[]{}\"'"
            ).lower()
            for word in text.split()
        }

        return {
            word
            for word in words
            if word
            and word not in stop_words
            and len(word) > 2
        }