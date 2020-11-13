import argparse
from os import path
from matplotlib import pyplot as plt

from utils import *


def main(opts):
    """
    Main executable function for script.

    Parameters
    ----------
    opts : argparse object
        Object containing variables set by default or the user via command line
    """
    check_file_validity([opts.as2_types_file, opts.as_rel2_file, opts.as_rv2_file, opts.as_org_file])

    (as_org_df, as_org_id_df) = get_org_dfs(opts.as_org_file)
    as2_type_df = get_df_from_file(opts.as2_types_file)
    as_rel2_df = get_df_from_file(opts.as_rel2_file)
    as_rv2_df = get_rv2_df(opts.as_rv2_file)

    data_dict = sort_classifications(as2_type_df)
    data_dict = sort_relationships(data_dict, as_rel2_df)
    data_dict = sort_ip_prefixes(data_dict, as_rv2_df)


    get_graph_1(data_dict)
    get_graph_2(data_dict)
    get_graph_3(data_dict)
    get_graph_4(data_dict)

    t1_ASes = infer_T1_ASes(data_dict)
    get_table_1(t1_ASes, as_org_df, as_org_id_df)


def get_graph_1(data_dict):
    """
    Given data in the form of a dictionary of AS (Autonomous Systems) Nodes, create a pie chart describing the
    distribution of the classes of AS Nodes.

    Parameters
    ----------
    data_dict : dictionary of AS Node objects
        data frame that contains AS data in the format of AS | source | Type
    """
    labels = ['Transit/Access', 'Content', 'Enterprise']
    bins = [0]*len(labels)
    for i in data_dict:
        if data_dict[i].classification == 'Transit/Access':
            bins[0] += 1
        elif data_dict[i].classification == 'Content':
            bins[1] += 1
        elif data_dict[i].classification == 'Enterprise':
            bins[2] += 1
    for i in range(len(bins)):
        labels[i] = f'{labels[i]} {round(bins[i]/sum(bins),2)}%'
    fig = plt.figure(figsize=(6, 3))
    ax = fig.add_subplot(111)
    ax.axis('equal')
    plt.title(f'Autonomous System Classification')
    pie = plt.pie(x=bins, explode=[0.05] * len(labels))
    ax.legend(pie[0], labels, loc='right', prop={'size': 4})
    plt.savefig(f'as_classifications.png', dpi=300, format='png', bbox_inches="tight")
    plt.close(fig)


def get_graph_2(data_dict):
    """
    Given data in the form of a dictionary of AS (Autonomous Systems) Nodes, create histogram of the node ranking
    categorized by six bins.

    Parameters
    ----------
    data_dict : dictionary of AS Node objects
        data frame that contains AS data in the format of AS | source | Type
    """
    labels = ['1', '2-5', '6-100', '101-200', '201-1000', '1000+']
    bins = [0]*len(labels)

    for i in data_dict:
        if data_dict[i].degree == 1:
            bins[0] += 1
        elif 2 < data_dict[i].degree <= 5:
            bins[1] += 1
        elif 5 < data_dict[i].degree <= 100:
            bins[2] += 1
        elif 100 < data_dict[i].degree <= 200:
            bins[3] += 1
        elif 200 < data_dict[i].degree <= 1000:
            bins[4] += 1
        elif 1000 < data_dict[i].degree:
            bins[5] += 1
    fig, ax1 = plt.subplots()
    rects = ax1.bar(list(range(len(bins))), bins)
    for rect in rects:
        height = rect.get_height()
        ax1.text(rect.get_x() + rect.get_width() / 2.,
                 height + 10, '%d' % int(height), ha='center', va='bottom')
    plt.xticks(list(range(len(labels))), labels)
    plt.xlabel('Number of Distinct Links')
    plt.ylabel('Number of Autonomous Systems')
    plt.title('Autonomous System Node Degree Distribution')
    plt.savefig('node_degree_dist.png', dpi=300)
    plt.close(fig)


def get_graph_3(data_dict):
    """
    Given a dataframe of AS (Autonomous Systems) IP mappings, create histogram of the IP space assigned to each AS

    Parameters
    ----------
    data_dict : dictionary of AS node object
    """
    labels = ['0-1000', '1000-10K', '10k-100k', '100k-1M', '1M-10M', '10M+']
    bins = [0]*len(labels)
    for i in data_dict:
        if data_dict[i].calc_space() <= 1000:
            bins[0] += 1
        elif 1000 < data_dict[i].calc_space() <= 10E3:
            bins[1] += 1
        elif 10E3 < data_dict[i].calc_space() <= 100E3:
            bins[2] += 1
        elif 100E3 < data_dict[i].calc_space() <= 1E6:
            bins[3] += 1
        elif 1E6 < data_dict[i].calc_space() <= 10E6:
            bins[4] += 1
        elif 10E6 < data_dict[i].calc_space():
            bins[5] += 1
    fig, ax1 = plt.subplots()
    rects = ax1.bar(list(range(len(bins))), bins)
    for rect in rects:
        height = rect.get_height()
        ax1.text(rect.get_x() + rect.get_width() / 2.,
                 height + 10, '%d' % int(height), ha='center', va='bottom')
    plt.xticks(list(range(len(labels))), labels)
    plt.xlabel('# of IPv4 addresses')
    plt.ylabel('Number of Autonomous Systems')
    plt.title('Autonomous System IP Space Distribution')
    plt.savefig('ip_space_dist.png', dpi=300)
    plt.close(fig)


