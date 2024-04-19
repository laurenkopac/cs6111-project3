# CS6111 Adv Database Systems Spring 24 - Project 3
April 22, 2024

## Team
Amari Byrd (ab5311) and Lauren Kopac (ljk2148)

## Files in Submission
|File Name| Description|
|---------|------------|
|`main.py`||
|`INTEGRATED-DATASET.csv`| Our processed dataset, cleaned from the web-export as detailed in the Data Cleaning section below|
|`example-run.txt`| Text file export from example run, tuned with the specifications detailed in the Example Run section below|
|`requirements.txt`| Requirements file for our program|

## Files NOT in Submission
The below files were used in our program to produce our cleaned dataset (`INTEGRATED-DATASET.csv`), but are not required to run the program assuming you already have access to the data.

|File Name| Description|
|---------|------------|
|`data_clean.py`|Scripted used to clean raw dataset from NYC Open Data|
|`restaurant_inspection_results.csv`| Original dataset exported from NYC Open Data|
|`Violation-Health-Code-Mapping.csv`| CSV file mapping violation codes to generalized descriptions|

## How to Use
Navigate to the project's root file and run the following to install needed packages after activating the python virtual environment:

```bash
$ pip install -r requirements.txt
```

To run the program, enter the following into the command line within the Project3 directory:

```bash
python main.py INTERGRATED-DATASET.csv <min_sup> <min_conf>
```
## The Dataset

### Motiviation
Every who has spent time in NYC is familiar with the graded pieces of paper hanging outside every restaurant and food service establishment. These grades serve an important purpose to inform the public of any health and food safety concerns assocaited with the establishment, and assure patrons that where they are choosing to eat has been vetted by the city of New York.

For our project, we are deriving association rules to find any interesting trends linking certain health inspection grades and violations to restaurant features such as `BORO` or `CUISINE`. Further, we hope to be able to draw assocations between violations given to resturants and the overall grade they ended up receiving, assuming that some violations are more severe than others.

Objectively, we chose this dataset because it is large and actively maintained by the city of New York. This allows for flexibility when parsing and cleaning the data. 

### Dataset Description

