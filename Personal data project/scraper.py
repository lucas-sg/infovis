from datetime import datetime, timedelta
import json
from bs4 import BeautifulSoup


def get_score(match, all_stats):
    score = match.find('td', class_='csgo_scoreboard_score').text
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
    elif label == 'Score':
        return 'Player score'
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


def format_date(date):
    extracted_datetime = datetime.strptime(date, '%Y-%m-%d %H:%M:%S GMT')
    arg_datetime = extracted_datetime - timedelta(hours=3)
    
    return arg_datetime.strftime('%d/%m %H:%M')


def get_match_stats(match):
    stats = {}
    all_players_stats = get_all_stats(match)
    [map_, date, _, duration] = get_metadata(match)
    stats['Map'] = map_.partition('Competitive ')[2]
    stats['Date'] = format_date(date)
    stats['Duration'] = duration.partition('Match Duration: ')[2]
    stats['Friends'] = count_friends(all_players_stats)
    stats['Score'] = get_score(match, all_players_stats)
    stats.update(all_players_stats)
    update_result(stats)

    return stats


def update_result(match):
    match['Result'] = 'tied' if match['Score'] == TIE else ('won' if won(match) else 'lost')
    match['Team'] = get_my_team(match)

    del match['Winners']
    del match['Losers']


def get_my_team(match):
    return match['Winners'] if I_AM in match['Winners'] else match['Losers']


def won(match):
    [us, _, them] = match['Score'].partition(SCORE_DIVIDER)

    return int(us) > int(them)


def i_got_disconnected(match):
    my = match['Team'][I_AM]

    return my['Kills'] == 0 and my['Assists'] == 0 and my['Deaths'] == 0


def my_stats_only(original_matches):
    matches = original_matches.copy()

    for match in matches:
        for player in match['Team']:
            if I_AM == player:
                match.update(match['Team'][player])
                del match['Team']

    return matches


def get_csgo_stats():
    stats = [get_match_stats(match) for match in matches]

    for match in stats:
        if i_got_disconnected(match):
            del stats[match]
    
    return stats


I_AM = 'Tablon James'
SCORE_DIVIDER = ' : '
TIE = '15 : 15'
FRIENDS = json.load(open('steam_friends.json', 'r'))
csgo_file = open('./data/csgo_steam_stats.html', 'r')
soup = BeautifulSoup(csgo_file, 'html.parser')
labels = get_stat_labels()
matches = soup.findAll('table', class_='csgo_scoreboard_inner_right')
