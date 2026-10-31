# Faculty viva questions

## 1 What problem does the project solve?

It compares PM2.5 levels, timing and relative high hours across six Bengaluru stations and measures how often high hours coincide.

## 2 Is this real time?

No. It analyzes historical batch data from resources labelled 15-minute observations. A live ingestion service is not implemented.

## 3 What are the Big Data characteristics?

Volume is the saved source row and byte count; velocity refers to source reporting cadence; variety is the pollutant, weather and metadata fields; veracity covers missingness and measurement issues. Local size is modest.

## 4 Why use Spark if pandas is sufficient?

The assignment requires a justified Big Data workflow. Spark implements distributed-style DataFrame operations; pandas is also used as an independent check. We do not claim Spark is necessary at this size.

## 5 What is a Spark DataFrame?

A distributed table with named typed columns and an execution plan. Spark optimizes operations before actions execute them.

## 6 What is lazy evaluation?

Transformations build a plan; actions such as count or collect run it. Timers must include an action to measure computation.

## 7 Which operations are used?

CSV reading, column selection and parsing, filters, duplicate removal, grouped aggregations, exact percentiles and timestamp joins; SQL supplies calendar summaries.

## 8 Where does the data come from?

Six OpenCity KSPCB/CPCB-labelled monitoring resources. Exact URLs, hashes, sizes and raw row counts are in data/manifest.json.

## 9 Does the project analyze AQI?

No. The selected resources are labelled AQI but expose pollutant concentrations. We use PM2.5 in µg/m³ and do not convert it to AQI.

## 10 How are timestamps handled?

We honor the encoded UTC offset, convert calendar calculations to Asia/Kolkata, and retain the local 2024–2025 window. The upstream sensor timezone convention remains a limitation.

## 11 How are missing values handled?

Missing or invalid PM2.5 observations are excluded with reason counts. They are never replaced with zero. An hour needs three distinct valid quarter-hours.

## 12 How are duplicates handled?

Identical selected station/time/PM2.5 rows collapse; conflicting values at one station and timestamp are averaged and counted. No arbitrary first-record choice is used.

## 13 Why are hourly means used?

They align the supplied quarter-hour series at a common hourly interval while enforcing a minimum 75% within-hour observation count.

## 14 How is a spike defined?

An hourly mean strictly above the station-specific exact 95th percentile of valid study-window hourly means. It is a retrospective statistical threshold.

## 15 Are precisely 5% of readings spikes?

Not necessarily. Strict comparison, tied values and interpolated quantiles can change the flagged fraction.

## 16 Is the threshold a health standard?

No. It describes the upper tail of that station’s observations and should not be interpreted as an AQI category or regulatory exceedance.

## 17 How do stations align?

Pairs use an inner join on hourly timestamps. Missing observations cannot become zeros or non-spike flags. Six-station summaries use only complete-case hours.

## 18 What does lift mean?

It is observed simultaneous spike hours divided by expected hours under independence, calculated using the same overlap-hour marginals. Values above one indicate more coincidence than that simple baseline.

## 19 Does synchronization prove pollutant movement?

No. Weather, seasonal patterns and other shared factors can create coincidence. We do not estimate transport directions or causes.

## 20 What are the main observed results?

398,420 source rows become 92,479 valid station-hours. There are 461 multiple-spike hours among 7,990 complete six-station hours. Exact station and pair results are in the tables.

## 21 How is correctness checked?

A separate pandas implementation recomputes every processed hourly row, summary, percentile, spike count, pair overlap and temporal mean. The recorded checks passed.

## 22 What performance comparison was measured?

Three warm grouped-statistic repetitions on the same hourly data: median Spark 0.4934 s, pandas 0.0306 s. Startup and cleaning are excluded from both.

## 23 Does the experiment establish scalability?

No. It runs locally on two worker threads with a modest dataset. Distributed hardware and increasing workload sizes would be required to test scalability.

## 24 How does it differ from the research paper?

The paper studies multiple pollutants and meteorological associations across northern locations; this project examines Bengaluru PM2.5 and timestamp-aligned spike coincidence in Spark. It does not replicate trajectory modeling.

## 25 What would you improve next?

Confirm timestamp and sensor metadata, add stations, evaluate held-out thresholds, control seasonality in the baseline, and measure distributed performance only if larger workloads justify it.