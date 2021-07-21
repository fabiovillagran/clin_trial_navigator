import pandas as pd
import query
import outcomes

    
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
#pd.set_option('max_colwidth', 1000)

def main():                 
    
    # build a new query for clinicaltrials.gov API
    new_query = query.Query()
    new_query.build_query()
    
    study_table = new_query.build_study_table(new_query.get_url())
    outcome_table = new_query.build_outcome_table()
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
        
        searching = input('\n\nWould you like to search for an endpoint within the current query?\n')
    
        if searching.strip().lower()[0] == 'y':
            
            outcomes.tokenize_column(outcome_table, 'OutcomeMeasureTitle', 'OutcomeMeasureTitleTokenized')

            search_results = outcomes.search_outcomes(outcome_table, 'OutcomeMeasureTitleTokenized')

            print('\n\nNumber of hits from your search: {}\n'.format(search_results.shape[0]))
            outcomes.plot_outcome_search(search_results)
            print('\n\nTable result from your search: \n')
            print(search_results)

            save_file = input('\n\nWould you like to save the results from your search?\n')

            if save_file.strip().lower()[0] == 'y':
                search_results.to_csv('search_results.csv')
                print('\n\n1 CSV file has been created:\n\n')
                print('search_results (results from your search of the endpoint data table)\n')

        elif searching.strip().lower()[0] == 'n':
            going = False
        else:
            continue

main()
