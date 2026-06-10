# Data Dictionary

## Repair_Orders

| Column | Description |
|---|---|
| RO Number | Repair order identifier |
| Customer | Demo customer name |
| Vehicle | Vehicle year/make/model |
| VIN Last 8 | Last 8 characters of demo VIN |
| Advisor | Service advisor assigned to the RO |
| Technician | Technician assigned to the RO |
| Status | Current service workflow status |
| Pay Type | Customer Pay, Warranty, Internal, or Maintenance Plan |
| Open Date | Date RO was opened |
| Promise Date | Date promised to customer |
| Closed Date | Close date if closed |
| Labor Hours Sold | Sold labor hours |
| Labor Hours Flagged | Flagged/booked labor hours |
| Estimate Amount | Current estimate or RO value |
| Customer Updated | Yes/No indicator that customer has been updated |
| Last Customer Contact | Last recorded customer contact date |
| Comeback | Yes/No comeback indicator |
| Concern | Customer concern / reason for visit |

## Parts_Delays

| Column | Description |
|---|---|
| RO Number | Related repair order |
| Customer | Customer name |
| Advisor | Service advisor |
| Part Number | Demo part number |
| Part Description | Description of delayed part |
| Vendor | Vendor or source |
| Order Date | Date part was ordered |
| ETA | Expected arrival date |
| Days Waiting | Number of days waiting |
| Part Cost | Demo part cost |
| Customer Updated | Whether customer has been updated |
| Last Customer Update | Last customer update date |

## Declined_Services

| Column | Description |
|---|---|
| RO Number | Related repair order |
| Customer | Customer name |
| Advisor | Service advisor |
| Vehicle | Vehicle year/make/model |
| Service Declined | Service declined by customer |
| Declined Amount | Estimated value of declined service |
| Declined Date | Date service was declined |
| Follow Up Date | Date advisor should follow up |
| Contacted | Whether follow-up contact has occurred |
| Safety Related | Whether the declined item is safety-related |
