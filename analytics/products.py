from .database import fetch_all


def get_top_products(
    start_date: str,
    end_date: str,
    limit: int = 10,
    metric: str = "revenue",
) -> list[dict]:
    allowed_metrics = {"revenue", "profit", "units_sold", "orders"}

    if metric not in allowed_metrics:
        raise ValueError(
            f"metric must be one of {sorted(allowed_metrics)}"
        )

    sql = f"""
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.brand,
        ROUND(COALESCE(SUM(o.revenue), 0), 2) AS revenue,
        ROUND(COALESCE(SUM(o.profit), 0), 2) AS profit,
        COALESCE(SUM(o.quantity), 0) AS units_sold,
        COUNT(o.order_id) AS orders
    FROM products p
    LEFT JOIN orders o
        ON p.product_id = o.product_id
       AND o.order_status = 'Delivered'
       AND o.order_date >= :start_date
       AND o.order_date < :end_date
    GROUP BY
        p.product_id,
        p.product_name,
        p.category,
        p.brand
    ORDER BY {metric} DESC
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
            "product_id": row["product_id"],
            "product_name": row["product_name"],
            "category": row["category"],
            "brand": row["brand"],
            "revenue": float(row["revenue"] or 0),
            "profit": float(row["profit"] or 0),
            "units_sold": int(row["units_sold"] or 0),
            "orders": int(row["orders"] or 0),
        }
        for index, row in enumerate(rows)
    ]


def get_category_performance(
    start_date: str,
    end_date: str,
) -> list[dict]:
    sql = """
    SELECT
        p.category,
        ROUND(SUM(o.revenue), 2) AS revenue,
        ROUND(SUM(o.profit), 2) AS profit,
        SUM(o.quantity) AS units_sold,
        COUNT(*) AS orders,
        ROUND(
            100 * SUM(o.profit) / NULLIF(SUM(o.revenue), 0),
            2
        ) AS margin_percent
    FROM orders o
    JOIN products p
        ON p.product_id = o.product_id
    WHERE o.order_status = 'Delivered'
      AND o.order_date >= :start_date
      AND o.order_date < :end_date
    GROUP BY p.category
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
            "category": row["category"],
            "revenue": float(row["revenue"] or 0),
            "profit": float(row["profit"] or 0),
            "units_sold": int(row["units_sold"] or 0),
            "orders": int(row["orders"] or 0),
            "margin_percent": float(row["margin_percent"] or 0),
        }
        for row in rows
    ]


def get_brand_performance(
    start_date: str,
    end_date: str,
    limit: int = 10,
) -> list[dict]:
    """Return top brands by revenue."""
    sql = """
    SELECT
        p.brand,
        ROUND(SUM(o.revenue), 2) AS revenue,
        ROUND(SUM(o.profit), 2) AS profit,
        SUM(o.quantity) AS units_sold,
        COUNT(*) AS orders
    FROM orders o
    JOIN products p
        ON p.product_id = o.product_id
    WHERE o.order_status = 'Delivered'
      AND o.order_date >= :start_date
      AND o.order_date < :end_date
    GROUP BY p.brand
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
            "brand": row["brand"],
            "revenue": float(row["revenue"] or 0),
            "profit": float(row["profit"] or 0),
            "units_sold": int(row["units_sold"] or 0),
            "orders": int(row["orders"] or 0),
        }
        for index, row in enumerate(rows)
    ]
