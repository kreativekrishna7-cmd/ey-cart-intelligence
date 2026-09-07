from .database import fetch_all


def get_inventory_risk(limit: int = 20) -> list[dict]:
    sql = """
    SELECT
        i.product_id,
        p.product_name,
        p.category,
        COUNT(*) AS snapshots,
        SUM(
            CASE WHEN i.stockout THEN 1 ELSE 0 END
        ) AS stockout_snapshots,
        ROUND(AVG(i.closing_stock), 2) AS avg_closing_stock,
        SUM(i.units_sold) AS units_sold,
        ROUND(
            SUM(
                CASE WHEN i.stockout THEN 1 ELSE 0 END
            )::numeric / NULLIF(COUNT(*), 0) * 100,
            2
        ) AS stockout_rate_percent
    FROM inventory i
    JOIN products p
        ON p.product_id = i.product_id
    GROUP BY
        i.product_id,
        p.product_name,
        p.category
    HAVING SUM(
        CASE WHEN i.stockout THEN 1 ELSE 0 END
    ) > 0
    ORDER BY
        stockout_snapshots DESC,
        units_sold DESC
    LIMIT :limit
    """

    rows = fetch_all(sql, {"limit": limit})

    return [
        {
            "rank": index + 1,
            "product_id": row["product_id"],
            "product_name": row["product_name"],
            "category": row["category"],
            "snapshots": int(row["snapshots"] or 0),
            "stockout_snapshots": int(
                row["stockout_snapshots"] or 0
            ),
            "stockout_rate_percent": float(
                row["stockout_rate_percent"] or 0
            ),
            "avg_closing_stock": float(
                row["avg_closing_stock"] or 0
            ),
            "units_sold": int(row["units_sold"] or 0),
        }
        for index, row in enumerate(rows)
    ]


def get_inventory_summary() -> dict:
    """Return overall inventory health."""
    sql = """
    SELECT
        COUNT(*) AS snapshots,
        COUNT(DISTINCT product_id) AS products,
        SUM(
            CASE WHEN stockout THEN 1 ELSE 0 END
        ) AS stockout_snapshots,
        ROUND(AVG(closing_stock), 2) AS average_closing_stock,
        SUM(units_sold) AS units_sold
    FROM inventory
    """

    rows = fetch_all(sql)
    row = rows[0] if rows else {}

    snapshots = int(row.get("snapshots") or 0)
    stockouts = int(row.get("stockout_snapshots") or 0)

    return {
        "snapshots": snapshots,
        "products": int(row.get("products") or 0),
        "stockout_snapshots": stockouts,
        "stockout_rate_percent": round(
            stockouts / snapshots * 100,
            2,
        ) if snapshots else 0,
        "average_closing_stock": float(
            row.get("average_closing_stock") or 0
        ),
        "units_sold": int(row.get("units_sold") or 0),
    }


def get_category_inventory_risk(
    limit: int = 20,
) -> list[dict]:
    """Return stockout exposure by category."""
    sql = """
    SELECT
        p.category,
        COUNT(*) AS snapshots,
        SUM(
            CASE WHEN i.stockout THEN 1 ELSE 0 END
        ) AS stockout_snapshots,
        ROUND(AVG(i.closing_stock), 2) AS avg_closing_stock,
        SUM(i.units_sold) AS units_sold
    FROM inventory i
    JOIN products p
        ON p.product_id = i.product_id
    GROUP BY p.category
    ORDER BY stockout_snapshots DESC
    LIMIT :limit
    """

    rows = fetch_all(sql, {"limit": limit})

    return [
        {
            "category": row["category"],
            "snapshots": int(row["snapshots"] or 0),
            "stockout_snapshots": int(
                row["stockout_snapshots"] or 0
            ),
            "stockout_rate_percent": round(
                int(row["stockout_snapshots"] or 0)
                / max(int(row["snapshots"] or 0), 1)
                * 100,
                2,
            ),
            "avg_closing_stock": float(
                row["avg_closing_stock"] or 0
            ),
            "units_sold": int(row["units_sold"] or 0),
        }
        for row in rows
    ]
