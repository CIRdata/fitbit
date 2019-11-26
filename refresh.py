# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 12:24:50 2019

@author: croma
"""

import fitbit
import gather_keys_oauth2 as oauth2
import pandas as pd
import numpy as np
import datetime
import time
import os



f = open('settings', 'r')
settings_str = f.read()
f.close()

from ast import literal_eval
settings_dict = literal_eval(settings_str)

def date_fr_str(d):
    return datetime.datetime.date(datetime.datetime.strptime(d, '%Y-%m-%d'))
    
def date_fr_datetime(d):
    return datetime.datetime.date(d)

#connect to fitbit server
server = oauth2.OAuth2Server(settings_dict['client_id'], settings_dict['client_secret'])
server.browser_authorize()

ACCESS_TOKEN = str(server.fitbit.client.session.token['access_token'])
REFRESH_TOKEN = str(server.fitbit.client.session.token['refresh_token'])
auth2_client = fitbit.Fitbit(settings_dict['client_id'], settings_dict['client_secret'], oauth2=True, access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN)

initialdate = settings_dict['initialdate']
dateinterval = 30

#check we have a log of the historical fitbit data available
if os.path.exists('fitbit_data.pickle'):
    dfp = pd.read_pickle('fitbit_data.pickle')
    download_start = datetime.datetime.strptime(dfp['date'].max(), '%Y-%m-%d')
    download_start = datetime.datetime.strftime(download_start, '%Y-%m-%d')
else:
    download_start = initialdate


startdate = datetime.datetime.strptime(download_start, '%Y-%m-%d') 
enddate = startdate + datetime.timedelta(days=dateinterval)
today = datetime.datetime.now()
days = (today-startdate).days

weight_date = []
weight_fat = []
weight_time = []
weight_weight = []

for i in range(0,days,30):
    if i != 0:
        time.sleep(5)
    startdate_str = datetime.datetime.strftime(startdate, '%Y-%m-%d') 
    enddate_str = datetime.datetime.strftime(enddate, '%Y-%m-%d') 
    startdate = startdate + datetime.timedelta(days=dateinterval)
    enddate = enddate + datetime.timedelta(days=dateinterval)
    fit_bodyweight = auth2_client.get_bodyweight(base_date=startdate_str, end_date=enddate_str)
    for d in fit_bodyweight['weight']:
        weight_date.append(d['date'])
        weight_fat.append(d['fat'])
        weight_time.append(d['time'])
        weight_weight.append(d['weight'])
    

df = pd.DataFrame({'date':weight_date,'fatpercent':weight_fat, 'weight': weight_weight})

#store the raw data
if os.path.exists('fitbit_data.pickle'):
    df = df.append(dfp)
    os.remove('fitbit_data.pickle')

df.to_pickle('fitbit_data.pickle')
df.set_index('date')


#clean the data

#dedup on date by averaging fat%/weight by day
dfdd = df.groupby('date')['fatpercent', 'weight'].mean()

#list of dates we should have
dfdt = pd.DataFrame([today - datetime.timedelta(days=x) for x in range((today - datetime.datetime.strptime(initialdate, '%Y-%m-%d')).days)])
dfdt['date']=dfdt[0].dt.date
dfdd = dfdd.reset_index()
dfdd.date = pd.to_datetime(dfdd['date'])
dfdd.date = dfdd['date'].dt.date

#join list of dates we should have with data we do have, the non-match dates show nan fat%/weight
dfd = pd.merge(dfdt, dfdd, left_on='date', right_on='date',how='left')[['date','fatpercent','weight']].sort_values('date',ascending=True)
dfd = dfd.reset_index()
dfd = dfd.drop(['index'], axis = 1)

def row_ffill(x):
    
    #forwardfill: stepping thru the records this is the most recent non-nan value
    #errorcount: this a sequential count of nan values, it resets to zero with each non-nan value
    forwardfill = None
    errorcount = 0
    ret = []
    
    for datavalue in x:
        if ~np.isnan(datavalue):
            errorcount = 0
            forwardfill = datavalue
        else:
            datavalue = 0
            errorcount = errorcount + 1
        ret.append([datavalue, forwardfill, errorcount])
    return ret

def missing_values_fill(val):
    #run the ffill function in the forward as well as reverse directions
    fwd = row_ffill(val)
    rev = row_ffill(np.flip(val))

    #label columns and concatinate the forward and reversed record sets and concat into a dataframe

    df_rev = pd.DataFrame(np.flip(np.asarray(rev),axis=0),columns=['backdata', 'backfill', 'backnacount'])
    df_fwd = pd.DataFrame(np.asarray(fwd),columns=['forwarddata', 'forwardfill', 'forwardnacount'])
    df_calc = pd.concat([df_rev,df_fwd], axis=1)
    
    # calculate the fill value
    df_calc['totalcount']=df_calc.forwardnacount+df_calc.backnacount

    df_calc['ret'] = df_calc.forwardfill+(df_calc.backfill-df_calc.forwardfill)*\
        (df_calc.forwardnacount.div(df_calc.totalcount.where(df_calc.totalcount != 0, df_calc.backdata)))
    
    return df_calc['ret']

#fill in missing data
dfd['fatper_fill'] = missing_values_fill(dfd['fatpercent'])
dfd['weight_fill'] = missing_values_fill(dfd['weight'])

#find lead/trail 5 rolling data max/mins
dfd['fatper_fill_min_roll5_trail'] = dfd['fatper_fill'].rolling(5).min().shift(1).fillna(dfd['fatper_fill'])
dfd['fatper_fill_min_roll5_lead'] = dfd['fatper_fill'].rolling(5).min().shift(-5).fillna(dfd['fatper_fill'])

dfd['fatper_fill_max_roll5_trail'] = dfd['fatper_fill'].rolling(5).max().shift(1).fillna(dfd['fatper_fill'])
dfd['fatper_fill_max_roll5_lead'] = dfd['fatper_fill'].rolling(5).max().shift(-5).fillna(dfd['fatper_fill'])

#if fat% is more than 1% point greater or less than any of the measures +-5days we will set to nan
dfd.loc[(dfd.fatpercent < (dfd['fatper_fill_min_roll5_trail']-1)) & (dfd.fatpercent < (dfd['fatper_fill_min_roll5_lead']-1)),'fatpercent']=np.nan

#fill missing values created by nulling outliers
dfd['fatper_fill'] = missing_values_fill(dfd['fatpercent'])


#create a clean dataset for export
dfd['fat']=dfd.fatper_fill*dfd.weight_fill/100
dfd['lean']=dfd.weight_fill-dfd.fat
dfd_export = dfd[['date','weight_fill','lean','fat','fatper_fill']]
dfd_export.columns=['date','weight','lean','fat','fat_percent']


#store the cleaned data
if os.path.exists('fitbit_data_clean.pickle'):
    os.remove('fitbit_data_clean.pickle')

dfd_export.to_pickle('fitbit_data_clean.pickle')
