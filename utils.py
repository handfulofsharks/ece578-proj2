class ASNode:
    """
    Class to contain AS (Autonomous Systems) node information

    Parameters
    ----------
    node_name : string
        String containing the name of the node

    Returns
    -------
    None

    Raises
    ------
    None
    """
    def __init__(self, node_name):
        self.name = node_name
        self.degree = 0
        self.connections = list()
        self.customers = list()
        self.ip_prefs = list()
        self.classification = None
        self.org_type = ''
        self.org_id = 0
        self.cone_rank = 0
        self.ipv4_out = 0
        self.ipv4_pref_out = 0
    def calc_space(self):
        space = 0
        for ip in self.ip_prefs:
            space += ip.space
        return space


class IP_Prefix:
    def __init__(self, prefix, length):
        self.prefix = prefix
        self.length = length
        self.space = pow(2, 32 - self.length)
    
def sort_classifications(df):
    """
    Read in a data frame that contains AS (Autonomous Systems) classification data and parse it into node
    objects.

    Parameters
    ----------
    df : pandas dataframe
        data frame that contains AS data in the format of AS | source | Type

    Returns
    -------
    data_dict
        dictionary of AS Node objects

    Raises
    ------
    None
    """
    df = df.set_index(df.columns.values[0])
    data_dict = dict()
    for index, row in df.iterrows():
        data_dict[index] = ASNode(node_name=index)
        data_dict[index].classification = row.type
    return data_dict


def sort_relationships(data_dict, df):
    """
    Read in a data frame that contains AS (Autonomous Systems) relationship data and parse it into node
    objects.

    Parameters
    ----------
    data_dict : dictionary of node objections
        dictionary of AS Node objects
    df : pandas dataframe
        data frame that contains AS data in the format of ASa | ASb | Link

    Returns
    -------
    data_dict
        dictionary of node objects

    Raises
    ------
    None
    """
    df.set_index(df.columns.values[0], inplace=True)
    for index, row in df.iterrows():
        if index in data_dict:
            data_dict[index].degree += 1
            data_dict[index].connections.append(row.ASb)
        else:
            data_dict[index] = ASNode(node_name=index)
            data_dict[index].degree += 1
            data_dict[index].connections.append(row.ASb)
        if row.ASb in data_dict:
            data_dict[row.ASb].degree += 1
            data_dict[row.ASb].connections.append(index)
        else:
            data_dict[row.ASb] = ASNode(node_name=row.ASb)
            data_dict[row.ASb].degree += 1
            data_dict[row.ASb].connections.append(index)
        if row.Link == -1:
            data_dict[index].customers.append(row.ASb)
    return data_dict

def sort_ip_prefixes(data_dict, df):
    import re
    df.set_index(df.columns.values[2], inplace=True)
    for index, row in df.iterrows():
        ASes = re.findall(r'\d+', index)
        if ASes:
            for AS in ASes:
                AS = int(AS)
                if AS in data_dict:
                    data_dict[AS].ip_prefs.append(IP_Prefix(row[0], row[1]))
                else:
                    data_dict[AS] = ASNode(node_name=AS)
                    data_dict[AS].ip_prefs.append(IP_Prefix(row[0], row[1]))
    return data_dict

def check_file_validity(files):
    """
    Given a list of files, verifies that files can be found.

    Parameters
    ----------
    files : list of strings
        list containing file path strings

    Returns
    -------
    None

    Raises
    ------
    None
    """
    from os import path
    import sys
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


def get_df_from_file(file_):
    """
    Given a file, reads in that file via pandas and attempts to correctly determine header information

    Parameters
    ----------
    file_ : string
        String of the path to the file

    Returns
    -------
    df: pandas dataframe
        dataframe containing information from the file read

    Raises
    ------
    None
    """
    import pandas as pd
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

def get_rv2_df(file_):
    import pandas as pd
    df = pd.read_csv(file_, header=None, sep="\t")
    df.columns = ['IP', 'Prefix-Length', 'AS']
    return df