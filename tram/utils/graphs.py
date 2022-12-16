import graphviz
import sys


class Graph:
    def __init__(self, list_of_edges=None):
        self._adjacencylist = {}
        self._valuelist = self.build_value_list()

        if list_of_edges:
            for (u, v) in list_of_edges:
                self.add_edge(u, v)

    def build_value_list(self):
        value_list = {}
        for vertex in self.vertices():
            value_list[vertex] = 1

        return value_list

    def neighbours(self, v):
        return self._adjacencylist[v]

    def vertices(self):
        list_of_vertices = []
        for vertex in self._adjacencylist:
            if vertex not in list_of_vertices:
                list_of_vertices.append(vertex)

        return list_of_vertices

    def edges(self):
        edges = []
        for a in self._adjacencylist:
            for b in self._adjacencylist[a]:
                if {a, b} not in edges:
                    edges.append({a, b})

        edges = [tuple(fs) for fs in edges]

        return edges

    def __len__(self):
        nr_of_vertices = 0
        for i in self._adjacencylist:
            nr_of_vertices += 1

        return nr_of_vertices

    def add_vertex(self, vertex):
        if vertex not in self._adjacencylist.keys() and vertex:
            self._adjacencylist[vertex] = []

    def add_edge(self, vertex1, vertex2):
        if vertex1 == vertex2:
            return
        if vertex1 in self._adjacencylist:
            if vertex2 not in self._adjacencylist[vertex1]:
                self._adjacencylist[vertex1].append(vertex2)
        else:
            self._adjacencylist[vertex1] = [vertex2]
        if vertex2 in self._adjacencylist:
            if vertex1 not in self._adjacencylist[vertex2]:
                self._adjacencylist[vertex2].append(vertex1)
        else:
            self._adjacencylist[vertex2] = [vertex1]

    def remove_vertex(self, vertex):
        pass

    def remove_edge(self, vertex1, vertex2):
        pass

    def get_vertex_value(self, vertex):
        if vertex in self.vertices():
            return self._valuelist[vertex]

    def set_vertex_value(self, vertex, value):
        if vertex in self.vertices():
            self._valuelist[vertex] = value


class WeightedGraph(Graph):
    def __init__(self, list_of_edges=None):
        super().__init__(list_of_edges)
        self._weightlist = self.build_weightlist()

    def build_weightlist(self):
        weight_list = {}
        for edge in self.edges():
            weight_list[edge] = 1

        return weight_list

    def set_weight(self, vertex1, vertex2, weight):
        if (vertex1, vertex2) in self._weightlist:
            self._weightlist[(vertex1, vertex2)] = weight
        elif (vertex2, vertex1) in self._weightlist:
            self._weightlist[(vertex2, vertex1)] = weight
        else:
            raise IndexError

    def get_weight(self, vertex1, vertex2):
        if (vertex1, vertex2) in self._weightlist:
            return self._weightlist[(vertex1, vertex2)]
        elif (vertex2, vertex1) in self._weightlist:
            return self._weightlist[(vertex2, vertex1)]


def dijkstra(graph, source, cost=lambda u, v: 1):
    inf = sys.maxsize
    length_of_paths = {v: float(inf) for v in graph.vertices()}
    prev_stops = {previous: None for previous in graph.vertices()}
    length_of_paths[source] = 0

    temp_verts = [v for v in graph.vertices()]
    while len(temp_verts) > 0:
        upper_bounds = {v: length_of_paths[v] for v in temp_verts}
        u = min(upper_bounds, key=upper_bounds.get)

        temp_verts.remove(u)
        for v in graph.neighbours(u):
            alt = length_of_paths[u] + cost(u, v)
            if alt < length_of_paths[v]:
                length_of_paths[v] = alt
                prev_stops[v] = u

    keys = list(prev_stops.keys())
    paths = {}
    for i in prev_stops.keys():
        path = [i]

        for key in keys:
            while key != i and path[-1] is not None:
                path.append(prev_stops[path[-1]])
        path.pop()
        paths[i] = path

    dict_of_path_and_cost = {target: {'path': paths[target], 'cost': None} for target in paths}
    for stop in length_of_paths:
        dict_of_path_and_cost[stop]['cost'] = length_of_paths[stop]

    return dict_of_path_and_cost


def random_pos(graph):
    from random import randrange
    return randrange(len(graph)), randrange(len(graph))


def visualize(graph, name='mygraph', nodecolors=None):
    dot = graphviz.Graph(engine='fdp')

    # ADDING NODES
    for v in graph.vertices():
        try:
            v = v.get_name()
            x, y = graph.stop_position(v)[1], graph.stop_position(v)[0]
        except AttributeError:
            v = v
            x, y = random_pos(graph)
        if nodecolors:
            if str(v) in nodecolors:
                dot.node(str(v), style='filled', fillcolor=nodecolors[str(v)], pos=str(x) + ',' + str(y) + '!')
            else:
                dot.node(str(v))
        else:
            dot.node(str(v))

    # ADDING EDGES
    for a, b in graph.edges():
        try:
            a = a.get_name()
            b = b.get_name()
        except AttributeError:
            a = a
            b = b
        dot.edge(str(a), str(b))

    dot.render(name+'.gv', view=True)


def view_shortest(graph, source, target, cost=lambda u, v: 1):

    try:
        source = graph._stopdict[source]
        target = graph._stopdict[target]
    except AttributeError:
        source = source
        target = target

    path = dijkstra(graph, source, cost)[target]['path']

    if target in path:
        try:
            colormap = {v.get_name(): 'orange' for v in path}
            visualize(graph, nodecolors=colormap)
        except AttributeError:
            colormap = {str(v): 'orange' for v in path}
            visualize(graph, nodecolors=colormap)
    else:
        print("No way from {} to {}".format(source, target))




