#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import pickle
from tabula import read_pdf
import math


# In[2]:


#This option is to prevent pandas from truncating columns that are strings.
#Old versions of pandas may need -1 instead of None
pd.set_option('display.max_colwidth', None)


#This specifies how many days of employement data we require before a work stoppage. 
#Right now it is set to six months, meaning we are only working
#with work stoppages where we have at least six months of data before the work
#stoppage began and six months of data after the work stoppage ended.
time_window = pd.Timedelta(180,"days")


#This specifies to print out messages while processing the data.
be_verbose = True


# In[3]:


#This cell loads in all the data.
#The cleaned data is stored later, so this doesn't need to be rerun unless we're improving the data.


#This excel file contains data on each work stoppage.
#Industry is by 2017 NAICS code. 
#This data is from 1988 to 2020.
#We changed the xlsx file to a xls file because of compatibility issues with pandas reading a xlsx file with xlrd.
#This file is originally from https://www.bls.gov/web/wkstp/monthly-listing.xlsx
work_stoppage_df = pd.read_excel("work_stop_monthly.xls", 
    header=1, skipfooter=6, dtype={"Industry code[1]":int}   )
#There is an entry or two with the states list empty, we replace the NaN value with an empty string.
work_stoppage_df.fillna("", inplace=True)

#This text file contains a table with info about each industry type.
#We use it to convert the NAICS industry code of work_stoppage_df to the industry code used 
#in the Current Employment Statistics files. This doesn't give a perfect match up,
#so we have to match many of the entries by hand.
#This file is originally from https://download.bls.gov/pub/time.series/ce/ce.industry
industry_lookup_df = pd.read_csv("ce.industry", sep="\t")

#This text file contains info about each series_id.
#We use it to turn a BLS industry code into a Current Employment Statistic series_id.
#This file is orginally from https://download.bls.gov/pub/time.series/ce/ce.series
current_employment_series_df = pd.read_csv("/Users/nyssacornelius/Desktop/COMP4477/FProj/FProj/CurrentEmploymentStats/ce.series.txt", sep="\t", header=0,
    names=['series_id', 'supersector_code', 'industry_code',
       'data_type_code', 'seasonal', 'series_title', 'footnote_codes',
       'begin_year', 'begin_period', 'end_year', 'end_period'],
     converters={'series_id':str.strip} )
#The header=0 and names is to fix some white space issues with the column names.
#The converter is to fix white space issues with the series_id values.
#We restrict this data set to only the rows for average weekly earnings of all employees, 
#which is data_type_code 11, and we use the seasonally adjusted data (seasonally adjusted 
#is good for comparing monthly data, whereas unadjusted is good for comparing yearly data).
#Depending on what we do, we might want to switch to seasonable data or even use both.
#Non-adjusted is 'U' instead of 'S'
current_employment_series_df = current_employment_series_df[
    (current_employment_series_df["data_type_code"]==11)
    &(current_employment_series_df["seasonal"]=='S')]

#This text file contains the value for the each Current Employment Statistic.
#This data set is from 1939 to 2021, but not for all series. It is very spotty.
#This file is originally from https://download.bls.gov/pub/time.series/ce/ce.data.0.AllCESSeries
current_employment_statistic_df = pd.read_csv("/Users/nyssacornelius/Desktop/COMP4477/FProj/FProj/CurrentEmploymentStats/ce.data.0.AllCESSeries.txt", 
    sep="\t", header=0, 
    names=['series_id', 'year', 'period', 'value','footnote_codes'],
    converters={'series_id':str.strip} )
#The header=0 and names is to fix some white space issues with the column names.
#The converter is to fix white space issues with the series_id values.



#The datasets oe.data.0.Current and oe.data.1.AllData are only for 2020, so we can't use them for much.
#occupation_employment_df = pd.read_csv(".\OccEmployment\oe.data.0.Current", sep="\s+")
#occupation_employment_df1 = pd.read_csv(".\OccEmployment\oe.data.1.AllData", sep="\s+")





#Below are some data frames for state level data.

