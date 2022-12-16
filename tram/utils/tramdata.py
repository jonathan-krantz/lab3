import json
import csv
import sys

TRAMLINES = 'tramlines.txt'
TRAMSTOPS = 'tramstops.json'
TRAMNETWORK = './tramnetwork1.json'


# ------------ STOPS --------------------


def json_to_dict_of_pos(file):
    data = open(file, 'r')
    tramstops = json.load(data)

    return {stop: {'lat': tramstops[stop]['position'][0], 'lon': tramstops[stop]['position'][1]} for stop in tramstops}


# ------------ LINES -------------------


def txt_to_list_of_stops(file):
    file = open(file, "r")
    list_of_stops = []
    list_of_times = []

    for line in file:
        line_list = line.strip().split('  ', 1)
        line_list_2 = line.strip().split('  ', 1)
        if len(line_list) > 1:
            line_list.remove(line_list[1])
            line_list_2.remove(line_list_2[0])
        for stop in line_list:
            list_of_stops.append(stop)
        for time in line_list_2:
            list_of_times.append(time)

    return [list_of_stops, list_of_times]


def list_to_dict_stops(file):
    list_of_stops = txt_to_list_of_stops(file)[0]
    dict_of_stops = {}

    list_stops = []
    for i in list_of_stops:
        if not i[0:1].isdigit() and i[0:1] != '':
            list_stops.append(i)
        elif i[0:1].isdigit() and not i[0:2].isdigit():
            list_stops = []
            dict_of_stops[i[0:1]] = list_stops
        elif i[0:1].isdigit() and i[0:2].isdigit():
            list_stops = []
            dict_of_stops[i[0:2]] = list_stops

    return dict_of_stops


def list_to_dict_times(file):
    list_of_times = txt_to_list_of_stops(file)[1]
    dict_of_arrival_times = {}

    list_stops = []
    for i in list_of_times:
        if i == "":
            continue
        if i[-1].isdigit() and i != '':
            list_stops.append(int(i[-2:]))
        elif i[0:1].isdigit() and not i[0:2].isdigit():
            list_stops = []
            dict_of_arrival_times[i[0:1]] = list_stops
        elif i[0:1].isdigit() and i[0:2].isdigit():
            list_stops = []
            dict_of_arrival_times[i[0:2]] = list_stops

    return dict_of_arrival_times


# ------------ TIMES -------------------


def dict_to_timedict(file):
    dict_of_arrival_times = list_to_dict_times(file)
    dict_of_stops = list_to_dict_stops(file)
    dict_of_time_differences = {}
    for i in dict_of_stops.values():
        temp_index = list(dict_of_stops.values()).index(i)
        for k in range(len(i) - 1):
            if i[k] not in list(dict_of_time_differences.keys()):
                dict_of_time_differences[i[k]] = {i[k + 1]: (list(dict_of_arrival_times.values())[temp_index][k + 1] -
                                                             list(dict_of_arrival_times.values())[temp_index][k])}
            elif i[k] in list(dict_of_time_differences.keys()):
                dict_of_time_differences[i[k]][i[k + 1]] = (list(dict_of_arrival_times.values())[temp_index][k + 1] -
                                                            list(dict_of_arrival_times.values())[temp_index][k])

    return [dict_of_time_differences, dict_of_stops]


# ----------- SUMMARIZED ------------------


def summarize_data(dict_stops, dict_lines, dict_times):
    return {'stops': dict_stops, 'lines': dict_lines, 'times': dict_times}


def build_json(in_file1, in_file2, in_file3):
    with open(in_file1, "w") as file:
        json.dump(
            summarize_data(json_to_dict_of_pos(in_file2), dict_to_timedict(in_file3)[1], dict_to_timedict(in_file3)[0]),
            file, indent=6)

    file.close()

    with open(TRAMNETWORK) as trams:
        summarized_dict = json.loads(trams.read())

    return summarized_dict


# ----------- QUERY FUNCTIONS -------------


