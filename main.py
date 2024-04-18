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

    min_sup_count = min_sup * df.shape[0]  # Calculate minimum support count threshold

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
                    #calculate support
                    current_freq = sum(1 for _, rows in df.iterrows() if union_set.issubset(rows['items']))

                    # Filter out infrequent itemsets
                    if current_freq >= min_sup_count:
                            current_support = current_freq / df.shape[0]
                            new_candidate_itemsets.add((tuple(sorted(union_set)), current_support))
                        

    return new_candidate_itemsets

def generate_freq_itemsets(df, min_sup):
    """
    Generate candidate item sets starting from size 2.
    """
    # Extract individual items from the 'items' column, 
    itemsets = df['items'].explode().value_counts()
    total_rows = df.shape[0]
    itemsets = itemsets / total_rows

    frequent_1_itemsets = {item: support for item, support in itemsets.items() if support >= min_sup}

    freq_itemsets = {'frequent_1_itemsets': frequent_1_itemsets}
    candidate_itemsets = set(frequent_1_itemsets.keys())

    k = 2

    while True:
        # Generate candidate item sets of size k
        new_candidate_itemsets = join_sets(candidate_itemsets, k, min_sup, df)
        if not new_candidate_itemsets:
            # Terminate the loop when no new candidates can be generated
            break

        current_freq_name = 'frequent_' + str(k) + '_itemsets'
        freq_itemsets[current_freq_name] = new_candidate_itemsets
        candidate_itemsets = {itemset for itemset, _ in new_candidate_itemsets}
        k += 1

    return freq_itemsets

def generate_assoc_rules(freq_itemsets, min_conf):
    """
    Generate association rules from frequent item sets with a min_conf inputted by the user through cmnd
    """
    assoc_rules = []
    for itemnum, itemsets in freq_itemsets.items():
        if itemnum == 'frequent_1_itemsets': # single itemset (1-itemset) cannot be used in association rules
            continue
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
                    
                    # find support for LHS in freq_itemsets
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


def run_apriori(df, min_sup, min_conf):
    print("Generating frequent itemsets...")
    freq_itemsets = generate_freq_itemsets(df, min_sup)
    print("Generating association rules...")
    assoc_rules = generate_assoc_rules(freq_itemsets, min_conf)

    return freq_itemsets, assoc_rules

def format_itemsets(itemsets):
    all_itemsets = []
    for _, value in itemsets.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                all_itemsets.append((sub_key, sub_value))
        elif isinstance(value, set):
            for itemset, support in value:
                all_itemsets.append((itemset, support))

    all_itemsets_sorted = sorted(all_itemsets, key=lambda x: x[1], reverse=True)
    
    formatted_itemsets = ""
    for itemset, support in all_itemsets_sorted:
        formatted_itemsets += f"       {[itemset]} -- {support*100}%\n".replace('(','').replace(')','')
        
    return formatted_itemsets

def write_output(filename, itemsets, assoc_rules, min_sup, min_conf):
    with open(filename, 'w') as output:
        output.write(f'====== Frequent itemsets (min_sup = {min_sup*100}%) ======\n')
        output.write(format_itemsets(itemsets))

        output.write('\n')
        output.write(f'====== High-confidence association rules (min_conf = {min_conf*100}%) ======\n')
        # Sort association rules by confidence in descending order
        assoc_rules_sorted = sorted(assoc_rules, key=lambda x: x[2], reverse=True)

        for lhs, rhs, confidence, combined_supp in assoc_rules_sorted:
            lhs_str = ", ".join(lhs)
            rhs_str = ", ".join(rhs)
            output.write(f'       [{lhs_str}] => [{rhs_str}] -- (Conf: {confidence*100:.2f}%, Supp: {combined_supp:.2%})\n')

def main(min_sup,min_conf,df):
    
    query_print_cmd(min_sup,min_conf,df)

    print("Running A Priori algorithm...")
    freq_itemsets, assoc_rules = run_apriori(df,min_sup,min_conf)

    print("Exporting...")
    write_output('output.txt',freq_itemsets,assoc_rules,min_sup,min_conf)

if __name__ == "__main__":
    min_sup, min_conf, df = cmd_line()
    main(min_sup,min_conf,df)