# CS6111 Adv Database Systems Spring 24 - Project 3
April 22, 2024

## Team
Amari Byrd (ab5311) and Lauren Kopac (ljk2148)

## Files in Submission
|File Name| Description|
|---------|------------|
|`main.py`| Main `.py` file responsible for parsing provided dataset for frequent itemsets, association rules, and produces a text output.|
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
$ pip3 install -r requirements.txt
```

To run the program, enter the following into the command line within the `/home/ab5311/Project3` directory after activating the virtual environment, set up as `dbproj3`:

```bash
python3 main.py INTERGRATED-DATASET.csv <min_sup> <min_conf>
```

### Parameters
* `INTEGRATED-DATASET.csv` - provided for you, no further action is needed to clean or complie the dataset, but it must be called exactly as it appears here
* `min_sup` - Minimum support threshold; float; must be a value greater than 0 and less than or equal to 1
* `min_conf` - Minimum confidence threshold; float; must be a value greater than 0 and less than or equal to 1

## The Dataset

### Motiviation
Anyone who has spent time in NYC is familiar with the graded pieces of paper hanging outside every restaurant or food service establishment. These grades serve an important purpose to inform the public of any health and food safety concerns associated with the establishment, and assure patrons that where they are choosing to eat has been vetted by the city of New York's Department of Heath and Mental Hygiene (DOHMH).

For our project, we are deriving association rules to find any interesting trends linking certain health inspection grades (`GRADE`) or violation  types (`CATEGORY_DESC`) to restaurant features such as `BORO` or `CUISINE`. Further, we hope to be able to draw associations between violations given to resturants and the overall grade they ended up receiving, assuming that some violations are more severe than others. We will also be looking for associations with boro where the restaurant is located, and cuisine type. 

From an objective standpoint, we chose this dataset because it is large and actively maintained by the city of New York. This allows for flexibility when parsing and cleaning the data. 

### Dataset Description

We worked with the [NYC Restaurant Inspection Results](https://data.cityofnewyork.us/Health/DOHMH-New-York-City-Restaurant-Inspection-Results/43nn-pn8j/about_data) dataset from NYC Open data. 

Only active establishments are included in the dataset. For purposes of our project, this data is current as of 2024-04-14.

Establishments are uniquely identified by their CAMIS (record ID) number. The dataset contains results from every insepection conducted by the DOHMH for establishments that are open and operational as of the most recent record date. Records are also included for each restaurant that has applied for a permit but has not yet been inspected and for inspections resulting in no violations. Establishments with inspection date of 1/1/1900 are new establishments that have not yet received an inspection. Restaurants that received no violations are represented by a single row and coded as having no violations using the ACTION field.

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
To clean our large dataset, we used the `data_clean.py` script, relying primarily on the `pandas` package to handle data transformations. For simplicity, and because the A Priori algorithm can be computationally expensive, we decided to use only 5 fields to find association rules (see field table with descriptions below). To further clean our dataset, we generized the `CUISINE DESCRIPTION` and `VIOLATION CODE` fields, which we found to be unnecessarily specific and granular for our purposes. To generalize cuisines, we provided the full list of cuisine options in our dataset to ChatGPT [1] and prompted it to generalize into a smaller subset of broader categories. We then used a dictionary to map the possibilities. For violation codes, we were fortunate to find a mapping of violation codes (generally 3 character codes) to short descriptions (1 - 4 word summaries of the violations) on Github [2]. We used this mapping and generalized even further, grouping like categories together (i.e., converting HOT HANDLING and COLD HANDLING to simply FOOD HANDLING). Lastly, we filtered out any nondescript cuisines, violation descriptions, or incomplete/invalid grades that we believed to be unhelpful in forming association rules. Once the data was cleaned, we asserted that were left with at least 1000 rows. Again, because A Priori can be computationally expensive, we limited our cleaned dataset to 10,000 randomly sampled rows (ensuring each row was sampled only once).

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
For additional details on data cleaning, and why we made certain decisions throughout the process, please see the Data Cleaning section above. Below details the procedure.

1. Import the DOHMH dataset and violation code mapping using `pd.read_csv()`
2. Clean headers for readability - convert all to uppercase using `.str.upper()` and replace spaces with underscores using `.str.replace(' ','_')`
3. For inspections (rows) that did not result in any violations, `VIOLATION_CODE` will be `NaN`, replace with a placecoder code `000`
    ```python
    df['VIOLATION_CODE'].fillna('000',inplace=True)
    ```
4. Map violation code description categories (`CATEGORY_DESC`) from our external dataset (`Violation-Health-Code-Mapping.csv`) to our working dataset.
5. Further clean `CATEGORY_DESC` by lumping together similar violations, i.e. COLD HANDLING and HOT HANDLING become FOOD HANDLING:
    ```python
    # For a full list of transformations, please see the data_clean.py file
    df['CATEGORY_DESC'] = df['CATEGORY_DESC'].str.replace('COLD HOLDING','FOOD HANDLING')
    df['CATEGORY_DESC'] = df['CATEGORY_DESC'].str.replace('HOT HOLDING','FOOD HANDLING')
    ```
6. Map specific provided cuisines to general categories using a dictionary generated by ChatGPT using a few shot prompt (i.e. take this list of cuisines and provide general descriptions - for example: 'Burgers': 'American', 'Fruits/Vegetables': 'Vegetarian').
7. Drop nondescript rows (i.e. no cuisine provided, non-valid grades)
8. Assert that there at least 1000 rows of data left after cleaning. If left with more than 10000 rows, randomly sample 10000 to save to our `INTEGRATED-DATASET.csv`
    ```python
    if df.shape[0] > 10000:
        # Set random_state for reproducablity, ensure each row is only sampled once
        sampled_df = df.sample(n=10000, replace=False, random_state=111)
        sampled_df.to_csv(target_file_name, index=False)
    else:
        df.to_csv(target_file_name, index=False)
    ```

### Phase 2: Finding Frequent Itemsets
In this phase of the program, the A Priori algorithm is utilized to generate candidate itemsets of increasing sizes starting from size 2. For our implimentation of the algorithm, we went with the general idea outlined in Section 2.1 of the Agrawal and Srikant paper in VLDB 1994 [3] with the concept of the A Priori pruning technique to cut down on runtime.

1. Initially, singleton itemsets (individual items) are extracted from the dataset.
2. Frequent singleton itemsets are identified based on their support being greater than or equal to the minimum support threshold.
3. The frequent singleton itemsets are stored, and candidate itemsets of size 2 or more are then generated using the A Priori algorithm.
4. The A Priori algorithm iterates through different itemset sizes, joining frequent itemsets of size k-1 to generate candidate itemsets of size k. 
5. Before adding a candidate itemset to `new_candidate_itemsets`, a priori prining is applied: if any (k-1)-size subset is not a frequent itemset, the candidate itemset is deemed infrequent and passed over. This is the implementation of the downward closure property of frequent itemsets - any subset of a frequent itemset must also be frequent.
6. The process continues until no new candidate itemsets can be generated.
```python
# Terminate the loop when no new candidates can be generated
if not new_candidate_itemsets:
    break
