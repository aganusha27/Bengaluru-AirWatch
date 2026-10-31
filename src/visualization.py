"""Eight figures from saved Spark output tables, without synthetic values."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate(root):
    tables=root/'outputs/tables'; out=root/'outputs/charts'
    def load(name):return pd.read_csv(tables/f'{name}.csv')
    def short(s):return s.split(',')[0]
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,
                         'figure.dpi':130,'savefig.dpi':180})
    def save(fig,name):
        fig.tight_layout();fig.savefig(out/name,bbox_inches='tight');plt.close(fig)
    stats=load('station_statistics').sort_values('mean',ascending=False)
    fig,ax=plt.subplots(figsize=(9,4.7));ax.bar(stats.station.map(short),stats['mean'],color='#246b83')
    ax.set(title='Average hourly PM2.5 by station',ylabel='PM2.5 (µg/m³)',xlabel='Monitoring station')
    ax.tick_params(axis='x',rotation=22);save(fig,'01_station_average.png')
    daily=load('daily');daily['day']=pd.to_datetime(daily.day)
    fig,ax=plt.subplots(figsize=(10,4.8))
    for s,g in daily.groupby('station'):
        # Gaps stay missing. Require >=18 valid hours for plotted daily means.
        g=g.set_index('day').sort_index();series=g['mean'].where(g.n>=18).asfreq('D')
        ax.plot(series.index,series,linewidth=.75,alpha=.85,label=short(s))
    ax.set(title='Daily PM2.5 from valid hourly means',ylabel='PM2.5 (µg/m³)',xlabel='Date in Bengaluru time')
    ax.set_xlim(pd.Timestamp('2024-01-01'),pd.Timestamp('2025-12-31'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3));ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.legend(ncol=3,fontsize=8);save(fig,'02_daily_time_series.png')
    hp=load('hourly_pattern');fig,ax=plt.subplots(figsize=(9,4.8))
    for s,g in hp.groupby('station'):
        g=g.sort_values('hour_ist');ax.plot(g.hour_ist,g['mean'],label=short(s),marker='.',linewidth=1.5)
    ax.set(title='PM2.5 profile across the day',xlabel='Hour of day IST',ylabel='PM2.5 (µg/m³)',xticks=range(0,24,2))
    ax.legend(ncol=3,fontsize=8);save(fig,'03_hourly_pattern.png')
    w=load('weekday_weekend').pivot(index='station',columns='day_type',values='mean');w.index=w.index.map(short)
    fig,ax=plt.subplots(figsize=(9,4.7));w[['Weekday','Weekend']].plot.bar(ax=ax,color=['#246b83','#d09145'])
    ax.set(title='Weekday and weekend hourly PM2.5',xlabel='Monitoring station',ylabel='PM2.5 (µg/m³)');ax.tick_params(axis='x',rotation=22)
    ax.legend(title='Day type')
    save(fig,'04_weekday_weekend.png')
    m=load('monthly');m['date']=pd.to_datetime(m.month+'-01');fig,ax=plt.subplots(figsize=(9,4.7))
    for s,g in m.groupby('station'):
        g=g.sort_values('date');ax.plot(g.date,g['mean'],marker='.',label=short(s))
    ax.set(title='Monthly PM2.5 trend',xlabel='Month in Bengaluru time',ylabel='PM2.5 (µg/m³)')
    ax.set_xlim(pd.Timestamp('2024-01-01'),pd.Timestamp('2025-12-01'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3));ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.legend(ncol=3,fontsize=8);save(fig,'05_monthly_trend.png')
    fig,ax=plt.subplots(figsize=(9,4.7));ax.bar(stats.station.map(short),stats.stddev,color='#7e639e')
    ax.set(title='Variability of hourly PM2.5',xlabel='Monitoring station',ylabel='Sample standard deviation (µg/m³)')
    ax.tick_params(axis='x',rotation=22);save(fig,'06_station_variability.png')
    mat=hp.pivot(index='station',columns='hour_ist',values='mean').sort_index();fig,ax=plt.subplots(figsize=(10,4.4))
    im=ax.imshow(mat,aspect='auto',cmap='YlOrRd');ax.set_yticks(range(len(mat)),mat.index.map(short));ax.set_xticks(range(0,24,2),range(0,24,2))
    ax.set(title='Station and hour PM2.5 pattern',xlabel='Hour of day IST',ylabel='Monitoring station');fig.colorbar(im,ax=ax,label='PM2.5 (µg/m³)')
    save(fig,'07_station_hour_heatmap.png')
    pairs=load('synchronization_pairs');names=sorted(stats.station);matrix=np.full((len(names),len(names)),np.nan)
    for row in pairs.itertuples():
        i,j=names.index(row.station_a),names.index(row.station_b);matrix[i,j]=matrix[j,i]=row.lift
    fig,ax=plt.subplots(figsize=(8.8,5.5));im=ax.imshow(matrix,cmap='YlOrRd',vmin=0)
    ax.set_xticks(range(len(names)),[short(s) for s in names],rotation=30,ha='right');ax.set_yticks(range(len(names)),[short(s) for s in names])
    for i in range(len(names)):
        for j in range(len(names)):
            ax.text(j,i,'-' if i==j else f'{matrix[i,j]:.2f}',ha='center',va='center',fontsize=10)
    ax.set(title='Simultaneous PM2.5 spike lift over independence',xlabel='Monitoring station',ylabel='Monitoring station')
    fig.colorbar(im,ax=ax,label='Observed / expected simultaneous spike hours')
    save(fig,'08_spike_synchronization.png')
    return sorted(p.name for p in out.glob('*.png'))
