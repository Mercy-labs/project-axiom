from dataclasses import dataclass

from .knowledge import KnowledgeBase
from .literature import SafeLiteratureSearcher
from .hypothesis import HypothesisEngine, Hypothesis
from .evidence import EvidenceExtractor, Evidence
from .reasoner import AxiomReasoner, ReasoningResult


@dataclass
class ResearchContext:
    question: str
    papers_found: int
    knowledge_summary: str
    hypotheses: list[Hypothesis]
    evidence: list[Evidence]
    reasoning: ReasoningResult
    source_status: list


class ScientificResearcher:
    def __init__(
        self,
        literature_searcher: SafeLiteratureSearcher,
        knowledge_base: KnowledgeBase,
        hypothesis_engine: HypothesisEngine,
    ):
        self.literature = literature_searcher
        self.knowledge = knowledge_base
        self.hypotheses = hypothesis_engine
        self.evidence_extractor = EvidenceExtractor()
        self.reasoner = AxiomReasoner()

    def investigate(self, question: str) -> ResearchContext:
        # 1. Search real scientific literature.
        search_result = self.literature.search_with_status(
            query=question,
            limit=5,
        )

        papers = []
        source_status = []

        for result in search_result:
            papers.extend(result.papers)
            source_status.append(result)

        # 2. Store the papers in Axiom's knowledge base.
        self.knowledge.add_papers(papers)

        # 3. Build the knowledge context.
        context = self.knowledge.context()

        # 4. Generate initial hypotheses.
        hypotheses = self.hypotheses.generate(
            question=question,
            knowledge_context=context,
        )

        # 5. Extract evidence from the papers.
        evidence = self.evidence_extractor.extract(
            papers
        )

        # 6. Turn hypotheses into claims for the reasoner.
        claims = [
            hypothesis.statement
            for hypothesis in hypotheses
        ]

        # 7. Let Axiom reason over the evidence.
        reasoning = self.reasoner.reason(
            question=question,
            evidence=[
                item.statement
                for item in evidence
            ],
            claims=claims,
        )

        return ResearchContext(
            question=question,
            papers_found=len(papers),
            knowledge_summary=context,
            hypotheses=hypotheses,
            evidence=evidence,
            reasoning=reasoning,
            source_status=source_status,
        )