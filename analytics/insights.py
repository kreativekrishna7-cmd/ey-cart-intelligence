from .sales import get_executive_kpis
from .products import get_category_performance
from .customers import get_region_performance, get_customer_segment_performance
from .marketing import get_marketing_performance
from .inventory import get_inventory_risk
from .returns import get_return_rate


def get_executive_summary(start_date: str, end_date: str) -> dict:
    kpis = get_executive_kpis(start_date, end_date)
    categories = get_category_performance(start_date, end_date)
    regions = get_region_performance(start_date, end_date)
    segments = get_customer_segment_performance(start_date, end_date)
    marketing = get_marketing_performance(start_date, end_date, limit=5)
    inventory = get_inventory_risk(limit=5)
    returns = get_return_rate(start_date, end_date)

    return {
        "period": {"start": start_date, "end": end_date},
        "kpis": kpis,
        "top_categories": categories[:3],
        "regions": regions,
        "customer_segments": segments,
        "top_marketing_performers": marketing,
        "inventory_risks": inventory,
        "returns": returns,
    }
