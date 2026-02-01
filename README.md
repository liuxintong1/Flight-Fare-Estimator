# Flight Fare Estimator

## ARTIFACT

-  [Deployed Application URL] (<https://liuxintong1-flight-fare-estimator-flight-estimator-a5mxfd.streamlit.app/>)

## TL;DR

- **Problem:** Existing flight pricing tools focus on **current and historical fares** but lack **forward-looking price estimates**, making long-term travel planning difficult.
- **Solution:** This project builds a **Flight Fare Analytics Application** that analyzes **multi-year domestic flight data** to **forecast future fares** using historical trends and seasonality.
- **Key Achievements:** Designed a **custom DataFrame-like data structure**, generated **connecting-flight fares from direct-flight data**, and implemented **projection logic** to estimate prices for **2025–2026**.

---

## Introduction

Airfare prices vary significantly due to **seasonal demand**, **route structure**, and broader **market dynamics**. Most consumer-facing tools rely on real-time scraped prices and short-term historical trends, offering little insight into how fares are likely to evolve. As a result, travelers lack visibility into **future price behavior**, making informed long-term planning challenging.

This project addresses that gap by building a **Flight Fare Analytics Application** that performs **historical analysis and forward projection** on multi-year U.S. domestic flight data. The system computes **year-over-year fare changes**, identifies **consistent seasonal patterns**, and applies **growth-rate-based forecasting** to estimate route-level prices for **2025 and 2026**.

To better reflect real-world travel scenarios, the application also supports **indirect (connecting) routes**, even though the source dataset contains only direct flights. It constructs **valid two-leg connections** by matching flights on **connecting city, year, and quarter**, aggregates **distance and fare totals**, and applies the same **projection logic** used for direct routes.

Backed by a **custom-built data processing layer**—including **CSV parsing**, **row-level filtering**, **group-by operations**, and **join logic**—and exposed through an **interactive FAQ-style interface**, the project demonstrates both **data engineering fundamentals** and **applied analytical modeling** for understanding **historical and future flight fare dynamics**.

# Running the Application Locally

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

Install the required Python packages:

```bash
pip install streamlit plotly
```

## Running the Application

### Step 1: Navigate to the Project Directory

```bash
cd Flight-Fare-Estimator
```

### Step 2: Launch the Streamlit App

```bash
streamlit run Flight_Estimator.py
```

The application will start and automatically open in your default web browser at `http://localhost:8501`.

If the browser doesn't open automatically, you can manually navigate to the URL shown in the terminal output.

## Troubleshooting

### Error: CSV file not found

Ensure `US Airline Flight Routes and Fares 1993-2024.csv` is in the same directory as `Flight_Estimator.py`.

### Error: Module not found

```bash
pip install streamlit plotly
```

### Port Already in Use

Use a different port:

```bash
streamlit run Flight_Estimator.py --server.port 8502
```

