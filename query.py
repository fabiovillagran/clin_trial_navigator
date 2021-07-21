import requests
import json
import pandas as pd
from pandas.io.json import json_normalize # tranform JSON file into a pandas dataframe
import study


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
        study_1 = study.Study(self, query_df_master['NCTId'][0])
        
        outcomes_df = study_1.extract_outcomes()
        
        study_x = study.Study(self, query_df_master['NCTId'][1])
        df = study_x.extract_outcomes()
        outcomes_df = pd.concat([outcomes_df, df], axis=0, ignore_index=False)
        
        for i in range(1, len(query_df_master)):                         # concatenate each study to the dataframe to generate master dataframe
            study_x = study.Study(self, query_df_master['NCTId'][i])
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