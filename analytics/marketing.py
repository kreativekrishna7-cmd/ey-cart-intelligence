from .database import fetch_all


def get_marketing_performance(
    start_date: str,
    end_date: str,
    limit: int = 20,
) -> list[dict]:
    sql = """
    SELECT
        marketing_channel,
        region,
        ROUND(SUM(spend), 2) AS spend,
        SUM(impressions) AS impressions,
        SUM(clicks) AS clicks,
        SUM(conversions) AS conversions,
        ROUND(SUM(revenue), 2) AS revenue,
        ROUND(
            SUM(revenue) / NULLIF(SUM(spend), 0),
            2
        ) AS roas,
        ROUND(
            SUM(spend) / NULLIF(SUM(conversions), 0),
            2
        ) AS cac,
        ROUND(
            SUM(clicks)::numeric / NULLIF(SUM(impressions), 0) * 100,
            2
        ) AS ctr_percent,
        ROUND(
            SUM(conversions)::numeric / NULLIF(SUM(clicks), 0) * 100,
            2
        ) AS conversion_rate_percent
    FROM marketing_campaigns
    WHERE campaign_date >= :start_date
      AND campaign_date < :end_date
    GROUP BY marketing_channel, region
    ORDER BY roas DESC
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
            "marketing_channel": row["marketing_channel"],
            "region": row["region"],
            "spend": float(row["spend"] or 0),
            "impressions": int(row["impressions"] or 0),
            "clicks": int(row["clicks"] or 0),
            "conversions": int(row["conversions"] or 0),
            "revenue": float(row["revenue"] or 0),
            "roas": float(row["roas"] or 0),
            "cac": float(row["cac"] or 0),
            "ctr_percent": float(row["ctr_percent"] or 0),
            "conversion_rate_percent": float(
                row["conversion_rate_percent"] or 0
            ),
        }
        for index, row in enumerate(rows)
    ]


def get_channel_summary(
    start_date: str,
    end_date: str,
) -> list[dict]:
    sql = """
    SELECT
        marketing_channel,
        ROUND(SUM(spend), 2) AS spend,
        SUM(impressions) AS impressions,
        SUM(clicks) AS clicks,
        SUM(conversions) AS conversions,
        ROUND(SUM(revenue), 2) AS revenue,
        ROUND(
            SUM(revenue) / NULLIF(SUM(spend), 0),
            2
        ) AS roas,
        ROUND(
            SUM(spend) / NULLIF(SUM(conversions), 0),
            2
        ) AS cac
    FROM marketing_campaigns
    WHERE campaign_date >= :start_date
      AND campaign_date < :end_date
    GROUP BY marketing_channel
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
            "marketing_channel": row["marketing_channel"],
            "spend": float(row["spend"] or 0),
            "impressions": int(row["impressions"] or 0),
            "clicks": int(row["clicks"] or 0),
            "conversions": int(row["conversions"] or 0),
            "revenue": float(row["revenue"] or 0),
            "roas": float(row["roas"] or 0),
            "cac": float(row["cac"] or 0),
        }
        for row in rows
    ]


def get_campaign_performance(
    start_date: str,
    end_date: str,
    limit: int = 20,
) -> list[dict]:
    sql = """
    SELECT
        campaign_id,
        campaign_name,
        campaign_date,
        marketing_channel,
        region,
        ROUND(spend, 2) AS spend,
        impressions,
        clicks,
        conversions,
        ROUND(revenue, 2) AS revenue,
        ROUND(roas, 2) AS roas,
        ROUND(cac, 2) AS cac
    FROM marketing_campaigns
    WHERE campaign_date >= :start_date
      AND campaign_date < :end_date
    ORDER BY roas DESC
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
            "campaign_id": row["campaign_id"],
            "campaign_name": row["campaign_name"],
            "campaign_date": str(row["campaign_date"]),
            "marketing_channel": row["marketing_channel"],
            "region": row["region"],
            "spend": float(row["spend"] or 0),
            "impressions": int(row["impressions"] or 0),
            "clicks": int(row["clicks"] or 0),
            "conversions": int(row["conversions"] or 0),
            "revenue": float(row["revenue"] or 0),
            "roas": float(row["roas"] or 0),
            "cac": float(row["cac"] or 0),
        }
        for index, row in enumerate(rows)
    ]
