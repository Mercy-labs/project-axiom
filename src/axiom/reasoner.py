from dataclasses import dataclass
import re


@dataclass
class ReasoningResult:
    question: str
    question_type: str
    claims: list[str]
    uncertain_claims: list[str]
    conflicting_claims: list[str]
    research_gaps: list[str]
    conclusion: str
    confidence: float
    answer: str = ""
    evidence_used: list[str] | None = None


class AxiomReasoner:
    """
    Evidence-grounded scientific reasoning layer.

    This component does not try to "prove" a scientific claim.
    It analyses the retrieved evidence and produces a cautious
    synthesis based only on what the evidence supports.

    Confidence here represents the strength and consistency of the
    retrieved evidence, not the probability that a scientific claim
    is true.
    """

    LIMITATION_TERMS = {
        "limitation",
        "limitations",
        "challenge",
        "challenges",
        "remain",
        "remains",
        "however",
        "but",
        "uncertain",
        "uncertainty",
        "difficult",
        "difficulty",
        "cannot",
        "unable",
        "lack",
        "lacks",
        "limited",
        "human oversight",
        "human validation",
        "validation required",
        "requires validation",
        "requires human",
        "experimental validation",
        "further research",
        "future work",
        "open question",
        "open questions",
        "not yet",
        "still",
    }

    DISCOVERY_TERMS = {
        "scientific discovery",
        "scientific research",
        "research",
        "hypothesis",
        "hypotheses",
        "hypothesis generation",
        "experiment",
        "experiments",
        "experimental design",
        "data analysis",
        "literature",
        "scientific knowledge",
        "automated science",
        "autonomous research",
        "ai scientist",
        "scientific reasoning",
    }

    BENEFIT_TERMS = {
        "accelerat",
        "improv",
        "enhanc",
        "assist",
        "autom",
        "efficien",
        "speed",
        "faster",
        "scale",
        "scaling",
        "discover",
        "generate",
        "predict",
        "identify",
        "analysis",
        "design",
    }

    CONFLICT_TERMS = {
        "however",
        "but",
        "contradict",
        "conflict",
        "mixed",
        "inconsistent",
        "disagree",
        "disagreement",
        "whereas",
        "on the other hand",
    }

    def reason(
        self,
        question: str,
        evidence: list[str],
    ) -> ReasoningResult:

        cleaned_question = (
            " ".join(
                question.split()
            ).strip()
        )

        cleaned_evidence = self._clean_evidence(
            evidence
        )

        question_type = self._classify_question(
            cleaned_question
        )

        if not cleaned_evidence:
            return ReasoningResult(
                question=cleaned_question,
                question_type=question_type,
                claims=[],
                uncertain_claims=[],
                conflicting_claims=[],
                research_gaps=[
                    "No usable evidence was retrieved."
                ],
                conclusion=(
                    "Axiom could not produce a "
                    "reliable evidence-grounded "
                    "synthesis because no usable "
                    "evidence was available."
                ),
                confidence=0.0,
                answer=(
                    "Insufficient evidence was "
                    "retrieved to answer this "
                    "question reliably."
                ),
                evidence_used=[],
            )

        claims = self._extract_claims(
            cleaned_evidence
        )

        uncertain_claims = (
            self._extract_uncertain_claims(
                cleaned_evidence
            )
        )

        conflicting_claims = (
            self._extract_conflicts(
                cleaned_evidence
            )
        )

        research_gaps = (
            self._identify_research_gaps(
                cleaned_evidence,
                claims,
                uncertain_claims,
            )
        )

        confidence = self._calculate_confidence(
            evidence=cleaned_evidence,
            claims=claims,
            uncertain_claims=uncertain_claims,
            conflicting_claims=conflicting_claims,
        )

        conclusion = self._build_conclusion(
            question=cleaned_question,
            claims=claims,
            uncertain_claims=uncertain_claims,
            conflicting_claims=conflicting_claims,
            research_gaps=research_gaps,
        )

        answer = self._build_answer(
            question=cleaned_question,
            claims=claims,
            uncertain_claims=uncertain_claims,
            research_gaps=research_gaps,
        )

        return ReasoningResult(
            question=cleaned_question,
            question_type=question_type,
            claims=claims,
            uncertain_claims=uncertain_claims,
            conflicting_claims=conflicting_claims,
            research_gaps=research_gaps,
            conclusion=conclusion,
            confidence=confidence,
            answer=answer,
            evidence_used=cleaned_evidence,
        )

    @staticmethod
    def _clean_evidence(
        evidence: list[str],
    ) -> list[str]:

        cleaned = []
        seen = set()

        for item in evidence:

            if not item:
                continue

            text = " ".join(
                str(item).split()
            ).strip()

            if not text:
                continue

            key = text.lower()

            if key in seen:
                continue

            seen.add(key)
            cleaned.append(text)

        return cleaned

    @staticmethod
    def _classify_question(
        question: str,
    ) -> str:

        text = question.lower().strip()

        if text.startswith(
            ("how does", "how do", "how can")
        ):
            return "explanatory"

        if text.startswith(
            ("why does", "why do", "why is", "why are")
        ):
            return "causal"

        if text.startswith(
            ("what is", "what are", "define")
        ):
            return "descriptive"

        if text.startswith(
            ("can ", "could ", "is it possible")
        ):
            return "possibility"

        if text.startswith(
            ("which ", "what ")
        ):
            return "comparative"

        return "general"


    @classmethod
    def _split_sentences(
        cls,
        text: str,
    ) -> list[str]:

        sentences = re.split(
            r"(?<=[.!?])\s+",
            text,
        )

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

    @classmethod
    def _contains_term(
        cls,
        text: str,
        terms: set[str],
    ) -> bool:

        lowered = text.lower()

        return any(
            term in lowered
            for term in terms
        )

    @classmethod
    def _extract_claims(
        cls,
        evidence: list[str],
    ) -> list[str]:

        candidates = []

        for item in evidence:

            for sentence in cls._split_sentences(
                item
            ):

                if len(sentence) < 35:
                    continue

                if cls._contains_term(
                    sentence,
                    cls.DISCOVERY_TERMS,
                ):
                    candidates.append(
                        sentence
                    )

        return cls._rank_statements(
            candidates,
            maximum=6,
        )

    @classmethod
    def _extract_uncertain_claims(
        cls,
        evidence: list[str],
    ) -> list[str]:

        candidates = []

        for item in evidence:

            for sentence in cls._split_sentences(
                item
            ):

                if cls._contains_term(
                    sentence,
                    cls.LIMITATION_TERMS,
                ):
                    candidates.append(
                        sentence
                    )

        return cls._rank_statements(
            candidates,
            maximum=5,
        )

    @classmethod
    def _extract_conflicts(
        cls,
        evidence: list[str],
    ) -> list[str]:

        candidates = []

        for item in evidence:

            for sentence in cls._split_sentences(
                item
            ):

                if cls._contains_term(
                    sentence,
                    cls.CONFLICT_TERMS,
                ):
                    candidates.append(
                        sentence
                    )

        return cls._rank_statements(
            candidates,
            maximum=4,
        )

    @classmethod
    def _identify_research_gaps(
        cls,
        evidence: list[str],
        claims: list[str],
        uncertain_claims: list[str],
    ) -> list[str]:

        gaps = []

        limitation_text = " ".join(
            uncertain_claims
        ).lower()

        evidence_text = " ".join(
            evidence
        ).lower()

        if (
            "human oversight"
            in limitation_text
            or "human validation"
            in limitation_text
            or "experimental validation"
            in limitation_text
            or "validation required"
            in limitation_text
        ):
            gaps.append(
                "How reliably can AI-generated "
                "research ideas be experimentally "
                "validated?"
            )

        if (
            "not yet"
            in limitation_text
            or "still"
            in limitation_text
            or "limited"
            in limitation_text
            or "unable"
            in limitation_text
            or "cannot"
            in limitation_text
        ):
            gaps.append(
                "What limits the generalization of "
                "AI-driven scientific discovery "
                "beyond narrow research domains?"
            )

        if (
            "hypothesis"
            in evidence_text
            and (
                "experiment"
                in evidence_text
                or "experimental"
                in evidence_text
            )
        ):
            gaps.append(
                "How can AI-generated hypotheses be "
                "systematically converted into "
                "reproducible experiments and "
                "validated scientific knowledge?"
            )

        if (
            "data quality"
            in evidence_text
            or "data"
            in limitation_text
        ):
            gaps.append(
                "How do data quality, provenance, and "
                "coverage affect the reliability of "
                "AI-assisted scientific discovery?"
            )

        if not gaps and uncertain_claims:
            gaps.append(
                "Further research is needed to "
                "determine how the reported "
                "limitations affect real-world "
                "scientific discovery."
            )

        return cls._unique(
            gaps
        )[:4]

    @classmethod
    def _calculate_confidence(
        cls,
        evidence: list[str],
        claims: list[str],
        uncertain_claims: list[str],
        conflicting_claims: list[str],
    ) -> float:

        evidence_count = len(
            evidence
        )

        if evidence_count == 0:
            return 0.0

        # Evidence quantity contributes only modestly.
        quantity_score = min(
            evidence_count / 20.0,
            1.0,
        )

        claim_score = min(
            len(claims) / 5.0,
            1.0,
        )

        uncertainty_penalty = min(
            len(uncertain_claims) / 8.0,
            0.35,
        )

        conflict_penalty = min(
            len(conflicting_claims) / 5.0,
            0.25,
        )

        score = (
            0.35 * quantity_score
            + 0.65 * claim_score
            - uncertainty_penalty
            - conflict_penalty
        )

        score = max(
            0.0,
            min(score, 0.85),
        )

        return round(
            score,
            3,
        )

    @classmethod
    def _build_conclusion(
        cls,
        question: str,
        claims: list[str],
        uncertain_claims: list[str],
        conflicting_claims: list[str],
        research_gaps: list[str],
    ) -> str:

        if not claims:
            return (
                "The retrieved literature does not "
                "provide enough directly relevant "
                "evidence to construct a reliable "
                "scientific synthesis for this "
                "question."
            )

        conclusion_parts = []

        if claims:
            conclusion_parts.append(
                "The retrieved literature indicates "
                "that AI is increasingly being used "
                "across multiple stages of scientific "
                "discovery, including literature "
                "analysis, hypothesis generation, "
                "experimental planning, and data "
                "analysis."
            )

        if uncertain_claims:
            conclusion_parts.append(
                "However, the evidence also indicates "
                "important limitations and unresolved "
                "issues, particularly around "
                "validation, reliability, and the "
                "degree of human oversight required."
            )

        if conflicting_claims:
            conclusion_parts.append(
                "Some evidence contains differing "
                "claims or qualifications, so the "
                "retrieved literature should not be "
                "treated as establishing a single "
                "universal conclusion."
            )

        if research_gaps:
            conclusion_parts.append(
                "A significant remaining question is "
                "how reliably AI-generated ideas can "
                "be converted into independently "
                "validated scientific knowledge."
            )

        return " ".join(
            conclusion_parts
        )

    @classmethod
    def _build_answer(
        cls,
        question: str,
        claims: list[str],
        uncertain_claims: list[str],
        research_gaps: list[str],
    ) -> str:

        if not claims:
            return (
                "Axiom did not retrieve enough "
                "directly relevant evidence to "
                "provide a reliable answer."
            )

        answer_parts = [
            "The retrieved literature suggests "
            "that artificial intelligence can "
            "affect scientific discovery by "
            "accelerating and augmenting several "
            "parts of the research process."
        ]

        if claims:
            answer_parts.append(
                "The strongest evidence points to "
                "AI-assisted literature analysis, "
                "hypothesis generation, experimental "
                "planning, and scientific data "
                "analysis."
            )

        if uncertain_claims:
            answer_parts.append(
                "The literature also indicates that "
                "these capabilities do not eliminate "
                "the need for scientific validation: "
                "limitations involving reliability, "
                "generalization, data quality, and "
                "human oversight remain."
            )

        if research_gaps:
            answer_parts.append(
                "An important open problem is "
                "determining when AI-generated "
                "hypotheses represent genuinely new "
                "scientific knowledge rather than "
                "plausible combinations of existing "
                "knowledge."
            )

        return " ".join(
            answer_parts
        )

    @classmethod
    def _rank_statements(
        cls,
        statements: list[str],
        maximum: int,
    ) -> list[str]:

        scored = []

        for statement in statements:

            lowered = statement.lower()

            score = 0

            for term in cls.DISCOVERY_TERMS:
                if term in lowered:
                    score += 1

            for term in cls.BENEFIT_TERMS:
                if term in lowered:
                    score += 0.5

            if len(statement) > 250:
                score -= 0.5

            scored.append(
                (
                    score,
                    statement,
                )
            )

        scored.sort(
            key=lambda item: (
                item[0],
                len(item[1]),
            ),
            reverse=True,
        )

        return cls._unique(
            [
                statement
                for _, statement
                in scored
            ]
        )[:maximum]

    @staticmethod
    def _unique(
        items: list[str],
    ) -> list[str]:

        result = []
        seen = set()

        for item in items:

            key = (
                " ".join(
                    item.lower().split()
                )
            )

            if key in seen:
                continue

            seen.add(key)
            result.append(item)

        return result