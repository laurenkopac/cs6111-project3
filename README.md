# CS6111 Adv Database Systems Spring 24 - Project 3
April 22, 2024

## Team
Amari Byrd (ab5311) and Lauren Kopac (ljk2148)

## Files in Submission
|File Name| Description|
|---------|------------|
|`main.py`||
|`INTEGRATED-DATASET.csv`||
|`example-run.txt`||
|`requirements.txt`||



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

### Data Cleaning
While there are 27 fields in the original dataset, we narrowed the scope of our project to down to 5.

|Field Name| Description|
|---------|------------|
| `CAMISID`| Unique identifier for the entity (restaurant); 10-digit integer, static per restaurant permit|
|`BORO`| Borough in which entity is located; text (Manhattan, Brooklyn, Bronx, Queens, State Island)|
|`CUISINE_DESC`| Describes the entity cuisine; Optional field provided by entity; see below for mapping methodology and possible cuisines; text|
|`CATEGORY_DESC`| Describes the category of health code violation; see below for mapping methodology and possible categories; text| 


## Internal Design

### Phase 1: Data Cleaning

### Phase 2: Finding Frequent Itemsets

### Phase 3: Creating Association Rules

### Phase 4: Export

## Results of Example Run
To produce the results of the provided example run in `example-run.txt`, we tuned our parameters to the following:

 * `min_sup` = 
 * `min_conf` = 

With these thresholds on our `INTEGRATED-DATASET.csv`, we found the following association rules: 

## External Libraries
Our programs relies on the following Python frameworks:

|Library | Use |
|---------|------------|
|`pandas` | Used primarily in data cleaning of the original dataset|
|`

## External References
[1] https://github.com/nychealth/Food-Safety-Health-Code-Reference/blob/main/README.md for health code violation mapping
