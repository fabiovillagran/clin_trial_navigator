# Clinical Trial Navigator
### See the 'clin_trial_outcomes.ipynb' file for a walkthrough of this tool.  Web version is currently under development, which will have a more user-friendly, graphical interface.

This project queries the clinicaltrials.gov database based on custom search criteria, returns up to 1,000 clinical trials with detailed information on trial design 
and outcome measures, and converts the results into an easy-to-read format on which analyses can be performed.

An example use case would be identifying all pivotal Phase III trials in a specific disease state (i.e., severe asthma) in the past 10 years, and comparing trial duration, sample size, outcomes measured, and relative efficacy performance across the trials. These data could then be used in conjunction with historical sales + access data to 
inform pricing strategy for a pharmaceutical manufacturer developing a new product.



The .ipynb file demonstrates some of the tool's current capabilities and the intended outputs in a cleaner format.

The .py file allows you to run the program in real-time on your own system.  
Simply clone this repository and install the required dependencies found in the requirements.txt file (preferably in a virtual environment)

The tool should then be ready to run
