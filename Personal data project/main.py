import json
from datetime import datetime, timedelta
from scraper import my_team_only, my_stats_only, get_csgo_stats
from csv_builder import build_csv, build_csv_only_me, build_csv_matches_per_weekday


csgo_stats = get_csgo_stats()

# with open('./data/csgo_matches_including_both_teams.json', 'w') as outfile:
#     json.dump(csgo_stats, outfile)

my_team_stats = my_team_only(csgo_stats)

with open('./data/csgo_matches.json', 'w') as outfile:
    json.dump(my_team_stats, outfile)

build_csv(my_team_stats)

my_stats = my_stats_only(my_team_stats)

with open('./data/csgo_matches_only_me.json', 'w') as outfile:
    json.dump(my_stats, outfile)

build_csv_only_me(my_stats)
build_csv_matches_per_weekday(my_stats)

# for match in my_stats[:2]:
    # print(datetime.strptime(match['Date'], '%Y-%m-%d %H:%M:%S GMT') - timedelta(hours=3))