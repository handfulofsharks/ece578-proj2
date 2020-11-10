import argparse
from os import path
from matplotlib import pyplot as plt
import sys
import pandas as pd


def main(options):
    check_file_validity([options.as2_types_file, options.as_rel2_file])
    as2_type_df = get_df_from_file(options.as2_types_file)
    get_pie_chart(as2_type_df)


def get_df_from_file(file_):
    with open(file_, 'r') as f:
        skip = 0
        lines = f.readlines()
    for line in lines:
        if line.startswith("#"):
            skip += 1
    column_values_str = lines[0].split(' ')[-1].strip('\n')
    sep = list(set([x for x in column_values_str if not x.isalpha() and x != ":" and not x.isnumeric()]))[0]
    columns_list = column_values_str.split(sep)
    df = pd.read_csv(file_, delimiter=sep, skiprows=skip)
    df.columns = columns_list
    df = df.set_index(df.columns.values[0])
    return df


def get_pie_chart(df):
    unique_vals = list(set(df.type.values.tolist()))
    vals_to_num = [x for x in range(len(unique_vals))]
    vals_dict = {unique_vals[i]: vals_to_num[i] for i in range(len(unique_vals))}
    df.type.replace(vals_dict, inplace=True)
    df.plot.pie(y='type')
    plt.show()


def check_file_validity(files):
    validity = 0
    for file_ in files:
        if not path.exists(file_) and not path.isfile(file_):
            print(f'INVALID file: {file_}')
        else:
            validity = 1
            print(f'VALID file:   {file_}')
    if validity != 1:
        sys.exit('Could not find user provided files.')
    else:
        return


class Options:
    def __init__(self):
        description = 'Command line inputs for project.'
        parser = argparse.ArgumentParser(description=description)
        # parses command line inputs.
        inputs = self.parse_args(parser)
        # assigns inputs from parseArgs function to class members
        self.as2_types_file = inputs.as2_types_file
        self.as_rel2_file = inputs.as_rel2_file

    def parse_args(self, parser):
        parser.add_argument('--as2-types', dest='as2_types_file', type=str,
                            action='store',
                            default=path.abspath(path.join(path.dirname(__file__), 'datasets/20201001.as2types.txt')),
                            help='AS2 type text file')

        parser.add_argument('--as-rel2', dest='as_rel2_file', type=str,
                            action='store',
                            default=path.abspath(path.join(path.dirname(__file__), 'datasets/20201001.as-rel2.txt')),
                            help='AS-rel2 text file.')

        return parser.parse_args()


if __name__ == "__main__":
    options = Options()
    main(options)
