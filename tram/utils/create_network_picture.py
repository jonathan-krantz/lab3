import graphviz
import json
import os
from django.conf import settings
import requests
from bs4 import BeautifulSoup
import static as st

TRAM_URLS = 'static/tram-url.json'
SHORTEST_PATH_SVG = os.path.join(settings.BASE_DIR,
                                 'tram/templates/tram/images/shortest_path.svg')

gbg_linecolors = {
    1: 'gray', 2: 'yellow', 3: 'blue', 4: 'green', 5: 'red',
    6: 'orange', 7: 'brown', 8: 'purple', 9: 'blue',
    10: 'lightgreen', 11: 'black', 13: 'pink'}


def scaled_position(network):
    # compute the scale of the map
    minlat, minlon, maxlat, maxlon = network.extreme_positions()
    size_x = maxlon - minlon
    scalefactor = len(network) / 4  # heuristic
    x_factor = scalefactor / size_x
    size_y = maxlat - minlat
    y_factor = scalefactor / size_y

    return lambda xy: (x_factor * (xy[1] - minlon), y_factor * (xy[0] - minlat))


def get_stop_url():
    response = requests.get('https://www.vasttrafik.se/reseplanering/hallplatslista/#C')

    soup = BeautifulSoup(response.text, 'html.parser')

    lines = soup.find_all('a')

    dict_of_url = {}
    for line in lines:
        temp_url = line['href']
        data = str(line.string).split('\n')
        if len(data) > 3:
            station = data[1].split(',')[0].strip()
            zone = data[3].split(',')[0].strip()
            dict_of_url[
                f"{station} {zone}"] = 'https://avgangstavla.vasttrafik.se/?source=vasttrafikse-depatureboardlinkgenerator&stopAreaGid=' + \
                                       temp_url.split('/')[-2]

    with open(TRAM_URLS, 'w') as file:
        json.dump(dict_of_url, file, indent=6)


def network_graphviz(network, outfile, colors=None, positions=scaled_position):
    dot = graphviz.Graph(engine='fdp', graph_attr={'size': '12,12'})

    get_stop_url()
    with open(TRAM_URLS, 'r') as file:
        url_dict = json.load(file)

    for stop in network.all_stops():

        x, y = network.stop_position(stop)
        if positions:
            x, y = positions(network)((x, y))
        pos_x, pos_y = str(x), str(y)

        if colors and stop in colors:
            col = colors[stop]
        else:
            col = 'white'

        dot.node(stop, label=stop, shape='rectangle', pos=pos_x + ',' + pos_y + '!',
                 fontsize='8pt', width='0.4', height='0.05',
                 URL=url_dict[stop + ' Zon A'],
                 fillcolor=col, style='filled')

    for line in network.all_lines():
        _stops = network.line_stops(line).get_stops()
        stops = [i.get_name() for i in _stops]
        for i in range(len(stops) - 1):
            dot.edge(stops[i], stops[i + 1],
                     color=gbg_linecolors[int(line)], penwidth=str(2))

    dot.format = 'svg'
    s = dot.pipe().decode('utf-8')
    with open(outfile, 'w') as file:
        file.write(s)

