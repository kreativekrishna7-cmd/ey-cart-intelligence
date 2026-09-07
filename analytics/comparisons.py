from .database import fetch_all
from .sales import get_executive_kpis


def compare_periods(
    current_start: str,
    current_end: str,
    previous_start: str,
    previous_end: str,
) -> dict:
    current = get_executive_kpis(current_start, current_end)
    previous = get_executive_kpis(previous_start, previous_end)

    def growth(current_value: float, previous_value: float) -> float:
        if previous_value == 0:
            return 0
        return round(
            (current_value - previous_value) / previous_value * 100,
            2,
        )

    return {
        "current_period": current,
        "previous_period": previous,
        "growth_percent": {
            "revenue": growth(current["revenue"], previous["revenue"]),
            "profit": growth(current["profit"], previous["profit"]),
            "orders": growth(current["orders"], previous["orders"]),
            "units_sold": growth(
                current["units_sold"],
                previous["units_sold"],
            ),
            "customers": growth(
                current["customers"],
                previous["customers"],
            ),
            "aov": growth(current["aov"], previous["aov"]),
            "margin_percentage_points": round(
                current["margin_percent"]
                - previous["margin_percent"],
                2,
            ),
        },
    }


def compare_categories(
    category_1: str,
    category_2: str,
    start_date: str,
    end_date: str,
) -> dict:
    """Compare two product categories."""
    sql = """
    SELECT
        p.category,
        ROUND(SUM(o.revenue), 2) AS revenue,
        ROUND(SUM(o.profit), 2) AS profit,
        SUM(o.quantity) AS units_sold,
        COUNT(*) AS orders
    FROM orders o
    JOIN products p ON p.product_id = o.product_id
    WHERE o.order_status = 'Delivered'
      AND p.category IN (:category_1, :category_2)
      AND o.order_date >= :start_date
      AND o.order_date < :end_date
    GROUP BY p.category
    """

    rows = fetch_all(
        sql,
        {
            "category_1": category_1,
            "category_2": category_2,
            "start_date": start_date,
            "end_date": end_date,
        },
    )

    result = {}
    for row in rows:
        revenue = float(row["revenue"] or 0)
        profit = float(row["profit"] or 0)
        result[row["category"]] = {
            "revenue": revenue,
            "profit": profit,
            "units_sold": int(row["units_sold"] or 0),
            "orders": int(row["orders"] or 0),
            "margin_percent": round(
                profit / revenue * 100, 2
            ) if revenue else 0,
        }

    return {
        "period": {
            "start": start_date,
            "end": end_date,
        },
        "categories": result,
    }
