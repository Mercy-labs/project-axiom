class EvidenceEvaluator:

    def analyse(self, results):
        if not results:
            return {
                "relationship": "unknown",
                "average": 0,
                "highest": 0,
                "lowest": 0,
            }

        outputs = [
            result["output"]
            for result in results
        ]

        average = sum(outputs) / len(outputs)
        highest = max(outputs)
        lowest = min(outputs)

        if len(outputs) >= 2:
            change = outputs[-1] - outputs[0]
        else:
            change = 0

        if change > 2:
            relationship = "positive"
        elif change < -2:
            relationship = "negative"
        else:
            relationship = "uncertain"

        return {
            "relationship": relationship,
            "average": average,
            "highest": highest,
            "lowest": lowest,
        }

    def evaluate_hypothesis(self, hypothesis, analysis):
        relationship = analysis["relationship"]

        statement = hypothesis.statement.lower()

        if relationship == "positive":
            if "positive" in statement:
                return "supported"

            if "negative" in statement:
                return "contradicted"

        if relationship == "negative":
            if "negative" in statement:
                return "supported"

            if "positive" in statement:
                return "contradicted"

        return "uncertain"