def dialogue(jsonfile):
    print("""
Accepted inputs are:
via <stop>
between <stop1> and <stop2>
time with <line> from <stop1> to <stop2>
distance from <stop1> to <stop2>
quit

Obs: All stations must start with a capital letter.""")
    while True:
        try:
            input_string = input("> ")
            if "via" in input_string:
                print(lines_via_stop(input_string, jsonfile))
            elif "between" in input_string and not "time" in input_string:
                print(lines_between_stops(input_string, jsonfile))
            elif "time" in input_string:
                print(time_between_stops(input_string, jsonfile))
            elif "distance from" in input_string:
                print(get_distance_between_stops(input_string, jsonfile))
            elif "quit" in input_string:
                break
            else:
                print('Incorrect input format')
        except IndexError:
            print("Incorrect input format")
        except ValueError:
            print("Unknown argument")


def lines_via_stop(input_string, summarized_dict_):
    try:
        station = input_string.lstrip(" via ")
        station_list = []
    except IndexError:
        station = input_string
        station_list = []
    for line in summarized_dict_["lines"]:
        for element in summarized_dict_["lines"][line]:
            if element == station:
                station_list.append(line)
    if not station_list:
        return "There are no tramline that passes that tramstop."
    else:
        return station_list


def lines_between_stops(input_string, summarized_dict_):
    station1 = input_string.split("between ")[1]
    stops = station1.split(" and ")
    station_list = []
    for line in summarized_dict_["lines"]:
        if stops[0] in summarized_dict_["lines"][line] and stops[1] in summarized_dict_["lines"][line]:
            station_list.append(line)
    if not station_list:
        return "There are no tramlines that connects the given tramstops."
    elif stops[0] == stops[1]:
        return "You can't travel to the station your are already at, silly!"
    else:
        return (station_list)


def time_between_stops(input_string, summarized_dict_, line=None):
    station_list = []
    time_counter = 0

    if type(input_string) == str:
        split1 = input_string.split("time with ")[1]
        split2 = split1.split(" from ")[1].split(" to ")
        list_line_and_stations = [split1.split(" from ")[0], split2[0], split2[1]]
    else:
        list_line_and_stations = [line, input_string[0], input_string[1]]
    if list_line_and_stations[0] not in summarized_dict_["lines"]:
        return "No such line"
    else:
        index1 = summarized_dict_["lines"][list_line_and_stations[0]].index(list_line_and_stations[1])
        index2 = summarized_dict_["lines"][list_line_and_stations[0]].index(list_line_and_stations[2])
    if index1 > index2:
        index1, index2 = index2, index1
    for i in range(index1, index2 + 1):
        station_list.append(summarized_dict_["lines"][list_line_and_stations[0]][i])
    if station_list:
        for i in range(len(station_list) - 1):
            time_counter += summarized_dict_["times"][station_list[i]][station_list[i + 1]]
        return time_counter
    else:
        return "No stops inbetween the given stations"


def get_distance_between_stops(input_string, summarized_dict_):
    import math
    stop_dict = summarized_dict_['stops']

    if type(input_string) == str:
        stop1, stop2 = (input_string.split('distance from ')[1]).split(' to ')[0], \
                       (input_string.split('distance from ')[1]).split(' to ')[1]
    else:
        stop1, stop2 = input_string[0], input_string[1]

    if stop1 in stop_dict and stop2 in stop_dict:
        lat1, lon1 = float(stop_dict[stop1]['lat']), float(stop_dict[stop1]['lon'])
        lat2, lon2 = float(stop_dict[stop2]['lat']), float(stop_dict[stop2]['lon'])

        R = 6371000  # radius of Earth in meters

        phi_1 = math.radians(lat1)
        phi_2 = math.radians(lat2)

        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi_1) * math.cos(phi_2) * math.sin(delta_lambda / 2.0) ** 2

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c / 1000.0
    else:
        raise ValueError


if __name__ == '__main__':
    if sys.argv[1:] == ['init']:
        build_json(TRAMNETWORK, TRAMSTOPS, TRAMLINES)
    else:
        dialogue(build_json(TRAMNETWORK, TRAMSTOPS, TRAMLINES))
