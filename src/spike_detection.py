"""Station-specific exact 95th percentile of valid hourly means."""
from pyspark.sql import functions as F

def detect(hourly):
    thresholds=hourly.groupBy('station').agg(F.percentile('pm25',0.95).alias('threshold_p95'))
    events=hourly.join(thresholds,'station').withColumn('spike',(F.col('pm25')>F.col('threshold_p95')).cast('int')).cache()
    summary=events.groupBy('station','threshold_p95').agg(F.count('*').alias('valid_hours'),F.sum('spike').alias('spike_hours'))
    return thresholds,events,summary