#This text file is for states_metro_employment_series. It has information about the
#series in the entries of sa.data.0.Current. Unfortunately, the industry data is all 
#over the place with this data set. Using this might require a lot of data matching done by hand,
#it doesn't even look like we can easily pull average wage data for an entire state.
state_series_df = pd.read_csv("sa_series.txt", delim_whitespace=True,
    names= ['series_id', 'state_code', 'area_code', 'industry_code', 'detail_code',
       'data_type_code', 'seasonal', 'benchmark_year', 'begin_year',
       'begin_period', 'end_year', 'end_period'],
      header=None, skiprows=1, index_col=False )              
#We restrict to data_type_code 4, which  is Average Weekly Earnings In Dollars    
state_series_df = state_series_df[ (state_series_df["data_type_code"]==4) ]


#This text file contains the actual data for a given series.
states_metro_employment_stats = pd.read_csv("/Users/nyssacornelius/Desktop/COMP4477/FProj/FProj/StateMetroEmployment/sa.data.0.Current.csv", sep="\s+")
#This uses SIC code for industry, or so they say. It doesn't look to match the actual SIC codes.
#This isn't currently in use, because of matching the data with the work stoppage data.


# In[4]:


#This is a bunch of hand matched codes based on the cell below.
#This was matched based on the values in 2-6 digit_2017_Codes.xlsx
#and ce.industry.
naics_to_ce_industry = {
92:90922920,
923:60541612,
3152:32315280,
21221:10212200,
22121:44221200,
22131:None,
23731:20237300,
31212:32329140,
31523:32315280,
32721:31327200,
33341:31333400,
33421:None,
33441:31334400,
33451:None,
33612:None,
33621:31336200,
33641:31336400,
33651:31336900,
48521:43485500,
48831:43488390,
48849:43488400,
49211:43492100,
51711:50517000,
61111:65611100,
61121:65611200,
61131:65611300,
62111:65621100,
62210:65622100,
62211:65622100,
62311:65623100,
71111:70711190,
92211:None,
92214:None,
92313:None,
211111:10211000,
212112:10212113,
212230:10212200,
212231:10212200,
212234:10212200,
221110:44221110,
221210:44221200,
236000:20236000,
236200:20236200,
236220:20236220,
237310:20237300,
237990:20237000,
238140:20238140,
238160:20238160,
238210:20238210,
238220:20238220,
238320:20238320,
238350:20238350,
238910:20238910,
311313:None,
311320:None,
311812:32311813,
313312:32313000,
315299:32315280,
325180:32325180,
325221:32325211,
325222:32325211,
326199:32326190,
326210:32326210,
326211:32326210,
331110:31331100,
331111:31331100,
331310:31331300,
331312:31331300,
331513:31331510,
332112:31331400,
332913:32326120,
332992:31332994,
333111:None,
333611:31333600,
333618:None,
333921:None,
333996:None,
334290:31334200,
334612:None,
335222:31335200,
335224:31335200,
335931:31335930,
336120:31336100,
336212:31336214,
336300:31336300,
336321:31336320,
336322:31336320,
336330:31336330,
336350:31336350,
336360:31336360,
336410:31336400,
336414:31336419,
336510:31336900,
336900:None,
336992:None,
424410:41424410,
441110:42441110,
445110:42445110,
481111:43481100,
482111:None,
484210:43484210,
485110:43485500,
485111:43485500,
485112:43482000,
485113:43485500,
485310:43485310,
485991:43485900,
488190:43488100,
488310:43488390,
488320:43488320,
488330:43488390,
488490:43488400,
512110:50512110,
517110:50517000,
524114:55524110,
561612:60561613,
561720:60561720,
561920:60561920,
562111:60562100,
562219:60562219,
611110:65611100,
611111:65611100,
611210:65611200,
611310:65611300,
621610:65611610,
622110:65622100,
622210:65622200,
624110:65624110,
624410:65624400,
721110:70721110,
721120:70721120,
722510:70722500,
921100:None,
921110:None,
921111:None,
921190:None}  


# In[5]:


#This cell goes through the work stoppage data frame and tries to match it up with the CE data
#The data is written to a pickle file, so this does not need to be rerun, unless we're 
#improving the data.

#For each work stoppage:
#    Get the BLS industry code from the work stoppage NAICS code. 
#        This usually fails, so we record the NAICS codes we still need to match.
#    Get the relevant CES series id from the BLS industry code. 
#        This fails some of the time, but I don't think there's anyhing to be done
#        about it. The data just isn't there.
#    If there is data for the CES series that is from before the work stoppage (at least time_window days), then
#        we record the series id. This we can use to look up whatever data we want.
#        Since this data is at the national level, we don't bother separating by state.
#    The initial run keeps track of the NAICS codes that weren't matched at all and then these
#        are matched later by hand. So on the second run, everything is matched that can be matched.
#        The matches are stored in the dictionary naics_to_ce_industry.


