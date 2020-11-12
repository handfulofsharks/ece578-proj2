class ASNode:
    def __init__(self, node_name):
        self.name = node_name
        self.degree = 0
        self.connections = list()
        self.customer = list()
        self.ip_prefs = list()
        self.classification = None
        self.org_type = ''
        self.org_id = 0
        self.cone_rank = 0
        self.ipv4_out = 0
        self.ipv4_pref_out = 0

    def sort_classifications(df):
        df = df.set_index(df.columns.values[0])
        data_dict = dict()
        for index, row in df.iterrows():
            data_dict[index] = ASNode(node_name=index)
            data_dict[index].classification = row.type
        return data_dict

    def sort_relationships(self, df):
        x = 5
