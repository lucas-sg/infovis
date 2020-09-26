import requests
import urllib.request
import time
import json
from bs4 import BeautifulSoup


def get_score(match):
    return match.find('td', class_="csgo_scoreboard_score").text


def get_stat_labels():
    match = soup.find('table', class_="csgo_scoreboard_inner_right")
    parent_tag = match.find('th', class_="inner_name").parent
    tags = parent_tag.findAll('th', class_=None)

    return [get_label_name(tag.text) for tag in tags]


def get_label_name(label):
    if label == 'K':
        return 'Kills'
    elif label == 'A':
        return 'Assists'
    elif label == 'D':
        return 'Deaths'
    elif label == '★':
        return 'MVP'
    else:
        return label


def parse_mvp(mvp):
    star = '\u2605'

    if mvp[:1] == star:
        return mvp[1:] if mvp[1:] else "1"
    else:
        return "0"


def get_players(match):
    return [row for row in match.findAll('tr') if row.findAll('td', class_="inner_name")]


def get_stats_for_player(player):
    stats = [tag.text for tag in player.findAll('td', class_=None)]
    stats[labels.index("MVP")] = parse_mvp(stats[labels.index("MVP")])

    return stats


def get_stats_for_players(players):
    players_stats = {}

    for player in players:
        player_stats = get_stats_for_player(player)
        name = player.find('a', class_="linkTitle").text
        players_stats[name] = {}

        for label in labels:
            players_stats[name][label] = player_stats[labels.index(label)]

    return players_stats


def get_all_stats(match):
    all_stats = {}
    players = get_players(match)
    all_stats['Winners'] = get_stats_for_players(players[0:5])
    all_stats['Losers'] = get_stats_for_players(players[5:10])

    return all_stats


def get_metadata(match):
    parent_tag = match.parent.parent.find(
        'table', class_="csgo_scoreboard_inner_left")

    return [tag.text for tag in parent_tag.findAll('td', class_=None)][:4]


def get_match_stats(match):
    stats = {}
    [map_, date, _, duration] = get_metadata(match)
    stats['Map'] = map_
    stats['Date'] = date
    stats['Duration'] = duration.partition("Match Duration: ")[2]
    stats['Score'] = get_score(match)
    stats.update(get_all_stats(match))

    return stats


csgo_file = open("./csgo_matches.html")
soup = BeautifulSoup(csgo_file, "html.parser")
labels = get_stat_labels()
matches = soup.findAll('table', class_="csgo_scoreboard_inner_right")

with open("matches.json", "w") as outfile:
    json.dump([get_match_stats(match) for match in matches], outfile)

# matches = soup.findAll('table', class_="csgo_scoreboard_inner_right")
# [print(get_metadata(match)) for match in matches]
