import sys
import time

from .axiom import run_research


def main() -> None:

    if len(sys.argv) < 2:
        print(
            'Usage: python -m src.axiom.research_cli '
            '"your research question"'
        )
        raise SystemExit(1)

    question = " ".join(
        sys.argv[1:]
    ).strip()

    if not question:
        print(
            "Research question cannot be empty."
        )
        raise SystemExit(1)

    print(
        "=== AXIOM RESEARCH STARTED ==="
    )
    print(
        f"Question: {question}"
    )
    print()

    start = time.perf_counter()

    print(
        "Searching scientific literature..."
    )

    report = run_research(
        question
    )

    elapsed = (
        time.perf_counter()
        - start
    )

    if report is None:
        print(
            "ERROR: research returned no report."
        )
        raise SystemExit(1)

    rendered = report.render()

    if not rendered:
        print(
            "ERROR: report rendering returned "
            "an empty result."
        )
        raise SystemExit(1)

    print(
        f"Research completed in "
        f"{elapsed:.2f} seconds."
    )
    print()
    print(
        rendered
    )


if __name__ == "__main__":
    main()