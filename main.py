import argparse
from os import path
from matplotlib import pyplot as plt
import sys
import pandas as pd

from node_utils import ASNode


def main(opts):
    check_file_validity([opts.as2_types_file, opts.as_rel2_file])
    as2_type_df = get_df_from_file(opts.as2_types_file)
    data_dict = ASNode.sort_classifications(as2_type_df)
    get_graph_1(data_dict)
    import pdb; pdb.set_trace()
    as_rel2_df = get_df_from_file(opts.as_rel2_file)
    get_graph_2(df=as_rel2_df.T)


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
    df = pd.read_csv(file_, header=None, names=columns_list, delimiter=sep, skiprows=skip)
    return df


def get_graph_1(data_dict):
    labels = ['Transit/Access', 'Content', 'Enterprise']
    bins = [0]*len(labels)
    for i in data_dict:
        if data_dict[i].classification == 'Transit/Access':
            bins[0] += 1
        elif data_dict[i].classification == 'Content':
            bins[1] += 1
        elif data_dict[i].classification == 'Enterprise':
            bins[2] += 1
    fig, ax = plt.subplots()
    plt.pie(x=bins, autopct="%1.1f%%", explode=[0.05] * len(labels), labels=labels)
    ax.axis('equal')
    plt.title(f'AS Categories')
    plt.savefig(f'as_classifications.png', dpi=300, format='png')
    plt.close()


def get_graph_2(df):
    data_dict = {}
    for i in df:
        data_dict[df[i].ASa] = ASNode(node_name=df[i].ASa)
        data_dict[df[i].ASa].connections.append(df[i].ASb)
        data_dict[df[i].ASa].degree += 1
        if df[i].ASb in data_dict:
            data_dict[df[i].ASb].degree += 1
        else:
            data_dict[df[i].ASb] = ASNode(node_name=df[i].ASb)
            data_dict[df[i].ASb].connections.append(df[i].ASb)
            data_dict[df[i].ASb].degree += 1
        if df[i].Link == -1:
            data_dict[df[i].ASa].customer.append(df[i].ASb)
            
    bins = [0]*6
    for i in data_dict:
        import pdb; pdb.set_trace()
        if data_dict[i]['degree'] == 1:
            bins[0] += 1
        elif 2 < data_dict[i]['degree'] <= 5:
            bins[1] += 1
        elif 5 < data_dict[i]['degree'] <= 100:
            bins[2] += 1
        elif 100 < data_dict[i]['degree'] <= 200:
            bins[3] += 1
        elif 200 < data_dict[i]['degree'] <= 1000:
            bins[4] += 1
        elif 1000 < data_dict[i]['degree']:
            bins[5] += 1
    bin_names = ['1', '2-5', '6-100', '101-200', '201-1000', '1000+']

    fig1, ax1 = plt.subplots()
    rects = ax1.bar([0, 1, 2, 3, 4, 5], bins)
    plt.xticks([0, 1, 2, 3, 4, 5], bin_names)
    plt.title('AS Node Degree Distribution')
    plt.xlabel('Number of Distinct Links')
    plt.ylabel('Number of ASes')

    for rect in rects:
        height = rect.get_height()
        ax1.text(rect.get_x() + rect.get_width() / 2., height + 10, '%d' % int(height), ha='center', va='bottom')

    plt.savefig('node_degree_dist.png', dpi=300)


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
