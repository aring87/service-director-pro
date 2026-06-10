"""Application-level settings for the Service Director Command Center."""

APP_NAME = "Service Director Command Center"
APP_SUBTITLE = "Fixed Ops exception management, advisor workload, technician capacity, and follow-up automation."
DEMO_FILE = "demo_data/service_director_demo.xlsx"

SHEETS = {
    "repair_orders": "Repair_Orders",
    "parts_delays": "Parts_Delays",
    "declined_services": "Declined_Services",
}

REQUIRED_REPAIR_ORDER_COLUMNS = [
    "RO Number",
    "Customer",
    "Vehicle",
    "Advisor",
    "Technician",
    "Status",
    "Pay Type",
    "Open Date",
    "Promise Date",
    "Labor Hours Sold",
    "Labor Hours Flagged",
    "Estimate Amount",
    "Customer Updated",
    "Comeback",
]

STATUS_ORDER = [
    "Checked In",
    "Waiting Diagnosis",
    "Diagnosis Complete",
    "Waiting Approval",
    "Waiting Parts",
    "In Repair",
    "Quality Check",
    "Ready for Pickup",
    "Closed",
]
