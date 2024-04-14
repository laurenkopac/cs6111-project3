"""
main.py
"""

# Environment Set up
import sys
from itertools import combinations
import pandas as pd

# Initialize variables for minimum support and confidence, file name

def cmd_line():
    """
    Gather needed input from the user to run the program. If the structure is not correct, exit and give example usage. 

    Input: Command line input from user python main.py 
    Output: Either exit and explain proper usage or continue to execute the program
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

    Input: Number iteration (starting with 0 for initial search), and desired relation description
    Output: A terminal print out for the user summarizing their inputed args
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
    df = pd.read_csv(filename)

    df['items'] = df[['BORO',
                      'CUISINE_DESC',
                      'CATEGORY_DESC',
                      'GRADE']].apply(lambda row: [str(item) for item in row], axis=1)
    
    return df

def join_sets(itemsets, k, min_sup, df):
    """
    Join frequent item sets of size k-1 to generate candidate item sets of size k.
    Apply Apriori pruning by checking the subsets of the candidate itemsets.
    """
    new_candidate_itemsets = set()
    hash_tree = {}  # Hash tree to efficiently store and retrieve itemsets

    min_sup_count = min_sup * df.shape[0]  # Calculate minimum support count threshold

   # Construct the hash tree
    for itemset in itemsets:
        if len(itemset) == k - 1:
            for subset in combinations(itemset, k - 1):
                subset_set = frozenset(subset)
                hash_tree[subset_set] = True

    rows = df['items'].apply(frozenset)

    """
    TODO: remove hash tree functionality
    incorporate singleton sets into freq item sets if applicable
    what's going on with the grades column?
    """

    for itemset1 in itemsets:
        for itemset2 in itemsets:
            # Ensure itemset1 and itemset2 are sets of items
            itemset1_set = set(itemset1)
            itemset2_set = set(itemset2)
            
            union_set = itemset1_set.union(itemset2_set)
            if len(union_set) == k:
                # Generate k-size subsets
                subsets = [frozenset(subset) for subset in combinations(union_set, k - 1)]
                # Check if all (k-1)-size subsets are in the hash tree
                is_valid = all(subset in hash_tree for subset in subsets)
                if is_valid:
                    support = rows.apply(lambda rows: union_set.issubset(rows)).sum()
                    if support >= min_sup_count:
                        new_candidate_itemsets.add(frozenset(union_set))
                        # Add the new itemset to the hash tree
                        hash_tree[frozenset(union_set)] = True

    return new_candidate_itemsets

def generate_freq_itemsets(df, min_sup):
    """
    Generate candidate item sets starting from size 2.
    """
    # Extract individual items from the 'items' column, splitting them into words seperated by commas
    items = [set(item.split(',')) for sublist in df['items'] for item in sublist if len(item) > 1]
    unique_items = set(frozenset(item) for item in items)

    # Initialize candidate itemsets with singleton sets
    candidate_itemsets = {item: items.count(item) for item in unique_items}

    k = 2
    freq_itemsets = {}

    while True:
        new_candidate_itemsets = join_sets(candidate_itemsets.keys(), k, min_sup, df)
        if not new_candidate_itemsets:
            # Terminate the loop when no new candidates can be generated
            break
        
        # Filter out infrequent itemsets
        for itemset in new_candidate_itemsets:
            support = sum(1 for _, rows in df.iterrows() if itemset.issubset(rows['items']))
            if support >= min_sup:
                freq_itemsets[itemset] = support / df.shape[0]

        candidate_itemsets = {itemset: support for itemset, support in freq_itemsets.items()}
        k += 1

    return freq_itemsets

"""
TODO - assoc rules not currently returning any values
double check/fix conf calc
should it be support counts or supp % ?
"""

def generate_assoc_rules(freq_itemsets, min_conf, df_length):
    """
    Generate association rules from frequent item sets with a min_conf inputted by the user through cmnd
    """
    assoc_rules = []
    for itemset, support in freq_itemsets.items():
        if len(itemset) > 1:
            for i in range(1, len(itemset)):
                for lhs in combinations(itemset, i):
                    lhs = frozenset(lhs)  # Convert set to frozenset
                    # Find RHS by removing items that are found on the LHS
                    rhs = itemset - lhs
                    # Calculate support for the combined itemset
                    support_combined = support
                    # Calculate support for the LHS (only if LHS is a freq itemset)
                    try:
                        support_lhs = freq_itemsets[lhs]
                    except:
                        continue
                    # Calculate confidence
                    confidence = support_combined / support_lhs if support_lhs > 0 else 0
                    if confidence >= min_conf:
                        assoc_rules.append((lhs, rhs, confidence))
    return assoc_rules


def run_apriori(df, min_sup, min_conf):
    print("Generating frequent itemsets...")
    freq_itemsets = generate_freq_itemsets(df, min_sup)
    print("Generating association rules...")
    assoc_rules = generate_assoc_rules(freq_itemsets, min_conf)

    return freq_itemsets, assoc_rules

def write_output(filename, itemsets, assoc_rules, min_sup, min_conf):
    with open(filename, 'w') as output:
        output.write(f'====== Frequent itemsets (min_sup = {min_sup*100}%) ======\n')
        for itemset, support in sorted(itemsets.items(), key=lambda x: x[1], reverse=True):
            items_str = ", ".join(itemset)
            output.write(f'       [{items_str}] -- {support*100:.2f}%\n')

        output.write('\n')
        output.write(f'====== High-confidence association rules (min_conf = {min_conf*100}%) ======\n')
        for lhs, rhs, confidence in assoc_rules:
            lhs_str = ", ".join(lhs)
            rhs_str = ", ".join(rhs)
            output.write(f'       [{lhs_str}] => [{rhs_str}] -- (Confidence: {confidence*100:.2f}%)\n')

def main(min_sup,min_conf,df):
    
    query_print_cmd(min_sup,min_conf,df)

    print("Running A Priori algorithm...")
    freq_itemsets, assoc_rules = run_apriori(df,min_sup,min_conf)
    print("Exporting...")
    write_output('output.txt',freq_itemsets,assoc_rules,min_sup,min_conf)

if __name__ == "__main__":
    # itemsets -- contains all large itemsets with their support
    min_sup, min_conf, df = cmd_line()
    main(min_sup,min_conf,df)