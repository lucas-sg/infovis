import json
from datetime import datetime, timedelta
from scraper import my_stats_only, get_csgo_stats
from csv_builder import build_csv_only_me, build_csv_matches_per_weekday, \
    build_csv_net_wins_per_map_timeline, build_csv_matches_per_map_timeline, build_csv_matches_per_hour, \
    build_csv_acc_matches_per_map_timeline


csgo_stats = get_csgo_stats()
my_stats = my_stats_only(csgo_stats)

with open('./data/csgo_matches_only_me.json', 'w') as outfile:
    json.dump(my_stats, outfile)

build_csv_only_me(my_stats)
build_csv_matches_per_weekday(my_stats)
build_csv_matches_per_hour(my_stats)
build_csv_net_wins_per_map_timeline(my_stats)
build_csv_matches_per_map_timeline(my_stats)
build_csv_acc_matches_per_map_timeline(my_stats)