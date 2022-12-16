# baseline tram visualization for Lab 3, modified to work with Django

from .trams import readTramNetwork
from .graphs import dijkstra
import graphviz
import os
from django.conf import settings
import requests
from bs4 import BeautifulSoup
import tram.utils.create_network_picture as bt


def show_shortest(dep, dest):
    # TODO: uncomment this when it works with your own code
    network = readTramNetwork()
    dep = network._stopdict[dep]
    dest = network._stopdict[dest]

    # TODO: replace this mock-up with actual computation using dijkstra.
    # First you need to calculate the shortest and quickest paths, by using appropriate
    # cost functions in dijkstra().
    # Then you just need to use the lists of stops returned by dijkstra()
    #
    # If you do Bonus 1, you could also tell which tram lines you use and where changes
    # happen. But since this was not mentioned in lab3.md, it is not compulsory.
    quickest = dijkstra(network, dep, cost=lambda u, v: network.get_weight(u, v))
    shortest = dijkstra(network, dep, cost=lambda u, v: network.geo_distance(u, v))

    quickest_path = quickest[dest]['path']
    shortest_path = shortest[dest]['path']

    cost_of_quickest_path = quickest[dest]['cost']
    cost_of_shortest_path = shortest[dest]['cost']
    print(cost_of_shortest_path)

    quickest_path_names = [i.get_name() for i in quickest_path][::-1]
    shortest_path_names = [i.get_name() for i in shortest_path][::-1]

    timepath = 'Quickest from ' + dep.get_name() + ' to ' + dest.get_name() + ' is: ' + '[' + ' '.join(
        quickest_path_names) + ']' + ' and it takes ' + str(cost_of_quickest_path) + ' minutes'
    geopath = 'Shortest from ' + dep.get_name() + ' to ' + dest.get_name() + ' is: ' + '[' + ' '.join(
        shortest_path_names) + ']' + ' and it is ' + str(cost_of_shortest_path) + ' km long'

    # TODO: run this with the shortest-path colors to update the svg image
    if dest.get_name() in quickest_path_names:
        colormap = {str(v): 'orange' for v in quickest_path_names}
    if dest.get_name() in shortest_path_names:
        for v in shortest_path_names:
            if str(v) in colormap:
                colormap[str(v)] = 'cyan'
            else:
                colormap[str(v)] = 'green'

    bt.network_graphviz(network, bt.SHORTEST_PATH_SVG, colors=colormap)

    return timepath, geopath
