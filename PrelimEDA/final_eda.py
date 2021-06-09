#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 30 16:13:39 2021

@author: nyssacornelius
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels
import pickle
import plotly.express as px
from scipy import stats as sts
from scipy.stats import pearsonr
from statsmodels.stats.multicomp import pairwise_tukeyhsd

clean_national_data = pd.read_pickle(".\\Cleaned\\clean_national_data.pkl")
clean_state_data = pd.read_pickle(".\\Cleaned\\clean_state_data.pkl")
work_stop = pd.read_pickle(".\\PrelimEDA\\work_stop.pkl")
# minwagestate = pd.read_pickle(".\\PrelimEDA\\minwagestate.pkl")
minwagestate = pd.read_csv("/Users/nyssacornelius/Desktop/COMP4477/FProj/FProj/min_wage_state.csv", usecols=["Year", "State", "Federal.Minimum.Wage", "Effective.Minimum.Wage","Effective.Minimum.Wage.2020.Dollars","CPI.Average"])


minwagestate = minwagestate[(minwagestate['State']!= 'District of Columbia') &\
                          (minwagestate['State']!= 'U.S. Virgin Islands') &\
                              (minwagestate['State']!= 'Country Of Mexico') &\
                                  (minwagestate['State']!= 'Puerto Rico') &\
                                  (minwagestate['State']!= 'Guam')]

#do industries with the lowest wages have the more work stoppages?
#do states with the lowest minimum wages have more work stoppages?

# CLEAN UP DATA:
    #Minimum wage:
minwagestate['State'] = minwagestate['State'].astype('string')

