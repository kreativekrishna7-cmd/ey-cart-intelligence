import pandas as pd
import plotly.express as px
from sqlalchemy import text

from analytics.database import engine


def monthly_revenue(
    start_date: str,
    end_date: str,
):

    query = text(
        """
        SELECT
            DATE_TRUNC('month', order_date) AS month,
            SUM(revenue) AS revenue
        FROM orders
        WHERE order_date >= :start_date
          AND order_date < :end_date
        GROUP BY 1
        ORDER BY 1
        """
    )

    with engine.connect() as connection:

        result = connection.execute(
            query,
            {
                "start_date": start_date,
                "end_date": end_date,
            },
        )

        rows = result.fetchall()

    if not rows:
        return None

    df = pd.DataFrame(
        rows,
        columns=["month", "revenue"],
    )

    df["month"] = pd.to_datetime(
        df["month"]
    ).dt.strftime("%b %Y")

    fig = px.line(
        df,
        x="month",
        y="revenue",
        markers=True,
        title="Monthly Revenue",
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Revenue",
        hovermode="x unified",
    )

    return fig


def yearly_revenue_profit(
    start_date_1: str,
    end_date_1: str,
    start_date_2: str,
    end_date_2: str,
):

    query = text(
        """
        SELECT
            :label AS period,
            COALESCE(SUM(revenue), 0) AS revenue,
            COALESCE(SUM(profit), 0) AS profit
        FROM orders
        WHERE order_date >= :start_date
          AND order_date < :end_date
        """
    )

    rows = []

    periods = [
        (
            "2025",
            start_date_1,
            end_date_1,
        ),
        (
            "2026",
            start_date_2,
            end_date_2,
        ),
    ]

    with engine.connect() as connection:

        for label, start, end in periods:

            result = connection.execute(
                query,
                {
                    "label": label,
                    "start_date": start,
                    "end_date": end,
                },
            )

            row = result.mappings().first()

            rows.append(
                {
                    "period": label,
                    "revenue": float(
                        row["revenue"] or 0
                    ),
                    "profit": float(
                        row["profit"] or 0
                    ),
                }
            )

    df = pd.DataFrame(rows)

    fig = px.bar(
        df,
        x="period",
        y=["revenue", "profit"],
        barmode="group",
        title="Revenue and Profit Comparison",
    )

    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Amount",
        legend_title="Metric",
    )

    return fig


def category_revenue(
    start_date: str,
    end_date: str,
):

    query = text(
        """
        SELECT
            p.category,
            SUM(o.revenue) AS revenue
        FROM orders o
        JOIN products p
          ON o.product_id = p.product_id
        WHERE o.order_date >= :start_date
          AND o.order_date < :end_date
        GROUP BY p.category
        ORDER BY revenue DESC
        """
    )

    with engine.connect() as connection:

        result = connection.execute(
            query,
            {
                "start_date": start_date,
                "end_date": end_date,
            },
        )

        rows = result.fetchall()

    if not rows:
        return None

    df = pd.DataFrame(
        rows,
        columns=[
            "category",
            "revenue",
        ],
    )

    fig = px.pie(
        df,
        names="category",
        values="revenue",
        title="Revenue Contribution by Category",
    )

    return fig


def top_products(
    start_date: str,
    end_date: str,
    limit: int = 10,
):

    query = text(
        """
        SELECT
            p.product_name,
            SUM(o.revenue) AS revenue
        FROM orders o
        JOIN products p
          ON o.product_id = p.product_id
        WHERE o.order_date >= :start_date
          AND o.order_date < :end_date
        GROUP BY p.product_name
        ORDER BY revenue DESC
        LIMIT :limit
        """
    )

    with engine.connect() as connection:

        result = connection.execute(
            query,
            {
                "start_date": start_date,
                "end_date": end_date,
                "limit": limit,
            },
        )

        rows = result.fetchall()

    if not rows:
        return None

    df = pd.DataFrame(
        rows,
        columns=[
            "product",
            "revenue",
        ],
    )

    df = df.sort_values(
        "revenue",
        ascending=True,
    )

    fig = px.bar(
        df,
        x="revenue",
        y="product",
        orientation="h",
        title=f"Top {limit} Products by Revenue",
    )

    fig.update_layout(
        xaxis_title="Revenue",
        yaxis_title="Product",
    )

    return fig