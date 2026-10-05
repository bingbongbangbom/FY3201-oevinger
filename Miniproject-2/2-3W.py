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


if not CLIENT_ID:
    raise ValueError(
        "CLIENTID is missing. Run this first in PowerShell: "
        "$env:CLIENTID='your Client ID'"
    )


# =========================
# RETRIEVE WIND DATA
# =========================

def get_wind_data(start_date, end_date):

    params = {
        "sources": STATION,
        "referencetime": f"{start_date}/{end_date}",
        "elements": "mean(wind_speed P1D)"
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
                    "wind": observation["value"]
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
        f"Retrieving wind data for {year}..."
    )

    data = get_wind_data(
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
        "No wind data was found. Check the Client ID, "
        "station, and whether the wind element is available "
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
# 1. NORMAL MONTHLY WIND SPEED
# =========================

normal_wind = (
    df.groupby("month")["wind"]
    .mean()
)

normal_wind.index = [
    month_names[m]
    for m in normal_wind.index
]


plt.figure(figsize=(10, 5))

normal_wind.plot(
    kind="bar"
)

plt.title(
    "Normal Monthly Wind Speed in Tromsø, 1991–2021"
)

plt.xlabel("Month")

plt.ylabel(
    "Average Wind Speed (m/s)"
)

plt.xticks(
    rotation=0
)

plt.tight_layout()

plt.savefig(
    "tromso_normal_wind_1991_2021.png",
    dpi=300
)

plt.show()


# =========================
# 2. WIND SPEED OVER TIME
# =========================

annual_wind = (
    df.groupby("year")["wind"]
    .mean()
)


plt.figure(figsize=(10, 5))

plt.plot(
    annual_wind.index,
    annual_wind.values
)

plt.title(
    "Average Wind Speed in Tromsø, 1991–2021"
)

plt.xlabel("Year")

plt.ylabel(
    "Average Wind Speed (m/s)"
)

plt.grid(
    True,
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    "tromso_wind_over_time.png",
    dpi=300
)

plt.show()


# =========================
# 3. VARIATION BETWEEN MONTHS
# =========================

plt.figure(figsize=(10, 6))

df.boxplot(
    column="wind",
    by="month"
)

plt.title(
    "Variation in Wind Speed by Month in Tromsø, 1991–2021"
)

plt.suptitle("")

plt.xlabel("Month")

plt.ylabel(
    "Wind Speed (m/s)"
)

plt.tight_layout()

plt.savefig(
    "tromso_wind_variation_months.png",
    dpi=300
)

plt.show()


# =========================
# PRINT RESULTS
# =========================

monthly_results = (
    df.groupby("month")["wind"]
    .mean()
    .sort_values(
        ascending=False
    )
)


print(
    "\nAverage wind speed per month:"
)

print(
    monthly_results
)

print(
    "\nKey results:"
)


most_windy = (
    monthly_results.idxmax()
)

least_windy = (
    monthly_results.idxmin()
)


print(
    f"Windiest month: "
    f"{month_names[most_windy]} "
    f"({monthly_results.max():.2f} m/s)"
)


print(
    f"Calmest month: "
    f"{month_names[least_windy]} "
    f"({monthly_results.min():.2f} m/s)"
)


print(
    f"Average wind speed for the entire period: "
    f"{df['wind'].mean():.2f} m/s"
)