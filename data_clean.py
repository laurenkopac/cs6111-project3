"""
File used to clean the dataset found at: https://data.cityofnewyork.us/Health/DOHMH-New-York-City-Restaurant-Inspection-Results/43nn-pn8j/about_data

DOHMH New York City Restaurant Inspection Results
"""

# Environment Set Up
import pandas as pd

# Source file name, change as needed
## Assumes source file is in the same directory as data_clean.py
source_file_name = 'restaurant_inspection_results.csv'

# Use pandas to read in the CSV
df = pd.read_csv(source_file_name)

# Clean columns
df.columns = df.columns.str.replace(' ','_').str.upper()
df.rename(columns={'DBA':'RESTAURANT_NAME'})

# Rename Columns
print(df.info())