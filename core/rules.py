"""Business rule engine for fixed-ops exceptions."""
from __future__ import annotations

from datetime import date

import pandas as pd


CLOSED_STATUSES = {"Closed"}


def _safe_date(value) -> date | None:
    if pd.isna(value):
        return None
    return pd.to_datetime(value).date()


def build_alerts(repair_orders: pd.DataFrame, parts_delays: pd.DataFrame, declined_services: pd.DataFrame, today: date | None = None) -> pd.DataFrame:
    """Create an exception queue from repair orders, parts delays, and declined work."""
    today = today or date.today()
    alerts: list[dict] = []

    for _, row in repair_orders.iterrows():
        ro_number = row.get("RO Number", "")
        customer = row.get("Customer", "")
        advisor = row.get("Advisor", "")
        status = row.get("Status", "")
        open_date = _safe_date(row.get("Open Date"))
        promise_date = _safe_date(row.get("Promise Date"))
        customer_updated = bool(row.get("Customer Updated", False))
        comeback = bool(row.get("Comeback", False))

        if status not in CLOSED_STATUSES and open_date:
            age_days = (today - open_date).days
            if age_days >= 5:
                alerts.append({
                    "Priority": "Critical" if age_days >= 8 else "High",
                    "Category": "Aging RO",
                    "RO Number": ro_number,
                    "Customer": customer,
                    "Owner": advisor,
                    "Issue": f"Repair order has been open {age_days} days.",
                    "Recommended Action": "Review blockers, update customer, and assign next action owner.",
                })

        if status not in CLOSED_STATUSES and promise_date and promise_date < today:
            alerts.append({
                "Priority": "Critical",
                "Category": "Missed Promise",
                "RO Number": ro_number,
                "Customer": customer,
                "Owner": advisor,
                "Issue": f"Promise date passed on {promise_date.isoformat()}.",
                "Recommended Action": "Contact customer and reset promise time with technician/parts status.",
            })

        if status not in CLOSED_STATUSES and not customer_updated:
            alerts.append({
                "Priority": "Medium",
                "Category": "Customer Update Needed",
                "RO Number": ro_number,
                "Customer": customer,
                "Owner": advisor,
                "Issue": "Customer update flag is not marked complete.",
                "Recommended Action": "Advisor should call/text customer and record update.",
            })

        if comeback:
            alerts.append({
                "Priority": "High",
                "Category": "Comeback",
                "RO Number": ro_number,
                "Customer": customer,
                "Owner": advisor,
                "Issue": "Vehicle is marked as a comeback.",
                "Recommended Action": "Escalate to service manager and verify quality-control path.",
            })

    for _, row in parts_delays.iterrows():
        eta = _safe_date(row.get("ETA"))
        if eta and eta < today:
            alerts.append({
                "Priority": "High",
                "Category": "Parts ETA Missed",
                "RO Number": row.get("RO Number", ""),
                "Customer": row.get("Customer", ""),
                "Owner": row.get("Advisor", ""),
                "Issue": f"Part ETA passed on {eta.isoformat()}.",
                "Recommended Action": "Confirm vendor ETA, update customer, and review loaner/rental need.",
            })

    for _, row in declined_services.iterrows():
        follow_up = _safe_date(row.get("Follow Up Date"))
        contacted = bool(row.get("Contacted", False))
        if follow_up and follow_up <= today and not contacted:
            alerts.append({
                "Priority": "Medium",
                "Category": "Declined Service Follow-Up",
                "RO Number": row.get("RO Number", ""),
                "Customer": row.get("Customer", ""),
                "Owner": row.get("Advisor", ""),
                "Issue": f"Follow-up due for ${row.get('Declined Amount', 0):,.0f} declined service.",
                "Recommended Action": "Call customer with safety/maintenance value explanation.",
            })

    result = pd.DataFrame(alerts)
    if result.empty:
        return pd.DataFrame(columns=["Priority", "Category", "RO Number", "Customer", "Owner", "Issue", "Recommended Action"])

    priority_rank = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    result["Priority Rank"] = result["Priority"].map(priority_rank).fillna(9)
    result = result.sort_values(["Priority Rank", "Category", "RO Number"]).drop(columns=["Priority Rank"])
    return result.reset_index(drop=True)
