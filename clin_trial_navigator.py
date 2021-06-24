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
        
        print('\n\nSearch Term: \n\n'+self.query_terms+'\n\n')
        
        query_tokenized = self.query_terms.split()
        
        field_values = ['NCTId', 'BriefTitle', 'Condition', 'Phase', 'StudyType',
                        'EnrollmentCount', 'StartDate', 'PrimaryCompletionDate', 'EligibilityCriteria', 'InterventionName', 
                        'ArmGroupInterventionName', 'ArmGroupDescription', 'InterventionArmGroupLabel', 'OutcomeMeasureType', 'OutcomeMeasureTitle',
                        'OutcomeMeasureDescription', 'OutcomeMeasureTimeFrame', 'OutcomeMeasurementValue', 'OutcomeMeasureUnitOfMeasure']
        
        max_rank = 1000             # max # of items returned by the API query (max for the clinicaltrials.gov API is 1000)
        
        
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
        
        print('\n\nQuerying up to 1,000 trials from clinicaltrials.gov with the following url...\n\n'+url+'\n\n')
        
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
                                                                    # extract list entries, reformat data in these columns as strings
        try:                                            
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
        
        
        for i in range(len(df_master['Phase'])):                    # extract clinical trial phase(s)
            if df_master['Phase'][i]:
                if len(df_master['Phase'][i]) > 1:
                    df_master['Phase'][i] = df_master['Phase'][i][0] + ', ' + df_master['Phase'][i][1]
                else:
                    df_master['Phase'][i] = df_master['Phase'][i][0]
            else:
                df_master['Phase'][i] = 'Unknown'
        
        
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
        #df_master['PrimaryCompletionDate'] = pd.to_datetime(df_master['PrimaryCompletionDate'])            # future version of this project will convert starting / ending date to datetime format, to calculate/analyze trial duration
        
        self.df_master = df_master
        
        return self.df_master
    
    def build_outcome_table(self):
        
        # initialize an outcomes_df from the first study within the query study table
        
        query_df_master = self.get_df_master()
        query_df_master = query_df_master[query_df_master['Phase'].str.match('.*3.*', na=False)].reset_index()          # filter ONLY phase 3 studies, which represent pivotal efficacy/safety trials used by the FDA when evaluating a new product 
        study_1 = Study(self, query_df_master['NCTId'][0])
        
        outcomes_df = study_1.extract_outcomes()
        
        study_x = Study(self, query_df_master['NCTId'][1])
        df = study_x.extract_outcomes()
        outcomes_df = pd.concat([outcomes_df, df], axis=0, ignore_index=False)
        
        for i in range(1, len(query_df_master)):                         # concatenate each study to the dataframe to generate master dataframe
            study_x = Study(self, query_df_master['NCTId'][i])
            df = study_x.extract_outcomes()
            outcomes_df = pd.concat([outcomes_df, df], axis=0, ignore_index=False)
        
        outcomes_df = outcomes_df.reset_index().drop(columns='index')
        
        return outcomes_df

    
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
            self.df_outcomes = self.df_outcomes.drop(columns=['Rank', 'Condition', 'StudyType', 'EnrollmentCount', 'StartDate', 'PrimaryCompletionDate', 'EligibilityCriteria', 'ArmGroupDescription'])
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

        beginning = 0
        increment = self.measures_per_outcome               # maps correct number of outcome measures reported in the study, as multiple performance values may pertain to each endpoint (i.e. value for each intervention arm + placebo)
       
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
        self.df_outcomes['Phase'] = [item for item in self.entry['Phase']][0]
        self.df_outcomes['BriefTitle'] = [item for item in self.entry['BriefTitle']][0]
        
        return self.df_outcomes

# function that takes a query object as input and outputs a dataframe containing all the outcome measures for ONLY phase 3 trials, along with the NCTId those measures correspond to

def outcome_track(outcome_list, track_dict):  # function to build a dictionary counter object that tracks the count of each endpoint within the outcome list
                                              ## can be used to plot the top N outcome measures used in clinical studies for a certain indication
    
    for outcome in outcome_list:
        if outcome in track_dict.keys():
            track_dict[outcome] += 1
        else:
            track_dict[outcome] = 1

def plot_outcomes(outcome_df, query):                   # function to plot the top 10 outcome measures used in the outcomes dataframe provided as input
    
    n_endpoints = 10                                      # how many endpoints will be plotted (top N endpoints)
    fig = plt.figure(figsize=[36, 10]).tight_layout(w_pad=2.0, h_pad = 2.0)
    ax = sns.barplot(data=outcome_df.head(n_endpoints), x='index', y='Frequency', estimator=sum, ci=None)

    for p in ax.patches:
        ax.text(x = p.get_x()+(p.get_width()/2),y = p.get_height()+0.05,s = '{}'.format(p.get_height(),ha = 'center'))

    labels = []
    
    for label in ax.get_xticklabels():
        labels.append(label.get_text())

    labels = [ '\n'.join(wrap(l, 20)) for l in labels]              # wrap label text to improve presentability (many endpoints are long text blocks)

    ax.set_title('Top 10 Most Common Primary + Secondary Outcome Measures Reported in {} Clinical Trials'.format(query.query_terms.title()), fontsize=14)
    ax.set_xticklabels(labels, fontsize=13, va='top', ha='center')
    ax.set_xlabel('Outcome Measure', fontsize=14)
    plt.show()

    
