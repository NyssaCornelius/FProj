#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 30 16:13:39 2021

@author: nyssacornelius
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import plotly
import xlrd

clean_national_data = pd.read_pickle(".\\Cleaned\\clean_national_data.pkl")
clean_state_data = pd.read_pickle(".\\Cleaned\\clean_state_data.pkl")
work_stop = pd.read_pickle(".\\PrelimEDA\\work_stop.pkl")
minwagestate = pd.read_csv("/Users/nyssacornelius/Desktop/COMP4477/FProj/FProj/min_wage_state.csv", usecols=["Year","State","Effective.Minimum.Wage","Effective.Minimum.Wage.2020.Dollars","CPI.Average"])

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
work_stop = work_stop.rename(columns={'Days idle, cumulative for this work stoppage[3]': 'TotalDaysIdle', 'Industry code[1]': 'IndustryCode'})

#Remove the weird [4] and make the column an integer data type:
# work_stop = work_stop.replace('[4]', np.NaN) #NOT NEEDED
work_stop['TotalDaysIdle'] = pd.to_numeric(work_stop['TotalDaysIdle'], errors='coerce', downcast='integer')
work_stop['TotalDaysIdle'] = work_stop['TotalDaysIdle'].astype('Int64')

#Fix workstop end date:
work_stop['Work stoppage ending date'] = pd.to_datetime(work_stop['Work stoppage ending date'], errors='coerce', format = '%Y-%m-%d')

#Column for duration of work stoppage:
    #Represents number of days
work_stop['WSDuration'] = (work_stop['Work stoppage ending date'] - work_stop['Work stoppage beginning date'])/np.timedelta64(1,'D')+1
# work_stop['WSDuration'] = work_stop['WSDuration']+1

#Change states from string to list of strings:
work_stop['States'] = work_stop['States'].str.split(",")

#VISUALIZATIONS:
#NOTES:
    #x-axes, per usual, are squished and need to be corrected. Can do this in jupyter more easily than Spyder.
    

#Minimum wage state data:
# minwagestate.hist(column='Effective.Minimum.Wage')
# minwagestate.boxplot(column='Effective.Minimum.Wage', by = ["State"], rot = 75)


#Work Stoppage state data:
    #Need to put states into a list instead of a string:
        # words = text.split(",")
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
# iCodes['IndustryTitle'] = iCodes['IndustryTitle'].astype('|S')


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

#fill in nans:
work_stop.loc[work_stop['iCodeAb'].isnull(), ['iCodeAb']] = work_stop.loc[work_stop['iCodeAb'].isnull(), ['IndustryCode']].values

#Copy column:
work_stop['iTitle'] = work_stop['iCodeAb'].astype(str)

#Get name from industry code:
work_stop['iTitle'] = work_stop['iTitle'].replace({k:v for k, v in zip(iCodes['NAICS_Code2017'], iCodes['IndustryTitle'])})


#Industry strikes aggregated by count:
work_stop['iTitle'].value_counts()

#Frequency of strikes by state:
otherStates = {k:'Other' for k in ['East Coast States', 'Nationwide', 'Interstate']}
stateCounts = pd.Series(np.concatenate(work_stop['States'])).str.strip().replace(otherStates)
stateCounts = pd.Series(np.where(stateCounts == "", None, stateCounts)).value_counts().reset_index().rename({'index': 'State', 0: 'Counts'}, axis = 1)
 #Need to look and see what they mean by nationwide, east coast states, and interstate



