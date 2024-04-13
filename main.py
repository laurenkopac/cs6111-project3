"""
main.py
"""

# Environment Set up
import sys
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

    df = read_in_data(filename)

    if df.shape[0] < 1000:
        print("Your cleaned dataset did not yield enough rows for this project.")
        print("Revisit your methodology and try again.")
        exit()

    return min_sup, min_conf, df

def query_print_cmd(min_sup, min_conf,df):
    """
    Display user inputted parameters and information about the dataset

    Input: Number iteration (starting with 0 for initial search), and desired relation description
    Output: A terminal print out for the user summarizing their inputed args
    """

    print("____")
    print('Parameters:')
    print(f"Minimum Support = {min_sup}")
    print(f"Minimum Confidence = {min_conf}")
    print(f"CSV Filename = {sys.argv[1]}")
    print(f"Number of Rows in Dataset = {df.shape[0]:,.0f}")

def read_in_data(filename):
    """
    Reads in data from user inputed filename

    INPUT: a CSV filename
    OUTPUT: a usable dataframe
    """
    df = pd.read_csv(filename)

    return df

def main():
    min_sup, min_conf, df = cmd_line()
    query_print_cmd(min_sup,min_conf,df)

if __name__ == "__main__":
    main()