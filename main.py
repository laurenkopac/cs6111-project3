"""
Main file for Project 3.

This program takes a dataset and 
"""

# Environment Set up
import sys
from itertools import combinations
import pandas as pd

# Initialize variables for minimum support and confidence, file name

def cmd_line():
    """
    Gather needed input from the user to run the program. If the structure is not correct, exit and give example usage. 

    INPUT: Command line input from user python main.py 
    OUTPUT: Either exit and explain proper usage or continue to execute the program
    """
    # If too few or too many args passed, exit and explain
    if len(sys.argv) != 4:
        print(f"Usage: python3 main.py INTEGRATED-DATASET.csv <min_sup> <min_conf>: {len(sys.argv)}")
        exit(1)

    # Extract command line arguments: min_sup and min_conf
    try:
        # Asserts the parameters passed are floats
        min_sup = float(sys.argv[2])
        min_conf = float(sys.argv[3])

        # Check to make sure parameters are greater than or equal to 0, and less than 1.
        if (min_sup <= 0) or (min_conf <=0):
            raise ValueError("Your parameters for min_sup and min_conf cannot be less than or equal to 0.")
        if (min_sup > 1) or  (min_conf > 1):
            raise ValueError("Your parameters for min_sup and min_conf cannot be greater than 1.")

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    filename = sys.argv[1]

    df = read_in_df(filename)

    return min_sup, min_conf, df

def query_print_cmd(min_sup, min_conf,df):
    """
    Display user inputted parameters and information about the dataset

    INPUT: Number iteration (starting with 0 for initial search), and desired relation description
    OUTPUT: A terminal print out for the user summarizing their inputed args
    """

    print("____")
    print('Parameters:')
    print(f"Minimum Support = {min_sup * 100}%")
    print(f"Minimum Confidence = {min_conf * 100}%")
    print(f"CSV Filename = {sys.argv[1]}")
    print(f"Number of Rows in dataset = {df.shape[0]:,.0f}")
    print("____")

def read_in_df(filename):
    """
    Reads in df from user inputed filename

    INPUT: a CSV filename
    OUTPUT: a usable dataframe
    """
    
    # Read our CSV file into a dataframe
    df = pd.read_csv(filename)

    # Combine the non-ID columns into an items column to be parsed for associations
    df['items'] = df[['BORO',
                      'CUISINE_DESC',
                      'CATEGORY_DESC',
                      'GRADE']].apply(lambda row: [str(item) for item in row], axis=1)
    
    # Return the newly formatted df
    return df

def join_sets(itemsets, k, min_sup, df):
    """
    Join frequent item sets of size k-1 to generate candidate item sets of size k.
    Apply Apriori pruning by checking the subsets of the candidate itemsets.

    INPUT: itemsets, k, min_sup passed by the user, the preprocessed dataframe
    OUTPUT: New candidate itemsets
    """

    # Initialize a set for unique new candidate itemsets
    new_candidate_itemsets = set()

    # Calculate minimum support count threshold using min_sup and the length of the df
    min_sup_count = min_sup * df.shape[0] 

    # Keep the user informed of which iteration of the A Priori algorithm is currently running
    print(f"Current iteration: k = {k}")

    for itemset1 in itemsets:
        for itemset2 in itemsets:
            # Ensure itemset1 and itemset2 are sets of items
            itemset1_set = set(itemset1.split(',') if isinstance(itemset1, str) else itemset1)
            itemset2_set = set(itemset2.split(',') if isinstance(itemset2, str) else itemset2)     
            union_set = itemset1_set | itemset2_set
       
            if len(union_set) == k:
                subsets = []
                
                if k <= 2:
                    subsets = [subset[0] for subset in combinations(union_set, k - 1)]
                else:
                    subsets = list(combinations(union_set, k - 1))
    
                # Check if all (k-1)-size listssubsets are in the itemsets 
                is_valid = all(tuple(sorted(subset)) in itemsets for subset in subsets) if k >= 3 else all(subset in itemsets for subset in subsets)
                if is_valid:

                    # Calculate support
                    current_freq = sum(1 for _, rows in df.iterrows() if union_set.issubset(rows['items']))

                    # Filter out infrequent itemsets
                    if current_freq >= min_sup_count:
                            current_support = current_freq / df.shape[0]
                            new_candidate_itemsets.add((tuple(sorted(union_set)), current_support))
                        
    return new_candidate_itemsets

def generate_freq_itemsets(df, min_sup):
    """
    Generate candidate item sets starting from size 2 using the a priori algorithm. 

    INPUT: Our dataset in a dataframe, min_sup passed by the user
    OUTPUT: Frequent itemsets
    """
    # Extract individual items from the 'items' column
    itemsets = df['items'].explode().value_counts()
    total_rows = df.shape[0]
    itemsets = itemsets / total_rows

    # Save frequent singleton itemsets to a dictionary
    frequent_1_itemsets = {item: support for item, support in itemsets.items() if support >= min_sup}

    # Store the freq singleton itemset dictionary to the freq_itemset dictionary under the key for singleton sets (frequent_1_itemsets)
    freq_itemsets = {'frequent_1_itemsets': frequent_1_itemsets}
    candidate_itemsets = set(frequent_1_itemsets.keys())

    # Initialize k at 2
    k = 2

    # Begin running a priori algorithm to generate larger itemsets starting with size k = 2
    ## Increment until no larger itemsets can be found
    while True:
        # Generate candidate item sets of size k
        new_candidate_itemsets = join_sets(candidate_itemsets, k, min_sup, df)
        if not new_candidate_itemsets:
            # Terminate the loop when no new candidates can be generated
            break
        
        # Save itemsets and associate them with the current iteration of the loop (size k)
        current_freq_name = 'frequent_' + str(k) + '_itemsets'
        freq_itemsets[current_freq_name] = new_candidate_itemsets
        candidate_itemsets = {itemset for itemset, _ in new_candidate_itemsets}

        # Increment k
        k += 1

    return freq_itemsets

