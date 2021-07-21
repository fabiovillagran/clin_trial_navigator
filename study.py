import pandas as pd
import query

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
