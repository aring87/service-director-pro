"""Data loading and normalization utilities."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

import pandas as pd

from config.app_config import REQUIRED_REPAIR_ORDER_COLUMNS, SHEETS


@dataclass(frozen=True)
class DealershipData:
    repair_orders: pd.DataFrame
    parts_delays: pd.DataFrame
    declined_services: pd.DataFrame
    warnings: list[str]


def _read_sheet(source: str | Path | BinaryIO, sheet_name: str) -> pd.DataFrame:
    try:
        return pd.read_excel(source, sheet_name=sheet_name)
    except ValueError:
        return pd.DataFrame()


def _normalize_dates(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    df = df.copy()
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def _normalize_booleans(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    df = df.copy()
    truthy = {"yes", "true", "1", "y", "x"}
    for col in columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.lower().isin(truthy)
    return df


def load_dealership_workbook(source: str | Path | BinaryIO) -> DealershipData:
    """Load the workbook expected by this app.

    The app is intentionally export-friendly: it accepts a workbook with a few
    simple sheets instead of requiring a direct DMS integration.
    """
    warnings: list[str] = []

    ro = _read_sheet(source, SHEETS["repair_orders"])
    parts = _read_sheet(source, SHEETS["parts_delays"])
    declined = _read_sheet(source, SHEETS["declined_services"])

    missing = [col for col in REQUIRED_REPAIR_ORDER_COLUMNS if col not in ro.columns]
    if missing:
        warnings.append("Repair_Orders is missing required columns: " + ", ".join(missing))

    ro = _normalize_dates(ro, ["Open Date", "Promise Date", "Closed Date", "Last Customer Contact"])
    parts = _normalize_dates(parts, ["ETA", "Order Date", "Last Customer Update"])
    declined = _normalize_dates(declined, ["Declined Date", "Follow Up Date"])

    ro = _normalize_booleans(ro, ["Customer Updated", "Comeback"])
    parts = _normalize_booleans(parts, ["Customer Updated"])
    declined = _normalize_booleans(declined, ["Contacted"])

    numeric_cols = ["Labor Hours Sold", "Labor Hours Flagged", "Estimate Amount"]
    for col in numeric_cols:
        if col in ro.columns:
            ro[col] = pd.to_numeric(ro[col], errors="coerce").fillna(0)

    for col in ["Days Waiting", "Part Cost"]:
        if col in parts.columns:
            parts[col] = pd.to_numeric(parts[col], errors="coerce").fillna(0)

    for col in ["Declined Amount"]:
        if col in declined.columns:
            declined[col] = pd.to_numeric(declined[col], errors="coerce").fillna(0)

    return DealershipData(ro, parts, declined, warnings)
