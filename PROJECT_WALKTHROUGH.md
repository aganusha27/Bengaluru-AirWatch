# Project walkthrough

We study how PM2.5 varies across six Bengaluru monitoring stations and whether unusually high hours occur together. We chose this topic because the same city can contain different concentration patterns, and matching timestamps lets us distinguish coincident from single-station high readings.

## Actual dataset
The six real OpenCity files contain 398,420 source rows and matching schemas. Each row usually represents a station and a quarter-hour timestamp; six year separator rows are rejected. Station Name identifies the monitoring location; Timestamp encodes UTC; PM2.5 (µg/m³) measures fine-particle mass concentration. PM10, gases and meteorological columns are available but not combined into a single pollutant average. This project does not compute AQI.

## Why PySpark
Spark expresses a repeatable ingestion, cleaning, grouping and joining pipeline through DataFrames and SQL. It can execute these operations on distributed infrastructure, but our local run uses two worker threads and does not prove cluster scalability. Pandas is sufficient for this data size and independently checks the results.

## Workflow and files
data_ingestion.py checks pinned downloads and their schemas. preprocessing.py parses types, audits rejection reasons, deduplicates selected observations and averages at least three valid quarter-hours into each hourly mean. analysis.py computes station statistics and SQL time patterns. spike_detection.py creates exact 95th-percentile thresholds. synchronization.py joins overlapping hours and computes joint counts and lift. visualization.py makes eight charts from tables. verification.py separately recomputes the real-data results using pandas. main.py orchestrates actions and timing; build_report.py reads the saved evidence to create the report.

## Spark operations
read.csv reads the files; select chooses the measurement; withColumn and try_cast parse data; filter implements quality rules; dropDuplicates collapses repeated selected observations; groupBy and agg compute means, counts and percentiles; join aligns stations. SQL derives local hour, weekday and month. Caching avoids repeating the hourly calculation. count and collect force actual work before a timer stops.

## Spike detection
Sort the valid hourly means conceptually and choose the exact interpolated 95th percentile separately for each station. A spike strictly exceeds that station's value. It is unusually high for that station, not a health category or legal limit. Thresholds are fitted retrospectively, and ties can change the fraction flagged.

## Synchronization
For a station pair, inner-join timestamps so both observations exist. Count each station's spikes and simultaneous spikes on those matched hours. Expected simultaneous hours under independence = A × B / N. Lift = observed / expected. It describes coincidence and does not remove shared seasonality or prove transport. Across 7,990 complete six-station hours, 461 have at least two spikes.

## Actual results
Cleaning retains 92,479 station-hour means. Bapuji Nagar has the highest available-hour mean, 34.14 µg/m³. The highest pairwise lift is 10.88, for Hebbal and Jayanagar 5th Block. Read the full common-hour comparison and all pair denominators before interpreting these differences.

## The eight charts
1. Station average compares observed means, with unequal coverage.
2. Daily time series shows temporal change and gaps, requiring >=18 valid hours per plotted day.
3. Hour profile shows average local time-of-day patterns.
4. Weekday/weekend bars compare unadjusted hourly means.
5. Monthly lines show changing monthly means and differing coverage.
6. Standard deviation bars compare absolute variability; CSVs also include IQR and CV.
7. Station-hour heatmap displays the hour-profile matrix on a common color scale.
8. Spike lift heatmap compares pairwise simultaneous spikes with marginal independence.

## Performance
The actual total excluding downloads is 126.294 seconds. Warm grouped-statistics medians are Spark 0.4934 s and pandas 0.0306 s. Both benchmarks exclude startup, parsing and cleaning. They use the same hourly values and operations. The benchmark does not establish cluster scalability or compare complete pipelines.

## Research relationship
Soni et al. (2024) examine temporal and spatial pollutant patterns and meteorological associations in northern India. We study six stations within Bengaluru and compare timestamp-aligned relative spikes using Spark. We do not reproduce HYSPLIT or the paper's source-attribution methods. Its internally differing period descriptions are disclosed in the review.

## Limitations to explain to faculty
Coverage is incomplete; monitoring sites are not all neighborhoods; timezone conversion relies on source labels; sensor validation is unavailable; repeated source readings may not be independent; thresholds are retrospective; and lift is descriptive. No prediction model, causal transport analysis, or distributed speedup is claimed. The independent real-data checks in verification.json must pass before citing revised results.
