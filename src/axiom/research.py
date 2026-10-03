from dataclasses import dataclass

from .knowledge import KnowledgeBase
from .literature import SafeLiteratureSearcher
from .hypothesis import HypothesisEngine, Hypothesis


@dataclass
class ResearchContext:
    question: str
    papers_found: int
    knowledge_summary: str
    hypotheses: list[Hypothesis]


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

    def investigate(
        self,
        question: str,
    ) -> ResearchContext:

        papers = self.literature.search(
            query=question,
            limit=5,
        )

        self.knowledge.add_papers(papers)

        context = self.knowledge.context()

        hypotheses = self.hypotheses.generate(
            question=question,
            knowledge_context=context,
        )

        return ResearchContext(
            question=question,
            papers_found=len(papers),
            knowledge_summary=context,
            hypotheses=hypotheses,
        )