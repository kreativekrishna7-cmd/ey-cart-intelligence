from .database import fetch_all, fetch_one


def get_return_rate(
    start_date: str,
    end_date: str,
) -> dict:
    sql = """
    SELECT
        (
            SELECT COALESCE(SUM(quantity), 0)
            FROM returns
            WHERE return_date >= :start_date
              AND return_date < :end_date
        ) AS returned_units,
        (
            SELECT COALESCE(SUM(quantity), 0)
            FROM orders
            WHERE order_date >= :start_date
              AND order_date < :end_date
              AND order_status = 'Delivered'
        ) AS sold_units,
        (
            SELECT COALESCE(SUM(refund_amount), 0)
            FROM returns
            WHERE return_date >= :start_date
              AND return_date < :end_date
        ) AS refund_amount
    """

    row = fetch_one(
        sql,
        {
            "start_date": start_date,
            "end_date": end_date,
        },
    ) or {}

    returned = int(row.get("returned_units") or 0)
    sold = int(row.get("sold_units") or 0)

    return {
        "period": {
            "start": start_date,
            "end": end_date,
        },
        "returned_units": returned,
        "sold_units": sold,
        "return_rate_percent": round(
            returned / sold * 100,
            2,
        ) if sold else 0,
        "refund_amount": float(
            row.get("refund_amount") or 0
        ),
    }


def get_return_performance(
    start_date: str,
    end_date: str,
    limit: int = 20,
) -> list[dict]:
    """Return return reasons by category."""
    sql = """
    SELECT
        p.category,
        r.return_reason,
        COUNT(*) AS return_count,
        SUM(r.quantity) AS returned_units,
        ROUND(SUM(r.refund_amount), 2) AS refund_amount
    FROM returns r
    JOIN products p
        ON p.product_id = r.product_id
    WHERE r.return_date >= :start_date
      AND r.return_date < :end_date
    GROUP BY
        p.category,
        r.return_reason
    ORDER BY refund_amount DESC
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
            "category": row["category"],
            "return_reason": row["return_reason"],
            "return_count": int(row["return_count"] or 0),
            "returned_units": int(row["returned_units"] or 0),
            "refund_amount": float(
                row["refund_amount"] or 0
            ),
        }
        for index, row in enumerate(rows)
    ]


def get_category_return_rates(
    start_date: str,
    end_date: str,
) -> list[dict]:
    sql = """
    WITH sold AS (
        SELECT
            p.category,
            SUM(o.quantity) AS sold_units
        FROM orders o
        JOIN products p
            ON p.product_id = o.product_id
        WHERE o.order_status = 'Delivered'
          AND o.order_date >= :start_date
          AND o.order_date < :end_date
        GROUP BY p.category
    ),
    returned AS (
        SELECT
            p.category,
            SUM(r.quantity) AS returned_units,
            SUM(r.refund_amount) AS refund_amount
        FROM returns r
        JOIN products p
            ON p.product_id = r.product_id
        WHERE r.return_date >= :start_date
          AND r.return_date < :end_date
        GROUP BY p.category
    )
    SELECT
        sold.category,
        sold.sold_units,
        COALESCE(returned.returned_units, 0) AS returned_units,
        ROUND(
            COALESCE(returned.returned_units, 0)::numeric
            / NULLIF(sold.sold_units, 0) * 100,
            2
        ) AS return_rate_percent,
        ROUND(
            COALESCE(returned.refund_amount, 0),
            2
        ) AS refund_amount
    FROM sold
    LEFT JOIN returned
        ON returned.category = sold.category
    ORDER BY return_rate_percent DESC
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
            "sold_units": int(row["sold_units"] or 0),
            "returned_units": int(
                row["returned_units"] or 0
            ),
            "return_rate_percent": float(
                row["return_rate_percent"] or 0
            ),
            "refund_amount": float(
                row["refund_amount"] or 0
            ),
        }
        for row in rows
    ]
