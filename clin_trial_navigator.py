from textwrap import wrap
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import json
from pandas.io.json import json_normalize # tranform JSON file into a pandas dataframe
import time
    
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
#pd.set_option('max_colwidth', 1000)

class Query:        # class to create a query from the clinicaltrials API that will house the list of clinical trials returned from the API, with detailed information for each
    
    def __init__(self, name = 'Query_1'):
        self.name = name
        self.study_tracker = []         # build list that tracks which studies have been built via build_study within the query

    def build_query(self):
        self.query_terms = input('\n\nEnter the search query term: \n\n')           # input search terms used to query the clinicaltrials.gov API - tokenize into a list of search terms
        query_tokenized = self.query_terms.split()
        
        field_values = ['NCTId', 'BriefTitle', 'Condition', 'Phase', 'StudyType',
                        'EnrollmentCount', 'StartDate', 'PrimaryCompletionDate', 'EligibilityCriteria', 'InterventionName', 
                        'ArmGroupInterventionName', 'ArmGroupDescription', 'InterventionArmGroupLabel', 'OutcomeMeasureType', 'OutcomeMeasureTitle',
                        'OutcomeMeasureDescription', 'OutcomeMeasureTimeFrame', 'OutcomeMeasurementValue', 'OutcomeMeasureUnitOfMeasure']
        
        max_rank = 1000             # max # of items returned by the API query
        
        
        url = 'https://clinicaltrials.gov/api/query/study_fields?expr='
        
        for i, word in enumerate(query_tokenized):              # build query URL by adding all search terms and field values to the query URL, following the appropriate format
            if i == 0:
                url = url + word
            else:
                url = url + '+' + word
            
        url = url + '&fields='
        
        for i, word in enumerate(field_values):
            if i == 0:
                url = url + word
            else:
                url = url + '%2C' + word
        
        url = url + '&min_rnk=1&max_rnk=' + str(max_rank) + '&fmt=json' 
        url = url.strip()
        self.url = url
        
        print('\n\nQuerying 1,000 trials from clinicaltrials.gov with the following url...\n\n'+url)
        
        return self.url
        
    def build_study_table(self, url):
          
        ## convert the clinicaltrials.gov JSON response to a pandas dataframe
        
        result = requests.get(url).json()
        result_list = [result for result in result['StudyFieldsResponse']['StudyFields'] if result['OutcomeMeasureType']]     #loop through the list and identify ONLY studies with outcome measures reported 
        df_master = json_normalize(result_list[0])      # initialize dataframe using JSON result

        try:
            for study in result_list[1:]:        # concatenate each study to the dataframe to generate master dataframe
                df = json_normalize(study)
                df_master = pd.concat([df_master, df], axis=0, ignore_index=True)
        except:
            pass
        
        try:                                            # extract list entries, reformat data in these columns as strings
            df_master['NCTId'] = [df_master['NCTId'][i][0] for i in range(len(df_master['NCTId'])) if len(df_master['NCTId'][i]) > 0]
        except:
            pass        
        try:
            df_master['BriefTitle'] = [df_master['BriefTitle'][i][0] for i in range(len(df_master['BriefTitle'])) if len(df_master['BriefTitle'][i]) > 0]
        except:
            pass       
        try:
            df_master['Condition'] = [df_master['Condition'][i][0] for i in range(len(df_master['Condition'])) if len(df_master['Condition'][i]) > 0]
        except:
            pass
        try:
            df_master['StudyType'] = [df_master['StudyType'][i][0] for i in range(len(df_master['StudyType'])) if len(df_master['StudyType'][i]) > 0]
        except:
            pass
        
        for i in range(len(df_master['Phase'])):                    #extract clinical trial phase(s)
            if df_master['Phase'][i]:
                if len(df_master['Phase'][i]) > 1:
                    df_master['Phase'][i] = df_master['Phase'][i][0] + ', ' + df_master['Phase'][i][1]
                else:
                    df_master['Phase'][i] = df_master['Phase'][i][0]
            else:
                df_master['Phase'][i] = 'Unknown'
        