```

### Phase 3: Creating Association Rules
Association rules are derived from the frequent itemsets discovered in Phase 2.

1. Iterates through each frequent itemset of size greater than 1 (removing the singleton sets) and generates association rules based on confidence exceeding the minimum confidence threshold.
2. For each frequent itemset, all possible combinations of left-hand side (LHS) and right-hand side (RHS) are examined to generate association rules.
3. Confidence for each association rule is calculated and compared with the minimum confidence threshold.
4. If the rule meets or exceeds the minimum threshold - the lhs, rhs, confidence, and combined support values are appended to a list, later to be printed to our output.

### Phase 4: Export
Once all itemsets above the set support and association rules above the set confidence are found, they are exported to a local `.txt` file for the user to analyze. 

1. Create (or open) a file named `output.txt`.
2. Write a header for the frequent itemsets, using `min_sup` to indicate the inputed minimum support threshold.
3. Call the helper function `format_itemsets()` to unpack itemsets found at every iteration `k` of the A Priori algorithm.
4. Return print friendly versions of each itemset along with their support values.
5. Write a header for the high-confidence association rules, using `min_conf` to indicate the inputed minimum support threshold.
6. Because association rules are stored in a simple list, traverse the list and print out each component (lhs, rhs, confidence, and combined support)
7. Close the `.txt` file and exit the program.

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

### Analysis of Association Rules
We find from our example run, that Beverage establishments are associated with A grades most strongly, followed by American cuisines, particularly those ones located in Manhattan. 

If you are looking to try a new spot in NYC, you are likely to find one up to code in Manhattan, Brooklyn, or Queens. Unfortunately The Bronx and Staten Island did not meet our confidence thershold to be strongly enough associated with an A grade.

We should also note that we have found two association rules that (with high confidence) associate violations (CONTAMINATION and FOOD HANDLING) with A grades.

Initially, looking only at our association rules, we were confused why any violation would be associated with an 'A' grade with 70% confidence. However, this makes more sense with the context that the grade 'A' is itself a frequent itemset, with a support of 81%. This tells us that overwhelming, restaurants receive As in their insections from the NYC DOH.

This motivated us to learn more about how the grades are actually assigned in the process. We learned that grades are assigned based on a scoring system (the lower the better), and that each grade has a range associated with it (i.e. 0-13 for A, 14-27 for B, and >=28 for C). We experimented with assigning grades combined with scores by introducing A-, B-, C- to make more sense of violations receiveing As. Unfortunately, this was not successful in producing meaningful results and rules. We instead reverted back to the original grades and built rules on that.

Our conclusion is that violations associated with A grades with high confidence are likely not serious offenses, and did not score poorly enough in these categories to be dropped into B and C ranges.

## External Libraries
Our programs relies on the following Python frameworks:

|Library | Use |
|---------|------------|
|`pandas` | Used primarily in data cleaning of the original dataset|
|`sys` | For grabbing agruments passed through the cmd line by the user|
|`itertools`| Used to construct all possible combinations of itemsets in the A Priori algorithm |

## External References
[1] OpenAI. ChatGPT. April 14, 2024, https://chat.openai.com/.

[2] NYC Health. Food Safety Health Code Reference. GitHub, April 14, 2024. https://github.com/nychealth/Food-Safety-Health-Code-Reference.

[3] Chapter 1 ("Data Mining") Rakesh Agrawal and Ramakrishnan Srikant: Fast Algorithms for Mining Association Rules in Large Databases, VLDB 1994