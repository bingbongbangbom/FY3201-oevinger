import os
import requests
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# SETTINGS
# ============================================================

STATION = "SN90450"          # Tromsø
YEAR = 2025

HIST_START = 1991
HIST_END = 2021

API_URL = "https://frost.met.no/observations/v0.jsonld"


# ============================================================
# MET NORWAY CLIENT ID
# ============================================================

CLIENT_ID = os.getenv("CLIENTID")

if not CLIENT_ID:
    raise RuntimeError(
        "CLIENTID is missing.\n\n"
        "Run this in PowerShell first:\n"
        '$env:CLIENTID="YOUR_CLIENT_ID"'
    )


# ============================================================
# FUNCTION FOR RETRIEVING DATA
# ============================================================

def hent_data(start_date, end_date):

    print(f"Retrieving data from {start_date} to {end_date}...")

    params = {
        "sources": STATION,

        "referencetime":
            f"{start_date}/{end_date}",

        "elements":
            "min(air_temperature P1D),"
            "max(air_temperature P1D),"
            "mean(air_temperature P1D)",

        "timeoffsets": "default",

        "levels": "default",

        "qualities": "0,1,2,3,4"
    }

    response = requests.get(
        API_URL,
        params=params,
        auth=(CLIENT_ID, ""),
        timeout=120
    )

    if response.status_code != 200:
        print(response.text)

        raise RuntimeError(
            f"MET API error: {response.status_code}"
        )

    result = response.json()

    rows = []

    for item in result.get("data", []):

        row = {
            "date": pd.to_datetime(
                item["referenceTime"]
            ),
            "min_temp": None,
            "max_temp": None,
            "mean_temp": None
        }

        for observation in item["observations"]:

            element = observation["elementId"]
            value = observation["value"]

            if element == "min(air_temperature P1D)":
                row["min_temp"] = float(value)

            elif element == "max(air_temperature P1D)":
                row["max_temp"] = float(value)

            elif element == "mean(air_temperature P1D)":
                row["mean_temp"] = float(value)

        rows.append(row)

    df = pd.DataFrame(rows)

    if df.empty:
        raise RuntimeError(
            "No temperature data was found."
        )

    df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values("date")

    return df


# ============================================================
# START
# ============================================================

print()
print("=" * 65)
print("TEMPERATURE ANALYSIS FOR TROMSØ")
print("=" * 65)
print()


# ============================================================
# RETRIEVE HISTORICAL DATA
# ============================================================

print("1. Retrieving historical data from 1991–2021...")

historical = hent_data(
    f"{HIST_START}-01-01",
    f"{HIST_END + 1}-01-01"
)

print(
    f"   Retrieved {len(historical)} observations."
)

print()


# ============================================================
# RETRIEVE DATA FOR 2025
# ============================================================

print("2. Retrieving data for 2025...")

data_2025 = hent_data(
    "2025-01-01",
    "2026-01-01"
)

print(
    f"   Retrieved {len(data_2025)} observations."
)

print()


# ============================================================
# CREATE MONTH
# ============================================================

historical["month"] = (
    historical["date"].dt.month
)

data_2025["month"] = (
    data_2025["date"].dt.month
)


# ============================================================
# CALCULATE MONTHLY AVERAGES
# ============================================================

print("3. Calculating monthly averages...")


# 2025
monthly_2025 = (
    data_2025
    .groupby("month")
    .agg(
        min_2025=("min_temp", "mean"),
        mean_2025=("mean_temp", "mean"),
        max_2025=("max_temp", "mean")
    )
    .reset_index()
)


# 1991–2021
monthly_normal = (
    historical
    .groupby("month")
    .agg(
        min_normal=("min_temp", "mean"),
        mean_normal=("mean_temp", "mean"),
        max_normal=("max_temp", "mean")
    )
    .reset_index()
)


# ============================================================
# MERGE THE DATA
# ============================================================

monthly = pd.merge(
    monthly_2025,
    monthly_normal,
    on="month"
)


# ============================================================
# MONTH NAMES
# ============================================================

months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec"
]

monthly["month_name"] = monthly["month"].apply(
    lambda x: months[x - 1]
)


# ============================================================
# DISPLAY TABLE
# ============================================================

print()
print("=" * 95)
print("MONTHLY TEMPERATURES IN TROMSØ")
print("2025 COMPARED WITH 1991–2021")
print("=" * 95)
print()

print(
    monthly[
        [
            "month_name",
            "min_2025",
            "min_normal",
            "mean_2025",
            "mean_normal",
            "max_2025",
            "max_normal"
        ]
    ]
    .round(1)
    .to_string(index=False)
)

print()


# ============================================================
# PLOT 1 – MAXIMUM TEMPERATURE
# ============================================================

plt.figure(figsize=(12, 7))

plt.plot(
    monthly["month_name"],
    monthly["max_2025"],
    marker="o",
    linewidth=3,
    label="2025"
)

plt.plot(
    monthly["month_name"],
    monthly["max_normal"],
    marker="o",
    linestyle="--",
    linewidth=3,
    label="1991–2021"
)

plt.title(
    "Maximum Temperature in Tromsø",
    fontsize=16
)

plt.xlabel(
    "Month",
    fontsize=12
)

plt.ylabel(
    "Temperature (°C)",
    fontsize=12
)

plt.grid(
    True,
    alpha=0.3
)

plt.legend()

plt.tight_layout()

plt.savefig(
    "tromso_maximum_2025_vs_1991_2021.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# PLOT 2 – MINIMUM TEMPERATURE
# ============================================================

plt.figure(figsize=(12, 7))

plt.plot(
    monthly["month_name"],
    monthly["min_2025"],
    marker="o",
    linewidth=3,
    label="2025"
)

plt.plot(
    monthly["month_name"],
    monthly["min_normal"],
    marker="o",
    linestyle="--",
    linewidth=3,
    label="1991–2021"
)

plt.title(
    "Minimum Temperature in Tromsø",
    fontsize=16
)

plt.xlabel(
    "Month",
    fontsize=12
)

plt.ylabel(
    "Temperature (°C)",
    fontsize=12
)

plt.grid(
    True,
    alpha=0.3
)

plt.legend()

plt.tight_layout()

plt.savefig(
    "tromso_minimum_2025_vs_1991_2021.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# PLOT 3 – MEAN TEMPERATURE
# ============================================================

plt.figure(figsize=(12, 7))

plt.plot(
    monthly["month_name"],
    monthly["mean_2025"],
    marker="o",
    linewidth=3,
    label="2025"
)

plt.plot(
    monthly["month_name"],
    monthly["mean_normal"],
    marker="o",
    linestyle="--",
    linewidth=3,
    label="1991–2021"
)

plt.title(
    "Mean Temperature in Tromsø",
    fontsize=16
)

plt.xlabel(
    "Month",
    fontsize=12
)

plt.ylabel(
    "Temperature (°C)",
    fontsize=12
)

plt.grid(
    True,
    alpha=0.3
)

plt.legend()

plt.tight_layout()

plt.savefig(
    "tromso_mean_2025_vs_1991_2021.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# FINISHED
# ============================================================

print("=" * 65)
print("THE ANALYSIS IS COMPLETE!")
print("=" * 65)
print()

print("You now have three separate figures:")

print()
print("1. tromso_maximum_2025_vs_1991_2021.png")
print("2. tromso_minimum_2025_vs_1991_2021.png")
print("3. tromso_mean_2025_vs_1991_2021.png")

print()
print("All temperatures are monthly averages.")
print("2025 is compared with the period 1991–2021.")