"""Acquire pinned public source files and inspect actual CSV schemas."""
import csv
import hashlib
import json
import urllib.request
from pathlib import Path
import pandas as pd

PM = 'PM2.5 (µg/m³)'
CATALOG = 'https://data.opencity.in/dataset/bengaluru-hourly-air-quality-reports'

def acquire(root):
    manifest = json.loads((root / 'data/manifest.json').read_text())
    for item in manifest:
        path = root / 'data/raw' / item['file']
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            with urllib.request.urlopen(item['url'], timeout=180) as response:
                path.write_bytes(response.read())
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != item['sha256']:
            raise ValueError(f'Source changed: {path.name}. Review the source and refresh manifest explicitly.')
    return manifest

def inspect_sources(root, manifest):
    inventory, columns, frames = [], [], []
    for item in manifest:
        frame = pd.read_csv(root / 'data/raw' / item['file'], dtype=str)
        if PM not in frame or 'Timestamp' not in frame:
            raise ValueError(f"Required fields absent from {item['file']}")
        times = pd.to_datetime(frame['Timestamp'], utc=True, errors='coerce')
        inventory.append(dict(file=item['file'], station=frame['Station Name'].iloc[0],
                              records=len(frame), bytes=item['bytes'], columns=len(frame.columns),
                              start_utc=str(times.min()), end_utc=str(times.max()),
                              timezone='UTC offset explicitly encoded in CSV', has_aqi='AQI' in frame,
                              pm25_unit='ug/m3', schema_compatible=list(frame.columns)==manifest[0]['columns']))
        for col in frame:
            profile=dict(file=item['file'], column=col, missing=int(frame[col].isna().sum()),
                         nonmissing=int(frame[col].notna().sum()))
            if col not in ['Station ID','State','City','Station Name','Timestamp']:
                num=pd.to_numeric(frame[col],errors='coerce')
                profile.update(nonnumeric_nonmissing=int((frame[col].notna() & num.isna()).sum()),
                               numeric_min=num.min(),numeric_max=num.max(),negative_count=int((num<0).sum()))
            columns.append(profile)
        frames.append(frame[['Station Name','Timestamp',PM]].copy())
    pd.DataFrame(inventory).to_csv(root/'outputs/tables/dataset_inventory.csv',index=False)
    pd.DataFrame(columns).to_csv(root/'outputs/tables/column_completeness.csv',index=False)
    return pd.concat(frames, ignore_index=True)

def read_spark(spark, root, manifest):
    paths=[str((root/'data/raw'/m['file']).resolve()) for m in manifest]
    # Each supplied file contains a one-field year separator. Retain it for the audit.
    # PERMISSIVE fills its absent fields with null; cleaning assigns a rejection reason.
    raw=spark.read.option('header',True).option('mode','PERMISSIVE').csv(paths)
    (root/'outputs/metrics/raw_schema.json').write_text(raw.schema.json())
    return raw
