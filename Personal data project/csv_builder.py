import csv
import json


def build_csv(matches):
    with open('csgo_matches.csv', 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Map', 'Date', 'Duration', 'Friends', 'Score', 'Result',
                             'Player', 'Ping', 'Kills', 'Assists', 'Deaths', 'MVP', 'HSP', 'Score'])

        for match in matches:
            match_stats = get_general_match_stats(match)

            for player in match['Team']:
                player_stats = get_player_stats(match['Team'][player])
                csv_writer.writerow(match_stats + [player] + player_stats)


def get_general_match_stats(match):
    return [match['Map'], match['Date'], match['Duration'], match['Friends'], match['Score'], match['Result']]


def get_player_stats(player):
    return [player['Ping'], player['Kills'], player['Assists'], player['Deaths'], player['MVP'], player['HSP'], player['Score']]
