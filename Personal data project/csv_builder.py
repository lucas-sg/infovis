import csv
import json
from datetime import datetime
import calendar


def build_csv(matches):
    with open('./data/csgo_matches.csv', 'w') as csv_file:
        csv_writer = write_title_row(csv_file)
        
        for match in matches:
            match_stats = get_general_match_stats(match)

            for player in match['Team']:
                player_stats = get_player_stats(match['Team'][player])
                csv_writer.writerow(match_stats + [player] + player_stats)


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
            day_number = get_day_number(match['Date'])
            weekdays[day_number] += 1

        for day_num in range(len(weekdays)):
            csv_writer.writerow([calendar.day_name[day_num], weekdays[day_num]])

def get_day_number(date):
    return datetime.strptime(date, '%d/%m %H:%M').replace(year=2020).weekday()