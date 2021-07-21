import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


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