def tokenize_column(outcome_table, column_name, new_column_name):           # function to convert the text contained in one column into a tokenized, lowercase list of terms (stripped of whitespace and parentheses characters)
                                                                            ## in a new column
    outcome_table[new_column_name] = outcome_table[column_name].str.split()
    
    for i in range(len(outcome_table[new_column_name])):
        for j in range(len(outcome_table[new_column_name][i])):
            outcome_table[new_column_name][i][j] = outcome_table[new_column_name][i][j].lower().strip(' ()')
    
def search_outcomes(outcome_table, col_to_search):                           # function to search an outcomes table and determine how many times ALL the terms in a keyword search appear in the tokenized lise 
    
    global search_term 
    search_term = input('\nEnter your search term here: \n')
    tokenized = search_term.split()
    tokenized_clean = [word.lower().strip() for word in tokenized]

    match_tracker = []

    for i in range(len(outcome_table)):
        matches=0    
        for word in tokenized_clean:
            if word in outcome_table[col_to_search][i]:
                matches +=1
        if matches == len(tokenized_clean):
            match_tracker.append(i)
    
    # create empty dataframe with identical columns to outcomes df; iterate through index values in match_tracker; append outcomes_df.iloc[index]

    outcome_table_filtered = pd.DataFrame(columns=outcome_table.columns)

    for ind in match_tracker:
        outcome_table_filtered.loc[ind] = outcome_table.loc[ind] 
            
    outcome_table_filtered = outcome_table_filtered.reset_index()
    outcome_table_filtered
    
    print('\nSearching outcomes that contain the following key terms:\n')
    print(tokenized_clean)

    return outcome_table_filtered

def plot_outcome_search(outcome_table_filtered):
    
    outcome_plot_dict = {}
    outcome_plot_dict[search_term] = outcome_table_filtered.shape[0]

    outcome_plot_df = pd.Series(outcome_plot_dict).to_frame('Frequency').reset_index().sort_values(by='Frequency', ascending=False).reset_index()

    fig = plt.figure(figsize=[14,6]).tight_layout(pad=8.0)
    ax = sns.barplot(data=outcome_plot_df, x='index', y='Frequency', estimator=sum)

    for p in ax.patches:
            ax.text(x = p.get_x()+(p.get_width()/2),y = p.get_height()*1.01,s = '{}'.format(p.get_height(),ha = 'center'), fontsize=14)

    ax.set_title('Number of Endpoints Returned from Search')
    ax.set_xlabel('search term')

# main function - build a user-generated query, generate a list of clinical studies that fit the query search terms, generate a list of outcome 
## measures used within all those clinical studies, output a .csv file containing the studies, and a .csv file containing the outcomes


def main():                 
    
    ## psuedocode:   

    # prompt user for a query
    # build study table, and outcome table for the query
    # prompt user if they wish to save excel files of the study table, outcome table  -  if yes, save csv file of tables generated
    # ask if user wishes to search for an outcome  -  if so, run search function
    # result from search function should be:
    ##  print how many results were returned
    ##  print frequency chart of the return of hits
    ##  print data table
    ##  prompt user if they wish to save csv of data table generated - if so, save the search query table
    # ask the user whether they wish to repeat the search function
    
    query = Query()
    query.build_query()
    
    study_table = query.build_study_table(query.get_url())
    outcome_table = query.build_outcome_table()
    outcome_table_primary = outcome_table[outcome_table['OutcomeMeasureType'].str.match('.*[Pp]rimary.*')]

    print('\n\nTop 10 results from the study table: \n\n')
    print(study_table.head(10))

    print('\n\nTop 10 results from the outcome table: \n\n')
    print(outcome_table.head(10))

    #print('\n\nTop 10 results from the primary outcome table: \n\n')
    #print(outcome_table_primary.head(10))

    search = input("\nWould you like to save the query results? \n\n")
        
    if search.strip().lower()[0] == 'y':
        study_table.to_csv('study_table.csv')
        outcome_table.to_csv('outcome_table.csv')
        outcome_table_primary.to_csv('outcome_table_primary.csv')

        print('\n3 CSV files have been created:\n\n')
        print('study_table (list of clinical studies returned from the query)\n')
        print('outcome_table (list of all outcomes used in all studies within the query)\n')
        print('primary_outcome_table (list of all PRIMARY outcomes used in all studies within the query)\n\n')

    going = True
    while going == True:
        
        searching = input('\nWould you like to search for an endpoint within the current query?\n')
    
        if searching.strip().lower()[0] == 'y':
            
            tokenize_column(outcome_table, 'OutcomeMeasureTitle', 'OutcomeMeasureTitleTokenized')

            search_results = search_outcomes(outcome_table, 'OutcomeMeasureTitleTokenized')

            print('\nNumber of hits from your search: {}\n'.format(search_results.shape[0]))
            plot_outcome_search(search_results)
            print('\nTable result from your search: \n')
            print(search_results)

            save_file = input('Would you like to save the results from your search?\n')

            if save_file.strip().lower()[0] == 'y':
                search_results.to_csv('search_results.csv')
                print('\n1 CSV file has been created:\n\n')
                print('search_results (results from your search of the endpoint data table)\n')

        elif searching.strip().lower()[0] == 'n':
            going = False
        else:
            continue

main()