"""Pair comparisons use only timestamps with both stations observed."""
from pyspark.sql import functions as F

def synchronize(events,nstations):
    left=events.select('timestamp',F.col('station').alias('station_a'),F.col('spike').alias('spike_a'))
    right=events.select('timestamp',F.col('station').alias('station_b'),F.col('spike').alias('spike_b'))
    pairs=(left.join(right,'timestamp').filter(F.col('station_a')<F.col('station_b'))
        .groupBy('station_a','station_b').agg(F.count('*').alias('overlap_hours'),
            F.sum('spike_a').alias('a_spike_hours'),F.sum('spike_b').alias('b_spike_hours'),
            F.sum(F.col('spike_a')*F.col('spike_b')).alias('both_spike_hours'))
        .withColumn('expected_independent_hours',F.col('a_spike_hours')*F.col('b_spike_hours')/F.col('overlap_hours'))
        .withColumn('joint_rate',F.col('both_spike_hours')/F.col('overlap_hours'))
        .withColumn('lift',F.when(F.col('expected_independent_hours')>0,F.col('both_spike_hours')/F.col('expected_independent_hours')))
        .withColumn('jaccard',F.when((F.col('a_spike_hours')+F.col('b_spike_hours')-F.col('both_spike_hours'))>0,
            F.col('both_spike_hours')/(F.col('a_spike_hours')+F.col('b_spike_hours')-F.col('both_spike_hours')))))
    timeline=events.groupBy('timestamp').agg(F.count('*').alias('available_stations'),F.sum('spike').alias('spiking_stations'))
    complete=timeline.filter(F.col('available_stations')==nstations)
    return pairs,timeline,complete
