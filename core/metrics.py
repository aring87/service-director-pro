"""Metric calculations for the fixed-ops dashboard."""
from __future__ import annotations

from datetime import date

import pandas as pd


CLOSED_STATUSES = {"Closed"}


def active_repair_orders(repair_orders: pd.DataFrame) -> pd.DataFrame:
    if repair_orders.empty or "Status" not in repair_orders.columns:
        return repair_orders.copy()
    return repair_orders[~repair_orders["Status"].isin(CLOSED_STATUSES)].copy()


def calculate_kpis(repair_orders: pd.DataFrame, parts_delays: pd.DataFrame, declined_services: pd.DataFrame, alerts: pd.DataFrame, today: date | None = None) -> dict:
    today = today or date.today()
    active = active_repair_orders(repair_orders)

    overdue = 0
    if "Promise Date" in active.columns:
        overdue = int((pd.to_datetime(active["Promise Date"], errors="coerce").dt.date < today).sum())

    waiting_parts = 0
    if "Status" in active.columns:
        waiting_parts = int((active["Status"] == "Waiting Parts").sum())

    cp_revenue = 0.0
    if {"Pay Type", "Estimate Amount"}.issubset(active.columns):
        cp_revenue = float(active.loc[active["Pay Type"] == "Customer Pay", "Estimate Amount"].sum())

    declined_value = float(declined_services.get("Declined Amount", pd.Series(dtype=float)).sum()) if not declined_services.empty else 0.0

    critical_alerts = int((alerts.get("Priority", pd.Series(dtype=str)) == "Critical").sum()) if not alerts.empty else 0
    high_alerts = int((alerts.get("Priority", pd.Series(dtype=str)) == "High").sum()) if not alerts.empty else 0

    health_score = max(0, 100 - (critical_alerts * 12) - (high_alerts * 6) - (overdue * 3) - (waiting_parts * 1))

    return {
        "Active ROs": int(len(active)),
        "Overdue Promise": overdue,
        "Waiting Parts": waiting_parts,
        "Critical Alerts": critical_alerts,
        "Customer Pay Estimate": cp_revenue,
        "Declined Opportunity": declined_value,
        "Operational Health": health_score,
    }


def advisor_summary(repair_orders: pd.DataFrame, alerts: pd.DataFrame) -> pd.DataFrame:
    active = active_repair_orders(repair_orders)
    if active.empty or "Advisor" not in active.columns:
        return pd.DataFrame()

    summary = active.groupby("Advisor", dropna=False).agg(
        Active_ROs=("RO Number", "count"),
        Estimate_Total=("Estimate Amount", "sum"),
        Avg_RO_Value=("Estimate Amount", "mean"),
        Comebacks=("Comeback", "sum"),
        Customer_Updates=("Customer Updated", "sum"),
    ).reset_index()

    if not alerts.empty and "Owner" in alerts.columns:
        alert_counts = alerts.groupby("Owner").size().rename("Open_Alerts").reset_index()
        summary = summary.merge(alert_counts, left_on="Advisor", right_on="Owner", how="left").drop(columns=["Owner"])
    else:
        summary["Open_Alerts"] = 0

    summary["Open_Alerts"] = summary["Open_Alerts"].fillna(0).astype(int)
    summary["Customer_Update_Rate"] = (summary["Customer_Updates"] / summary["Active_ROs"]).fillna(0)
    return summary.sort_values(["Open_Alerts", "Active_ROs"], ascending=False)


def technician_summary(repair_orders: pd.DataFrame) -> pd.DataFrame:
    active = active_repair_orders(repair_orders)
    if active.empty or "Technician" not in active.columns:
        return pd.DataFrame()

    summary = active.groupby("Technician", dropna=False).agg(
        Active_Jobs=("RO Number", "count"),
        Hours_Sold=("Labor Hours Sold", "sum"),
        Hours_Flagged=("Labor Hours Flagged", "sum"),
    ).reset_index()

    summary["Efficiency"] = (summary["Hours_Flagged"] / summary["Hours_Sold"]).replace([float("inf"), -float("inf")], 0).fillna(0)
    summary["Capacity_Gap"] = 40 - summary["Hours_Sold"]
    return summary.sort_values("Hours_Sold", ascending=False)


def status_summary(repair_orders: pd.DataFrame) -> pd.DataFrame:
    active = active_repair_orders(repair_orders)
    if active.empty or "Status" not in active.columns:
        return pd.DataFrame()
    return active.groupby("Status").size().rename("Count").reset_index().sort_values("Count", ascending=False)
