"""Spark DataFrame and SQL summaries; all measures concern hourly PM2.5."""
from pyspark.sql import functions as F

def station_statistics(hourly):
    return hourly.groupBy('station').agg(F.count('*').alias('valid_hours'),F.avg('pm25').alias('mean'),
        F.percentile('pm25',0.5).alias('median'),F.min('pm25').alias('min'),F.max('pm25').alias('max'),
        F.stddev_samp('pm25').alias('stddev'),F.percentile('pm25',0.25).alias('q25'),
        F.percentile('pm25',0.75).alias('q75'),F.min('timestamp').alias('start_ist'),F.max('timestamp').alias('end_ist')) 

def temporal_tables(spark,hourly):
    hourly.createOrReplaceTempView('hourly_pm25')
    queries={
      'hourly_pattern': "SELECT station, hour(timestamp) AS hour_ist, avg(pm25) AS mean, count(*) AS n FROM hourly_pm25 GROUP BY station,hour(timestamp)",
      'day_of_week': "SELECT station, weekday(timestamp) AS weekday_monday0, avg(pm25) AS mean, count(*) AS n FROM hourly_pm25 GROUP BY station,weekday(timestamp)",
      'weekday_weekend': "SELECT station, CASE WHEN weekday(timestamp)>=5 THEN 'Weekend' ELSE 'Weekday' END AS day_type, avg(pm25) AS mean, count(*) AS n FROM hourly_pm25 GROUP BY station,CASE WHEN weekday(timestamp)>=5 THEN 'Weekend' ELSE 'Weekday' END",
      'monthly': "SELECT station, date_format(timestamp,'yyyy-MM') AS month, avg(pm25) AS mean, count(*) AS n FROM hourly_pm25 GROUP BY station,date_format(timestamp,'yyyy-MM')",
      'daily': "SELECT station, date_format(timestamp,'yyyy-MM-dd') AS day, avg(pm25) AS mean, count(*) AS n FROM hourly_pm25 GROUP BY station,date_format(timestamp,'yyyy-MM-dd')"
    }
    return {name:spark.sql(q) for name,q in queries.items()}
