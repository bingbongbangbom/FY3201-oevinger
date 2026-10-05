import os
import requests
import pandas as pd
import matplotlib.pyplot as plt


# =========================
# SETTINGS
# =========================

CLIENT_ID = os.getenv("CLIENTID")

STATION = "SN90450"       # Tromsø / Vervarslinga
START_YEAR = 1991
END_YEAR = 2021

API_URL = "https://frost.met.no/observations/v0.jsonld"


# =========================
# CHECK CLIENT ID
# =========================

if not CLIENT_ID:
    raise ValueError(
        "CLIENTID is missing. Run this first in PowerShell: "
        "$env:CLIENTID='your Client ID'"
    )


# =========================
# RETRIEVE PRESSURE DATA
# =========================

def get_pressure_data(start_date, end_date):

    params = {
        "sources": STATION,
        "referencetime": f"{start_date}/{end_date}",
        "elements": "mean(surface_air_pressure P1D)"
    }

    response = requests.get(
        API_URL,
        params=params,
        auth=(CLIENT_ID, ""),
        timeout=120
    )

    if response.status_code != 200:
        print("Error:", response.status_code)
        print(response.text)
        return []

    data = response.json()

    results = []

    for item in data.get("data", []):

        for observation in item.get(
            "observations", []
        ):

            if "value" in observation:

                results.append({
                    "date": item["referenceTime"],
                    "pressure": observation["value"]
                })

    return results


# =========================
# RETRIEVE ALL YEARS
# =========================

all_data = []

for year in range(
    START_YEAR,
    END_YEAR + 1
):

    start = f"{year}-01-01"
    end = f"{year + 1}-01-01"

    print(
        f"Retrieving pressure data for {year}..."
    )

    data = get_pressure_data(
        start,
        end
    )

    all_data.extend(data)


# =========================
# CREATE DATAFRAME
# =========================

df = pd.DataFrame(all_data)


if df.empty:

    raise ValueError(
        "No pressure data was found. Check the Client ID, "
        "station, and whether the pressure element is available "
        "for the station."
    )


df["date"] = pd.to_datetime(
    df["date"]
)

df["year"] = df["date"].dt.year

df["month"] = df["date"].dt.month


month_names = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec"
}


# =========================
# 1. NORMAL MONTHLY PRESSURE
# =========================

normal_pressure = (
    df.groupby("month")["pressure"]
    .mean()
)


normal_pressure.index = [
    month_names[m]
    for m in normal_pressure.index
]


plt.figure(figsize=(10, 5))

normal_pressure.plot(
    kind="bar"
)

plt.title(
    "Normal Monthly Atmospheric Pressure in Tromsø, 1991–2021"
)

plt.xlabel("Month")

plt.ylabel(
    "Average Pressure (hPa)"
)

plt.xticks(
    rotation=0
)

plt.tight_layout()

plt.savefig(
    "tromso_normal_pressure_1991_2021.png",
    dpi=300
)

plt.show()


# =========================
# 2. PRESSURE OVER TIME
# =========================

annual_pressure = (
    df.groupby("year")["pressure"]
    .mean()
)


plt.figure(figsize=(11, 5))

plt.plot(
    annual_pressure.index,
    annual_pressure.values,
    marker="o"
)

plt.title(
    "Average Atmospheric Pressure in Tromsø, 1991–2021"
)

plt.xlabel("Year")

plt.ylabel(
    "Average Pressure (hPa)"
)

plt.grid(
    True,
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    "tromso_pressure_over_time.png",
    dpi=300
)

plt.show()


# =========================
# 3. PRESSURE VARIATION BY MONTH
# =========================

plt.figure(figsize=(10, 6))

df.boxplot(
    column="pressure",
    by="month"
)

plt.title(
    "Variation in Atmospheric Pressure by Month in Tromsø, 1991–2021"
)

plt.suptitle("")

plt.xlabel("Month")

plt.ylabel(
    "Atmospheric Pressure (hPa)"
)

plt.xticks(
    range(1, 13),
    [
        month_names[i]
        for i in range(1, 13)
    ]
)

plt.tight_layout()

plt.savefig(
    "tromso_pressure_variation_months.png",
    dpi=300
)

plt.show()


# =========================
# 4. MONTHLY PRESSURE RANGE
# =========================

monthly_pressure = (
    df.groupby("month")["pressure"]
    .agg(
        mean="mean",
        minimum="min",
        maximum="max"
    )
)


plt.figure(figsize=(11, 6))

plt.plot(
    month_names.values(),
    monthly_pressure["mean"],
    marker="o",
    linewidth=3,
    label="Average"
)

plt.fill_between(
    month_names.values(),
    monthly_pressure["minimum"],
    monthly_pressure["maximum"],
    alpha=0.2,
    label="Observed range"
)

plt.title(
    "Monthly Atmospheric Pressure Range in Tromsø, 1991–2021"
)

plt.xlabel("Month")

plt.ylabel(
    "Atmospheric Pressure (hPa)"
)

plt.grid(
    True,
    alpha=0.3
)

plt.legend()

plt.tight_layout()

plt.savefig(
    "tromso_pressure_monthly_range.png",
    dpi=300
)

plt.show()


# =========================
# RESULTS
# =========================

monthly_results = (
    df.groupby("month")["pressure"]
    .mean()
    .sort_values(
        ascending=False
    )
)


print()
print("================================")
print("PRESSURE RESULTS")
print("================================")


print(
    "\nAverage atmospheric pressure per month:"
)

for month, value in monthly_results.items():

    print(
        f"{month_names[month]}: "
        f"{value:.1f} hPa"
    )


highest_pressure_month = (
    monthly_results.idxmax()
)

lowest_pressure_month = (
    monthly_results.idxmin()
)


print()

print(
    f"Highest average pressure: "
    f"{month_names[highest_pressure_month]} "
    f"({monthly_results.max():.1f} hPa)"
)


print(
    f"Lowest average pressure: "
    f"{month_names[lowest_pressure_month]} "
    f"({monthly_results.min():.1f} hPa)"
)


print()

print(
    f"Average atmospheric pressure for the entire period: "
    f"{df['pressure'].mean():.1f} hPa"
)


print()

print("Finished!")

print(
    "Four figures have been saved in the project folder."
)