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
    question_type: str = "unknown"


class AxiomReasoner:
    """
    Deterministic evidence-based reasoning layer for Project Axiom.

    This is a research reasoning prototype. It does not determine
    scientific truth. It classifies research questions and compares
    claims against available evidence using transparent heuristic rules.
    """

    def reason(
        self,
        question: str,
        evidence: list[str],
        claims: list[str] | None = None,
    ) -> ReasoningResult:

        question_type = self._classify_question(
            question
        )

        if claims is None:
            claims = self._generate_claims(
                question=question,
                question_type=question_type,
            )

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

            if (
                support_score > conflict_score
                and support_score >= 0.25
            ):
                supported_claims.append(claim)

            elif (
                conflict_score > support_score
                and conflict_score >= 0.25
            ):
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
            question_type=question_type,
            supported_claims=supported_claims,
            conflicting_claims=conflicting_claims,
        )

        conclusion = self._build_conclusion(
            question_type=question_type,
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
            question_type=question_type,
        )

    def _classify_question(
        self,
        question: str,
    ) -> str:

        text = question.lower().strip()

        causal_terms = {
            "does",
            "do",
            "cause",
            "causes",
            "effect",
            "affect",
            "impact",
            "improve",
            "increase",
            "decrease",
            "better",
            "worse",
            "versus",
            "compare",
            "comparison",
        }

        explanatory_terms = {
            "why",
            "how does",
            "how do",
            "what causes",
            "what determines",
            "factors",
            "mechanism",
            "mechanisms",
        }

        descriptive_terms = {
            "what",
            "which",
            "where",
            "who",
            "when",
            "how are",
            "how is",
            "describe",
            "used",
            "applications",
            "examples",
        }

        if any(
            term in text
            for term in explanatory_terms
        ):
            return "explanatory"

        if any(
            term in text
            for term in causal_terms
        ):
            return "causal_or_comparative"

        if any(
            term in text
            for term in descriptive_terms
        ):
            return "descriptive"

        return "unknown"

    def _generate_claims(
        self,
        question: str,
        question_type: str,
    ) -> list[str]:

        if question_type == "descriptive":

            return [
                (
                    f"The available scientific literature "
                    f"contains evidence relevant to describing "
                    f"{question}"
                ),
                (
                    f"The literature identifies documented "
                    f"applications, methods, or systems relevant "
                    f"to {question}"
                ),
                (
                    f"The available evidence provides a complete "
                    f"description of {question}"
                ),
            ]

        if question_type == "causal_or_comparative":

            return [
                (
                    f"The available scientific literature "
                    f"contains evidence relevant to evaluating "
                    f"{question}"
                ),
                (
                    f"The available evidence reports measurable "
                    f"effects or differences relevant to "
                    f"{question}"
                ),
                (
                    f"The current evidence is sufficient to "
                    f"establish a strong causal conclusion about "
                    f"{question}"
                ),
            ]

        if question_type == "explanatory":

            return [
                (
                    f"The available scientific literature "
                    f"contains evidence relevant to explaining "
                    f"{question}"
                ),
                (
                    f"The literature identifies factors or "
                    f"mechanisms relevant to {question}"
                ),
                (
                    f"The available evidence is sufficient to "
                    f"establish a complete explanation of "
                    f"{question}"
                ),
            ]

        return [
            (
                f"The available scientific literature provides "
                f"evidence relevant to: {question}"
            ),
            (
                f"The available evidence contains findings "
                f"relevant to answering: {question}"
            ),
            (
                f"The current evidence is sufficient to establish "
                f"a strong conclusion about: {question}"
            ),
        ]

    def _support_score(
        self,
        claim: str,
        evidence: list[str],
    ) -> float:

        if not evidence:
            return 0.0

        claim_words = self._important_words(
            claim
        )

        if not claim_words:
            return 0.0

        total_score = 0.0

        for statement in evidence:

            evidence_words = self._important_words(
                statement
            )

            overlap = claim_words.intersection(
                evidence_words
            )

            if not overlap:
                continue

            similarity = (
                len(overlap)
                / len(claim_words)
            )

            total_score += similarity

        return min(
            total_score / max(len(evidence), 1),
            1.0,
        )

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

        claim_words = self._important_words(
            claim
        )

        if not claim_words:
            return 0.0

        conflict_score = 0.0

        for statement in evidence:

            evidence_words = self._important_words(
                statement
            )

            overlap = claim_words.intersection(
                evidence_words
            )

            if not overlap:
                continue

            conflict_words = (
                evidence_words.intersection(
                    conflict_terms
                )
            )

            if conflict_words:

                conflict_score += (
                    len(conflict_words)
                    / max(len(evidence_words), 1)
                )

        return min(
            conflict_score / max(len(evidence), 1),
            1.0,
        )

    def _calculate_confidence(
        self,
        evidence: list[str],
        supported_claims: list[str],
        conflicting_claims: list[str],
    ) -> float:

        if not evidence:
            return 0.0

        evidence_factor = min(
            len(evidence) / 10.0,
            1.0,
        )

        support_factor = min(
            len(supported_claims)
            / max(len(supported_claims) + 1, 1),
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
            max(
                0.0,
                min(confidence, 1.0),
            ),
            3,
        )

    def _build_hypotheses(
        self,
        question: str,
        question_type: str,
        supported_claims: list[str],
        conflicting_claims: list[str],
    ) -> list[str]:

        hypotheses = []

        if supported_claims:

            if question_type == "descriptive":

                hypotheses.append(
                    (
                        f"The available evidence can be "
                        f"used to further characterize "
                        f"{question}"
                    )
                )

            elif question_type == "causal_or_comparative":

                hypotheses.append(
                    (
                        f"The available evidence supports "
                        f"further investigation of the "
                        f"relationship described by: {question}"
                    )
                )

            elif question_type == "explanatory":

                hypotheses.append(
                    (
                        f"The available evidence supports "
                        f"further investigation of the factors "
                        f"or mechanisms behind: {question}"
                    )
                )

            else:

                hypotheses.append(
                    (
                        f"The available evidence supports "
                        f"further investigation of: {question}"
                    )
                )

        if conflicting_claims:

            hypotheses.append(
                (
                    f"The evidence contains competing or "
                    f"insufficiently resolved findings related "
                    f"to: {question}"
                )
            )

        if question_type == "descriptive":

            hypotheses.append(
                (
                    f"Additional literature may reveal "
                    f"further documented aspects of: {question}"
                )
            )

        elif question_type == "causal_or_comparative":

            hypotheses.append(
                (
                    f"Additional evidence and experiments "
                    f"may be needed to test: {question}"
                )
            )

        elif question_type == "explanatory":

            hypotheses.append(
                (
                    f"Additional evidence may be needed "
                    f"to distinguish between explanations "
                    f"for: {question}"
                )
            )

        else:

            hypotheses.append(
                (
                    f"Additional evidence is needed "
                    f"to investigate: {question}"
                )
            )

        return hypotheses

    def _build_conclusion(
        self,
        question_type: str,
        supported_claims: list[str],
        conflicting_claims: list[str],
        confidence: float,
    ) -> str:

        if supported_claims and not conflicting_claims:

            if question_type == "descriptive":

                return (
                    "The available evidence supports "
                    "a descriptive research direction, "
                    f"with an estimated reasoning confidence "
                    f"of {confidence:.3f}."
                )

            if question_type == "causal_or_comparative":

                return (
                    "The available evidence supports "
                    "further evaluation of the causal or "
                    "comparative question, with an estimated "
                    f"reasoning confidence of {confidence:.3f}."
                )

            if question_type == "explanatory":

                return (
                    "The available evidence supports "
                    "further investigation of the explanatory "
                    f"question, with an estimated reasoning "
                    f"confidence of {confidence:.3f}."
                )

            return (
                "The available evidence supports the current "
                "claims, with an estimated reasoning confidence "
                f"of {confidence:.3f}."
            )

        if conflicting_claims and not supported_claims:

            return (
                "The available evidence conflicts with the "
                "current claims, so further investigation is "
                "required."
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
                "Conflicting evidence needs further "
                "investigation."
            )

        if not supported_claims:

            gaps.append(
                "No claim currently has sufficient support."
            )

        return gaps

    @staticmethod
    def _important_words(
        text: str,
    ) -> set[str]:

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