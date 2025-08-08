<img src="http://imgur.com/1ZcRyrc.png" style="float: left; margin: 10px; height: 120px">

# Connecting Queens: Leveraging Data-Driven Insights for Better Transit Planning

*Deval Mehta*

## Table of Contents
1) [Overview](#Overview) 
2) [Data Dictionary](<#Data Dictionary>)
3) [Requirements](#Requirements)
4) [Executive Summary](<#Executive Summary>)
    1) [Purpose](<#Purpose>)
    2) [Data Handling](<#Data Handling>)
    3) [Exploration](#Exploration)
    4) [Analysis](#Analysis)
    5) [Findings and Implications](<#Findings and Implications>)
    6) [Next Steps](#Next-Steps)

## Overview
The newly announced congestion pricing scheme to enter lower Manhattan aims to restrict private vehicular traffic through New York City, but stands to reroute arterial traffic through less-traveled routes, making commutes from places such as Eastern Queens, where there is no real subway access, especially difficult. In order to complement the state's strategy to reduce arterial traffic, we must optimize bus routes across the Eastern Queens Transit Desert to provide better access to the other boroughs and swift subway access, ensuring that highly congested areas receive adequate service and underserved communities receive the transportation support they need. Our goal is to characterize the underserved communities and transit hubs of Eastern Queens, so that we may work toward implementing more optimized bus routes in the future, leaving space for expansion of the existing subway system into Eastern Queens.

## Data Dictionary

This project contains several datasets, most of which fall under the umbrella of "real-time data by bus route." In addition to real time data, we have collected static geographic data, outlining all the bus stops across the 23 bus routes that service the Eastern Queens Transit Desert and two `.geojson` files containing the boundaries for the boroughs of New York City (`borough_boundaries.geojson`) and the neighborhood boundaries for New York City (`nyc_by_neighborhood.geojson`). We leave open the possibility of including population data as well (note for now).

### Static Data
| Feature | Data Type | Description |
|---|---|---|
| Route ID | `string` | Identifier for the bus route |
| Stop ID | `string` | Identifier for each given bus stop |
| Stop Name | `string` | Intersection nearest to where the bus stop is placed |
| Latitude | `float` | Global latitude coordinate for each stop |
| Longitude | `float` | Global longitude oordinates for each stop |

### Real-Time Data
| Feature | Data Type | Description |
|---|---|---|
| Route ID | `string` | Identifier for the bus route |
| Vehicle ID | `string` | Identifier for each bus operating on each route |
| Latitude | `float` | Global latitude coordinate for each stop |
| Longitude | `float` | Global longitude coordinate for each stop |
| Timestamp | `string` | Time at which the bus was located at the exact coordinates where it appeared (converted to `datetime`) |

### Engineered Features
| Feature | Datatype | Dataset | Description |
|---|---|---|---|
| `coords` | `tuple` | `stops_data` | Tuple containing latitude and longitude for each stop. |
| `hdbscan_cluster` | `int` | `stops_data` | Cluster labels from the HDBSCAN algorithm. |
| `louvain_community` | `int` | `stops_data` | Community labels from the Louvain method applied to the transit network. |
| `nearest_stop_id` | `string` | `real_time_data` | The stop ID of the closest static stop to each real-time bus location. |
| `distance_to_stop` | `float` | `real_time_data` | Distance (in kilometers) between the bus location and its nearest stop. |
| `Time Gap` | `float` | `real_time_data` | Time difference (in minutes) between consecutive bus records. |
| `Cluster` | `int` | `louvain_temporal_data` | Temporal cluster labels from HDBSCAN on hourly bus activity. |
| `Activity Per Stop` | `float` | `service_summary` | Total vehicle activity divided by the total number of stops in a community. |
| `Activity-to-Stop Ratio`| `float` | `service_summary` | Total bus activity count divided by total stop count for each neighborhood. |
| `Average Temporal Activity` | `float` | `service_summary` | Average temporal activity of clusters within a Louvain community. |
| `Bus Activity Count` | `int` | `service_summary` | Total number of bus activity records in a neighborhood or community. |
| `Stop Count` | `int` | `service_summary` | Total number of stops in a neighborhood or Louvain community. |
| `weight` | `float` | Transit Network Graph | Inverse distance or frequency of transitions between stops (edge weight). |

## Requirements

### Software
| Library | Module | Purpose |
|---|---|---|
| `os` |  | Execute shell operations in Python. |
| `requests` |  | Send HTTP requests via Python. |
| `datetime` |  | Handle datetime objects |
| `glob` |  | Pattern-match file names to make mass imports easier. |
| `numpy` |  | Ease of basic aggregate operations on data. |
| `pandas` |  | Read our data into a DataFrame, clean it, engineer new features, and write it out to submission files. |
| `collections` | `Collections` | Counting hashable objects more easily. |
| `tqdm` |  | Display progress bars when running code. |
| `geopandas` |  | Handle GeoDataFrames, which incorporate geometry into the DataFrames. |
| `shapely` |  | `geometry` | Import `Point` to introduce compatible geometry for to create a GeoDataFrame. |
| `geopy` | `distance` | Compute "great circle" distances to employ the haversine metric. |
| `networkx` |  | Map and study graph-based networks. |
| `community` |  | Perform community mapping. |
| `itertools` | `combinatorics` | Produce combinatorial generators to produce edges for graph constructions. |
| `hdbscan` |  | Perform HDBSCAN modeling. |
| `scipy` | `spatial` | Import `cKDTree` to produce a KD Tree for quick k-neighbors calculations for clustering. |
|  | `stats` | Import `pearsonr` to compute the Pearson Correlation Coefficient|
| `sklearn` | `cluster` | Import `DBSCAN` to perform DBSCAN clustering. |
|  | `metrics` | Import `silhouette_score` and `root_mean_squared_error` to assess clustering and time-series models, respectively. |
|  | `neighbors` | Import `NearestNeighbors` to determine the k-nearest neighbors to a point in a space easily. |
|  | `preprocessing` | Import `StandardScaler` to scale the data prior to HDBSCAN clustering. |
| `statsmodels` | `tsa` | Import `seasonal.STL` to perform seasonal-trend decomposition and `api.SARIMAX` to predict from time-series data with a SARIMA model. |
| `matplotlib` | `pyplot` | Basic plotting functionality. |
|  | `mcolors` | Access options for color map setting. |
| `seaborn` |  | More control over plots. |

## Executive Summary
### Purpose
The [Queens Bus Network Redesign](https://mta.info/project/queens-bus-network-redesign) and [Interborough Express](https://mta.info/project/interborough-express) projects aim to improve transit access in Queens but focus primarily on improvements in the well-connected Western Queens. Eastern Queens has historically been underserved by public transit, despite the presence of the LIRR rail system. With the onset of the congestion pricing scheme in addition to preexisting issues, residents of the Eastern Queens transit desert require a more supportive transit network to make their way across the city without significant financial and quality of life strain. To diagnose the level of service in the Eastern Queens Transit Desert, we employ two methods of hierarchical clustering (HDBSCAN and [Louvain clustering](https://library.fiveable.me/key-terms/combinatorics/louvain-method)) on real-time data collected over the course of a week and the 

### Data Handling
We collected real-time data over the course of a week, between the hours of 6:00 AM and 10:00 PM EST. The data here can be considered representative of "a typical week," but does not account for seasonal effects over the course of a month or year. Due to the nature of the data collection process, there was no "missing data," per se, but we do recognize that there were buses running outside of the hours of collection that would have been missed. A more robust analysis would include historical data, as well as "round-the-clock" collection, facilitated by a big-data solution, such as AWS or Azure. There appears to be a set of data points from the Bronx, which we have ignored for this analysis. These likely arose due to a driver who neglected to mark their vehicle as off-route or who needed to take a detour due to some event-related closure.

### Exploration
Not much could be said about spatial data from summary statistics, except for which bus route is the most well-service (the Q27). For the initial data exploration, we resolved to do the following:
- Map the static data out and check which neighborhoods have the highest and lowest stop density
- Perform a similar spatial analysis for buses found throughout the day in each neighborhood
- Perform a temporal analysis to see when each route was the busiest and which were the most underserviced.

Further exploration was performed in preparation for time-series clustering, namely plotting trends and seasonality to verify that the real-time data was amenable to clustering and community-mapping. We also perform a predictive SARIMA model to explore how reliable the seasonality and trends are, with a profile similar to each weekday being generated for the next possible weekday, with an RMSE of 1.67 buses/hour, which indicates relative stability.

### Analysis
The problem at hand lends itself to unsupervised learning, in a machine learning context. There is no response variable, as we seek to fundamentally determine how the network of 2,300 bus stops across Eastern Queens may be categorized into low-service areas and high-activity transit hubs. We opt here to employ both clustering and network analysis, given the nature of the problem and data. In particular, we opted to employ Hierarchical Density-Based Spatial Clustering of Applications with Noise (HDBSCAN), which converts DBSCAN into a hierarchical clustering algorithm, then extracts a flat clustering based on cluster stability. [We welcome the enthusiastic colleague or student to read more about it here](https://hdbscan.readthedocs.io/en/latest/how_hdbscan_works.html). We also opt to use the Louvain Method, a greedy community-mapping algorithm, which first assigns each node in a graph to its own community, then clusters by maximizing on modularity score. Notably, Louvain is also a hierarchical clustering model. [For more information on the Louvain Method, see here](https://neo4j.com/docs/graph-data-science/current/algorithms/louvain/).

Initially we considered the two separately, as HDBSCAN clusters based on the density of nodes, providing a distance-related heuristic for mapping communities, and Louvain clusters based on modularity. By incorporating time-series data to standardize over the course of a week through a time-series HDBSCAN clustering, then filtering the results into a Louvain model, we were able to account for both. We evaluate our results on multiple metrics, detailed as follows:

- **HDBSCAN**: silhouette score
- **Louvain**: modularity score, coverage
- **Temporal HDBSCAN Clustering**: silhouette score

Silhouette score and modularity score are effectively the same metric: both measure how similar points within a cluster are to each other and how distinct the clusters formed are from each other, on a scale of -1 to 1, where -1 means there is no strong clustering and 1 means the clusters are perfectly distinct.

### Findings and Implications
Prior to accounting for real-time data, our HDBSCAN model performed with a silhouette score of 0.246. This indicates moderately strong density-based clusters, but not terribly strong ones. Our Louvain model, however, performs with a modularity score of 0.756, indicating strongly defined communities. On the other hand, the Louvain model also only has 40% coverage, meaning that only 40% of our possible network area is covered.

After incorporating time-series, the silhouette score rises to 0.71, indicating strong, well-defined denisty-based clusters. With strongly defined Louvain communities and density-based clusters, we compute some aggregate statistics to determine which communities are well-serviced and those that are under-served. Of the 27 distinct Louvain-HDB communities mapped, only 5 can be considered well-serviced and most of them are localized to the arterial Union Turnpike and Springfield Boulevard corridors, or to Jamaica, near the Jamaica Train Station. Meanwhile, we identify 17 of 27 communities as low-service areas, which are spread all across Eastern Queens. Both of these categories are determined based whether the community has an average stop activity in the top or bottom 25% of the data and more or less, respectively average temporal activity than the median amount.

We conclude thus that Eastern Queens is indeed incredibly underserviced, as suggested by the data, even when isolated from a comparison against the rest of the City. The massive lapse in service between low-service areas and the two transit hubs in Queens leaves commuters in a tenuous situation. We recommend, in the short-term, increasing the frequency on routes directed to underserved neighborhoods. Within the coming months, we'd like to direct resources to improving connectivity by remapping the eastern Queens bus route network to better service all communities. We hope to encourage the MTA as a whole to consider, in the long-term, expanding subway access to the outer borough transit deserts as a whole, to keep our City connected and whole.

### Next Steps
This project provides a taste of how can leverage data to improve the New York City transit system. From here, we can take several steps to ensure our commuters have the best possible experience and keep our city moving and green.

- Collect more data more frequently and for a longer period of time to better account for seasonal effects.
- Collect data across all of Queens to compare Eastern Queens service to Western Queens service.
- Collect data from routes across the whole City for a more holistic analysis. This immediately becomes a "big data" project and will thus have to be hosted on a service like AWS or Azure.
- Implement pathfinding algorithms such as minimal spanning trees or [genetic algorithms](https://www.cse.unr.edu/~sushil/class/gas/papers/Using%20a%20Genetic%20Algorithm%20to%20Explore%20A_-like%20Pathfinding%20Algorithms.pdf) to remap the bus network in Eastern Queens and NYC's other transit deserts.
- Incorporate population data to make more specific recommendations regarding frequency
- Check Louvain communities against the [Leiden method](https://www.nature.com/articles/s41598-019-41695-z), since Louvain distinctly produces non-overlapping communities. Leiden is more robust and mitigates this issue, as well as the resolution limit of modularity.
- Perform a similar analysis on subway routes to support a possible extension into eastern Queens and other transit deserts.
- Determine the gap in funding to implement each solution.

### Additional Notes
There has been significant work toward a Streamlit app to accompany the project that serves the interests of various stakeholders in the Transit Desert problem. The app does not yet work, but will be a continued effort.