def get_graph_4(data_dict):
    """
    Given data in the form of a dictionary of AS (Autonomous Systems) Nodes, create a pie chart describing the
    distribution of the classes of AS Nodes.

    Parameters
    ----------
    data_dict : dictionary of AS Node objects
        data frame that contains AS data in the format of AS | source | Type

    Returns
    -------
    None

    Raises
    ------
    None
    """
    labels = ['Transit/Access with\n >1 Customers', 'Transit/Access Other',
              'Content with no\n Customers and >1 peers', 'Content Other',
              'Enterprise with no\n Customers or Peers', 'Enterprise Other']
    bins = [0]*len(labels)
    for i in data_dict:
        if data_dict[i].classification == 'Transit/Access':
            if len(data_dict[i].customers) > 1:
                bins[0] += 1
            else:
                bins[1] += 1
        elif data_dict[i].classification == 'Content':
            if data_dict[i].degree > 1 and len(data_dict[i].customers) > 1:
                bins[2] += 1
            else:
                bins[3] += 1
        elif data_dict[i].classification == 'Enterprise':
            if data_dict[i].degree == 0 and len(data_dict[i].customers) == 0:
                bins[4] += 1
            else:
                bins[5] += 1
    for i in range(len(bins)):
        labels[i] = f'{labels[i]} {round(bins[i]/sum(bins),2)}%'
    fig = plt.figure(figsize=(6, 3))
    ax = fig.add_subplot(111)
    ax.axis('equal')
    ax.set_title(f'Detailed Autonomous System Classification')
    pie = plt.pie(x=bins, explode=[0.05] * len(labels))
    ax.legend(pie[0], labels, loc='right', prop={'size': 4})
    plt.savefig(f'as_classifications_detailed.png', dpi=300, format='png', bbox_inches="tight")
    plt.close(fig)

def get_table_1(top, org_df, id_df):
    for AS in top:
        org_id = id_df.loc[id_df['id'] == AS.name, 'org_id'].values[0]
        print(org_id)
        name = org_df.loc[org_df['org_id'] == org_id, 'name'].values[0]
        print(name)


def infer_T1_ASes(data_dict):
    sorted_dict = sorted(data_dict.items(), key=lambda x: x[1].degree, reverse=True)
    s = list()
    as_count = 0
    for AS in sorted_dict:
        if not s:
            s.append(AS[1])
        else:
            skip = False
            for node in s:
                if not AS[0] in node.connections:
                    if len(s) < 10:
                        skip = True
                        break
                    else:
                        return
            if not skip:
                s.append(AS[1])
        as_count += 1
        if as_count > 50:
            break
    return s

class Options:
    """
    Class to hold values that can be set by the user via command line or maintain default values and then assigns them
    to a class variable for later use.
    """
    def __init__(self):
        description = 'Command line inputs for project.'
        parser = argparse.ArgumentParser(description=description)
        inputs = self.parse_args(parser)
        self.as2_types_file = inputs.as2_types_file
        self.as_rel2_file = inputs.as_rel2_file
        self.as_rv2_file = inputs.as_rv2_file
        self.as_org_file = inputs.as_org_file

    @staticmethod
    def parse_args(parser):
        parser.add_argument('--as2-types', dest='as2_types_file', type=str,
                            action='store',
                            default=path.abspath(path.join(path.dirname(__file__), 'datasets/20201001.as2types.txt')),
                            help='AS2 type text file')
        parser.add_argument('--as-rel2', dest='as_rel2_file', type=str,
                            action='store',
                            default=path.abspath(path.join(path.dirname(__file__), 'datasets/20201001.as-rel2.txt')),
                            help='AS-rel2 text file.')
        parser.add_argument('--rv2', dest='as_rv2_file', type=str,
                            action='store',
                            default=path.abspath(path.join(path.dirname(__file__), 'datasets/routeviews-rv2-20201110-1200.pfx2as')),
                            help='AS-rv2 text file.')
        parser.add_argument('--orgs', dest='as_org_file', type=str,
                            action='store',
                            default=path.abspath(path.join(path.dirname(__file__), 'datasets/20201001.as-org2info.txt')),
                            help='Org info text file.')
        return parser.parse_args()


if __name__ == "__main__":
    options = Options()
    main(options)