We worked with the [NYC Restaurant Inspection Results](https://data.cityofnewyork.us/Health/DOHMH-New-York-City-Restaurant-Inspection-Results/43nn-pn8j/about_data) dataset from NYC Open data. 

The dataset contains every violation citation from Department of Health and Mental Hygiene inspections conducted for establishments that are open and operational as of the most recent record date. Only active establishments are included in the dataset. For purposes of our project, this data is current as of 2024-04-14.

Establishments are uniquely identified by their CAMIS (record ID) number. Records are also included for each restaurant that has applied for a permit but has not yet been inspected and for inspections resulting in no violations. Establishments with inspection date of 1/1/1900 are new establishments that have not yet received an inspection. Restaurants that received no violations are represented by a single row and coded as having no violations using the ACTION field.

Below is a complete list of the 27 fields associated with this dataset:

* CAMISID
* DBA (doing business as A.K.A. the name of the restaurant)
* BORO
* BUILDING
* STREET
* ZIPCODE
* PHONE
* CUISINE DESCRIPTION
* INSPECTION DATE
* ACTION
* VIOLATION CODE
* VIOLATION DESCRIPTION 
* CRITICAL FLAG
* SCORE
* GRADE
* GRADE DATE
* RECORD DATE
* INSPECTION TYPE
* Latitude
* Longitude
* Community Board
* Council District
* BIN
* BBL 
* NTA
* Location Point1

For more information on these fields, please visit the link above.

## Data Cleaning
To clean our large dataset, we used the `data_clean.py` script, relying primarily on the `pandas` package to handle data transformations. For simplicity, and because the A Priori algorithm can be computationally expensive, we decided to use only 5 fields to find association rules (see field table with descriptions below). To further clean our dataset, we generized the `CUISINE DESCRIPTION` and `VIOLATION CODE` fields, which we found to be unnecessarily specific and granular for our purposes. To generalize cuisines, we provided the full list of cuisine options in our dataset to ChatGPT and prompted it to generalize into a smaller subset of broader categories. We then used a dictionary to map the possibilities. For violation codes, we were fortunate to find a mapping of violation codes (generally 3 character codes) to short descriptions (1 - 4 word summaries of the violations) on Github [^1]. We used this mapping and generalized even further, grouping like categories together (i.e., converting HOT HANDLING and COLD HANDLING to simply FOOD HANDLING). Lastly, we filtered out any nondescript cuisines, violation descriptions, or incomplete/invalid grades that we believed to be unhelpful in forming association rules. Once the data was cleaned, we asserted that were left with at least 1000 rows. Again, because A Priori can be computationally expensive, we limited our cleaned dataset to 5000 randomly sampled rows (ensuring each row was sampled only once).

### Fields Used
While there are 27 fields in the original dataset, we narrowed the scope of our project to down to 5.

|Field Name| Description|
|---------|------------|
|`CAMISID`| Unique identifier for the entity (restaurant); 10-digit integer, static per restaurant permit|
|`BORO`| Borough in which entity is located; text (Manhattan, Brooklyn, Bronx, Queens, State Island)|
|`CUISINE_DESC`| Describes the entity cuisine; Optional field provided by entity; see below for mapping methodology and possible cuisines; text|
|`CATEGORY_DESC`| Describes the category of health code violation; see below for mapping methodology and possible categories; text| 
|`GRADE`| A letter grade assigned to the entity by the DOHMH. Highest distinction is 'A' followed by 'B' and 'C' as the lowest possible passing grade.

## Internal Design
Our program runs in 4 main phases: Data Cleaning, Generating Frequent Itemsets, Creating Association Rules, Exporting Results.

### Phase 1: Data Cleaning
For additional details on data cleaning, and why we made certain decisions throughout the process, please see the Data Cleaning section above. 

1. Import the DOHMH dataset and violation code mapping using `pd.read_csv()`
2. Clean headers for readability - convert all to uppercase using `.str.upper()` and replace spaces with underscores using `.str.replace(' ','_')`
3. For inspections (rows) that did not result in any violations, `VIOLATION_CODE` will be `Nan`, replace with a placecoder code `000`
    ```python
    df['VIOLATION_CODE'].fillna('000',inplace=True)
    ```
4. Map violation code description categories (`CATEGORY_DESC`) from our external dataset (`Violation-Health-Code-Mapping.csv`) to our working dataset.
5. Further clean `CATEGORY_DESC` by lumping together similar violations, i.e. COLD HANDLING and HOT HANDLING become FOOD HANDLING:
    ```python
    df['CATEGORY_DESC'] = df['CATEGORY_DESC'].str.replace('COLD HOLDING','FOOD HANDLING')
    df['CATEGORY_DESC'] = df['CATEGORY_DESC'].str.replace('HOT HOLDING','FOOD HANDLING')
    ```
6. Map specific provided cuisines to general categories using a dictionary generated by ChatGPT using a few shot prompt (i.e. take this list of cuisines and provide general descriptions - for example: 'Burgers': 'American', 'Fruits/Vegetables': 'Vegetarian').
7. Drop nondescript rows (i.e. no cuisine provided, non-valid grades)
8. Assert that there at least 1000 rows of data left after cleaning. If left with more than 5000 rows, randomly sample 5000 to save to our `INTERGATED-DATASET.csv`
    ```python
    if df.shape[0] > 5000:
        # Set random_state for reproducablity, ensure each row is only sampled once
        sampled_df = df.sample(n=5000, replace=False, random_state=111)
        sampled_df.to_csv(target_file_name, index=False)
    else:
        df.to_csv(target_file_name, index=False)
    ```

Certainly! Here's the content formatted in Markdown:

### Phase 2: Finding Frequent Itemsets
This phase begins by taking the necessary parameters, such as minimum support and confidence levels, and reading the integrated dataset into a `pandas` dataframe.

1. The A Priori algorithm is utilized to generate candidate item sets of increasing sizes starting from size 2.

```python
# Generate candidate item sets of size k
new_candidate_itemsets = join_sets(candidate_itemsets, k, min_sup, df)
```

2. For each candidate item set, support is calculated, representing the proportion of transactions containing the item set.

```python
# Calculate support for each candidate item set
current_freq = sum(1 for _, rows in df.iterrows() if union_set.issubset(rows['items']))
```

3. The process continues until no new candidate item sets can be generated, indicating that all frequent item sets have been identified.

```python
# Terminate the loop when no new candidates can be generated
if not new_candidate_itemsets:
    break
```

### Phase 3: Creating Association Rules
Association rules are derived from the frequent item sets discovered in Phase 2.

```python
# Generate association rules from frequent item sets
assoc_rules = generate_assoc_rules(freq_itemsets, min_conf)
```

1. Rules that do not meet the minimum confidence threshold specified by the user are filtered out.

```python
# Filter out rules that do not meet the minimum confidence threshold
if confidence >= min_conf:
    assoc_rules.append((lhs, rhs, confidence))
```

### Phase 4: Export
Once all itemsets above the set support and association rules above the set confidence are found, they are exported to a local `.txt` file for the user to analyze. 

1. 

## Results of Example Run
To produce the results of the provided example run in `example-run.txt`, we tuned our parameters to the following:

 * `min_sup` = 0.09
 * `min_conf` = 0.7

With these thresholds on our `INTEGRATED-DATASET.csv`, we found the following high frequency itemsets:
```
====== Frequent itemsets (min_sup = 9.0%) ======
       ['A'] -- 81.04%
       ['Manhattan'] -- 37.2%
       ['MAINTENANCE, CONSTRUCTION & PLACEMENT'] -- 31.81%
       ['A', 'Manhattan'] -- 30.43%
       ['American'] -- 28.99%
       ['Brooklyn'] -- 25.979999999999997%
       ['A', 'American'] -- 25.22%
       ['Queens'] -- 24.52%
       ['CONTAMINATION'] -- 22.41%
       ['A', 'Brooklyn'] -- 21.07%
       ['A', 'Queens'] -- 19.42%
       ['Asian'] -- 18.61%
       ['A', 'CONTAMINATION'] -- 17.71%
       ['FOOD HANDLING'] -- 15.32%
       ['A', 'Asian'] -- 13.36%
       ['PEST CONTROL'] -- 12.76%
       ['American', 'Manhattan'] -- 12.280000000000001%
       ['B'] -- 12.17%
       ['A', 'FOOD HANDLING'] -- 10.75%
       ['Beverages'] -- 10.72%
       ['Latin American'] -- 10.66%
       ['A', 'American', 'Manhattan'] -- 10.6%
       ['PLUMBING'] -- 10.0%
       ['A', 'Beverages'] -- 9.54%
       ['Italian'] -- 9.36%
```

and following association rules: 

```
====== High-confidence association rules (min_conf = 70.0%) ======
       [Beverages] => [A] -- (Conf: 88.99%, Supp: 9.54%)
       [American] => [A] -- (Conf: 87.00%, Supp: 25.22%)
       [American, Manhattan] => [A] -- (Conf: 86.32%, Supp: 10.60%)
       [Manhattan] => [A] -- (Conf: 81.80%, Supp: 30.43%)
       [Brooklyn] => [A] -- (Conf: 81.10%, Supp: 21.07%)
       [Queens] => [A] -- (Conf: 79.20%, Supp: 19.42%)
       [CONTAMINATION] => [A] -- (Conf: 79.03%, Supp: 17.71%)
       [Asian] => [A] -- (Conf: 71.79%, Supp: 13.36%)
       [FOOD HANDLING] => [A] -- (Conf: 70.17%, Supp: 10.75%)
```
### Motivation 
It was our hope with this dataset, we would find cuisines, boros, or combinations of the two, that are strongly associated with a type of Department of Health grade. That way, we could make more informed decisions on where to dine in NYC. To our surpise, we were not able to find strong association rules with grades lower than A. The grade B is the second most frequent grade, appearing in our frequent itemsets with a support of only 12.7% compared to A grades with a suport of 81%. We will chalk this up as a win for NYC restaurant owners and patrons :)

