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

    #Work stoppage:
work_stop = work_stop.rename(columns={'Days idle, cumulative for this work stoppage[3]': 'TotalDaysIdle'})

#Remove the weird [4] and make the column an integer data type:
# work_stop = work_stop.replace('[4]', np.NaN) #NOT NEEDED
work_stop['TotalDaysIdle'] = pd.to_numeric(work_stop['TotalDaysIdle'], errors='coerce', downcast='integer')
work_stop['TotalDaysIdle'] = work_stop['TotalDaysIdle'].astype('Int64')

#Fix workstop end date:
work_stop['Work stoppage ending date'] = pd.to_datetime(work_stop['Work stoppage ending date'], errors='coerce', format = '%Y-%m-%d')

#Column for duration of work stoppage:
    #Represents number of days
work_stop['WSDuration'] = (work_stop['Work stoppage ending date'] - work_stop['Work stoppage beginning date'])/np.timedelta64(1,'D')


#VISUALIZATIONS:
#NOTES:
    #x-axes, per usual, are squished and need to be corrected. Can do this in jupyter more easily than Spyder.
    

#Minimum wage state data:
minwagestate.hist(column='Effective.Minimum.Wage')
minwagestate.boxplot(column='Effective.Minimum.Wage', by = ["State"], rot = 75)


#Work Stoppage state data:
    #Need to put states into a list instead of a string:
        # words = text.split(",")
    #Need to quantify data by state using list comprehension as states are in lists:
work_stop.boxplot(column='WSDuration', by = ["States"], rot = 75)

work_stop.hist(column = "TotalDaysIdle") #Not super helpful


#TOMORROW TO-DO:
    ##CONFIGURE(?) GIT LFS BECAUSE APPARENTLY THESE FILES ARE TOO FREAKING BIG...UGH
#1) make histogram of work stop
#2) MORE EDA OF TIME SERIES
#3) Make choropleth of states work stoppage and minimum wage - will need to do in plotly and dash
#4) Can try to do jupyter-dash because prof wants it all in notebook form

work_stop.dtypes
