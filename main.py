import argparse
from os import path
from matplotlib import pyplot as plt
import sys
import pandas as pd

from node_utils import *


def main(opts):
    """
    Main executable function for script.

    Parameters
    ----------
    opts : argparse object
        Object containing variables set by default or the user via command line

    Returns
    -------
    None

    Raises
    ------
    None
    """
    check_file_validity([opts.as2_types_file, opts.as_rel2_file])
    as2_type_df = get_df_from_file(opts.as2_types_file)
    data_dict = sort_classifications(as2_type_df)
    get_graph_1(data_dict)
    as_rel2_df = get_df_from_file(opts.as_rel2_file)
    data_dict = sort_relationships(data_dict, as_rel2_df)
    get_graph_2(data_dict)


def get_graph_1(data_dict):
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
    plt.close(fig)


def get_graph_2(data_dict):
    """
    Given data in the form of a dictionary of AS (Autonomous Systems) Nodes, create histogram of the node ranking
    categorized by six bins.

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
    plt.title('AS Node Degree Distribution')
    plt.xlabel('Number of Distinct Links')
    plt.ylabel('Number of ASes')
    plt.savefig('node_degree_dist.png', dpi=300)
    plt.close(fig)
class Options:
    """
    Class to hold values that can be set by the user via command line or maintain default values and then assigns them
    to a class variable for later use.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Raises
    ------
    None
    """
    def __init__(self):
        description = 'Command line inputs for project.'
        parser = argparse.ArgumentParser(description=description)
        inputs = self.parse_args(parser)
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
