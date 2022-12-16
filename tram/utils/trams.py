import json

# imports added in Lab3 version
import math
import os
from .graphs import WeightedGraph
from django.conf import settings
from .tramdata import get_distance_between_stops, lines_via_stop


# path changed from Lab2 version
# TODO: copy your json file from Lab 1 here
TRAM_FILE = os.path.join(settings.BASE_DIR, 'static/tramnetwork1.json')


# TODO: use your lab 2 class definition, but add one method


class TramNetwork(WeightedGraph):
    def __init__(self, lines, stops, times):
        super().__init__(list_of_edges=TramNetwork.build_edges(times, stops))
        self._linedict = lines
        self._stopdict = stops
        self._timedict = times
        self.add_all_time_weights()

    @staticmethod
    def build_edges(times, stops):
        edges = []
        for stop, neighbours in times.items():
            for neighbour in neighbours.keys():
                stop_instance = stops[stop]
                neighbour_instance = stops[neighbour]
                if (stop_instance, neighbour_instance) not in edges and (
                        neighbour_instance, stop_instance) not in edges:
                    edges.append((stop_instance, neighbour_instance))

        return edges

    def add_all_time_weights(self):
        for edge in self.edges():
            try:
                self.set_weight(edge[0], edge[1],
                                self._timedict[edge[0].get_name()][
                                                     edge[1].get_name()])
            except KeyError:
                self.set_weight(edge[0], edge[1],
                                self._timedict[edge[1].get_name()][
                                                     edge[0].get_name()])

    def all_lines(self):
        return [line for line in self._linedict]

    def all_stops(self):
        return [stop for stop in self._stopdict.keys()]

    def extreme_positions(self):
        lan_list = [edge.get_position()[0] for edge in self._stopdict.values()]
        lon_list = [edge.get_position()[1] for edge in self._stopdict.values()]
        return min(lan_list), min(lon_list), max(lan_list), max(lon_list)

    def geo_distance(self, a, b):
        string_dict1 = {stop: {'lat': self.stop_position(stop)[0], 'lon': self.stop_position(stop)[1]} for stop in self._stopdict}
        string_dict2 = {'stops': string_dict1}

        return get_distance_between_stops([a.get_name(), b.get_name()], string_dict2)

    def line_stops(self, line):
        return self._linedict[line]

    def stop_line(self, a):
        lines_via_stop = []

        for stops in self._linedict:
            if a in self._linedict[stops].get_stops():
                lines_via_stop.append(stops)

        return lines_via_stop

    def stop_position(self, a):
        return self._stopdict[a].get_position()

    def transition_time(self, a, b):
        pass


class TramStop:
    def __init__(self, stop: str, lines=None, lat=None, lon=None):
        self._name = stop
        if lines:
            self._lines = lines
        else:
            self._lines = []
        if lat and lon:
            self._position = (lat, lon)
        else:
            self._position = ()

    def add_line(self, line):
        self._lines.append(line)

    def get_lines(self):
        return self._lines

    def get_name(self):
        return self._name

    def get_position(self):
        return self._position

    def set_position(self, lat, lon):
        self._position = (lat, lon)


class TramLine:
    def __init__(self, line_num, stops: list):
        self._number = line_num
        self._stops = stops

    def get_number(self):
        return self._number

    def get_stops(self):
        return self._stops


def readTramNetwork(file=TRAM_FILE):
    with open(file, 'r') as data:
        tramnetwork = json.load(data)

    dict_of_stops = {stop: TramStop(stop, lines_via_stop(stop, tramnetwork), float(tramnetwork['stops'][stop]['lat']),
                                    float(tramnetwork['stops'][stop]['lon'])) for stop in tramnetwork['stops']}
    dict_of_lines = {}
    for line in tramnetwork['lines']:
        dict_of_lines[line] = TramLine(line, [dict_of_stops[stop] for stop in tramnetwork['lines'][line]])

    return TramNetwork(dict_of_lines, dict_of_stops, tramnetwork['times'])


def build_new_graph(original_graph):
    # create an empty graph
    new_graph = TramNetwork({}, {}, {})

    # add vertices to the new graph
    for stop in original_graph.vertices():
        for line in original_graph.stop_line(stop):
            new_graph.add_vertex((stop.get_name(), line))

    # add edges to the new graph
    for edge in original_graph.edges():
        a, b = edge
        for line in original_graph.all_lines():
            if line in original_graph.stop_line(a) and line in original_graph.stop_line(b):
                new_graph.add_edge((a.get_name(), line), (b.get_name(), line))

    # add edges between vertices with the same stop
    for stop in original_graph.vertices():
        for line1 in original_graph.stop_line(stop):
            for line2 in original_graph.stop_line(stop):
                if line1 != line2:
                    new_graph.add_edge((stop.get_name(), line1), (stop.get_name(), line2))

    new_graph._weightlist = new_graph.build_weightlist()

    edges = new_graph.edges()
    for u, v in edges:
        new_graph.set_weight(u, v, original_graph.get_weight(original_graph._stopdict[u[0]], original_graph._stopdict[v[0]]))

    return new_graph


# Bonus task 1: take changes into account and show used tram lines

def specialize_stops_to_lines(network):
    # TODO: write this function as specified
    return network


def specialized_transition_time(spec_network, a, b, changetime=10):
    # TODO: write this function as specified
    return changetime


def specialized_geo_distance(spec_network, a, b, changedistance=0.02):
    # TODO: write this function as specified
    return changedistance