#         try:
#             df_master['Phase'] = [df_master['Phase'][i][0] for i in range(len(df_master['Phase'])) if df_master['Phase'][i]]
#         except:
#             print('ERROR YOU FUCK')
        
        try:
            df_master['EnrollmentCount'] = [df_master['EnrollmentCount'][i][0] for i in range(len(df_master['EnrollmentCount'])) if len(df_master['EnrollmentCount'][i]) > 0]
        except:
            pass
        try:
            df_master['StartDate'] = [df_master['StartDate'][i][0] for i in range(len(df_master['StartDate'])) if len(df_master['StartDate'][i]) > 0]
        except:
            pass
        try:
            df_master['PrimaryCompletionDate'] = [df_master['PrimaryCompletionDate'][i][0] for i in range(len(df_master['PrimaryCompletionDate'])) if len(df_master['PrimaryCompletionDate'][i]) > 0]
        except:
            pass
        try:
            df_master['EligibilityCriteria'] = [df_master['EligibilityCriteria'][i][0] for i in range(len(df_master['EligibilityCriteria'])) if len(df_master['EligibilityCriteria'][i]) > 0]
        except:
            pass
        
        #df_master['StartDate'] = pd.to_datetime(df_master['StartDate'])
        #df_master['PrimaryCompletionDate'] = pd.to_datetime(df_master['PrimaryCompletionDate'])
        
        self.df_master = df_master
        
        #self.df_master = df_master[df_master['Phase'].str.lower() == 'phase 3']          # return ONLY phase 3 trial results
        
        return self.df_master
    
    def get_url(self):
        return self.url

    def get_study_tracker(self):
        return self.study_tracker
    
    def get_df_master(self):
        if len(self.df_master)>0:
            return self.df_master
        else:
            return 'No df_master exists!'

class Study:
    
    def __init__(self, query, nct_id):                  # all studies are initialized within a query, and are identified via their unique NCT ID (created by clinicaltrials.gov)s
        
        self.nct_id = nct_id
        self.entry = query.get_df_master()[query.get_df_master()['NCTId']==nct_id].reset_index().drop(columns='index')      #build a unique df entry for this NCT ID
        self.df_outcomes = pd.DataFrame(columns=self.entry.columns)
        
        try:                            # identify the number of outcome measure values reported per outcome measure (i.e., measure at baseline, change at week N, P value, etc.)
            self.measures_per_outcome = len(self.entry['OutcomeMeasurementValue'][0])//len(self.entry['OutcomeMeasureTitle'][0])
        except:
            self.measures_per_outcome = 1
        
        if self.nct_id not in query.study_tracker:              #add the study to the query's study tracker
            query.study_tracker.append(self.nct_id)
        
    def get_entry(self):
        return self.entry
    
    def get_indication(self):
        return [item for item in self.entry['Condition']][0]     # returns the first list item within the list of indications

    def extract_outcomes(self):            #iterate thru all outcome measures, create a dataframe with all required info
        
        try:
            self.df_outcomes = self.df_outcomes.drop(columns=['Rank', 'Condition', 'Phase', 'BriefTitle', 'StudyType', 'EnrollmentCount', 'StartDate', 'PrimaryCompletionDate', 'EligibilityCriteria', 'ArmGroupDescription'])
        except:
            pass
        
        for i, item in enumerate(self.entry['OutcomeMeasureType']):
                
            try:
                self.df_outcomes['OutcomeMeasureType'] = [item for item in self.entry['OutcomeMeasureType']][0]
            except:
                pass
            try:
                self.df_outcomes['OutcomeMeasureTitle'] = [item for item in self.entry['OutcomeMeasureTitle']][0]
            except:
                pass
            try:
                self.df_outcomes['OutcomeMeasureDescription'] = [item for item in self.entry['OutcomeMeasureDescription']][0]
            except:
                pass
            try:
                self.df_outcomes['OutcomeMeasureTimeFrame'] = [item for item in self.entry['OutcomeMeasureTimeFrame']][0]
            except:
                pass
            try:
                self.df_outcomes['OutcomeMeasureUnitOfMeasure'] = [item for item in self.entry['OutcomeMeasureUnitOfMeasure']][0]
            except:
                pass
            
#             try:
#                 self.df_outcomes['InterventionArmGroupLabel'][i] = [self.entry['InterventionArmGroupLabel'][0]]
#             except:
#                 self.df_outcomes['InterventionArmGroupLabel'] = [self.entry['InterventionArmGroupLabel'][0]]
            
                                        
        beginning = 0
        increment = self.measures_per_outcome               # maps correct number of outcome measures reported in the study
       
        for i in range(len(self.df_outcomes)):
            try:
                self.df_outcomes['OutcomeMeasurementValue'][i] = self.entry['OutcomeMeasurementValue'][0][beginning:beginning+increment]
                beginning += increment
            except:
                pass
            try:
                self.df_outcomes['InterventionArmGroupLabel'][i] = self.entry['InterventionArmGroupLabel'][0]
            except:
                pass
            try:
                self.df_outcomes['InterventionName'][i] = self.entry['InterventionName'][0]
            except:
                pass
            try:
                self.df_outcomes['ArmGroupInterventionName'][i] = self.entry['ArmGroupInterventionName'][0]
            except:
                pass
        
        self.df_outcomes['NCTId'] = [item for item in self.entry['NCTId']][0]
        
        return self.df_outcomes

