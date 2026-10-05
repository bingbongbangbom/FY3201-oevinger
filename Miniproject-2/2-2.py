import os
import requests
import pandas as pd
import matplotlib.pyplot as plt


# ==========================================
# SETTINGS
# ==========================================

CLIENT_ID = os.getenv("CLIENTID")

STATION = "SN90450"       # Tromsø / Vervarslinga

START_YEAR = 1991
END_YEAR = 2021

COMPARISON_START_YEAR = 1970
COMPARISON_END_YEAR = 2020

YEAR_2025 = 2025

API_URL = "https://frost.met.no/observations/v0.jsonld"


# ==========================================
# CHECK CLIENT ID
# ==========================================

if not CLIENT_ID:
    print("CLIENTID was not found.")
    print("Run this in PowerShell first:")
    print('$env:CLIENTID="YOUR_CLIENT_ID"')
    exit()


# ==========================================
# FUNCTION FOR RETRIEVING PRECIPITATION DATA
# ==========================================

def get_precipitation(start_date, end_date):

    params = {
        "sources": STATION,
        "referencetime": f"{start_date}/{end_date}",
        "elements": "sum(precipitation_amount P1D)"
    }

    response = requests.get(
        API_URL,
        params=params,
        auth=(CLIENT_ID, ""),
        timeout=120
    )

    if response.status_code != 200:
        print("Error from Frost API:")
        print(response.text)
        return pd.DataFrame()

    data = response.json().get("data", [])

    rows = []

    for item in data:

        timestamp = item.get("referenceTime")

        observations = item.get("observations", [])

        for observation in observations:

            value = observation.get("value")

            if timestamp is not None and value is not None:

                rows.append({
                    "date": timestamp,
                    "precipitation": value
                })

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    df["date"] = pd.to_datetime(df["date"])
    df["precipitation"] = pd.to_numeric(
        df["precipitation"]
    )

    return df


# ==========================================
# RETRIEVE DATA FOR 1991–2021
# ==========================================

all_data = []

for year in range(START_YEAR, END_YEAR + 1):

    print(f"Retrieving data for {year}...")

    start = f"{year}-01-01"
    end = f"{year + 1}-01-01"

    df = get_precipitation(start, end)

    if not df.empty:

        all_data.append(df)

        print(
            f"  Found {len(df)} measurements."
        )

    else:

        print("  No data found.")


# ==========================================
# STOP IF NO DATA
# ==========================================

if not all_data:

    print()
    print("No data was found.")
    print("Check CLIENTID and station.")
    exit()


# Combine all years

df = pd.concat(
    all_data,
    ignore_index=True
)

df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month


print()
print(
    f"Total number of measurements: {len(df)}"
)


# ==========================================
# 1. NORMAL MONTHLY PRECIPITATION
# ==========================================

normal_month = (
    df.groupby("month")["precipitation"]
    .mean()
)

month_names = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]


plt.figure(figsize=(10, 5))

plt.bar(
    month_names,
    normal_month
)

plt.title(
    "Normal Monthly Precipitation in Tromsø (1991–2021)"
)

plt.xlabel("Month")
plt.ylabel("Precipitation (mm)")

plt.tight_layout()

plt.savefig(
    "tromso_normal_precipitation_1991_2021.png",
    dpi=300
)

plt.show()


# ==========================================
# 2. ANNUAL PRECIPITATION OVER TIME
# ==========================================

annual_precipitation = (
    df.groupby("year")["precipitation"]
    .sum()
)


plt.figure(figsize=(11, 5))

plt.plot(
    annual_precipitation.index,
    annual_precipitation.values,
    marker="o"
)

plt.title(
    "Annual Precipitation in Tromsø (1991–2021)"
)

plt.xlabel("Year")
plt.ylabel("Precipitation (mm)")

plt.grid(
    True,
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    "tromso_precipitation_over_time.png",
    dpi=300
)

plt.show()


# ==========================================
# 3. DISTRIBUTION OF MONTHLY PRECIPITATION
# ==========================================

monthly_precipitation = (
    df.groupby(
        ["year", "month"]
    )["precipitation"]
    .sum()
    .reset_index()
)


plt.figure(figsize=(10, 5))

plt.hist(
    monthly_precipitation["precipitation"],
    bins=20
)

plt.title(
    "Distribution of Monthly Precipitation in Tromsø (1991–2021)"
)

plt.xlabel("Precipitation per Month (mm)")
plt.ylabel("Number of Months")

plt.tight_layout()

plt.savefig(
    "tromso_precipitation_distribution.png",
    dpi=300
)

plt.show()


# ==========================================
# 4. 2025 VS. 1970–2020
# ==========================================

print()
print("=" * 60)
print("2025 VS. 1970–2020 PRECIPITATION COMPARISON")
print("=" * 60)


# ------------------------------------------
# Retrieve historical data: 1970–2020
# ------------------------------------------

