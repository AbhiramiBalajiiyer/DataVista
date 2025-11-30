---
title: DataVista
emoji: 📊
colorFrom: indigo
colorTo: blue
sdk: streamlit
sdk_version: "1.39.0"
app_file: app.py
pinned: false
---

# DataVista

DataVista is a Streamlit‑based multi‑agent AI data analyst. Upload any CSV and use natural‑language chat to run EDA, generate charts, create time‑series forecasts, and download auto‑generated PPTX reports.

## What it does

- 📂 Upload a tabular dataset (CSV)
- 🔍 Run automated exploratory data analysis (EDA)
- 📊 Create line/bar charts from numeric columns
- 🔮 Forecast future values for a selected metric
- 📑 Export an InsightOps‑style PowerPoint report (EDA + forecast + chart)
- 🧠 Keep session memory and logs for each conversation

## How it works

A Supervisor agent routes user requests to specialist agents:

- `SimpleDataAgent` – quick dataset overview  
- `EDAAgent` – detailed exploratory analysis  
- `ChartAgent` – Matplotlib chart generation  
- `ForecastAgent` – ARIMA/Auto‑ARIMA time‑series forecasting  
- `ReportAgent` – PPTX report creation with `python-pptx`

All of this is wrapped in a three‑column Streamlit UI and deployed on Hugging Face Spaces.