def generate_assoc_rules(freq_itemsets, min_conf):
    """
    Generate association rules from frequent item sets with a min_conf inputted by the user through cmd line

    INPUT: Frequent itemsets created by generate_freq_itemsets(), min_conf passed by the user
    OUTPUT: Association rules
    """
    assoc_rules = []
    for itemnum, itemsets in freq_itemsets.items():
        # Single itemset (1-itemset) cannot be used in association rules
        ## Pass over singletons
        if itemnum == 'frequent_1_itemsets': 
            continue
        # Loop through all other larger frequent itemsets
        for itemset, support in itemsets:
            itemset = set(itemset)

            for i in range(1, len(itemset)):
                for lhs in combinations(itemset, i):
                    lhs = set(lhs)
                    # Find RHS by removing items that are found on the LHS
                    rhs = itemset - lhs

                    # Calculate support for the combined itemset
                    support_combined = support

                    # Calculate support for the LHS (only if LHS is a freq itemset), first if i == 1, to handle 1-itemsets ( is a dict)
                    current_freq = freq_itemsets['frequent_' + str(i) + '_itemsets'].items() if i == 1 else freq_itemsets['frequent_' + str(i) + '_itemsets']
                    
                    # Find support for LHS in freq_itemsets
                    support_lhs = 0
                    for current_itemset, current_support in current_freq:
                            current_itemset = set((current_itemset.split(',')) if isinstance(current_itemset, str) else current_itemset)
                            if current_itemset == lhs:
                                support_lhs = current_support
                                break
                   
                    # Calculate confidence
                    confidence = support_combined / support_lhs if support_lhs > 0 else 0
                    if confidence >= min_conf:
                        assoc_rules.append((lhs, rhs, confidence, support_combined))
    return assoc_rules

def format_itemsets(itemsets):
    """
    Helper function to unpackage and format frequent itemsets for easier printing to the console.

    INPUT: Frequent itemsets
    OUTPUT: Print friendly frequent itemsets
    """

    # Initialize a list to store itemsets
    all_itemsets = []

    # Unpack itemsets to the list depending on their position in the dict/set
    for _, value in itemsets.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                all_itemsets.append((sub_key, sub_value))
        elif isinstance(value, set):
            for itemset, support in value:
                all_itemsets.append((itemset, support))

    # Sort all by support value (desc)
    all_itemsets_sorted = sorted(all_itemsets, key=lambda x: x[1], reverse=True)
    
    formatted_itemsets = ""

    # Format each itemset for print out per the project guidelines
    for itemset, support in all_itemsets_sorted:
        formatted_itemsets += f"       {[itemset]} -- {support*100:.3f}%\n".replace('(','').replace(')','')
        
    return formatted_itemsets

def write_output(filename, itemsets, assoc_rules, min_sup, min_conf):
    """"
    Write the results of the program to a text file following the format outlined for the project.

    INPUT: A filename, frequent itemsets, association rules, min_sup and min_conf
    OUTPUT: A .txt file exported to the directory
    """

    # Initalize a text file to write to as output
    with open(filename, 'w') as output:
        # Frequent itemset set header
        output.write(f'====== Frequent itemsets (min_sup = {min_sup*100}%) ======\n')
        # Call helper function to write frequent itemsets
        output.write(format_itemsets(itemsets))
        
        # Write a gap to seperate support from confidence for readability
        output.write('\n')

        # Confidence header
        output.write(f'====== High-confidence association rules (min_conf = {min_conf*100}%) ======\n')
        # Sort association rules by confidence in descending order
        assoc_rules_sorted = sorted(assoc_rules, key=lambda x: x[2], reverse=True)

        # Loop through confidence rules and print them to the output file
        for lhs, rhs, confidence, combined_supp in assoc_rules_sorted:
            lhs_str = ", ".join(lhs)
            rhs_str = ", ".join(rhs)
            output.write(f'       [{lhs_str}] => [{rhs_str}] -- (Conf: {confidence*100:.3f}%, Supp: {combined_supp:.3%})\n')

def run_apriori(df, min_sup, min_conf):
    """
    Helper function to run the different components of the a priori algorithm and associated components.

    INPUT: dataset in a dataframe, min_sup, min_conf passed by user
    OUTPUT: Frequent itemsets from dataset and association rules with support and confidence
    """

    print("Generating frequent itemsets...")
    freq_itemsets = generate_freq_itemsets(df, min_sup)
    print("Generating association rules...")
    assoc_rules = generate_assoc_rules(freq_itemsets, min_conf)

    return freq_itemsets, assoc_rules

def main(min_sup,min_conf,df):
    """
    Main driver of program
    """
    
    # Print feedback to the user in the terminal
    query_print_cmd(min_sup,min_conf,df)

    # Initiate the A Priori algorith on the preprepared dataset
    print("Running A Priori algorithm. This will take a few moments...")
    freq_itemsets, assoc_rules = run_apriori(df,min_sup,min_conf)

    # Export results to text
    print("Exporting...")
    write_output('output.txt',freq_itemsets,assoc_rules,min_sup,min_conf)

if __name__ == "__main__":
    min_sup, min_conf, df = cmd_line()
    main(min_sup,min_conf,df)