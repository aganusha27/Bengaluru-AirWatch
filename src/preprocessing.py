"""Clean only the selected PM2.5 variable; preserve raw data."""
from pyspark.sql import functions as F
from .data_ingestion import PM

def clean(raw):
    selected=raw.select(F.trim(F.col('Station Name')).alias('station'),
                        F.col('Timestamp').alias('timestamp_source'),
                        F.col('`'+PM+'`').alias('pm25_source'))
    selected=(selected.withColumn('timestamp',F.try_to_timestamp('timestamp_source'))
              .withColumn('pm25',F.expr('try_cast(pm25_source as double)'))
              .withColumn('reason',F.when(F.col('station').isNull() | (F.col('station')==''),'missing_station')
                          .when(F.col('timestamp').isNull(),'invalid_timestamp')
                          .when((F.col('timestamp')<F.to_timestamp(F.lit('2024-01-01 00:00:00'))) |
                                (F.col('timestamp')>=F.to_timestamp(F.lit('2026-01-01 00:00:00'))),'outside_study_window')
                          .when(F.col('pm25').isNull() | F.isnan('pm25'),'missing_or_invalid_pm25')
                          .when((F.col('pm25')<0) | (F.abs('pm25')==float('inf')),'negative_or_nonfinite_pm25')
                          .when(~F.minute('timestamp').isin(0,15,30,45) | (F.second('timestamp')!=0),'off_grid_timestamp')
                          .otherwise('valid')).cache())
    audit=selected.groupBy('station','reason').count()
    valid=selected.filter(F.col('reason')=='valid').select('station','timestamp','pm25')
    # Identical selected observations collapse; conflicting measurements are averaged explicitly.
    distinct=valid.dropDuplicates(['station','timestamp','pm25'])
    dedup=distinct.groupBy('station','timestamp').agg(F.avg('pm25').alias('pm25'),F.count('*').alias('conflict_values'))
    hourly_all=(dedup.groupBy('station',F.date_trunc('hour','timestamp').alias('timestamp'))
                .agg(F.avg('pm25').alias('pm25'),F.count('*').alias('valid_quarters')).cache())
    hourly=hourly_all.filter(F.col('valid_quarters')>=3).cache()
    return selected,valid,distinct,dedup,hourly_all,hourly,audit

def pandas_reference(frame):
    import pandas as pd
    import numpy as np
    x=frame.copy()
    x['station']=x['Station Name'].str.strip()
    x['timestamp']=pd.to_datetime(x['Timestamp'],utc=True,errors='coerce').dt.tz_convert('Asia/Kolkata')
    x['pm25']=pd.to_numeric(x.iloc[:,2],errors='coerce')
    good=(x['station'].notna() & x['station'].ne('') & x['timestamp'].notna() &
          x['timestamp'].ge(pd.Timestamp('2024-01-01',tz='Asia/Kolkata')) &
          x['timestamp'].lt(pd.Timestamp('2026-01-01',tz='Asia/Kolkata')) &
          x['pm25'].notna() & np.isfinite(x['pm25']) & x['pm25'].ge(0) &
          x['timestamp'].dt.minute.isin([0,15,30,45]) & x['timestamp'].dt.second.eq(0))
    x=x.loc[good,['station','timestamp','pm25']].drop_duplicates()
    x=x.groupby(['station','timestamp'],as_index=False).pm25.mean()
    x['timestamp']=x['timestamp'].dt.floor('h')
    x=x.groupby(['station','timestamp']).pm25.agg(['mean','count']).reset_index()
    x=x.loc[x['count']>=3].rename(columns={'mean':'pm25','count':'valid_quarters'})
    # Spark collected timestamps are converted through formatted strings in the pipeline.
    x['timestamp']=x['timestamp'].dt.tz_localize(None)
    return x.reset_index(drop=True)