comparison_data = []

for year in range(
    COMPARISON_START_YEAR,
    COMPARISON_END_YEAR + 1
):

    print(
        f"Retrieving comparison data for {year}..."
    )

    start = f"{year}-01-01"
    end = f"{year + 1}-01-01"

    comparison_df = get_precipitation(
        start,
        end
    )

    if not comparison_df.empty:

        comparison_data.append(
            comparison_df
        )


if not comparison_data:

    print(
        "No comparison data was found."
    )

else:

    comparison_df = pd.concat(
        comparison_data,
        ignore_index=True
    )

    comparison_df["year"] = (
        comparison_df["date"].dt.year
    )

    comparison_df["month"] = (
        comparison_df["date"].dt.month
    )


    # ------------------------------------------
    # Calculate monthly historical average
    # ------------------------------------------

    historical_monthly = (
        comparison_df
        .groupby(
            ["year", "month"]
        )["precipitation"]
        .sum()
        .reset_index()
        .groupby("month")["precipitation"]
        .mean()
    )


    # ------------------------------------------
    # Retrieve precipitation data for 2025
    # ------------------------------------------

    print()
    print("Retrieving precipitation data for 2025...")

    precipitation_2025 = get_precipitation(
        "2025-01-01",
        "2026-01-01"
    )


    if precipitation_2025.empty:

        print(
            "No precipitation data was found for 2025."
        )

    else:

        precipitation_2025["month"] = (
            precipitation_2025["date"].dt.month
        )


        # ------------------------------------------
        # Calculate monthly precipitation for 2025
        # ------------------------------------------

        monthly_2025 = (
            precipitation_2025
            .groupby("month")["precipitation"]
            .sum()
        )


        # ------------------------------------------
        # Create comparison plot
        # ------------------------------------------

        plt.figure(figsize=(12, 7))

        plt.plot(
            month_names,
            monthly_2025,
            marker="o",
            linewidth=3,
            label="2025"
        )

        plt.plot(
            month_names,
            historical_monthly,
            marker="o",
            linestyle="--",
            linewidth=3,
            label="1970–2020 average"
        )

        plt.title(
            "Monthly Precipitation in Tromsø: "
            "2025 vs. 1970–2020 Average",
            fontsize=16
        )

        plt.xlabel(
            "Month",
            fontsize=12
        )

        plt.ylabel(
            "Precipitation (mm)",
            fontsize=12
        )

        plt.grid(
            True,
            alpha=0.3
        )

        plt.legend()

        plt.tight_layout()

        plt.savefig(
            "tromso_precipitation_2025_vs_1970_2020.png",
            dpi=300,
            bbox_inches="tight"
        )

        plt.show()


# ==========================================
# 2. GJENNOMSNITTLIG ÅRSNEDBØR
# ==========================================

# Total nedbør per år
annual_precipitation = (
    df.groupby("year")["precipitation"]
    .sum()
)

# Gjennomsnittlig årsnedbør for hele perioden
average_annual_precipitation = (
    annual_precipitation.mean()
)

print()
print("Gjennomsnittlig årsnedbør 1991–2021:")
print(f"{average_annual_precipitation:.1f} mm")


# ==========================================
# LAG GRAF
# ==========================================

plt.figure(figsize=(12, 6))

# Nedbør hvert år
plt.plot(
    annual_precipitation.index,
    annual_precipitation.values,
    marker="o",
    linewidth=2,
    label="Årsnedbør"
)

# Gjennomsnittet for hele perioden
plt.axhline(
    average_annual_precipitation,
    linestyle="--",
    linewidth=2,
    label=f"Gjennomsnitt 1991–2021 ({average_annual_precipitation:.1f} mm)"
)

plt.title(
    "Årlig nedbør i Tromsø (1991–2021)",
    fontsize=16
)

plt.xlabel(
    "År",
    fontsize=12
)

plt.ylabel(
    "Nedbør (mm)",
    fontsize=12
)

plt.grid(
    True,
    alpha=0.3
)

plt.legend()

plt.tight_layout()

plt.savefig(
    "tromso_annual_precipitation_average.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ==========================================
# RESULTS
# ==========================================

most_precipitation = (
    normal_month.idxmax()
)

least_precipitation = (
    normal_month.idxmin()
)


print()
print("================================")
print("RESULTS")
print("================================")


print(
    f"Highest normal precipitation: "
    f"{month_names[most_precipitation - 1]} "
    f"({normal_month[most_precipitation]:.1f} mm)"
)


print(
    f"Lowest normal precipitation: "
    f"{month_names[least_precipitation - 1]} "
    f"({normal_month[least_precipitation]:.1f} mm)"
)


print()

print(
    f"Average annual precipitation: "
    f"{annual_precipitation.mean():.1f} mm"
)


print()

print("Finished!")
print("Four figures have been saved in the project folder.")