rows_to_add = []
naics_codes_to_match = []
for index, row in work_stoppage_df.iterrows():
    naics_code = row["Industry code[1]"]
    start_date = row["Work stoppage beginning date"]  
    end_date = row["Work stoppage ending date"]  

    industry_code = industry_lookup_df[ str(naics_code)==industry_lookup_df["naics_code"] ]["industry_code"] 
    if len(industry_code)!=0:#Did we get an industry code for free?
        industry_code = industry_code.iloc[0]
    else:#Do we have a match done by hand?
        industry_code = naics_to_ce_industry[naics_code]
    
    
    if not industry_code is None:
        series_id = current_employment_series_df[ 
            current_employment_series_df["industry_code"]==industry_code]["series_id"]
        if len(series_id)==0:
            if be_verbose:
                print("No series data available for this industry code.")
        elif len(series_id)>1:
            if be_verbose:
                print("Multiple series data available for this industry code. Weird.")
        else:
            series_id = series_id.iloc[0]
            wage_data = current_employment_statistic_df[
                current_employment_statistic_df["series_id"]==series_id]
 
            #Is there sufficient data from before the work stoppage began?
            #This is controlled by the time_window variable.
            ce_year = int(min(wage_data["year"]))
            ce_month = int(min(wage_data[wage_data["year"]==ce_year]["period"])[1:])
            ce_date = pd.Timestamp(year=ce_year,month=ce_month,day=1)
            earlier = start_date-time_window
    
            #do we got data?
            if earlier >= ce_date:
                print("We have some data to use!")
                organization = row['Organizations involved']                    
                areas = row['Areas']
                ownership = row['Ownership']
                states = row["States"].split(",")
                rows_to_add.append([organization, states,  areas, ownership, naics_code, 
                    start_date, end_date, series_id] )
            else:
                if be_verbose:
                    print("No data is available before the work stoppage.")
    else:
        #Load these into a dictionary and try to match by hand.
        if be_verbose:
            print(f"Here's a NAICS code we should try to match:{naics_code}")
        naics_codes_to_match.append(naics_code)
                
clean_national_data = pd.DataFrame( data=rows_to_add,
    columns=["organization", "states", "areas", "ownership", 
        "naics industry code", "start date", "end date", "series_id"] )

clean_national_data.to_pickle(".\\Cleaned\\clean_national_data.pkl")


# In[6]:


sa_state_code_to_abbr = {
1:"AL",
2:"AK",
4:"AZ",
5:"AR",
6:"CA",
8:"CO",
9:"CT",
10:"DE",
11:"DC",
12:"FL",
13:"GA",
15:"HI",
16:"ID",
17:"IL",
18:"IN",
19:"IA",
20:"KS",
21:"KY",
22:"LA",
23:"ME",
24:"MD",
25:"MA",
26:"MI",
27:"MN",
28:"MS",
29:"MO",
30:"MT",
31:"NE",
32:"NV",
33:"NH",
34:"NJ",
35:"NM",
36:"NY",
37:"NC",
38:"ND",
39:"OH",
40:"OK",
41:"OR",
42:"PA",
43:"PR",
44:"RI",
45:"SC",
46:"SD",
47:"TN",
48:"TX",
49:"UT",
50:"VT",
51:"VA",
52:"VI",
53:"WA",
54:"WV",
55:"WI",
56:"WY"
}


# In[7]:


