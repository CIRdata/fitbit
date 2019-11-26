
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

import datetime
import time
import os
import sys

args = sys.argv

start_of_analysis = args[1]

def datetime_fr_str(d):
    return datetime.datetime.strptime(d, '%Y-%m-%d')

def date_fr_datetime(d):
    return datetime.datetime.date(d)

def date_fr_str(d):
    return date_fr_datetime(datetime_fr_str(d))

if len(args) == 2:
    end_of_analysis = date_fr_datetime(datetime.datetime.now())
else:
    end_of_analysis = date_fr_str(args[2])
eoa_date = datetime_fr_str(start_of_analysis)
soa_date = date_fr_datetime(eoa_date-datetime.timedelta(days=7))
eoa_date = date_fr_datetime(eoa_date)

df_bm = pd.read_pickle('fitbit_data_clean.pickle')

dfd_export = df_bm

df_bm['date']=pd.to_datetime(df_bm['date']).apply(lambda x: x.date())
fat_bm = df_bm[(df_bm['date']>=soa_date) & (df_bm['date']<=eoa_date)][['fat']].mean()['fat']
lean_bm = df_bm[(df_bm['date']>=soa_date) & (df_bm['date']<=eoa_date)][['lean']].mean()['lean']
df_bm['fat_bm'] = fat_bm
df_bm['lean_bm'] = lean_bm

df_bm = df_bm[(df_bm['date']>=eoa_date) & (df_bm['date']<=(end_of_analysis))][['date','lean','fat','lean_bm','fat_bm']]


df_bm['weight'] = df_bm.lean+df_bm.fat
df_bm[['date','weight','lean','fat']].tail()


df_bm['date_datetime'] = pd.to_datetime(df_bm.date)


df_wk = df_bm.set_index('date_datetime')[['lean','fat','lean_bm','fat_bm']].resample('W').mean()
df_mth = df_bm.set_index('date_datetime')[['lean','fat','lean_bm','fat_bm']].resample('M').mean()

fig, ax = plt.subplots(2,2,figsize=(15,12))

ax[0,0].plot(pd.to_datetime(df_bm['date']),df_bm.fat-df_bm.fat_bm)
ax[0,0].plot(pd.to_datetime(df_bm['date']),df_bm.lean-df_bm.lean_bm)
ax[0,0].legend(['Fat Mass','Lean Mass'])
ax[0,0].set_ylabel('Change (lbs)')
ax[0,0].set(title='Change from Benchmark')

ax[0,1].stackplot(pd.to_datetime(df_bm['date']),df_bm.fat,df_bm.lean)
ax[0,1].set_ylabel('lbs')
ax[0,1].legend(['Fat Mass','Lean Mass'],loc=8)
ax[0,1].set(title='Total Weight')

ax[1,0].set(title='Change from Benchmark by Month')
ax[1,0].plot(df_mth.index, df_mth.fat-df_mth.fat_bm)
ax[1,0].plot(df_mth.index, df_mth.lean-df_mth.lean_bm)
ax[1,0].legend(['Fat Mass','Lean Mass'])
ax[1,0].set_ylabel('Change (lbs)')

ax[1,1].set(title='Change from Benchmark by Last 4 Weeks')
ax[1,1].plot(df_wk[-4:].index, df_wk[-4:].fat-df_wk[-4:].fat_bm)
ax[1,1].plot(df_wk[-4:].index, df_wk[-4:].lean-df_wk[-4:].lean_bm)
ax[1,1].legend(['Fat Mass','Lean Mass'])
ax[1,1].set_ylabel('Change (lbs)')