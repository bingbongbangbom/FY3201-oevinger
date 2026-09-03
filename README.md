# Miniprosjekter FY3201 Atmosfærefysikk og klimaendringer

Mini-projects for the course FY3201 (Atmospheric Physics and Climate Change). Each mini-project lives in its own top-level folder; this README gives a short overview of what's in each one. As more mini-projects are added, this file can be generalized and per-project detail moved into a `README.md` inside each project folder.

## Miniproject-1

Analysis of global temperature and greenhouse-gas records (Berkeley Earth land+ocean temperature, NOAA CO₂/CH₄, and population/obesity datasets). The five numbered notebooks are the core deliverable; each is commented in detail, so read the notebooks themselves for step-by-step explanations — this is just a map of what each one does.

| Notebook | What it does |
|---|---|
| `part_1.ipynb` | Loads a monthly anomaly series, removes the seasonal cycle to get monthly anomalies, and plots them with a 95% confidence band and a 12-month moving average. |
| `part_2_Q1.ipynb` | Placeholder — not yet implemented. |
| `part_2_Q2.ipynb` | Fits the 1970–2024 global temperature anomaly with (a) two separate linear trends (1970–1997 vs. 1998–2024) to compare warming rates, and (b) a single quadratic fit to test whether warming is accelerating, with confidence intervals and a significance test on the curvature term. |
| `part_2_Q3.ipynb` | Downloads temperature (Berkeley Earth), CO₂ and CH₄ (NOAA GML), and world population (Our World in Data) directly from source URLs, harmonises them to annual values, and computes Pearson correlations and scatter plots of temperature against each driver. |
| `part_2_Q4.ipynb` | Correlates Afghanistan's adult obesity rate against the global temperature anomaly over the same years — a worked example of a spurious correlation (two unrelated trends that still fit well statistically). |

**Data & outputs:** `data/Land_and_Ocean_complete.txt` is the raw Berkeley Earth series used by most notebooks. `harmonised_temperature_CO2_CH4_population.csv`, `correlation_results.csv`, and the `Q2_*.png` figures are generated outputs saved by `part_2_Q2.ipynb`/`part_2_Q3.ipynb` when they are run.