#This dictionary turns a NAICS code to the industry code of the sa data.
#These were all done by hand.
naics_to_sa_industry = {
62:None,
92:None,
236:200001,
237:215026,
322:426002,
336:337002,
517:548103,
622:880603,
623:880556,
923:None,
2211:None,
2362:215403,
3118:420503,
3141:422002,
3152:423002,
3221:426156,
3315:333203,
3324:334103,
3331:335303,
3361:337114,
4243:653026,
4244:651403,
4841:542103,
5311:765002,
21221:110002,
22112:None,
22121:549203,
22131:None,
23731:216103,
23811:217703,
23812:217703,
23814:217403,
23822:217103,
23829:215009,
23831:None,
23832:217203,
23835:217503,
31212:None,
31523:423002,
32721:332002,
33341:650703,
33421:548136,
33422:336536,
33441:336744,
33451:338136,
33593:336403,
33612:337144,
33621:337103,
33632:337103,
33641:337203,
33651:337403,
42482:651803,
44111:655103,
44511:654103,
44812:656203,
48412:542103,
48521:541002,
48831:544002,
48832:None,
48849:None,
49211:542103,
51111:427103,
51512:548303,
51711:548103,
53112:None,
54111:None,
54181:873103,
56172:None,
61111:882103,
61121:938224,
61131:882203,
62111:880103,
62210:880603,
62211:880603,
62311:880503,
71111:None,
72111:870103,
72112:870128,
92211:None,
92214:None,
92313:None,
211111:113002,
212112:112203,
212230:110002,
212231:110002,
212234:110002,
221110:None,
221112:None,
221122:549103,
221210:549203,
236000:215002,
236200:215403,
236220:215403,
237310:216103,
237990:215026,
238140:217403,
238160:217603,
238210:217303,
238220:217103,
238320:217203,
238350:217503,
238910:None,
311313:None,
311320:None,
311611:420114,
311615:420114,
311812:420503,
312111:420803,
313312:422002,
315299:423002,
321911:None,
325180:428103,
325211:428203,
325221:428203,
325222:428203,
326199:430803,
326210:430103,
326211:430103,
331110:333124,
331111:333124,
331310:None,
331312:333254,
331513:333254,
332112:334609,
332913:650703,
332992:None,
333111:335203,
333415:217103,
333611:335103,
333618:335103,
333921:None,
333996:None,
334290:336603,
334612:None,
335222:336303,
335224:336303,
335931:336434,
336111:337103,
336120:337109,
336212:337109,
336300:337144,
336321:337144,
336322:337144,
336330:337144,
336350:337144,
336360:337144,
336410:337203,
336411:337203,
336412:337203,
336414:337236,
336510:337403,
336611:337303,
336900:337009,
336992:None,
424410:651414,
441110:655303,
445110:654103,
481111:545103,
482111:540002,
484121:None,
484122:None,
484210:None,
485110:541002,
485111:541002,
485112:540002,
485113:541002,
485310:541002,
485991:None,
488190:545002,
488310:544002,
488320:None,
488330:None,
488490:None,
512110:None,
517110:548002,
517311:548002,
524114:763203,
561612:None,
561720:None,
561920:None,
562111:None,
562219:None,
611110:882103,
611111:882103,
611210:938224,
611310:882203,
621111:880103,
621491:763203,
621610:880556,
622110:None,
622210:None,
624110:883503,
624410:883503,
711211:None,
721110:870103,
721120:870128,
722510:658002,
921100:939133,
921110:939133,
921111:939133,
921190:949009
}


# In[8]:


#This cell goes through the work stoppage data frame and tries to match it up with the SA data
#The data is written to a pickle file, so this does not need to be rerun, unless we're 
#improving the data.

#For each work stoppage:  
#    Get the SA industry code from the work stoppage NAICS code.
#        These are stored in the dictionary naics_to_sa_industry.
#    Get the relevant SA series ids from the SA industry code. Since this is state level data,
#    we also require that the SA series is for a state appearing in the list of states 
#    for the work stoppage. 
#        This fails some of the time, but I don't think there's anyhing to be done
#        about it. The data just isn't there.
#        If a work stoppage occurred in multiple states and there is data for multiple states,
#        we record each different state data in a separate row.
#        The translation of an SA state code to a work stoppage state abbreviation is done via
#        the dictionary sa_state_code_to_abbr.
#    If there is data for the SA series that is from before the work stoppage (at least time_window days), then
#        we record the series id. This we can use to look up whatever data we want.


