"""Run real source acquisition, Spark analysis, plotting and independent checks."""
import argparse
import json
import os
import platform
import statistics
import subprocess
import sys
import time
import importlib.metadata
from pathlib import Path

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--download-only',action='store_true');args=parser.parse_args()
    root=Path(__file__).resolve().parent
    for folder in ['data/raw','data/processed','outputs/tables','outputs/charts','outputs/metrics']:(root/folder).mkdir(parents=True,exist_ok=True)
    from src.data_ingestion import acquire,inspect_sources,read_spark
    manifest=acquire(root)
    if args.download_only:return
    total=time.perf_counter();raw_pd=inspect_sources(root,manifest)
    import pandas as pd
    import psutil
    import pyspark
    from pyspark.sql import SparkSession,functions as F
    from src.preprocessing import clean
    from src.analysis import station_statistics,temporal_tables
    from src.spike_detection import detect
    from src.synchronization import synchronize
    os.environ.setdefault('SPARK_LOCAL_IP','127.0.0.1')
    os.environ.setdefault('PYSPARK_PYTHON',sys.executable)
    startup=time.perf_counter()
    spark=(SparkSession.builder.master('local[2]').appName('Bengaluru-AirWatch')
       .config('spark.driver.host','127.0.0.1').config('spark.driver.bindAddress','127.0.0.1')
       .config('spark.sql.session.timeZone','Asia/Kolkata').config('spark.sql.shuffle.partitions','4')
       .config('spark.default.parallelism','2').config('spark.ui.enabled','false')
       .config('spark.sql.adaptive.enabled','true').getOrCreate())
    spark.sparkContext.setLogLevel('ERROR')
    metrics={'startup_seconds':time.perf_counter()-startup,'python':sys.version,'pyspark':pyspark.__version__,
      'platform':platform.platform(),'processor':platform.processor(),'logical_cpus':os.cpu_count(),
      'physical_memory_bytes':psutil.virtual_memory().total,'raw_bytes':sum(x['bytes'] for x in manifest),
      'raw_records':sum(x['records'] for x in manifest),'spark_conf':dict(spark.sparkContext.getConf().getAll()),
      'run_time_ist':pd.Timestamp.now(tz='Asia/Kolkata').isoformat(),
      'java_version':subprocess.run(['java','-version'],capture_output=True,text=True).stderr.strip()}
    metrics['dependency_versions']={name:importlib.metadata.version(name) for name in ['pandas','numpy','matplotlib','psutil','pyspark']}
    if sys.platform=='win32':
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r'HARDWARE\DESCRIPTION\System\CentralProcessor\0') as key:
            metrics['processor']=winreg.QueryValueEx(key,'ProcessorNameString')[0].strip()
    def collect(frame):
        # Format Spark timestamps inside the JVM, avoiding driver OS timezone conversion.
        for field in frame.schema:
            if field.dataType.typeName()=='timestamp':frame=frame.withColumn(field.name,F.date_format(F.col(field.name),'yyyy-MM-dd HH:mm:ss'))
        return pd.DataFrame([r.asDict() for r in frame.collect()],columns=frame.columns)
    def save(name,frame):
        x=collect(frame);x.to_csv(root/f'outputs/tables/{name}.csv',index=False);return x
    t=time.perf_counter();raw=read_spark(spark,root,manifest)
    selected,valid,distinct,dedup,all_hours,hourly,audit=clean(raw)
    counts={}
    for name,df in [('raw',selected),('valid',valid),('distinct',distinct),('deduplicated',dedup),('candidate_hours',all_hours),('hourly',hourly)]:
        counts[name]=df.count()
    assert counts['raw']==metrics['raw_records']
    metrics['cleaning_counts']=counts;metrics['cleaning_seconds']=time.perf_counter()-t
    print('CLEANED',counts,flush=True)
    save('cleaning_audit',audit)
    save('duplicate_audit',dedup.groupBy('station').agg(F.sum(F.when(F.col('conflict_values')>1,1).otherwise(0)).alias('conflicting_timestamps')))
    quality=all_hours.groupBy('station').agg(F.count('*').alias('candidate_hours'),F.sum(F.when(F.col('valid_quarters')<3,1).otherwise(0)).alias('hours_rejected_low_coverage'))
    save('hourly_coverage',quality)
    t=time.perf_counter()
    stats=save('station_statistics',station_statistics(hourly))
    stats['iqr']=stats.q75-stats.q25;stats['cv']=stats.stddev/stats['mean'];stats.to_csv(root/'outputs/tables/station_statistics.csv',index=False)
    for name,frame in temporal_tables(spark,hourly).items():save(name,frame)
    thresholds,events,summary=detect(hourly);save('spike_summary',summary)
    pairs,timeline,complete=synchronize(events,len(manifest));save('synchronization_pairs',pairs)
    save('complete_case_spike_distribution',complete.groupBy('spiking_stations').count())
    save('availability_distribution',timeline.groupBy('available_stations').count())
    # Common-case station means provide a missingness sensitivity comparison.
    common=hourly.join(complete.select('timestamp'),'timestamp')
    save('common_case_station_statistics',station_statistics(common))
    metrics['aggregation_seconds']=time.perf_counter()-t
    t=time.perf_counter();hp=collect(hourly);hp.to_csv(root/'data/processed/hourly_pm25.csv',index=False)
    ep=collect(events);ep.to_csv(root/'data/processed/hourly_spikes.csv',index=False)
    metrics['export_seconds']=time.perf_counter()-t
    # Comparable warm grouped statistics; parsing, cleaning and startup excluded for BOTH.
    hp['pm25']=pd.to_numeric(hp.pm25)
    def spark_bench():return hourly.groupBy('station').agg(F.count('pm25').alias('count'),F.avg('pm25').alias('mean'),F.min('pm25').alias('min'),F.max('pm25').alias('max'),F.stddev_samp('pm25').alias('std')).collect()
    def pandas_bench():return hp.groupby('station').pm25.agg(['count','mean','min','max','std'])
    spark_bench();pandas_bench();bench=[]
    for i in range(3):
        for engine,func in [('Spark',spark_bench),('Pandas',pandas_bench)]:
            tick=time.perf_counter();func();bench.append({'engine':engine,'repeat':i+1,'seconds':time.perf_counter()-tick})
    pd.DataFrame(bench).to_csv(root/'outputs/tables/benchmark_repeats.csv',index=False)
    metrics['benchmark_median_seconds']={e:statistics.median(r['seconds'] for r in bench if r['engine']==e) for e in ['Spark','Pandas']}
    metrics['output_hourly_records']=len(hp);metrics['analysis_elapsed_seconds']=time.perf_counter()-total
    spark.stop()
    from src.visualization import generate
    t=time.perf_counter();metrics['charts']=generate(root);metrics['visualization_seconds']=time.perf_counter()-t
    from src.verification import verify
    t=time.perf_counter();verification=verify(root,raw_pd);metrics['verification_seconds']=time.perf_counter()-t
    metrics['total_seconds_excluding_download']=time.perf_counter()-total
    (root/'outputs/metrics/performance.json').write_text(json.dumps(metrics,indent=2))
    print(json.dumps({'status':verification['status'],'raw_records':metrics['raw_records'],'hourly_records':len(hp),'charts':len(metrics['charts']),'seconds':metrics['total_seconds_excluding_download']},indent=2),flush=True)

if __name__=='__main__':main()
