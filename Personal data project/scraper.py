import requests
import urllib.request
import time
import json
from bs4 import BeautifulSoup


def get_score(match, all_stats):
    score = match.find('td', class_='csgo_scoreboard_score').text
    SCORE_DIVIDER = ' : '
    [x, _, y] = score.partition(SCORE_DIVIDER)

    if I_AM in all_stats['Winners']:
        return score if int(x) >= int(y) else y + SCORE_DIVIDER + x
    else:
        [x, _, y] = score.partition(SCORE_DIVIDER)
        return score if int(x) < int(y) else y + SCORE_DIVIDER + x


def get_stat_labels():
    match = soup.find('table', class_='csgo_scoreboard_inner_right')
    parent_tag = match.find('th', class_='inner_name').parent
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


def parse_mvp(stats):
    mvp = stats[labels.index('MVP')]
    star = '\u2605'

    if mvp[:1] == star:
        stats[labels.index('MVP')] = mvp[1:] if mvp[1:] else '1'
    else:
        stats[labels.index('MVP')] = '0'


def parse_hsp(stats):
    hsp = stats[labels.index('HSP')]
    stats[labels.index('HSP')] = '0%' if hsp == '\u00a0' else hsp


def get_players(match):
    return [row for row in match.findAll('tr') if row.findAll('td', class_='inner_name')]


def get_stats_for_player(player):
    stats = [tag.text for tag in player.findAll('td', class_=None)]
    parse_mvp(stats)
    parse_hsp(stats)

    return stats


def get_stats_for_players(players):
    players_stats = {}

    for player in players:
        player_stats = get_stats_for_player(player)
        name = player.find('a', class_='linkTitle').text
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
        'table', class_='csgo_scoreboard_inner_left')

    return [tag.text for tag in parent_tag.findAll('td', class_=None)][:4]


def count_friends(match):
    team = match['Winners'] if I_AM in match['Winners'] else match['Losers']

    return len(set(team) & set(FRIENDS))


def get_match_stats(match):
    stats = {}
    all_players_stats = get_all_stats(match)
    [map_, date, _, duration] = get_metadata(match)
    stats['Map'] = map_.partition('Competitive ')[2]
    stats['Date'] = date
    stats['Duration'] = duration.partition('Match Duration: ')[2]
    stats['Friends'] = count_friends(all_players_stats)
    stats['Score'] = get_score(match, all_players_stats)
    stats.update(all_players_stats)

    return stats


def my_team_only(matches):
    for match in matches:
        if I_AM in match['Winners']:
            match['Result'] = 'won'
            match['Team'] = match['Winners']
        else:
            match['Result'] = 'lost'
            match['Team'] = match['Losers']

        del match['Winners']
        del match['Losers']

    return matches


I_AM = 'Tablon James'
FRIENDS = json.load(open('friends.json', 'r'))
csgo_file = open('./csgo_matches.html', 'r')
soup = BeautifulSoup(csgo_file, 'html.parser')
labels = get_stat_labels()
matches = soup.findAll('table', class_='csgo_scoreboard_inner_right')
csgo_stats = [get_match_stats(match) for match in matches]

with open('csgo_matches.json', 'w') as outfile:
    json.dump(my_team_only(csgo_stats), outfile)

time.sleep(5)

with open('csgo_matches_including_both_teams.json', 'w') as outfile:
    json.dump(csgo_stats, outfile)
