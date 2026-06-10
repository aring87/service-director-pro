# Service Director Command Center

A polished Streamlit MVP for auto dealership service leadership. The app turns simple dealership exports into a manager-ready command center for repair order flow, advisor workload, technician capacity, parts delays, declined-service follow-up, and exception management.

This is designed as a realistic business demo: it does **not** replace a DMS such as CDK, Reynolds, Tekion, Dealertrack, or an OEM tool. It sits above exported reports and answers the question:

> What needs the Service Director's attention today?

## Features

- Executive KPI bar
- Operational health score
- Active repair order tracking
- Advisor workload and coaching view
- Technician sold vs flagged hours
- Parts-delay tracker
- Declined-service follow-up tracker
- Exception queue with recommended actions
- CSV export buttons for filtered ROs, alerts, parts delays, and declined services
- Demo workbook included
- GitHub and Streamlit Community Cloud ready

## Folder structure

```text
service_director_pro/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   └── config.toml
├── config/
│   └── app_config.py
├── core/
│   ├── data_loader.py
│   ├── metrics.py
│   └── rules.py
├── demo_data/
│   └── service_director_demo.xlsx
└── docs/
    └── data_dictionary.md
```

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL Streamlit prints, usually:

```text
http://localhost:8501
```

## Workbook format

The app expects an Excel workbook with these sheets:

- `Repair_Orders`
- `Parts_Delays`
- `Declined_Services`

A fake demo workbook is included at:

```text
demo_data/service_director_demo.xlsx
```

See `docs/data_dictionary.md` for column definitions.

## Deploy to Streamlit Community Cloud

1. Push this folder to a GitHub repo.
2. Go to Streamlit Community Cloud.
3. Select your repo.
4. Set the main file path to:

```text
app.py
```

5. Deploy.

Your GitHub repo can be private. You can keep the app private or make the Streamlit app public for demo sharing.

## Recommended GitHub repo name

```text
service-director-command-center
```

## Initial git commands

```powershell
git init
git add .
git commit -m "Initial Service Director Command Center MVP"
git branch -M main
git remote add origin https://github.com/aring87/service-director-command-center.git
git push -u origin main
```

## Product direction

Strong next modules:

1. Notes and action ownership per alert
2. SQLite database for persistent alert status
3. Customer follow-up call queue
4. Advisor scorecard export
5. DMS export mapping wizard
6. Multi-store rollup dashboard
7. Login and role-based views