# function that takes a query object as input and outputs a dataframe containing all the outcome measures for ONLY phase 3 trials, along with the NCTId those measures correspond to

def build_outcome_table(query):
    
    # initialize an outcomes_df from the first study within the query study table
    
    query_df_master = query.get_df_master()
    query_df_master = query_df_master[query_df_master['Phase'].str.match('.*3.*', na=False)].reset_index()          #filter ONLY phase 3 studies
    study_1 = Study(query, query_df_master['NCTId'][0])
    
    outcomes_df = study_1.extract_outcomes()
    
    study_x = Study(query, query_df_master['NCTId'][1])
    df = study_x.extract_outcomes()
    outcomes_df = pd.concat([outcomes_df, df], axis=0, ignore_index=False)
    
    for i in range(1, len(query_df_master)):                         # concatenate each study to the dataframe to generate master dataframe
        study_x = Study(query, query_df_master['NCTId'][i])
        df = study_x.extract_outcomes()
        outcomes_df = pd.concat([outcomes_df, df], axis=0, ignore_index=False)
    
    outcomes_df = outcomes_df.reset_index().drop(columns='index')
    query.outcomes_df = outcomes_df
    
    return outcomes_df

def outcome_track(outcome_list, track_dict):  # function to build a dictionary counter object that tracks the count of each endpoint within the outcome list
    
    for outcome in outcome_list:
        if outcome in track_dict.keys():
            track_dict[outcome] += 1
        else:
            track_dict[outcome] = 1

def plot_outcomes(outcome_df, query):                   # function to plot the top 10 outcome measures used in the outcomes dataframe provided as input
    
    fig = plt.figure(figsize=[18, 10]).tight_layout(w_pad=6.0, h_pad = 3.0)
    ax = sns.barplot(data=outcome_df.head(10), x='index', y='Frequency', estimator=sum, ci=None)
    
    # for item in ax.get_xticklabels():
    #     item.set_rotation(90)

    for p in ax.patches:
        ax.text(x = p.get_x()+(p.get_width()/2),y = p.get_height()+0.05,s = '{}'.format(p.get_height(),ha = 'center'))

    labels = []
    
    for label in ax.get_xticklabels():
        labels.append(label.get_text())

    labels = [ '\n'.join(wrap(l, 20)) for l in labels]

    ax.set_title('Top 10 Most Common Primary + Secondary Outcome Measures Reported in {} Clinical Trials'.format(query.query_terms.title()))
    ax.set_xticklabels(labels, fontsize=7.7, va='top', ha='center')
    ax.set_xlabel('Outcome Measure')
    plt.show()

def search_outcomes(query):
    search_term = input('Enter your search term here: \n')
    tokenized = search_term.split().strip()
    #print(tokenized)
    outcome_table = build_outcome_table(query)
    
    df_search = outcome_table[outcome_table['OutcomeMeasureTitle'].str.match('.*{}.*'.format(search_term))]
    
    
    return df_search

# main function - build a user-generated query, generate a list of clinical studies that fit the query search terms, generate a list of outcome 
## measures used within all those clinical studies, output a .csv file containing the studies, and a .csv file containing the outcomes


def main():                 
    query = Query()
    query.build_query()
    
    study_table = query.build_study_table(query.get_url())
    outcome_table = build_outcome_table(query)
    outcome_table_primary = outcome_table[outcome_table['OutcomeMeasureType'].str.match('.*[Pp]rimary.*')]
    
    outcome_tracker = {}
    outcome_track(outcome_table_primary['OutcomeMeasureTitle'], outcome_tracker)
    outcome_tracker_df = pd.Series(outcome_tracker).to_frame('Frequency').reset_index().sort_values(by='Frequency', ascending=False).reset_index().drop(columns='level_0')
    
    plot_outcomes(outcome_tracker_df, query)

    study_table.to_csv('study_table.csv')
    outcome_table.to_csv('outcome_table.csv')
    outcome_table_primary.to_csv('outcome_table_primary.csv')

    print('\n3 CSV files have been created:\n\n')
    print('study_table (list of clinical studies returned from the query)\n')
    print('outcome_table (list of all outcomes used in all studies within the query)\n')
    print('primary_outcome_table (list of all PRIMARY outcomes used in all studies within the query)\n\n')
    
    going = True
    while going == True:
        keep_going = input('Would you like to search for an endpoint within the current query?\n')
    
        if keep_going[0].lower() == 'y':
            df_returned = search_outcomes(query)
            print(df_returned)

        elif keep_going[0].lower() == 'n':
            going=False
        else:
            continue

main()