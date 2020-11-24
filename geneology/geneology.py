import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
import random

'''
Запрос к базе данных, возвращающий пары "ребёнок - родитель"

SELECT child.id, child.surname, child.first_name, 
parent.id, parent.surname, parent.first_name,
relation."name"
FROM sociolinguistic_person child, 
sociolinguistic_person parent, 
sociolinguistic_personrelation person_relation,
sociolinguistic_relation relation
	WHERE person_relation.person1_id = child.id
	AND person_relation.person2_id = parent.id
	AND (person_relation.relation_id = 26 or person_relation.relation_id = 27)
	AND relation.id = person_relation.relation_id 
'''


class GeneologyTree:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.label_dict = {}
        self.edge_list_mother = []
        self.edge_list_father = []
        self.id_name, self.geneology = self.get_structures()
        self.filename = ""

    def get_data(self):
        data = pd.read_csv('query.csv', index_col=None, header=0, sep=",")
        data.rename(columns={'id': 'child_id',
                             'surname': 'child_surname',
                             'first_name': 'child_first_name',
                             r'id.1': 'parent_id',
                             r'surname.1': 'parent_surname',
                             r'first_name.1': 'parent_first_name',
                             'name': 'parent_rel'},
                    inplace=True)

        data['child_name'] = data['child_surname'] + ' ' + data['child_first_name']
        data['parent_name'] = data['parent_surname'] + ' ' + data['parent_first_name']
        data['child_name'].replace(np.nan, "(неизвестно)", inplace=True)
        data['parent_name'].replace(np.nan, "(неизвестно)", inplace=True)

        data.drop(columns=['child_surname', 'child_first_name',
                           'parent_surname', 'parent_first_name'])
        return data

    def create_id_name(self, person_id, person_name, id_name):
        if person_id not in id_name.keys():
            id_name[person_id] = person_name
        return id_name

    def create_geneology(self, child_id, parent_id, relation, geneology):
        if child_id in geneology.keys():
            if parent_id not in geneology[child_id].keys():
                geneology[child_id][parent_id] = relation
        else:
            geneology[child_id] = {}
            geneology[child_id][parent_id] = relation
        return geneology

    def get_structures(self):
        id_name = {}
        geneology = {}
        data = self.get_data()

        for child_id, child_name in zip(data['child_id'],
                                        data['child_name']):
            id_name = self.create_id_name(child_id, child_name, id_name)

        for parent_id, parent_name in zip(data['parent_id'],
                                          data['parent_name']):
            id_name = self.create_id_name(parent_id, parent_name, id_name)

        for child_id, child_name, parent_id, parent_name, parent_rel in zip(data['child_id'],
                                                                            data['child_name'],
                                                                            data['parent_id'],
                                                                            data['parent_name'],
                                                                            data['parent_rel']):
            geneology = self.create_geneology(child_id, parent_id, parent_rel, geneology)

        return id_name, geneology

    def get_person_id(self, person_name):
        if person_name in self.id_name.values():
            person_id = [key for key, value in self.id_name.items() if value == person_name]
            return person_id

    def add_node(self, person_id, person_name):
        if not self.graph.has_node(person_id):
            self.graph.add_node(person_id)
            if person_id not in self.label_dict.keys():
                self.label_dict[person_id] = person_name

    def add_edge(self, parent_id, child_id):
        if not self.graph.has_edge(parent_id, child_id):
            self.graph.add_edge(parent_id, child_id,
                                weight=1,
                                len=1)

    def add_relation(self, relation, parent_id, child_id):
        if relation == "mother":
            self.edge_list_mother.append((parent_id, child_id))
        else:
            self.edge_list_father.append((parent_id, child_id))

    def build_graph(self, parent_id, parent_name, child_id, child_name, relation):
        self.add_node(parent_id, parent_name)
        self.add_node(child_id, child_name)
        self.add_edge(parent_id, child_id)
        self.add_relation(relation, parent_id, child_id)

    def children(self, parent_id):
        for child_id, parents in self.geneology.items():
            if parent_id in parents.keys():
                parent_name = self.id_name[parent_id]
                child_name = self.id_name[child_id]
                relation = self.geneology[child_id][parent_id]
                self.build_graph(parent_id=parent_id,
                                 parent_name=parent_name,
                                 child_id=child_id,
                                 child_name=child_name,
                                 relation=relation)
                self.children(child_id)

        self.parents(parent_id)

    def parents(self, child_id):
        if child_id in self.geneology.keys():
            child_name = self.id_name[child_id]
            for parent_id in self.geneology[child_id].keys():
                parent_name = self.id_name[parent_id]
                relation = self.geneology[child_id][parent_id]
                self.build_graph(parent_id=parent_id,
                                 parent_name=parent_name,
                                 child_id=child_id,
                                 child_name=child_name,
                                 relation=relation)
                self.parents(parent_id)

    def geneology_tree(self, person_id):
        if person_id not in self.id_name.keys():
            return "Респондент с id %s не найден в базе данных" % person_id

        self.filename = self.id_name[person_id]
        self.children(person_id)
        self.parents(person_id)

    def geneology_tree_name(self, person_name):
        if person_name not in self.id_name.values():
            return "%s не найден в базе данных" % person_name

        self.filename = person_name
        person_ids = self.get_person_id(person_name)
        for person_id in person_ids:
            self.geneology_tree(person_id)

    def print_tree(self):
        pos = graphviz_layout(self.graph, prog="dot")
        nx.draw_networkx_edges(self.graph, pos,
                               edgelist=self.edge_list_mother,
                               edge_color="r",
                               width=2,
                               alpha=0.7)
        nx.draw_networkx_edges(self.graph, pos,
                               edgelist=self.edge_list_father,
                               edge_color="b",
                               width=2,
                               alpha=0.7)
        nx.draw_networkx_labels(self.graph, pos,
                                labels=self.label_dict,
                                font_weight='heavy')
        plt.show()

    def random_tree(self):
        person_id = random.choice(list(self.id_name.keys()))
        self.geneology_tree(person_id)
        self.print_tree()


# gt = GeneologyTree()
# # gt.random_tree()
# gt.geneology_tree_name("Макаров Николай")
# gt.geneology_tree(38275)
# gt.print_tree()
