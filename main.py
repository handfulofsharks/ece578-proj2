import argparse
from os import path
from matplotlib import pyplot as plt
import sys
import pandas as pd


def main(options):
    check_file_validity([options.as2_types_file, options.as_rel2_file])
    as2_type_df = get_df_from_file(options.as2_types_file)
    get_graph_1(as2_type_df)
    as_rel2_df = get_df_from_file(options.as_rel2_file)
    get_graph_2(as_rel2_df)


def get_df_from_file(file_):
    column_values_str = None
    with open(file_, 'r') as f:
        skip = 0
        lines = f.readlines()
    for line in lines:
        if line.startswith("#"):
            skip += 1
        if 'format' in line:
            column_values_str = lines[0].split(' ')[-1].strip('\n')
            if column_values_str is not None:
                continue
    if column_values_str is None:
        column_values_str = 'ASa|ASb|Link|Source'
    sep = list(set([x for x in column_values_str if not x.isalpha() and x != ":" and not x.isnumeric()]))[0]
    columns_list = column_values_str.split(sep)
    df = pd.read_csv(file_, delimiter=sep, skiprows=skip)
    df.columns = columns_list
    return df


def get_graph_1(df):
    df = df.set_index(df.columns.values[0])
    for column in df.columns:
        values = df[column].value_counts()
        labels = list(set(df[column].values.tolist()))
        plt.pie(x=values, autopct="%.1f%%", explode=[0.05] * len(labels), labels=labels, pctdistance=0.5)
        plt.title(f'AS2 {column}')
        plt.savefig(f'{column}-pie.png')
    plt.close()


def get_graph_2(df,dataFile='data.csv'):
    if not path.exists(dataFile):
        list_a = df.ASa.values.tolist()
        list_b = df.ASb.values.tolist()
        data_list = list_a + list_b
        data_set = list(set(data_list))
        data_set.sort()
        degree_dict = {}
        # this takes a hot second, be aware
        for i in data_set:
            count_ = data_list.count(i)
            degree_dict[i] = count_
        data_df = pd.DataFrame([degree_dict])
        data_df.to_csv('data.csv')
    else:
        data_df = pd.read_csv(dataFile)
        data_df.drop(data_df.columns[0], axis=1, inplace=True)
        degree_dict = {}
        for i in data_df:
            degree_dict[i] = data_df[i].values.tolist()[0]
    bins = {'1': 0, '2-5': 0, '6-100': 0, '101-200': 0, '201-1000': 0, '1000+': 0}
    for i in degree_dict:
        j = int(i)
        if j == 1:
            bins['1'] += degree_dict[i]
        elif 1 < j <= 5:
            bins['2-5'] += degree_dict[i]
        elif 6 < j <= 100:
            bins['6-100'] += degree_dict[i]
        elif 100 < j <= 200:
            bins['101-200'] += degree_dict[i]
        elif 200 < j <= 1000:
            bins['201-1000'] += degree_dict[i]
        elif 1000 < j:
            bins['1000+'] += degree_dict[i]
    plt.bar(*zip(*bins.items()))
    plt.title('Histogram of Node Degree Distribution (Not-Normalized)')
    plt.savefig('node_degree_hist.png')
    plt.close()

    total = sum(list(degree_dict.values()))
    normalized_bins = {}
    for i in bins:
        normalized_bins[i] = bins[i]/total

    plt.bar(*zip(*normalized_bins.items()))
    plt.title('Histogram of Node Degree Distribution (Normalized)')
    plt.savefig('node_degree_hist_normalized.png')
    plt.close()
    plt.bar(*zip(*normalized_bins.items()), log=True)
    plt.title('Histogram of Node Degree Distribution (Normalized) with Log Scaling')
    plt.savefig('node_degree_hist_normalized_log_scaling.png')
    plt.close()


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
