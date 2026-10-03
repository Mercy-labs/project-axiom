from dataclasses import dataclass


@dataclass
class ReasoningResult:
    claims: list[str]
    supported_claims: list[str]
    conflicting_claims: list[str]
    research_gaps: list[str]
    hypotheses: list[str]
    confidence: float
    conclusion: str


class AxiomReasoner:
    """
    Deterministic evidence-based reasoning layer for Project Axiom.

    This is a research reasoning prototype. It does not determine
    scientific truth. It compares claims against available evidence
    using transparent heuristic rules.
    """

    def reason(
        self,
        question: str,
        evidence: list[str],
        claims: list[str] | None = None,
    ) -> ReasoningResult:

        if claims is None:
            claims = self._generate_claims(question)

        supported_claims = []
        conflicting_claims = []

        for claim in claims:
            support_score = self._support_score(
                claim=claim,
                evidence=evidence,
            )

            conflict_score = self._conflict_score(
                claim=claim,
                evidence=evidence,
            )

            if support_score > conflict_score and support_score >= 0.25:
                supported_claims.append(claim)

            elif conflict_score > support_score and conflict_score >= 0.25:
                conflicting_claims.append(claim)

        confidence = self._calculate_confidence(
            evidence=evidence,
            supported_claims=supported_claims,
            conflicting_claims=conflicting_claims,
        )

        research_gaps = self._find_gaps(
            evidence=evidence,
            supported_claims=supported_claims,
            conflicting_claims=conflicting_claims,
        )

        hypotheses = self._build_hypotheses(
            question=question,
            supported_claims=supported_claims,
            conflicting_claims=conflicting_claims,
        )

        conclusion = self._build_conclusion(
            supported_claims=supported_claims,
            conflicting_claims=conflicting_claims,
            confidence=confidence,
        )

        return ReasoningResult(
            claims=claims,
            supported_claims=supported_claims,
            conflicting_claims=conflicting_claims,
            research_gaps=research_gaps,
            hypotheses=hypotheses,
            confidence=confidence,
            conclusion=conclusion,
        )

    def _generate_claims(self, question: str) -> list[str]:
        return [
            (
                f"The available scientific literature provides "
                f"evidence relevant to: {question}"
            ),
            (
                f"The available evidence suggests that "
                f"{question} has measurable effects or relationships."
            ),
            (
                f"The current evidence is sufficient to establish "
                f"a strong causal conclusion about: {question}"
            ),
        ]

    def _support_score(
        self,
        claim: str,
        evidence: list[str],
    ) -> float:

        if not evidence:
            return 0.0

        claim_words = self._important_words(claim)

        if not claim_words:
            return 0.0

        total_score = 0.0

        for statement in evidence:
            evidence_words = self._important_words(statement)

            overlap = claim_words.intersection(evidence_words)

            if not overlap:
                continue

            similarity = len(overlap) / len(claim_words)

            total_score += similarity

        return min(total_score / max(len(evidence), 1), 1.0)

    def _conflict_score(
        self,
        claim: str,
        evidence: list[str],
    ) -> float:

        if not evidence:
            return 0.0

        conflict_terms = {
            "not",
            "no",
            "cannot",
            "fails",
            "failed",
            "decrease",
            "decreases",
            "negative",
            "limited",
            "unclear",
            "inconclusive",
            "contradict",
            "contradicts",
            "conflict",
            "conflicting",
        }

        claim_words = self._important_words(claim)

        if not claim_words:
            return 0.0

        conflict_score = 0.0

        for statement in evidence:
            evidence_words = self._important_words(statement)

            overlap = claim_words.intersection(evidence_words)

            if not overlap:
                continue

            conflict_words = evidence_words.intersection(
                conflict_terms
            )

            if conflict_words:
                conflict_score += (
                    len(conflict_words) / max(len(evidence_words), 1)
                )

        return min(conflict_score / max(len(evidence), 1), 1.0)

    def _calculate_confidence(
        self,
        evidence: list[str],
        supported_claims: list[str],
        conflicting_claims: list[str],
    ) -> float:

        if not evidence:
            return 0.0

        evidence_factor = min(len(evidence) / 10.0, 1.0)

        support_factor = min(
            len(supported_claims) / max(len(supported_claims) + 1, 1),
            1.0,
        )

        conflict_penalty = min(
            len(conflicting_claims) * 0.15,
            0.6,
        )

        confidence = (
            0.2
            + (evidence_factor * 0.4)
            + (support_factor * 0.4)
            - conflict_penalty
        )

        return round(
            max(0.0, min(confidence, 1.0)),
            3,
        )

    def _build_hypotheses(
        self,
        question: str,
        supported_claims: list[str],
        conflicting_claims: list[str],
    ) -> list[str]:

        hypotheses = []

        if supported_claims:
            hypotheses.append(
                (
                    f"The available evidence supports further "
                    f"investigation of: {question}"
                )
            )

        if conflicting_claims:
            hypotheses.append(
                (
                    f"The evidence may contain competing explanations "
                    f"for: {question}"
                )
            )

        hypotheses.append(
            (
                f"Additional evidence and experiments are needed "
                f"to test the relationship described by: {question}"
            )
        )

        return hypotheses

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
                "or insufficiently