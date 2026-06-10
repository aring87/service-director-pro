from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from config.app_config import APP_NAME, APP_SUBTITLE, DEMO_FILE, STATUS_ORDER
from core.data_loader import load_dealership_workbook
from core.metrics import advisor_summary, calculate_kpis, status_summary, technician_summary, active_repair_orders
from core.rules import build_alerts

st.set_page_config(page_title=APP_NAME, page_icon="🚗", layout="wide")


def money(value: float) -> str:
    return f"${value:,.0f}"


def percent(value: float) -> str:
    return f"{value:.0%}"


def badge_priority(priority: str) -> str:
    styles = {
        "Critical": "background:#FEE2E2;color:#991B1B;border:1px solid #FCA5A5;",
        "High": "background:#FFEDD5;color:#9A3412;border:1px solid #FDBA74;",
        "Medium": "background:#FEF9C3;color:#854D0E;border:1px solid #FDE68A;",
        "Low": "background:#DCFCE7;color:#166534;border:1px solid #86EFAC;",
    }
    style = styles.get(priority, "background:#E2E8F0;color:#334155;border:1px solid #CBD5E1;")
    return f"<span style='padding:4px 8px;border-radius:999px;font-weight:700;{style}'>{priority}</span>"


def style_page() -> None:
    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.2rem;}
        div[data-testid="stMetricValue"] {font-size: 1.8rem;}
        .hero {
            padding: 1.1rem 1.25rem;
            border-radius: 18px;
            background: linear-gradient(135deg, #0F766E 0%, #0F172A 100%);
            color: white;
            margin-bottom: 1rem;
        }
        .hero h1 {margin: 0; font-size: 2.05rem;}
        .hero p {margin: .25rem 0 0 0; color: #CCFBF1;}
        .section-card {
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 1rem;
            background: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def load_source():
    st.sidebar.header("Data Source")
    uploaded = st.sidebar.file_uploader("Upload dealership workbook", type=["xlsx"])
    if uploaded is not None:
        return uploaded, "Uploaded workbook"

    demo_path = Path(DEMO_FILE)
    if not demo_path.exists():
        st.sidebar.error("Demo workbook not found. Add demo_data/service_director_demo.xlsx.")
        st.stop()
    return demo_path, "Included demo workbook"


def render_kpis(kpis: dict) -> None:
    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    c1.metric("Active ROs", f"{kpis['Active ROs']}")
    c2.metric("Overdue", f"{kpis['Overdue Promise']}")
    c3.metric("Waiting Parts", f"{kpis['Waiting Parts']}")
    c4.metric("Critical Alerts", f"{kpis['Critical Alerts']}")
    c5.metric("CP Estimate", money(kpis["Customer Pay Estimate"]))
    c6.metric("Declined $", money(kpis["Declined Opportunity"]))
    c7.metric("Health", f"{kpis['Operational Health']}/100")


def filter_panel(repair_orders: pd.DataFrame):
    st.sidebar.header("Filters")
    advisors = sorted([x for x in repair_orders.get("Advisor", pd.Series(dtype=str)).dropna().unique()])
    statuses = [s for s in STATUS_ORDER if s in repair_orders.get("Status", pd.Series(dtype=str)).unique()]
    pay_types = sorted([x for x in repair_orders.get("Pay Type", pd.Series(dtype=str)).dropna().unique()])

    selected_advisors = st.sidebar.multiselect("Advisor", advisors, default=advisors)
    selected_statuses = st.sidebar.multiselect("RO Status", statuses, default=statuses)
    selected_pay_types = st.sidebar.multiselect("Pay Type", pay_types, default=pay_types)
    show_closed = st.sidebar.checkbox("Include closed ROs", value=False)
    return selected_advisors, selected_statuses, selected_pay_types, show_closed


def apply_filters(repair_orders: pd.DataFrame, advisors, statuses, pay_types, show_closed: bool) -> pd.DataFrame:
    df = repair_orders.copy()
    if advisors and "Advisor" in df.columns:
        df = df[df["Advisor"].isin(advisors)]
    if statuses and "Status" in df.columns:
        df = df[df["Status"].isin(statuses)]
    if pay_types and "Pay Type" in df.columns:
        df = df[df["Pay Type"].isin(pay_types)]
    if not show_closed and "Status" in df.columns:
        df = active_repair_orders(df)
    return df


def render_alerts(alerts: pd.DataFrame) -> None:
    if alerts.empty:
        st.success("No open exceptions found for the current data set.")
        return

    display = alerts.copy()
    display["Priority"] = display["Priority"].map(badge_priority)
    st.markdown(display.to_html(escape=False, index=False), unsafe_allow_html=True)
    st.download_button(
        "Download exception queue CSV",
        alerts.to_csv(index=False).encode("utf-8"),
        file_name="service_exception_queue.csv",
        mime="text/csv",
    )


def main() -> None:
    style_page()
    st.markdown(f"<div class='hero'><h1>{APP_NAME}</h1><p>{APP_SUBTITLE}</p></div>", unsafe_allow_html=True)

    source, source_name = load_source()
    data = load_dealership_workbook(source)

    for warning in data.warnings:
        st.warning(warning)

    selected_advisors, selected_statuses, selected_pay_types, show_closed = filter_panel(data.repair_orders)
    filtered_ro = apply_filters(data.repair_orders, selected_advisors, selected_statuses, selected_pay_types, show_closed)
    alerts = build_alerts(filtered_ro, data.parts_delays, data.declined_services, today=date.today())
    kpis = calculate_kpis(filtered_ro, data.parts_delays, data.declined_services, alerts, today=date.today())

    st.caption(f"Source: {source_name} • Loaded {len(data.repair_orders):,} repair orders, {len(data.parts_delays):,} parts delays, {len(data.declined_services):,} declined-service records")
    render_kpis(kpis)

    tab_overview, tab_alerts, tab_advisors, tab_techs, tab_parts, tab_declined, tab_data = st.tabs([
        "Executive Overview",
        "Exception Queue",
        "Advisor Desk",
        "Technician Capacity",
        "Parts Delays",
        "Declined Services",
        "Data",
    ])

    with tab_overview:
        left, right = st.columns([1, 1])
        with left:
            st.subheader("RO Status Mix")
            status_df = status_summary(filtered_ro)
            if not status_df.empty:
                fig = px.bar(status_df, x="Status", y="Count", text="Count", title="Active Repair Orders by Status")
                fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=50, b=10))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No repair orders match the current filters.")
        with right:
            st.subheader("Alert Priority Mix")
            if not alerts.empty:
                priority_df = alerts.groupby("Priority").size().rename("Count").reset_index()
                fig = px.pie(priority_df, names="Priority", values="Count", hole=.45, title="Open Exceptions by Priority")
                fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.success("No current alerts.")

        st.subheader("Top Open Repair Orders")
        columns = [c for c in ["RO Number", "Customer", "Vehicle", "Advisor", "Technician", "Status", "Open Date", "Promise Date", "Estimate Amount", "Customer Updated", "Comeback"] if c in filtered_ro.columns]
        st.dataframe(filtered_ro[columns].head(25), use_container_width=True, hide_index=True)

    with tab_alerts:
        st.subheader("Exception Queue")
        st.write("This is the manager action list. It flags aging ROs, missed promise dates, customer-update gaps, comeback risk, parts ETA misses, and declined-service follow-ups.")
        render_alerts(alerts)

    with tab_advisors:
        st.subheader("Advisor Workload and Coaching View")
        advisor_df = advisor_summary(filtered_ro, alerts)
        if not advisor_df.empty:
            formatted = advisor_df.copy()
            formatted["Estimate_Total"] = formatted["Estimate_Total"].map(money)
            formatted["Avg_RO_Value"] = formatted["Avg_RO_Value"].map(money)
            formatted["Customer_Update_Rate"] = formatted["Customer_Update_Rate"].map(percent)
            st.dataframe(formatted, use_container_width=True, hide_index=True)
            fig = px.bar(advisor_df, x="Advisor", y=["Active_ROs", "Open_Alerts"], barmode="group", title="Advisor Active ROs vs Alerts")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No advisor data available.")

    with tab_techs:
        st.subheader("Technician Capacity")
        tech_df = technician_summary(filtered_ro)
        if not tech_df.empty:
            formatted = tech_df.copy()
            formatted["Efficiency"] = formatted["Efficiency"].map(percent)
            st.dataframe(formatted, use_container_width=True, hide_index=True)
            fig = px.bar(tech_df, x="Technician", y=["Hours_Sold", "Hours_Flagged"], barmode="group", title="Technician Sold vs Flagged Hours")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No technician data available.")

    with tab_parts:
        st.subheader("Parts Delay Tracker")
        if data.parts_delays.empty:
            st.info("No parts-delay data loaded.")
        else:
            st.dataframe(data.parts_delays, use_container_width=True, hide_index=True)
            st.download_button("Download parts delays CSV", data.parts_delays.to_csv(index=False).encode("utf-8"), "parts_delays.csv", "text/csv")

    with tab_declined:
        st.subheader("Declined Services Follow-Up")
        if data.declined_services.empty:
            st.info("No declined-service data loaded.")
        else:
            st.dataframe(data.declined_services, use_container_width=True, hide_index=True)
            st.download_button("Download declined services CSV", data.declined_services.to_csv(index=False).encode("utf-8"), "declined_services.csv", "text/csv")

    with tab_data:
        st.subheader("Raw Repair Order Data")
        st.dataframe(filtered_ro, use_container_width=True, hide_index=True)
        st.download_button("Download filtered repair orders CSV", filtered_ro.to_csv(index=False).encode("utf-8"), "filtered_repair_orders.csv", "text/csv")


if __name__ == "__main__":
    main()