us_state_abbrev = {'Alabama': 'AL', 'Alaska': 'AK',
'Arizona': 'AZ','Arkansas': 'AR',
'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}                                                           

minwagestate['StateCode'] = minwagestate['State'].map(us_state_abbrev)                                                             

#Work stoppage:
work_stop = work_stop.rename(columns={'Days idle, cumulative for this work stoppage[3]': 'TotalDaysIdle', 'Industry code[1]': 'IndustryCode', 'Work stoppage beginning date': 'StartDate', 'Work stoppage ending date': 'EndDate'})

# #Remove the weird [4] and make the column an integer data type:
# # work_stop = work_stop.replace('[4]', np.NaN) #NOT NEEDED
work_stop['TotalDaysIdle'] = pd.to_numeric(work_stop['TotalDaysIdle'], errors='coerce', downcast='integer')
work_stop['TotalDaysIdle'] = work_stop['TotalDaysIdle'].astype('Int64')

# #Fix workstop end date:
work_stop['EndDate'] = pd.to_datetime(work_stop['EndDate'], errors='coerce', format = '%Y-%m-%d')

# #Column for duration of work stoppage:
#     #Represents number of days
work_stop['WSDuration'] = (work_stop['EndDate'] - work_stop['StartDate'])/np.timedelta64(1,'D')+1
work_stop['WSDuration'] = work_stop['WSDuration']+1

#Change states from string to list of strings:
work_stop['States'] = work_stop['States'].str.split(",")

#Minimum wage state data:
# minwagestate.hist(column='Effective.Minimum.Wage')
# minwagestate.boxplot(column='Effective.Minimum.Wage', by = ["State"], rot = 75)


#Work Stoppage state data:
    #Need to quantify data by state using list comprehension as states are in lists:
#Are these two essentially the same? Neither are normal, left skewed.
# work_stop.hist(column='WSDuration')
# work_stop.hist(column = "TotalDaysIdle")


#TOMORROW TO-DO:
    ##CONFIGURE(?) GIT LFS BECAUSE APPARENTLY THESE FILES ARE TOO FREAKING BIG...UGH - still don't understand
#1) make histogram of work stop - done, not helpful
#3) Make choropleth of states work stoppage frequency - will need to do in plotly express


#Reminders:
    #compare wage data for a work stoppage at the state level with wage data
    #for that industry at the national level
    
    #choropleth maps of states for work stoppage counts.
    
    
#INDUSTRY DATA INFORMATION:
    #Willing to go down to 3-digit NAICS code, if not fruitful then up to only 2-digit NAICS
    #Best file will likely be 2-6 digit NAICS code xlsx file

iCodes = pd.read_csv('/Users/nyssacornelius/Desktop/COMP4477/FProj/FProj/2017NAICS_Codes2_6digit.csv', header=0, usecols=[0,1,2], skiprows=[1])
iCodes = iCodes.rename(columns={'2017 NAICS US   Code': 'NAICS_Code2017', '2017 NAICS US Title': 'IndustryTitle'})

#Remove wonky unicode character:
iCodes['IndustryTitle'] = iCodes['IndustryTitle'].str.replace('\ufffd', '')


#Will NAICS code need to be treated as a string to find it in work stoppage data?
#How will we map industries from NAICS to work stop?
#Would we use map to do this?

#Extract only codes with 2-digits:
codes2digit = iCodes.loc[iCodes['NAICS_Code2017'].str.contains('^\d{2}$'), ['NAICS_Code2017']].values

#Extract only 3-digit codes:
codes3digit = iCodes.loc[iCodes['NAICS_Code2017'].str.contains('^\d{3}$'), ['NAICS_Code2017']].values

#Apply a dictionary to all 3-digit codes:
# iCodes['2digit'] = iCodes['NAICS_Code2017'].str.extract(r'(\d{2})')
iCodes['3digit'] = iCodes['NAICS_Code2017'].str.extract(r'(\d{3})')

#Industry code abbreviated for work stop:
work_stop['iCodeAb'] = work_stop['IndustryCode'].astype(str).str.extract(r'(\d{3})')

# #fill in nans:
work_stop.loc[work_stop['iCodeAb'].isnull(), ['iCodeAb']] = work_stop.loc[work_stop['iCodeAb'].isnull(), ['IndustryCode']].values

# #Copy column:
work_stop['iTitle'] = work_stop['iCodeAb'].astype(str)

# #Get name from industry code:
work_stop['iTitle'] = work_stop['iTitle'].replace({k:v for k, v in zip(iCodes['NAICS_Code2017'], iCodes['IndustryTitle'])})


#Industry strikes aggregated by count:
industryCounts = work_stop['iTitle'].value_counts().reset_index().rename({'index': 'Industry', 'iTitle': 'Counts'}, axis = 1)

#Frequency of strikes by state:
otherStates = {k:'Other' for k in ['East Coast States', 'Nationwide', 'Interstate']}
stateCounts = pd.Series(np.concatenate(work_stop['States'])).str.strip().replace(otherStates)
stateCounts = pd.Series(np.where(stateCounts == "", None, stateCounts)).value_counts().reset_index().rename({'index': 'State', 0: 'Counts'}, axis = 1)


#Begin State-Metro Employment and Wage Data work:
smdata = pd.read_csv('https://download.bls.gov/pub/time.series/sm/sm.data.1.AllData', sep = '\t')

smdata.shape
smdata.columns

#Remove whitespace:
smdata.columns = smdata.columns.str.strip()
smdata['series_id'] = smdata['series_id'].str.strip()
smdata['value'] = smdata.value.astype(str).str.strip()

#Convert value to float

smdata['state_code'] = smdata['series_id'].str.extract(r'(\d{2})')
smdata = smdata.loc[~smdata['state_code'].isin(['00','11','72','78','99'])]

#Create columns for data types in series id:
smdata['data_type'] = smdata['series_id'].str.extract(r'(\d{2}$)')
smdata.head(20)

data_types = {'01': 'Employees',
              '11': 'AvgWeeklyEarnings'
              }

smdata = smdata.loc[smdata['data_type'].isin(data_types.keys())]
smdata['data_type'] = smdata['data_type'].replace(data_types)
smdata['value'] = np.where(smdata['value'] == '-', np.nan, smdata['value'])
smdata['value'] = smdata['value'].astype(float)

smdata['industry_code'] = smdata['series_id'].str.extract(r'\d{7}(\d{5})')+'000'


indCode = pd.read_csv('https://download.bls.gov/pub/time.series/sm/sm.industry', sep = '\t', dtype = {'industry_code': str})

mergedat = pd.merge(smdata, indCode, on = 'industry_code', how = 'left')

mergedat.loc[mergedat['industry_code'] != '00000000']
mergedat.loc[mergedat['industry_code'] == '90930000']


manInd = ['Utilities', 'Transportation and Warehousing', 'Professional, Scientific, and Technical Services',
          'State Government', 'Indian Tribes', 'Logging', 'Educational Services', 'Federal Government',
          'Federal Government', 'Federal Government', 'Local Government']
manIndreplace = {k:v for k,v in zip(mergedat.loc[mergedat['industry_name'].isnull(), 'industry_code'].unique(), manInd)}

mergedat.industry_code.replace(manIndreplace, inplace = True)
mergedat.loc[mergedat['industry_name'].isnull(), 'industry_name'] = mergedat.loc[mergedat['industry_name'].isnull(), 'industry_code']

stateCodes = pd.read_csv('https://download.bls.gov/pub/time.series/sm/sm.state', sep = '\t', dtype = {'state_code': str})

final_data = pd.merge(mergedat, stateCodes, on = 'state_code', how = 'left')

final_data.isnull().sum()
final_data.state_name.value_counts()

final_data.drop(['series_id', 'period', 'footnote_codes', 'state_code', 'industry_code'], axis = 1, inplace = True)

#Make pivot table
finalfull = final_data.pivot_table(index = ['state_name','industry_name','year'], columns = 'data_type', values = 'value', aggfunc = 'mean').reset_index()
finalfull.columns = finalfull.columns.str.strip()
final_earnings = finalfull.copy()
final_earnings = final_earnings.dropna().reset_index()
final_earnings = final_earnings.drop(labels = 'index', axis = 1)

final_earnings['StateCode'] = final_earnings['state_name'].map(us_state_abbrev)
finalfull['StateCode'] = finalfull['state_name'].map(us_state_abbrev)


#Need to group by industry and state, respectively and take the average over all years since 2007
earnInd = final_earnings.groupby(['industry_name'])['AvgWeeklyEarnings'].mean().sort_values(ascending = False)
earnInd = earnInd.reset_index()

earnState = final_earnings.groupby(['StateCode'])['AvgWeeklyEarnings'].mean().sort_values(ascending = False)
earnState = earnState.reset_index()

#Education and Health services have two of the highest rates of strike - in mid-low range of average weekly earnings
#However, this could be skewed by professionals in health industry that make a great deal more
#Can't know from this data
#Leisure is lowest average weekly earnings


cormin = minwagestate.corr(method='spearman')
#years increase eff min in 2020 $ decreases, obviously CPI increases almost 1:1
#Min wage 2020 $s decreases as years increase
#Min wage 2020 $s decreases as CPI average increases


#One way ANOVA on States Minimum Wage:
stateminwage = []
for state in list(minwagestate.State.unique()):
    stateminwage.append(list(minwagestate.loc[minwagestate['State'] == state,
                                              'Effective.Minimum.Wage.2020.Dollars']))

fvalue, pvalue = sts.f_oneway(*stateminwage)

m_comp = pairwise_tukeyhsd(endog=minwagestate['Effective.Minimum.Wage.2020.Dollars'], groups=minwagestate['State'],
                           alpha=0.05)
print(m_comp.summary())

#Have to look at in text file, too many groups:
with open('mcomp_stateminwage.txt', 'w') as f:
        print(m_comp.summary(), file=f)


#One way ANOVA on Avg Wage States:
avgwagestate = []
for state in list(final_earnings.state_name.unique()):
    avgwagestate.append(list(final_earnings.loc[final_earnings['state_name'] == state,
                                              'AvgWeeklyEarnings']))

fvalue_statewage, pvalue_statewage = sts.f_oneway(*avgwagestate)

m_comp_statewage = pairwise_tukeyhsd(endog=final_earnings['AvgWeeklyEarnings'], groups=final_earnings['state_name'],
                           alpha=0.05)

#Have to look at in text file, too many groups:
with open('mcomp_statewage.txt', 'w') as f:
        print(m_comp_statewage.summary(), file=f)

#One way ANOVA for Avg Wage by Industry:
avgwageindustry = []
for industry in list(final_earnings.industry_name.unique()):
    avgwageindustry.append(list(final_earnings.loc[final_earnings['industry_name'] == industry,
                                              'AvgWeeklyEarnings']))

fvalue_industrywage, pvalue_industrywage = sts.f_oneway(*avgwageindustry)

m_comp_industrywage = pairwise_tukeyhsd(endog=final_earnings['AvgWeeklyEarnings'], groups=final_earnings['industry_name'],
                           alpha=0.05)

with open('mcomp_industrywage.txt', 'w') as f:
        print(m_comp_industrywage.summary(), file=f)

#Subtract minwage from effective, if 0 = minwage state

#Mean of 0s and 1s for a state by comparing state min wage
#state min wage > fed min wage = 1, else 0
#mean > .4 = 1, else 0 for minwage state


#df: states, strikes, minwage or not
minwagestate['MinWageStatus'] = np.where((minwagestate['Effective.Minimum.Wage']-minwagestate['Federal.Minimum.Wage']) > 0, 1, 0)
state_status = minwagestate.groupby(['State'])['MinWageStatus'].mean().reset_index()
state_status['MinWageStatus'] = np.round(state_status['MinWageStatus'], 2)

state_status['MinWageStatus'] = np.where(state_status['MinWageStatus'] >= 0.4, 'GreaterMinWage', 'MinWage')

#Get full names for stateCounts in statestrikes:
statestrikes = stateCounts.copy()
statestrikes.State.replace({v:k for k,v in us_state_abbrev.items()}, inplace = True)

#Merge on state_status state, WY and SD are missing, need to be dropped:
wagestrike = pd.merge(state_status, statestrikes, on = 'State', how = 'left').dropna()

#One way ANOVA for MinWage and Strikes by State:
minornot = []
for status in list(wagestrike.MinWageStatus.unique()):
    minornot.append(list(wagestrike.loc[wagestrike['MinWageStatus'] == status,
                                              'Counts']))

fvalue_strikes, pvalue_strikes = sts.f_oneway(*minornot)

m_comp_strikes = pairwise_tukeyhsd(endog=wagestrike['Counts'], groups=wagestrike['MinWageStatus'],
                           alpha=0.05)

print(m_comp_strikes.summary())
#would reject because not significant
#however, minimum wage states do have less strikes, but it's not significantly different
#could still be due to chance


#Add in information for minimum wage data

# work_stop.to_pickle(".\\PrelimEDA\\work_stop.pkl")
# finalfull.to_pickle(".\\PrelimEDA\\finalfull.pkl")
# final_earnings.to_pickle(".\\PrelimEDA\\final_earnings.pkl")
# minwagestate.to_pickle(".\\PrelimEDA\\minwagestate.pkl")

# final_earnings.industry_name.value_counts()

# finalfull.to_csv('finalfull.csv', index = False)
# final_earnings.to_csv('final_earnings.csv', index = False)

