# Connecting Queens: Data-Driven Transit Analysis for Eastern Queens

*Deval Mehta | General Assembly Data Science Capstone | January 2025*

**Stack:** Python · GeoPandas · HDBSCAN · NetworkX · Louvain · SARIMA · MTA BusTime API  
**Data:** 1 week of real-time bus location data · 2,300 static stops across 23 routes

---

## What It Does

Connecting Queens analyzes bus service across the Eastern Queens Transit Desert —
a region of over 400,000 residents with no subway access. Using one week of
real-time MTA bus location data and static stop infrastructure, the project
identifies transit hubs and underserved neighborhoods through a combination of
density-based spatial clustering (HDBSCAN) and graph-based community detection
(Louvain method). A SARIMA time series model validates that service patterns are
stable enough to support the clustering results.

Of 27 identified communities, 5 qualify as transit hubs and 17 are low-service
areas — confirming that Eastern Queens is severely underserved even relative to
its own internal baseline.

---

## Why I Built This

I grew up in Eastern Queens. Getting anywhere without a car meant long waits,
indirect routes, and the constant awareness that the subway — visible from parts
of the neighborhood — might as well have been in another city. When I started the
General Assembly Data Science Bootcamp in late 2024, I knew immediately that this
was the problem I wanted to work on for my capstone.

The timing added urgency. New York City's congestion pricing scheme took effect
in early 2025, rerouting arterial traffic through exactly the corridors that
Eastern Queens residents depend on. The MTA's Queens Bus Network Redesign and
Interborough Express projects promise improvements, but focus primarily on
western Queens. I wanted to quantify what the data actually shows about eastern
Queens service — not just assert that it's bad, but measure it.

The project collects its own data via the MTA BusTime SIRI API, clusters stops
into communities using real-time vehicle movement patterns, and surfaces specific
neighborhoods where service intensity is lowest relative to infrastructure.

---

## What I Learned

**Technical skills**  
GeoPandas was entirely new to me coming into this project. Learning to perform
spatial joins, work with GeoDataFrames, and produce map visualizations at the
neighborhood level was one of the most rewarding parts of the month. HDBSCAN and
the Louvain method were also new — understanding how to combine a density-based
clustering algorithm with a graph-based community detection algorithm to get a
richer picture than either alone was the analytical core of the project.

**Data science insights**  
Summary statistics tell you almost nothing about spatial data. The Q27 having 153
stops is interesting, but it takes a map to understand what that means for a
neighborhood. I learned to lead with visualization when exploring geospatial
problems, not tables. I also learned the hard way that DBSCAN and PageRank, while
theoretically appealing, were wrong tools for this problem — DBSCAN's epsilon
parameter is nearly impossible to tune for geographic data at this scale, and
PageRank assumes directed graphs, which transit networks are not.

**Software engineering practices**  
Building a data collection pipeline from scratch — scheduler, per-route collection,
consolidation — taught me how much can go wrong between an API and a clean
DataFrame. I also learned to manage 23 parallel DataFrames using a dictionary
pattern, which made the entire analysis loop far cleaner than handling them as
separate variables would have been.

**Unexpected learnings**  
The Louvain method's coverage limitation (40% in this case) was initially
frustrating. Understanding why it happens — nodes with no graph edges simply
cannot be assigned to communities — turned into one of the most useful
methodological lessons of the project. It's a reminder that evaluation metrics
always need interpretation in context, not just comparison to a benchmark.

**Design decisions**  
I chose HDBSCAN over KMeans or standard DBSCAN because it doesn't require
specifying the number of clusters or an epsilon parameter — both of which are
difficult to justify a priori for geographic stop data. I chose Louvain over
Leiden (a more recent alternative) because Louvain is better documented and
easier to explain in an interview context, and the known limitations of Louvain
(non-overlapping communities, resolution limit) are not disqualifying for this
use case. I would try Leiden in a future iteration.

---

## Quick Start

### Requirements