rows_to_add = []
for index, row in work_stoppage_df.iterrows():
    naics_code = row["Industry code[1]"]
    states = row["States"]
    start_date = row["Work stoppage beginning date"]  
    end_date = row["Work stoppage ending date"]  

    industry_code = naics_to_sa_industry[naics_code]     
    if not industry_code is None:
        series_ids = state_series_df[ state_series_df.apply(
            lambda x: x["industry_code"]==industry_code and sa_state_code_to_abbr[x["state_code"]] in states, 
            axis=1)
        ]["series_id"]       

        if len(series_ids)==0:
            if be_verbose:
                print("No series data available for this industry code in the relevant states.")
        else:
            for series_id in series_ids:
                wage_data = states_metro_employment_stats[
                    states_metro_employment_stats["series_id"]==series_id]
        
                #Sometimes a valid series_id does not have any data.
                if len(wage_data)==0:
                    if be_verbose:
                        print("There is no data available for this series.")
                else:
                    #Is there sufficient data from before the work stoppage began?
                    #This is controlled by the time_window variable.
                    ce_year = int(min(wage_data["year"]))
                    ce_month = int(min(wage_data[wage_data["year"]==ce_year]["period"])[1:])
                    ce_date = pd.Timestamp(year=ce_year,month=ce_month,day=1)
                    earlier = start_date-time_window
    
                    #do we got data?
                    if earlier >= ce_date:
                        if be_verbose:
                            print("We have some data to use!")
                        organization = row['Organizations involved']                    
                        areas = row['Areas']
                        ownership = row['Ownership']
                        state = state_series_df[state_series_df.series_id==series_id]["state_code"]
                        state = sa_state_code_to_abbr[state.iloc[0]]
                        rows_to_add.append([organization, state, areas, ownership, naics_code, 
                            start_date, end_date, series_id] )
                    else:
                        print("No data is available before the work stoppage.")
    else:
        if be_verbose:
            print(f"Here's a NAICS code we could try to match:{naics_code}")
                
clean_state_data = pd.DataFrame( data=rows_to_add,
    columns=["organization", "state", "areas", "ownership", 
        "naics industry code", "start date", "end date", "series_id"] )

clean_state_data.to_pickle(".\\Cleaned\\clean_state_data.pkl")


# In[9]:


#This cell loads the clean_national_data from the pickle file
#Run this is we're just loading the data instead of loading and cleaning from scratch.
clean_national_data = pd.read_pickle(".\\Cleaned\\clean_national_data.pkl")


# In[10]:


#This cell loads the clean_state_data from the pickle file
#Run this is we're just loading the data instead of loading and cleaning from scratch.
clean_state_data = pd.read_pickle(".\\Cleaned\\clean_state_data.pkl")


# In[11]:


#Let's see what we can do with this data now:
display(clean_national_data.head())
print(f"There are {len(clean_national_data)} rows to consider. Let's see the first 5\n\n")
for j in range(0,5):
    row = clean_national_data.iloc[j]
    start_date = row['start date']
    series_id = row["series_id"]
    data = current_employment_statistic_df[
        (current_employment_statistic_df["series_id"]==series_id)
        &(current_employment_statistic_df["period"]!="M13")]
    #M13 is for the annual average

    earlier = start_date-time_window
    later = start_date+time_window 
    annoying = lambda row : pd.Timestamp(year=int(row["year"]), month=int(row["period"][1:]),day=1)
    data = data[ (data.apply(annoying,axis=1)>=earlier)
               & (data.apply(annoying,axis=1)<=later)]

    print(f"The work stoppage at {row['organization']} started on {row['start date']} "
        + f"and ended on {row['end date']}. The associated wage data is as follows.")          
    display(data)
    print(f"\n\n")
          


# In[12]:


#Let's see what we can do with this data now:
display(clean_state_data.head())
print(f"There are {len(clean_state_data)} rows to consider. Let's see the first 5\n\n")
for j in range(0,5):
    row = clean_state_data.iloc[j]
    start_date = row['start date']
    series_id = row["series_id"]
    data = states_metro_employment_stats[ (states_metro_employment_stats["series_id"]==series_id)
        &(states_metro_employment_stats["period"]!="M13")]
    #M13 is for the annual average

    earlier = start_date-time_window
    later = start_date+time_window 
    annoying = lambda row : pd.Timestamp(year=int(row["year"]), month=int(row["period"][1:]),day=1)
    data = data[ (data.apply(annoying,axis=1)>=earlier)
               & (data.apply(annoying,axis=1)<=later)]

    print(f"The work stoppage at {row['organization']} started on {row['start date']} "
        + f"and ended on {row['end date']}. The associated wage data is as follows.")          
    display(data)
    print(f"\n\n")


# In[ ]:
work_stoppage_df.to_pickle(".\\PrelimEDA\\work_stop.pkl")


