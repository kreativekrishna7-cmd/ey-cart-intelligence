from .database import fetch_all


def get_customer_segment_performance(
    start_date: str,
    end_date: str,
) -> list[dict]:
    sql = """
    SELECT
        c.customer_segment,
        COUNT(DISTINCT c.customer_id) AS customers,
        COUNT(o.order_id) AS orders,
        COALESCE(SUM(o.revenue), 0) AS revenue,
        COALESCE(SUM(o.profit), 0) AS profit,
        COALESCE(SUM(o.quantity), 0) AS units_sold
    FROM customers c
    LEFT JOIN orders o
        ON c.customer_id = o.customer_id
       AND o.order_status = 'Delivered'
       AND o.order_date >= :start_date
       AND o.order_date < :end_date
    GROUP BY c.customer_segment
    ORDER BY revenue DESC
    """

    rows = fetch_all(
        sql,
        {
            "start_date": start_date,
            "end_date": end_date,
        },
    )

    return [
        {
            "customer_segment": row["customer_segment"],
            "customers": int(row["customers"] or 0),
            "orders": int(row["orders"] or 0),
            "revenue": round(float(row["revenue"] or 0), 2),
            "profit": round(float(row["profit"] or 0), 2),
            "units_sold": int(row["units_sold"] or 0),
            "revenue_per_customer": round(
                float(row["revenue"] or 0)
                / max(int(row["customers"] or 0), 1),
                2,
            ),
        }
        for row in rows
    ]


def get_region_performance(
    start_date: str,
    end_date: str,
) -> list[dict]:
    """Return performance by EY CART region."""
    sql = """
    SELECT
        region,
        ROUND(SUM(revenue), 2) AS revenue,
        ROUND(SUM(profit), 2) AS profit,
        COUNT(*) AS orders,
        SUM(quantity) AS units_sold,
        COUNT(DISTINCT customer_id) AS customers
    FROM orders
    WHERE order_status = 'Delivered'
      AND order_date >= :start_date
      AND order_date < :end_date
    GROUP BY region
    ORDER BY revenue DESC
    """

    rows = fetch_all(
        sql,
        {
            "start_date": start_date,
            "end_date": end_date,
        },
    )

    return [
        {
            "region": row["region"],
            "revenue": float(row["revenue"] or 0),
            "profit": float(row["profit"] or 0),
            "orders": int(row["orders"] or 0),
            "units_sold": int(row["units_sold"] or 0),
            "customers": int(row["customers"] or 0),
            "aov": round(
                float(row["revenue"] or 0)
                / max(int(row["orders"] or 0), 1),
                2,
            ),
        }
        for row in rows
    ]


def get_city_performance(
    start_date: str,
    end_date: str,
    limit: int = 15,
) -> list[dict]:
    """Return top cities by revenue."""
    sql = """
    SELECT
        city,
        region,
        ROUND(SUM(revenue), 2) AS revenue,
        ROUND(SUM(profit), 2) AS profit,
        COUNT(*) AS orders
    FROM orders
    WHERE order_status = 'Delivered'
      AND order_date >= :start_date
      AND order_date < :end_date
    GROUP BY city, region
    ORDER BY revenue DESC
    LIMIT :limit
    """

    rows = fetch_all(
        sql,
        {
            "start_date": start_date,
            "end_date": end_date,
            "limit": limit,
        },
    )

    return [
        {
            "rank": index + 1,
            "city": row["city"],
            "region": row["region"],
            "revenue": float(row["revenue"] or 0),
            "profit": float(row["profit"] or 0),
            "orders": int(row["orders"] or 0),
        }
        for index, row in enumerate(rows)
    ]
