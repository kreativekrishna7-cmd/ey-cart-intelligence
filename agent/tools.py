from analytics.sales import (
    get_executive_kpis,
    get_revenue_trend,
)

from analytics.products import (
    get_top_products,
    get_category_performance,
)

from analytics.comparisons import (
    compare_periods,
)

from agent.sql_engine import execute_readonly_query


def get_ey_cart_kpis(
    start_date: str,
    end_date: str,
) -> dict:
    """
    Get EY CART executive KPIs for a date range.

    Use this for questions about overall revenue,
    profit, orders, customers, AOV and margin.
    """

    return get_executive_kpis(
        start_date,
        end_date,
    )


def get_ey_cart_revenue_trend(
    start_date: str,
    end_date: str,
) -> list[dict]:
    """
    Get monthly EY CART revenue and order trends.
    """

    return get_revenue_trend(
        start_date,
        end_date,
    )


def get_ey_cart_top_products(
    start_date: str,
    end_date: str,
    limit: int = 10,
    metric: str = "revenue",
) -> list[dict]:
    """
    Get top EY CART products by revenue, profit,
    units sold or orders.
    """

    return get_top_products(
        start_date,
        end_date,
        limit,
        metric,
    )


def get_ey_cart_categories(
    start_date: str,
    end_date: str,
) -> list[dict]:
    """
    Get EY CART performance by product category.
    """

    return get_category_performance(
        start_date,
        end_date,
    )


def compare_ey_cart_periods(
    current_start: str,
    current_end: str,
    previous_start: str,
    previous_end: str,
) -> dict:
    """
    Compare two EY CART date ranges.

    Returns revenue, profit, orders, AOV,
    customer and margin changes.
    """

    return compare_periods(
        current_start,
        current_end,
        previous_start,
        previous_end,
    )


def run_ey_cart_sql(sql: str) -> dict:
    """
    Execute a READ-ONLY SQL query against EY CART PostgreSQL.

    Use this for ad-hoc questions that cannot be answered
    by the specialized analytics tools.
    """

    rows = execute_readonly_query(sql)

    return {
        "sql": sql,
        "row_count": len(rows),
        "rows": rows,
    }