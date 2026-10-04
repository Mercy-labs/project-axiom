from dataclasses import dataclass


@dataclass
class ReasoningResult:
    claims: list[str]
    supported_claims: list[str]
    uncertain_claims: list[str]
    conflicting_claims: list[str]
    research_gaps: list[str]
    hypotheses: list[str]
    confidence: float
    conclusion: str
    question_type: str = "unknown"
    answer: str = ""
    evidence_used: list[str] | None = None


class AxiomReasoner:
    """
    Transparent evidence-synthesis layer for Project Axiom.

    Axiom does not pretend that a heuristic score is scientific truth.
    The answer is constructed from retrieved evidence and clearly
    labelled as evidence-backed synthesis.
    """

    def reason(
        self,
        question: str,
        evidence: list[str],
        claims: list[str] | None = None,
    ) -> ReasoningResult:

        question_type = (
            self._classify_question(
                question
            )
        )

        if claims is None:
            claims = self._generate_claims(
                question,
                question_type,
            )

        supported_claims = []
        uncertain_claims = []
        conflicting_claims = []

        for claim in claims:
            score = self._support_score(
                claim,
                evidence,
            )

            conflict = self._conflict_score(
                claim,
                evidence,
            )

            if (
                conflict > score
                and conflict >= 0.15
            ):
                conflicting_claims.append(
                    claim
                )
            elif score >= 0.15:
                supported_claims.append(
                    claim
                )
            else:
                uncertain_claims.append(
                    claim
                )

        answer = self._build_answer(
            question=question,
            evidence=evidence,
        )

        confidence = (
            self._calculate_confidence(
                evidence=evidence,
                supported_claims=supported_claims,
                uncertain_claims=uncertain_claims,
                conflicting_claims=conflicting_claims,
            )
        )

        gaps = self._find_gaps(
            evidence=evidence,
            supported_claims=supported_claims,
            conflicting_claims=conflicting_claims,
        )

        hypotheses = self._build_hypotheses(
            question,
            uncertain_claims,
            conflicting_claims,
        )

        conclusion = self._build_conclusion(
            answer=answer,
            confidence=confidence,
            evidence_count=len(evidence),
        )

        return ReasoningResult(
            claims=claims,
            supported_claims=supported_claims,
            uncertain_claims=uncertain_claims,
            conflicting_claims=conflicting_claims,
            research_gaps=gaps,
            hypotheses=hypotheses,
            confidence=confidence,
            conclusion=conclusion,
            question_type=question_type,
            answer=answer,
            evidence_used=evidence[:8],
        )

    def _build_answer(
        self,
        question: str,
        evidence: list[str],
    ) -> str:

        if not evidence:
            return (
                "Axiom could not retrieve enough usable "
                "evidence to produce an evidence-backed "
                "answer."
            )

        selected = []

        seen = set()

        for statement in evidence:
            cleaned = " ".join(
                statement.split()
            )

            key = cleaned.lower()

            if key in seen:
                continue

            seen.add(key)
            selected.append(cleaned)

            if len(selected) >= 6:
                break

        if not selected:
            return (
                "Axiom retrieved literature, but the "
                "available material did not contain enough "
                "usable evidence statements."
            )

        lines = [
            (
                "Based on the retrieved scientific literature, "
                f"the evidence suggests that {question.lower()} "
                "is influenced by multiple interacting factors."
            ),
            "",
            "Key evidence:",
        ]

        for statement in selected:
            lines.append(
                f"- {statement}"
            )

        lines.extend(
            [
                "",
                (
                    "This is an evidence-backed synthesis of "
                    "the retrieved literature, not a claim of "
                    "scientific certainty."
                ),
            ]
        )

        return "\n".join(
            lines
        )

    def _classify_question(
        self,
        question: str,
    ) -> str:

        text = question.lower()

        if any(
            phrase in text
            for phrase in (
                "why",
                "how does",
                "how do",
                "mechanism",
                "mechanisms",
                "what causes",
            )
        ):
            return "explanatory"

        if any(
            word in text
            for word in (
                "effect",
                "affect",
                "impact",
                "increase",
                "decrease",
                "compare",
                "versus",
                "better",
                "worse",
            )
        ):
            return "causal_or_comparative"

        if any(
            word in text
            for word in (
                "what",
                "which",
                "who",
                "where",
                "when",
                "applications",
                "examples",
            )
        ):
            return "descriptive"

        return "unknown"

    def _generate_claims(
        self,
        question: str,
        question_type: str,
    ) -> list[str]:

        if question_type == "explanatory":
            return [
                (
                    "The literature contains evidence "
                    "relevant to explaining the question."
                ),
                (
                    "The literature identifies mechanisms, "
                    "factors, or relationships relevant "
                    "to the question."
                ),
            ]

        if question_type == "causal_or_comparative":
            return [
                (
                    "The literature contains evidence "
                    "relevant to evaluating the stated "
                    "effect or relationship."
                ),
                (
                    "The literature reports measurable "
                    "effects, differences, or associations "
                    "relevant to the question."
                ),
            ]

        if question_type == "descriptive":
            return [
                (
                    "The literature contains documented "
                    "findings relevant to the question."
                ),
                (
                    "The literature provides examples, "
                    "methods, or applications relevant "
                    "to the question."
                ),
            ]

        return [
            (
                "The retrieved literature contains evidence "
                "relevant to the question."
            )
        ]

    def _support_score(
        self,
        claim: str,
        evidence: list[str],
    ) -> float:

        claim_words = self._important_words(
            claim
        )

        if not claim_words:
            return 0.0

        scores = []

        for statement in evidence:
            statement_words = (
                self._important_words(
                    statement
                )
            )

            overlap = (
                claim_words
                .intersection(
                    statement_words
                )
            )

            if overlap:
                scores.append(
                    len(overlap)
                    / len(claim_words)
                )

        if not scores:
            return 0.0

        return min(
            max(scores),
            1.0,
        )

    def _conflict_score(
        self,
        claim: str,
        evidence: list[str],
    ) -> float:

        claim_words = self._important_words(
            claim
        )

        conflict_terms = {
            "not",
            "cannot",
            "fails",
            "failed",
            "negative",
            "limited",
            "unclear",
            "inconclusive",
            "contradict",
            "contradicts",
            "conflict",
            "conflicting",
        }

        score = 0.0

        for statement in evidence:
            words = self._important_words(
                statement
            )

            if not claim_words.intersection(
                words
            ):
                continue

            if words.intersection(
                conflict_terms
            ):
                score += 0.15

        return min(
            score,
            1.0,
        )

    def _calculate_confidence(
        self,
        evidence: list[str],
        supported_claims: list[str],
        uncertain_claims: list[str],
        conflicting_claims: list[str],
    ) -> float:

        if not evidence:
            return 0.0

        evidence_factor = min(
            len(evidence) / 12.0,
            1.0,
        )

        sources = set()

        for statement in evidence:
            if " — " in statement:
                source = statement.split(
                    " — ",
                    1,
                )[0]

                sources.add(
                    source
                )

        source_factor = min(
            len(sources) / 4.0,
            1.0,
        )

        total_claims = (
            len(supported_claims)
            + len(uncertain_claims)
            + len(conflicting_claims)
        )

        if total_claims:
            support_factor = (
                len(supported_claims)
                / total_claims
            )
        else:
            support_factor = 0.0

        conflict_penalty = min(
            len(conflicting_claims)
            * 0.12,
            0.4,
        )

        confidence = (
            0.15
            + evidence_factor * 0.35
            + source_factor * 0.25
            + support_factor * 0.25
            - conflict_penalty
        )

        return round(
            max(
                0.0,
                min(
                    confidence,
                    1.0,
                ),
            ),
            3,
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
                "More usable evidence is needed."
            )

        if len(evidence) < 8:
            gaps.append(
                "The evidence sample is still relatively small."
            )

        if not supported_claims:
            gaps.append(
                "The retrieved evidence does not strongly "
                "support the generated claims."
            )

        if conflicting_claims:
            gaps.append(
                "Some retrieved evidence may point in "
                "different directions."
            )

        return gaps

    def _build_hypotheses(
        self,
        question: str,
        uncertain_claims: list[str],
        conflicting_claims: list[str],
    ) -> list[str]:

        hypotheses = []

        if uncertain_claims:
            hypotheses.append(
                (
                    "Some aspects of the question remain "
                    "uncertain and should be investigated "
                    "with additional evidence."
                )
            )

        if conflicting_claims:
            hypotheses.append(
                (
                    "Differences between studies may be "
                    "explained by differences in datasets, "
                    "methods, populations, or experimental "
                    "conditions."
                )
            )

        return hypotheses

    @staticmethod
    def _build_conclusion(
        answer: str,
        confidence: float,
        evidence_count: int,
    ) -> str:

        if evidence_count == 0:
            return (
                "No evidence-backed conclusion could be "
                "constructed."
            )

        return (
            "Axiom produced an evidence-backed synthesis "
            f"from {evidence_count} evidence statements. "
            f"Heuristic confidence: {confidence:.3f}."
        )

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
            "contains",
            "contains",
            "evidence",
            "available",
            "literature",
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
            if (
                word
                and word not in stop_words
                and len(word) > 2
            )
        }