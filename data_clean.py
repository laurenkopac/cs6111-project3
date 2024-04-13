"""
File used to clean the dataset found at: https://data.cityofnewyork.us/Health/DOHMH-New-York-City-Restaurant-Inspection-Results/43nn-pn8j/about_data

DOHMH New York City Restaurant Inspection Results
"""

# Environment Set Up
import pandas as pd

# Source file name, change as needed
## Assumes source file is in the same directory as data_clean.py
source_file_name = 'restaurant_inspection_results.csv'

# Target file name
target_file_name = 'INTEGRATED-DATASET.csv'

# Use pandas to read in the CSV
df = pd.read_csv(source_file_name)

# Clean columns
df.columns = df.columns.str.replace(' ','_').str.upper()
df.columns = df.columns.str.replace('DESCRIPTION','DESC')

# Change DBA (doing business as) to RESTAURANT_NAME for better readability
df.rename(columns={'DBA':'RESTAURANT_NAME'}, inplace=True)

# Remove rows that do not have a score and grade
df = df[['BORO','CUISINE_DESC','VIOLATION_CODE','CRITICAL_FLAG','GRADE']].dropna(subset=['GRADE'])

# Replace NaN VIOLATION CODE with custom value: 000
df['VIOLATION_CODE'].fillna('000',inplace=True)

if df.shape[0] < 1000:
    print("Your cleaned dataset did not yield enough rows for this project.")
    print("Revisit your methodology and try again.")
else:
    # Export cleaned dataset to directory
    df.to_csv(target_file_name, index=False)