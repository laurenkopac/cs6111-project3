"""
main.py
"""

# Environment Set up
import sys
from itertools import combinations
import pandas as pd
import operator

# Initialize variables for minimum support and confidence, file name

def cmd_line():
    """
    Gather needed input from the user to run the program. If the structure is not correct, exit and give example usage. 

    Input: Command line input from user python main.py 
    Output: Either exit and explain proper usage or continue to execute the program
    """
    # If too few or too many args passed, exit and explain
    if len(sys.argv) != 4:
        print(f"Usage: python3 main.py INTEGRATED-dfSET.csv <min_sup> <min_conf>: {len(sys.argv)}")
        exit(1)

    # Extract command line arguments: min_sup and min_conf
    try:
        # Asserts the parameters passed are numbers
        min_sup = float(sys.argv[2])
        min_conf = float(sys.argv[3])

        # Check to make sure parameters are greater than or equal to 0, and less than 1.
        if (min_sup <= 0) | (min_conf <=0):
            raise ValueError("Your parameters for min_sup and min_conf cannot be less than or equal to 0.")
        if (min_sup > 1) | (min_conf > 1):
            raise ValueError("Your parameters for min_sup and min_conf cannot be greater than 1.")

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    filename = sys.argv[1]

    df = read_in_df(filename)

    return min_sup, min_conf, df

def query_print_cmd(min_sup, min_conf,df):
    """
    Display user inputted parameters and information about the dfset

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
    OUTPUT: a usable dfframe
    """
    df = pd.read_csv(filename)

    return df

def init(df, min_sup):
    # Extract all large itemsets with a size of 1 and calculate the support metric
    cache = {}
    l1 = []
    n = df.shape[0]
    for index, row in df.iterrows():
        for item in row:
            item_str = str(item)  # Convert to string
            if len(item_str) == 0:
                continue
            if (item_str,) not in cache:  # Wrap item in a tuple to create a singleton itemset
                cache[(item_str,)] = 0
            cache[(item_str,)] += 1
    for item in sorted(cache.keys()):
        cur_supp = float(cache[item]) / n
        if cur_supp >= min_sup:
            item_sets[item] = cur_supp
            l1.append(item)
        else:
            cache.pop(item)
    return l1

def apriori_gen(l, k):
    c_k = []
    helper_set = set(l)
    for s in l:
        helper_set.add(s)
    for p, q in combinations(l, 2):
        if p[:k - 1] == q[:k - 1]:
            new_tuple = list(p)
            new_tuple.append(q[k - 2])
            c_k.append(tuple(sorted(new_tuple)))
    return c_k

def get_l(c_k, k, df, min_sup):
    cache = {}
    # Count the frequency
    helper_set = set()
    for c in c_k:
        helper_set.add(c)

    n = len(df)
    for index, row in df.iterrows():
        c_t = set()
        for i in row:
            c_t.add((i,))
        for c in c_t.intersection(helper_set):
            if c not in cache:
                cache[c] = 1.0
            else:
                cache[c] += 1
    # Calculate support and generate l_k
    l = []
    for c in sorted(cache.keys()):
        cur_supp = cache[c] / n
        if cur_supp >= min_sup:
            item_sets[c] = cur_supp
            l.append(c)
    return l

def apriori(df, min_sup):
    # Generate all large itemsets
    # l -- list type, is a table, each row is a tuple
    l = init(df,min_sup)
    k = 2
    while len(l) != 0:
        c_k = apriori_gen(l, k)
        l = get_l(c_k, k, df, min_sup)
        k += 1
    return item_sets

def generate(item_sets, min_conf):
    # Generate high-confidence rules
    rules = {}
    for itemset in item_sets.keys():
        if len(itemset) == 1:
            continue
        for item in itemset:
            LHS = list(itemset)
            LHS.remove(item)
            LHS_supp = item_sets[tuple(LHS)]
            RHS_and_LHS_supp = item_sets[itemset]
            if LHS_supp > 0:
                cur_conf = RHS_and_LHS_supp / LHS_supp
                RHS = []
                RHS.append(item)
                if cur_conf >= min_conf:
                    temp = {}
                    temp['conf'] = cur_conf
                    temp['supp'] = item_sets[itemset]
                    key = '[' + ', '.join(LHS) + '] => '
                    key += '[' + str(RHS[0]) + ']'
                    rules[key] = temp
    return rules

def write_output(filename,item_sets,min_sup,min_conf):

    with open(filename, 'w') as output:
        output.write(f'====== Frequent itemsets (min_sup = {min_sup*100}%) ======\n')
        for item_set, support in sorted(item_sets.items(), key=lambda x: x[1], reverse=True):
            items_str = ", ".join(item_set)
            output.write(f'       [{items_str}] -- {support*100:.2f}%\n')

        # Extract rules
        rules = generate(item_sets, min_conf)
        sorted_rules = sorted(rules.items(), key=lambda x: x[1]['conf'], reverse=True)

        output.write('\n')
        output.write(f'====== High-confidence association rules (min_conf = {min_conf*100}%) ======\n')
        for rule, metrics in sorted_rules:
            lhs_items_str = ", ".join(rule.split(' => ')[0][1:-1].split(', '))
            rhs_item_str = rule.split(' => ')[1][1:-1]
            conf = metrics['conf']*100
            supp = metrics['supp']*100
            output.write(f'       [{lhs_items_str}] => [{rhs_item_str}] -- (Conf: {conf:.2f}%  Supp: {supp:.2f}%)\n')

def main(min_sup,min_conf,df):
    
    query_print_cmd(min_sup,min_conf,df)

    print("Running A Priori algorithm...")
    apriori(df, min_sup)

    print("Exporting...")
    write_output('output.txt',item_sets,min_sup,min_conf)

if __name__ == "__main__":
    # item_sets -- contains all large itemsets with their support
    item_sets = {}
    min_sup, min_conf, df = cmd_line()
    main(min_sup,min_conf,df)