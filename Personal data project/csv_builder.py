import csv
import json
from datetime import datetime, timedelta
import calendar
import numpy as np
from collections import deque


def build_csv_only_me(matches):
    with open('./data/csgo_matches_only_me.csv', 'w') as csv_file:
        csv_writer = write_title_row(csv_file)

        for match in matches:
            match_stats = get_general_match_stats(match)
            csv_writer.writerow(get_my_stats(match))


def get_general_match_stats(match):
    return [match['Map'], match['Date'], match['Duration'], match['Friends'], match['Score'], match['Result']]


def get_player_stats(player):
    return [player['Ping'], player['Kills'], player['Assists'], player['Deaths'], player['MVP'], player['HSP'], player['Player score']]


def get_my_stats(match):
    return get_general_match_stats(match) + get_player_stats(match)


def write_title_row(csv_file):
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['Map', 'Date', 'Duration', 'Friends', 'Score', 'Result',
                         'Player', 'Ping', 'Kills', 'Assists', 'Deaths', 'MVP', 'HSP', 'Player score'])
    return csv_writer


def build_csv_matches_per_weekday(matches):
    weekdays = [0] * 7   # Monday=0, Tuesday=1, ..., Sunday=6

    with open('./data/csgo_matches_per_weekday.csv', 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Weekday', 'Matches'])

        for match in matches:
            day_number = format_date(match['Date']).weekday()
            weekdays[day_number] += 1

        for day_num in range(len(weekdays)):
            csv_writer.writerow(
                [calendar.day_name[day_num], weekdays[day_num]])


def format_date(date):
    return datetime.strptime(date, '%d/%m %H:%M').replace(year=2020)


def build_csv_net_wins_per_map_timeline(matches):
    maps = ['Inferno', 'Mirage', 'Cache', 'Dust II']

    with open('./data/csgo_net_wins_per_map_timeline.csv', 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Week'] + maps)
        net_results_per_date = get_matches_with_function(
            matches, maps, get_match_net_result)
        weekly_results = compress_matches_in_weeks(net_results_per_date, maps)
        [csv_writer.writerow(weekly_result)
         for weekly_result in weekly_results]


def get_matches_with_function(original_matches, maps, f):
    matches = original_matches.copy()
    matches.reverse()
    prev_match = [format_date(matches[0]['Date'])] + ([0] * len(maps))
    rows = []

    for match in matches[1:]:
        net_match_result = f(match, prev_match, maps)
        date = format_date(match['Date'])
        prev_match = [date] + net_match_result.copy()
        rows += [prev_match]

    return rows


def get_match_net_result(match, prev_match, maps):
    prev_results = prev_match[1:]
    result = 1 if match['Result'] == 'won' else - \
        1 if match['Result'] == 'lost' else 0
    map_index = maps.index(match['Map'])

    return [prev_results[i] + result if map_index == i else prev_results[i] for i in range(len(maps))]


def compress_matches_in_weeks(matches, maps):
    curr_week = get_week_of(matches[0][0])  # Second 0 is for the date
    weekly_matches = []
    week_num = 0

    for match in matches:
        if not match_is_in_curr_week(match, curr_week):
            curr_week += timedelta(weeks=1)
            week_num += 1

        weekly_matches = weekly_matches[:week_num] + [match]
        weekly_matches[week_num][0] = 'Week ' + str(week_num + 1)

    return weekly_matches


def match_is_in_curr_week(match, curr_week_monday):
    date = match[0]
    next_week_monday = curr_week_monday + timedelta(weeks=1)

    return date >= curr_week_monday and date < next_week_monday


def add_match_results_to_week(weekly_matches, match):
    weekly_results = np.array(weekly_matches[-1][1:])
    match_results = np.array(match[1:])

    return (weekly_results + match_results).tolist()


def build_csv_matches_per_map_timeline(matches):
    maps = ['Inferno', 'Mirage', 'Cache', 'Dust II']

    with open('./data/csgo_matches_per_map_timeline.csv', 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Week'] + maps + ['Total'])
        matches_per_map = get_matches_with_function(matches, maps, get_matches_per_map)
        weekly_results = compress_matches_in_weeks(matches_per_map, maps)
        [csv_writer.writerow(weekly_result + [sum(weekly_result[1:])])
         for weekly_result in weekly_results]


def build_csv_acc_matches_per_map_timeline(matches):
    maps = ['Inferno', 'Mirage', 'Cache', 'Dust II']

    with open('./data/csgo_acc_matches_per_map_timeline.csv', 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Week'] + maps)
        matches_per_map = get_matches_with_function(matches, maps, get_acc_matches_per_map)
        weekly_results = compress_matches_in_weeks(matches_per_map, maps)
        [csv_writer.writerow(weekly_result)
         for weekly_result in weekly_results]


def get_matches_per_map(match, prev_match, maps):
    match_week = get_week_of(format_date(match['Date']))
    prev_match_week = get_week_of(prev_match[0])
    prev_results = prev_match[1:]

    if match_week == prev_match_week:
        return [prev_results[i] + 1 if maps.index(match['Map']) == i else prev_results[i] for i in range(len(maps))]
    else:
        return [1 if maps.index(match['Map']) == i else 0 for i in range(len(maps))]


def get_acc_matches_per_map(match, prev_match, maps):
    match_week = get_week_of(format_date(match['Date']))
    prev_match_week = get_week_of(prev_match[0])
    prev_results = prev_match[1:]

    return [prev_results[i] + 1 if maps.index(match['Map']) == i else prev_results[i] for i in range(len(maps))]


def get_week_of(date):
    return (date - timedelta(days=date.weekday())).replace(hour=0, minute=0)


def build_csv_matches_per_hour(matches):
    hours = [0] * 24

    with open('./data/csgo_matches_per_hour.csv', 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Hour', 'Matches'])

        for match in matches:
            hour_played = get_hour_played(match)
            hours[hour_played] += 1
        
        matches_per_hour = deque([[ind, hourly_matches] for ind, hourly_matches in enumerate(hours)])
        matches_per_hour.rotate(12)
        [csv_writer.writerow(match) for match in matches_per_hour]


# Returns the hour (int) during which most of the match was played
def get_hour_played(match):
    date = format_date(match['Date'])
    duration = get_duration(datetime.strptime(match['Duration'], '%M:%S'))
    
    if (date.hour == (date + duration).hour):
        return date.hour
    
    next_hour = (date + timedelta(hours=1)).replace(minute=0, second=0)
    t_played_curr_hour = next_hour - date
    t_played_next_hour = date + duration - next_hour
    
    if (t_played_curr_hour > t_played_next_hour):
        return date.hour
    else:
        return next_hour.hour
    

def get_duration(d8time):
    return timedelta(minutes=d8time.minute, seconds=d8time.second)