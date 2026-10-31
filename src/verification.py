"""Independent pandas recomputation of the real-data Spark results."""
import json
import numpy as np
import pandas as pd
from .preprocessing import pandas_reference

def verify(root,raw):
    ref=pandas_reference(raw)
    actual=pd.read_csv(root/'data/processed/hourly_pm25.csv',parse_dates=['timestamp'])
    keys=['station','timestamp'];cols=keys+['pm25','valid_quarters']
    a=actual[cols].sort_values(keys).reset_index(drop=True)
    b=ref[cols].sort_values(keys).reset_index(drop=True)
    pd.testing.assert_frame_equal(a,b,check_dtype=False,rtol=1e-10,atol=1e-8)
    checks=['Every processed hourly record matches independent pandas cleaning and aggregation']
    stats=pd.read_csv(root/'outputs/tables/station_statistics.csv').set_index('station').sort_index()
    gs=ref.groupby('station').pm25
    expected=gs.agg(['count','mean','median','min','max','std'])
    for out_col,ref_col in [('valid_hours','count'),('mean','mean'),('median','median'),('min','min'),('max','max'),('stddev','std')]:
        np.testing.assert_allclose(stats[out_col],expected[ref_col],rtol=1e-9,atol=1e-8)
    np.testing.assert_allclose(stats.q25,gs.quantile(.25),rtol=1e-9,atol=1e-8)
    np.testing.assert_allclose(stats.q75,gs.quantile(.75),rtol=1e-9,atol=1e-8)
    np.testing.assert_allclose(stats.iqr,gs.quantile(.75)-gs.quantile(.25),rtol=1e-9,atol=1e-8)
    np.testing.assert_allclose(stats.cv,expected['std']/expected['mean'],rtol=1e-9,atol=1e-8)
    checks.append('All station counts and summary statistics match pandas')
    thresholds=pd.read_csv(root/'outputs/tables/spike_summary.csv').set_index('station').sort_index()
    q=gs.quantile(.95)
    np.testing.assert_allclose(thresholds.threshold_p95,q,rtol=1e-10,atol=1e-8)
    ref['spike']=(ref.pm25>ref.station.map(q)).astype(int)
    np.testing.assert_array_equal(thresholds.spike_hours,ref.groupby('station').spike.sum().sort_index())
    checks.append('Exact 95th percentiles and strict exceedance counts match pandas')
    pairs=pd.read_csv(root/'outputs/tables/synchronization_pairs.csv')
    for r in pairs.itertuples():
        aa=ref[ref.station==r.station_a].set_index('timestamp').spike
        bb=ref[ref.station==r.station_b].set_index('timestamp').spike
        ab=pd.concat([aa.rename('a'),bb.rename('b')],axis=1).dropna()
        assert len(ab)==r.overlap_hours
        assert int(ab.a.sum())==r.a_spike_hours and int(ab.b.sum())==r.b_spike_hours
        both=int((ab.a*ab.b).sum());assert both==r.both_spike_hours
        ex=ab.a.sum()*ab.b.sum()/len(ab)
        np.testing.assert_allclose(ex,r.expected_independent_hours,atol=1e-8)
        np.testing.assert_allclose(both/ex,r.lift,rtol=1e-9)
        np.testing.assert_allclose(both/len(ab),r.joint_rate,rtol=1e-9)
        np.testing.assert_allclose(both/(ab.a.sum()+ab.b.sum()-both),r.jaccard,rtol=1e-9)
    checks.append('All 15 station pairs match pandas inner-join spike counts and independence baseline')
    temporal={
        'hourly_pattern':(['station','hour_ist'],ref.assign(hour_ist=ref.timestamp.dt.hour)),
        'monthly':(['station','month'],ref.assign(month=ref.timestamp.dt.strftime('%Y-%m'))),
        'daily':(['station','day'],ref.assign(day=ref.timestamp.dt.strftime('%Y-%m-%d'))),
        'day_of_week':(['station','weekday_monday0'],ref.assign(weekday_monday0=ref.timestamp.dt.weekday)),
        'weekday_weekend':(['station','day_type'],ref.assign(day_type=np.where(ref.timestamp.dt.weekday>=5,'Weekend','Weekday')))
    }
    for name,(keys,x) in temporal.items():
        exp=x.groupby(keys).pm25.agg(['mean','count']).sort_index()
        act=pd.read_csv(root/f'outputs/tables/{name}.csv').set_index(keys).sort_index()
        np.testing.assert_allclose(act['mean'],exp['mean'],rtol=1e-9,atol=1e-8)
        np.testing.assert_array_equal(act.n,exp['count'])
    checks.append('All five temporal table means and sample counts match pandas')
    complete=ref.pivot(index='timestamp',columns='station',values='spike').dropna()
    saved=pd.read_csv(root/'outputs/tables/complete_case_spike_distribution.csv').set_index('spiking_stations')['count']
    counts=complete.sum(axis=1).astype(int).value_counts().sort_index()
    assert saved.to_dict()==counts.to_dict()
    checks.append('Six-station complete-case spike distribution matches pandas')
    matched=ref[ref.timestamp.isin(complete.index)]
    common_stats=pd.read_csv(root/'outputs/tables/common_case_station_statistics.csv').set_index('station').sort_index()
    gc=matched.groupby('station').pm25
    common_expected=gc.agg(['count','mean','median','min','max','std'])
    for out_col,ref_col in [('valid_hours','count'),('mean','mean'),('median','median'),('min','min'),('max','max'),('stddev','std')]:
        np.testing.assert_allclose(common_stats[out_col],common_expected[ref_col],rtol=1e-9,atol=1e-8)
    np.testing.assert_allclose(common_stats.q25,gc.quantile(.25),rtol=1e-9,atol=1e-8)
    np.testing.assert_allclose(common_stats.q75,gc.quantile(.75),rtol=1e-9,atol=1e-8)
    checks.append('Common-hour station summaries and quartiles independently match pandas')
    assert len(list((root/'outputs/charts').glob('*.png')))==8
    checks.append('All eight requested chart artifacts exist')
    result=dict(status='PASS',checks=checks,hourly_records=len(ref),station_pairs=len(pairs))
    (root/'outputs/metrics/verification.json').write_text(json.dumps(result,indent=2))
    return result
