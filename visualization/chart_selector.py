import re


def detect_visualization(question: str):

    text = question.lower().strip()

    if "pie chart" in text:
        return "pie"

    if "line chart" in text:
        return "line"

    if "bar chart" in text:
        return "bar"

    trend_patterns = [
        r"\btrend\b",
        r"\bover time\b",
        r"\bmonthly\b",
        r"\bmonth by month\b",
        r"\bquarterly\b",
        r"\bquarter by quarter\b",
    ]

    if any(
        re.search(pattern, text)
        for pattern in trend_patterns
    ):
        return "line"

    ranking_patterns = [
        r"\btop \d+",
        r"\btop products\b",
        r"\bhighest\b",
        r"\blowest\b",
        r"\bbest\b",
        r"\bworst\b",
        r"\branking\b",
    ]

    if any(
        re.search(pattern, text)
        for pattern in ranking_patterns
    ):
        return "products"

    if (
        "category contribution" in text
        or "category share" in text
        or "revenue contribution" in text
        or "revenue share" in text
    ):
        return "pie"

    if (
        "compare" in text
        or "comparison" in text
        or " vs " in text
        or "versus" in text
    ):
        return "comparison"

    return None