Python 3.11+. An MTA BusTime API key is required for data collection (free at
[bustime.mta.info](https://bustime.mta.info/wiki/Developers/Index)). Analysis
can be reproduced without an API key using the data already in `data/`.

### Installation
```bash
git clone https://github.com/dmehta94/project-capstone-transit-inequity-eastern-queens
cd project-capstone-transit-inequity-eastern-queens

python -m venv venv
source venv/Scripts/activate  # Windows GitBash
pip install -r requirements.txt
```

### Collect fresh data (optional)
```bash
export MTA_API_KEY='your_key_here'
python code/static_data_collection.py
python code/realtime_collection_scheduler.py  # Runs every 30 min — Ctrl+C to stop
python code/realtime_data_consolidation.py
```

### Run the analysis

Open JupyterLab and run the notebooks in order:
```bash
jupyter lab
```

1. `code/exploratory_data_analysis.ipynb` — spatial and temporal EDA
2. `code/analysis.ipynb` — HDBSCAN, Louvain, SARIMA, service summary

---

## Sample Output

The analysis produces the following key visualizations in `images/`:

| Output | Description |
|---|---|
| `eastern_queens_stop_density.png` | Stop count per neighborhood heatmap |
| `average_daily_bus_activity_by_hour_by_route.png` | Hourly activity curves for all 23 routes |
| `hdbscan_clusters_map.png` | HDBSCAN spatial clusters overlaid on Queens |
| `louvain_communities_map.png` | Louvain communities from real-time movement data |
| `hubs_and_lsas_eastern_queens.png` | Transit hubs (blue) and low-service areas (orange) |
| `activity_to_stop_ratio_heatmap.png` | Service intensity by neighborhood |

---

## Technical Details

### Architecture

The project has three stages:

**Collection** (`static_data_collection.py`, `realtime_data_collection.py`,
`realtime_collection_scheduler.py`) — pulls stop infrastructure and vehicle
positions from the MTA BusTime API and writes per-route CSVs.

**Consolidation** (`realtime_data_consolidation.py`) — merges 23 per-route files
into a single sorted CSV for analysis.

**Analysis** (`exploratory_data_analysis.ipynb`, `analysis.ipynb`) — spatial
joins, clustering, time series modeling, and service-level classification.

### Key Methods

**HDBSCAN** identifies dense spatial clusters of stops without requiring a fixed
cluster count or epsilon parameter. A grid search over `min_cluster_size` (50–150)
and `min_samples` (20–40) selects the configuration with the best silhouette score.
Spatial silhouette score: **0.246** (stops only) → **0.71** (after temporal
integration).

**Louvain community detection** builds a weighted graph where edges represent
consecutive stop visits by the same vehicle. Edge weight is the inverse of
geographic distance, so closer stops are more strongly connected. Resolution
parameter set to 2.0 for neighborhood-scale communities. Modularity: **0.756**.

**Temporal HDBSCAN** clusters routes by their hourly activity profiles, then
merges these temporal labels with the Louvain communities to distinguish
spatially-connected communities that are temporally inactive from those with
consistent service throughout the day.

**SARIMA(2,1,2)(1,1,1,24)** forecasts hourly bus activity for a single route,
validating that daily service patterns are stable enough to support the clustering
results. RMSE: **1.67 buses/hour**.

### Nearest-Stop Assignment

Real-time vehicle positions are matched to the nearest static stop using a
`scipy.spatial.cKDTree` — a vectorized k-nearest-neighbor structure that handles
hundreds of thousands of records efficiently. Coordinates are converted to radians
for haversine-compatible distance calculations.

### Dependencies

See `requirements.txt`. Key packages: `geopandas`, `hdbscan`, `networkx`,
`community` (Louvain), `statsmodels`, `scikit-learn`, `requests`, `schedule`.

---

## Limitations

**One week of data.** The analysis characterizes a single week in January 2025.
Seasonal effects, school calendars, and weather are not captured. A more robust
analysis would require months of data hosted on a cloud platform like AWS or Azure.

**Daytime collection only.** Data was collected between 6 AM and 10 PM. Overnight
service gaps are not reflected.

**40% Louvain coverage.** Stops with no graph edges (buses that never visited
consecutive stops within the collection window) cannot be assigned to communities.
These stops appear as noise and are excluded from the hub/low-service classification.

**Activity-to-stop ratio as a proxy.** The ratio measures data volume relative to
infrastructure — not actual passenger load, headway, or on-time performance. It is
a reasonable first-pass metric but not a substitute for ridership data.

**No comparison to western Queens.** The analysis characterizes eastern Queens
relative to itself. A comparison against the well-served western Queens network
would strengthen the equity argument.

---

## Next Steps

- Extend data collection to 4–6 weeks across multiple seasons
- Collect data across all of Queens for a direct east/west comparison
- Implement pathfinding algorithms (minimum spanning tree, genetic algorithms)
  to propose optimized route remappings
- Incorporate population and ridership data for passenger-weighted analysis
- Complete the Streamlit dashboard (in progress — see `code/transit_analysis_app.py`)
- Evaluate Leiden method as a more robust alternative to Louvain

---

## Credits

Data collection and analysis by Deval Mehta. Code cleanup and debugging assisted
by GPT-4 (OpenAI) and Claude (Anthropic). Real-time and static bus data from the
[MTA BusTime API](https://bustime.mta.info/wiki/Developers/Index). Geographic
boundary data from [NYC Open Data](https://opendata.cityofnewyork.us/).

---

## License

MIT License. See `LICENSE` for details.

**Contact:** [github.com/dmehta94](https://github.com/dmehta94)