### Association Rules
We find from our example run, that Beverage establishments are associated with A grades most strongly, followed by American cuisines, particularly those ones located in Manhattan. 

If you are looking to try a new spot in NYC, you are likely to find one up to code in Manhattan, Brooklyn, or Queens. Unfortunately The Bronx and Staten Island did not meet our confidence thershold to be strongly enough assocaited with an A grade.

### Analysis
Initially, looking only at our association rules, we were confused why any violation would be associated with an 'A' grade with 70% confidence. However, this makes more sense with the context that the grade 'A' is itself a frequent itemset, with a support of 81%. This tells us that overwhelming, restaurants receive As in their insections from the NYC DOH.

This motivated us to learn more about how the grades are actually assigned in the process. We learned that grades are assigned based on a scoring system (the lower the better), and that each grade has a range associated with it (i.e. 0-13 for A, 14-27 for B, and >=28 for C). We experimented with assigning grades combined with scores by introducing A-, B-, C- to make more sense of violations receiveing As. Unfortunately, this was not successful in producing meaningful results and rules. We instead reverted back to the original grades and built rules on that.

## External Libraries
Our programs relies on the following Python frameworks:

|Library | Use |
|---------|------------|
|`pandas` | Used primarily in data cleaning of the original dataset|
|`sys` | For grabbing agruments passed through the cmd line by the user|
|`itertools`| Used to construct all possible combinations of itemsets in the A Priori algorithm |

## External References
[^1] https://github.com/nychealth/Food-Safety-Health-Code-Reference/blob/main/README.md for health code violation mapping
