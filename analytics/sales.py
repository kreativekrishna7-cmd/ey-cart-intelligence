from .database import fetch_all, fetch_one


def get_monthly_performance(year: int, month: int) -> dict:
    sql = """
    SELECT
        COALESCE(SUM(revenue) FILTER (WHERE order_status = 'Delivered'), 0) AS revenue,
        COALESCE(SUM(profit) FILTER (WHERE order_status = 'Delivered'), 0) AS profit,
        COALESCE(SUM(quantity) FILTER (WHERE order_status = 'Delivered'), 0) AS units_sold,
        COUNT(*) FILTER (WHERE order_status = 'Delivered') AS orders,
        COUNT(*) FILTER (WHERE order_status = 'Cancelled') AS cancelled_orders
    FROM orders
    WHERE order_date >= make_date(:year, :month, 1)
      AND order_date < (make_date(:year, :month, 1) + INTERVAL '1 month')
    """

    row = fetch_one(sql, {"year": year, "month": month}) or {}

    revenue = float(row.get("revenue") or 0)
    profit = float(row.get("profit") or 0)
    orders = int(row.get("orders") or 0)

    return {
        "period": f"{year}-{month:02d}",
        "revenue": round(revenue, 2),
        "profit": round(profit, 2),
        "orders": orders,
        "units_sold": int(row.get("units_sold") or 0),
        "cancelled_orders": int(row.get("cancelled_orders") or 0),
        "aov": round(revenue / orders, 2) if orders else 0,
        "margin_percent": round((profit / revenue) * 100, 2) if revenue else 0,
    }


def get_executive_kpis(start_date: str, end_date: str) -> dict:
    """Return KPIs for an arbitrary date range. End date is exclusive."""
    sql = """
    SELECT
        COALESCE(SUM(revenue) FILTER (WHERE order_status = 'Delivered'), 0) AS revenue,
        COALESCE(SUM(profit) FILTER (WHERE order_status = 'Delivered'), 0) AS profit,
        COALESCE(SUM(quantity) FILTER (WHERE order_status = 'Delivered'), 0) AS units_sold,
        COUNT(*) FILTER (WHERE order_status = 'Delivered') AS orders,
        COUNT(DISTINCT customer_id) FILTER (WHERE order_status = 'Delivered') AS customers,
        COUNT(*) FILTER (WHERE order_status = 'Cancelled') AS cancelled_orders
    FROM orders
    WHERE order_date >= :start_date
      AND order_date < :end_date
    """

    row = fetch_one(
        sql,
        {"start_date": start_date, "end_date": end_date},
    ) or {}

    revenue = float(row.get("revenue") or 0)
    profit = float(row.get("profit") or 0)
    orders = int(row.get("orders") or 0)

    return {
        "period": {
            "start": start_date,
            "end": end_date,
        },
        "revenue": round(revenue, 2),
        "profit": round(profit, 2),
        "margin_percent": round((profit / revenue) * 100, 2) if revenue else 0,
        "orders": orders,
        "units_sold": int(row.get("units_sold") or 0),
        "customers": int(row.get("customers") or 0),
        "cancelled_orders": int(row.get("cancelled_orders") or 0),
        "aov": round(revenue / orders, 2) if orders else 0,
    }


def get_revenue_trend(start_date: str, end_date: str) -> list[dict]:
    """Return monthly revenue, orders and AOV for a date range."""
    sql = """
    SELECT
        TO_CHAR(DATE_TRUNC('month', order_date), 'YYYY-MM') AS month,
        ROUND(
            COALESCE(
                SUM(revenue) FILTER (WHERE order_status = 'Delivered'),
                0
            ), 2
        ) AS revenue,
        COUNT(*) FILTER (WHERE order_status = 'Delivered') AS orders,
        ROUND(
            COALESCE(
                SUM(revenue) FILTER (WHERE order_status = 'Delivered'),
                0
            )
            / NULLIF(COUNT(*) FILTER (WHERE order_status = 'Delivered'), 0),
            2
        ) AS aov
    FROM orders
    WHERE order_date >= :start_date
      AND order_date < :end_date
    GROUP BY DATE_TRUNC('month', order_date)
    ORDER BY DATE_TRUNC('month', order_date)
    """

    rows = fetch_all(
        sql,
        {"start_date": start_date, "end_date": end_date},
    )

    return [
        {
            "month": r["month"],
            "revenue": float(r["revenue"] or 0),
            "orders": int(r["orders"] or 0),
            "aov": float(r["aov"] or 0),
        }
        for r in rows
    ]


def compare_months(
    current_year: int,
    current_month: int,
    previous_year: int,
    previous_month: int,
) -> dict:
    current = get_monthly_performance(current_year, current_month)
    previous = get_monthly_performance(previous_year, previous_month)

    def growth(current_value: float, previous_value: float) -> float:
        if previous_value == 0:
            return 0
        return round((current_value - previous_value) / previous_value * 100, 2)

    return {
        "current_period": current,
        "previous_period": previous,
        "growth_percent": {
            "revenue": growth(current["revenue"], previous["revenue"]),
            "profit": growth(current["profit"], previous["profit"]),
            "orders": growth(current["orders"], previous["orders"]),
            "units_sold": growth(current["units_sold"], previous["units_sold"]),
            "aov": growth(current["aov"], previous["aov"]),
            "margin_percentage_points": round(
                current["margin_percent"] - previous["margin_percent"], 2
            ),
        },
    }
