<img src="http://imgur.com/1ZcRyrc.png" style="float: left; margin: 20px; height: 90px">

# Capstone Project: Optimizing Bus Routes in the Eastern Queens Transit Desert

*Deval Mehta*

## Table of Contents
1) [Overview](#Overview) 
2) [Data Dictionary](<#Data Dictionary>)
3) [Requirements](#Requirements)
4) [Executive Summary](<#Executive Summary>)
    1) [Purpose](<#Purpose>)
    2) [Data Handling](<#Data Handling>)
    3) [Analysis](#Analysis)
    4) [Findings and Implications](<#Findings and Implications>)
    5) [Next Steps](#Next-Steps)

## Overview
The newly announced congestion pricing scheme to enter lower Manhattan aims to restrict private vehicular traffic through New York City, but stands to reroute arterial traffic through various less-traveled routes, making commutes from places like Eastern Queens, where there is no real subway access, especially difficult. In order to complement the state's strategy to reduce arterial traffic, we aim to optimize bus routes across the Eastern Queens Transit Desert to provide better access through to the other boroughs and swift subway access, ensuring that highly congested areas receive adequate service and underserved communities receive the transportation support they need.

## Data Dictionary

This project contains several datasets, most of which fall under the umbrella of "real-time data by bus route." In addition to real time data, we have collected static geographic data, outlining all the bus stops across the 23 bus routes that service the Eastern Queens Transit Desert and two `.geojson` files containing the boundaries for the boroughs of New York City (`borough_boundaries.geojson`) and the neighborhood boundaries for New York City (`nyc_by_neighborhood.geojson`). We leave open the possibility of including population data as well (note for now).

### Static Data
| Variable | Data Type | Description |
|---|---|---|
| Route ID | `string` | Identifier for the bus route |
| Stop ID | `string` | Identifer for each given bus stop |
| Stop Name | `string` | Intersection nearest to where the bus stop is placed |
| Latitude | `float` | Global latitude coordinate for each stop |
| Longitude | `float` | Global longitude oordinates for each stop |

| Variable | Data Type | Description |
|---|---|---|
| Route ID | `string` | Identifier for the bus route |
| Vehicle ID | `string` | Identifer for each bus operating on each route |
| Latitude | `float` | Global latitude coordinate for each stop |
| Longitude | `float` | Global longitude oordinates for each stop |
| Timestamp | `string` | Time at which the bus was located at the exact coordinates where it appeared (converted to `datetime`) |

## Requirements

### Hardware

### Software
| Library | Module | Purpose |
|---|---|---|

## Executive Summary

### Purpose

### Data Handling

### Analysis

### Findings and Implications

### Next Steps