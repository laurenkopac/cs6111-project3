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

# Use pandas to read in the CSV files
df = pd.read_csv(source_file_name)
violation_code_mapping = pd.read_csv('Violation-Health-Code-Mapping.csv')

# Clean columns
df.columns = df.columns.str.replace(' ','_').str.upper()
df.columns = df.columns.str.replace('DESCRIPTION','DESC')

violation_code_mapping.columns = violation_code_mapping.columns.str.upper()
violation_code_mapping.columns = violation_code_mapping.columns.str.replace('DESCRIPTION','DESC')

# Change DBA (doing business as) to RESTAURANT_NAME for better readability
df.rename(columns={'DBA':'RESTAURANT_NAME'}, inplace=True)

# Replace NaN VIOLATION CODE with custom value: 000
df['VIOLATION_CODE'].fillna('000',inplace=True)

df = df.merge(violation_code_mapping[['VIOLATION_CODE','CATEGORY_DESC']], on='VIOLATION_CODE',how='left')

# Remove rows that do not have a score and grade
df = df[['CAMIS','BORO','CUISINE_DESC','CATEGORY_DESC','GRADE']]

# Replace NaN VIOLATION CODE with custom value: 000
df['CATEGORY_DESC'].fillna('NO VIOLATION FOUND',inplace=True)

# Clean Descriptions to be more general
df['CATEGORY_DESC'] = df['CATEGORY_DESC'].str.replace('COLD HOLDING','FOOD HANDLING')
df['CATEGORY_DESC'] = df['CATEGORY_DESC'].str.replace('HOT HOLDING','FOOD HANDLING')
df['CATEGORY_DESC'] = df['CATEGORY_DESC'].str.replace('REDUCE OXYGEN PACKAGE','FOOD HANDLING')
df['CATEGORY_DESC'] = df['CATEGORY_DESC'].str.replace('COOLING & REFRIGERATION','FOOD HANDLING')
df['CATEGORY_DESC'] = df['CATEGORY_DESC'].str.replace('TEMPERATURE REGULATING','FOOD HANDLING')
df['CATEGORY_DESC'] = df['CATEGORY_DESC'].str.replace('FOOD WORKERS','CONTAMINATION')
df['CATEGORY_DESC'] = df['CATEGORY_DESC'].str.replace('ADULTERATED','CONTAMINATION')
df['CATEGORY_DESC'] = df['CATEGORY_DESC'].str.replace('FOOD PROTECTION','CONTAMINATION')
df['CATEGORY_DESC'] = df['CATEGORY_DESC'].str.replace('HANDWASH/TOILET','PLUMBING')

# Drop NaN rows
df.dropna(inplace=True)

# Reject dataset if less than 1000 rows are left after cleaning
if df.shape[0] < 1000:
    print("Your cleaned dataset did not yield enough rows for this project.")
    print("Revisit your methodology and try again.")
    exit()

# Avoid support issues with too large a dataset
## If dataset is larger than 1000, randomly sample 1000 rows
if df.shape[0] > 5000:
    # Set random_state for reproducablity, ensure each row is only sampled once
    sampled_df = df.sample(n=5000, replace=False, random_state=123)
    sampled_df.to_csv(target_file_name, index=False)
else:
    df.to_csv(target_file_name, index=False)