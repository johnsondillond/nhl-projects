"""
This module is for organizing team data and getting matchup analysis
for determining teams with most games in a week & most rest days as well
"""
from datetime import date, timedelta
import json
import os
import sys
import requests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# pylint: disable=C0413
from Utils.Constants import Constants

class ESPN:
    def __init__(self):
        self.constant_obj = Constants()
        self.base_url = "https://api-web.nhle.com/v1/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        self.nhl_teams, self.nhl_clubhouse_links, self.nhl_roster_links, \
        self.nhl_stats_links, self.nhl_schedules_links = self.load_teams()
        # self.get_nhl_teams()
        # self.get_nhl_team_standings()
        # self.get_nhl_rem_schedule()
        # self.get_nhl_schedule()
        # self.get_nhl_team_rosters()
        # self.master_schedule_formatter()
        matchup_file = 'ESPNData/matchups/10/matchup_03.json'
        self.games_by_matchup(matchup_file,
            start_date=date(2025, 10, 20))
        self.matchup_analysis(matchup_file)
        # self.season_weekday_analysis()
        self.matchup_team_ranks(matchup_file)

    def get_nhl_teams(self):
        api_endpoint = self.base_url + "en/team"
        response = requests.get(api_endpoint, headers=self.headers, timeout=5)
        if response.status_code == 200:
            data = response.json
            with open("ESPNData/nhl_teams.json", "w", encoding='utf-8') as f:
                json.dump(data, f, indent=4)



    def load_teams(self):
        url = "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/teams"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            for team_data in data["sports"][0]["leagues"][0]["teams"]:
                if team_data["team"]["name"] in self.constant_obj.intl_teams:
                    data["sports"][0]["leagues"][0]["teams"].remove(team_data)

            with open("ESPNData/nhl_teams.json", "w", encoding='utf-8') as f:
                json.dump(data, f, indent=4)

            teams = data['sports'][0]["leagues"][0]["teams"]
            for team in teams:
                print(f"Team: {team["team"]['name']}, ID: {team["team"]['id']}")
        else:
            print(f"Error: Unable to fetch data. Status code: {response.status_code}")

        with open("ESPNData/nhl_teams.json", "r", encoding='utf-8') as f:
            saved_data = json.load(f)

        teams = saved_data["sports"][0]["leagues"][0]["teams"]

        team_clubhouses, team_rosters, team_stats, team_schedules, teams_list = [], [], [], [], []
        for index, _ in enumerate(teams):
            team = teams[index]["team"]
            teams_list.append(team['displayName'])
            team_abbrev = team["abbreviation"].lower()
            slug = team["slug"]
            links = {
                team_abbrev:
            {
                "clubhouse": f"https://www.espn.com/nhl/team/_/name/{team_abbrev}/{slug}",
                "roster": f"https://www.espn.com/nhl/team/roster/_/name/{team_abbrev}/{slug}",
                "stats": f"https://www.espn.com/nhl/team/stats/_/name/{team_abbrev}/{slug}",
                "schedule": f"https://www.espn.com/nhl/team/schedule/_/name/{team_abbrev}/{slug}"
            }
        }
            team_clubhouses.append(links[team_abbrev]["clubhouse"])
            team_rosters.append(links[team_abbrev]["roster"])
            team_stats.append(links[team_abbrev]["stats"])
            team_schedules.append(links[team_abbrev]["schedule"])

        return teams_list, team_clubhouses, team_rosters, team_stats, team_schedules

    def get_nhl_team_standings(self):
        api_endpoint = self.base_url + "standings/now"
        response = requests.get(api_endpoint, headers=self.headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            self.populate_team_standings(data)

        
    def populate_team_standings(self, standings_data):
        # min_ga_pct = ("", float('inf'))
        
        for standing in standings_data["standings"]:
            del standing["l10Ties"], standing["roadTies"], standing['homeTies'], standing['ties']

            standing["OtLosses"] = standing["otLosses"]
            standing['goalsAgainst'] = standing['goalAgainst']
            standing['goalsFor'] = standing['goalFor']
            del standing["otLosses"], standing['goalAgainst'], standing['goalFor']
            standing["OtWins"] = standing["regulationPlusOtWins"] - standing["regulationWins"]
            standing["OtWinPctg"] = standing["OtWins"] / (standing["OtWins"] + standing["OtLosses"])
            standing["shootoutWinPctg"] = standing["shootoutWins"] / (standing["shootoutWins"] + standing["shootoutLosses"]) if standing["shootoutWins"] != 0 and standing["shootoutLosses"] != 0 else 0
            standing["roadPointPctg"] = standing['roadPoints'] / (standing['roadGamesPlayed'] * 2)
            standing["homePointPctg"] = standing["homePoints"] / (standing['homeGamesPlayed'] * 2)
            standing['goalsAgainstPctg'] = standing['goalsAgainst'] / standing['gamesPlayed']

        #   if standing["goalsAgainstPctg"] < min_ga_pct[1]:
        #         min_ga_pct = (standing["teamName"]["default"], standing["goalsAgainstPctg"])
        # print(min_ga_pct)

        with open("ESPNData/nhl_team_standings.json", "w", encoding='utf-8') as f:
            json.dump(standings_data, f, indent=4)
        
    def get_nhl_team_rosters(self):
        data = {"nhlRosters": []}
        for name, abbrev in self.constant_obj.pro_team_abbrev.items():
            api_endpoint = self.base_url + f"roster/{abbrev}/current"
            response = requests.get(api_endpoint, headers=self.headers, timeout=5)
            if response.status_code == 200:
                data['nhlRosters'].append({name: response.json()})
                with open("ESPNData/nhl_team_rosters.json", "w", encoding='utf-8') as f:
                    json.dump(data, f, indent=4)

    def get_nhl_rem_schedule(self):
        data = {"nhlSchedules": []}
        for name, abbrev in self.constant_obj.pro_team_abbrev.items():
            api_endpoint = self.base_url + f"club-schedule-season/{abbrev}/now"
            response = requests.get(api_endpoint, headers=self.headers, timeout=5)
            if response.status_code == 200:
                data['nhlSchedules'].append({name: response.json()})
                with open("ESPNData/nhl_full_team_schedules.json", "w", encoding='utf-8') as f:
                    json.dump(data, f, indent=4)
            
    def get_nhl_schedule(self):
        data = {"nhlSchedules": {}}
        api_endpoint = self.base_url + "schedule/now"
        response = requests.get(api_endpoint, headers=self.headers, timeout=5)
        if response.status_code == 200:
            data['nhlSchedules'] = response.json()
            with open("ESPNData/nhl_week_team_schedules.json", "w", encoding='utf-8') as f:
                json.dump(data, f, indent=4)

    def master_schedule_formatter(self):
        """
        This should return only the games that are in season and at home for the team.
        """
        with open("ESPNData/nhl_full_team_schedules.json", "r", encoding='utf-8') as f:
            data = json.load(f)
        f.close()
        for index, _ in enumerate(data['nhlSchedules']):
            name = list(self.constant_obj.pro_team_abbrev.keys())[index]
            abbrev = self.constant_obj.pro_team_abbrev[name]
            data['nhlSchedules'][index][name]['games'] = [
                game for game in data['nhlSchedules'][index][name]['games']
                if game['gameType'] != 1 and game['awayTeam']['abbrev'] != abbrev
            ]

        with open("ESPNData/master_schedule_25_26_season.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def games_by_matchup(self, matchup_file: str,
            start_date: date=None, matchup_days: timedelta=None):
        """
        This should be the first week of reg season games
        """
        if start_date is None:
            start_date = self.constant_obj.curr_date
        if matchup_days is None:
            matchup_days = timedelta(7)

        with open("ESPNData/master_schedule_25_26_season.json", "r", encoding='utf-8') as f:
            data = json.load(f)

        date_list = []
        for i in range(matchup_days.days):
            date_list.append((start_date + timedelta(i)).isoformat())

        for index, _ in enumerate(data['nhlSchedules']):
            name = list(self.constant_obj.pro_team_abbrev.keys())[index]
            data['nhlSchedules'][index][name]['games'] = [
                game for game in data['nhlSchedules'][index][name]['games']
                if game['gameDate'] in date_list
            ]

        with open(matchup_file, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def matchup_analysis(self, matchup_file: str):
        team_names = []
        for i in range(32):
            team_names.append(list(self.constant_obj.pro_team_abbrev.keys())[i])
        matchup_num = int(matchup_file[-7:-5])
        if matchup_num - 1 > 0:
            matchup_num = matchup_num - 1
            if matchup_num > 10:
                prev_matchup_file = matchup_file.split('_')[0] + '_' + str(matchup_num) + '_ranked.json'
            else:
                prev_matchup_file = matchup_file.split('_')[0] + '_0' + str(matchup_num) + '_ranked.json'
            with open(prev_matchup_file, 'r', encoding='utf-8') as f:
                prev_data = json.load(f)
            prev_sunday_dict = {}
            for team_name in team_names:
                prev_sunday_dict[team_name] = prev_data[team_name]['Games']['Weekdays']['Sun']
        analysis_dict = {
            team_names[i]: {
                "Games": {
                    "Home": 0,
                    "Away": 0,
                    "Total": 0,
                    "Weekdays": {
                        "Mon": 0,
                        "Tue": 0,
                        "Wed": 0,
                        "Thu": 0,
                        "Fri": 0,
                        "Sat": 0,
                        "Sun": 0
                    },
                    'PrevSun': prev_sunday_dict[team_names[i]],
                    'BB': 0,
                    'Rest': 0
                }
            }
            for i in range(32)
        }
        with open(matchup_file, "r", encoding='utf-8') as f:
            data = json.load(f)
        data_list = data['nhlSchedules']
        for index, _ in enumerate(data_list):
            name = list(self.constant_obj.pro_team_abbrev.keys())[index]
            for game in data_list[index][name]['games']:
                away_name = self.constant_obj.pro_team_abbrev[game["awayTeam"]["abbrev"]]
                game_date = date.fromisoformat(game["gameDate"]).weekday()
                weekday_str = list(analysis_dict[name]["Games"]["Weekdays"].keys())[game_date]
                analysis_dict[name]["Games"]["Total"] += 1
                analysis_dict[name]["Games"]["Home"] += 1
                analysis_dict[name]["Games"]["Weekdays"][weekday_str] += 1

                analysis_dict[away_name]["Games"]["Total"] += 1
                analysis_dict[away_name]["Games"]["Away"] += 1
                analysis_dict[away_name]["Games"]["Weekdays"][weekday_str] += 1

        analysis_dict = self.rest_days_analysis(analysis_dict)
        analysis_sorted_dict = dict(sorted(analysis_dict.items(),
            key=lambda item: item[1]['Games']['BB']))
        analysis_sorted_dict = dict(sorted(analysis_sorted_dict.items(),
            key=lambda item: item[1]["Games"]["Total"], reverse=True))

        return analysis_sorted_dict

    def season_weekday_analysis(self):
        analysis_sorted_dict = self.matchup_analysis("ESPNData/master_schedule_25_26_season.json")

        for val in analysis_sorted_dict.values():
            val["Games"]["ODG"] = 82
        for val in analysis_sorted_dict.values():
            val["Games"]["ODG"] -= val["Games"]["Weekdays"]["Tue"]
            val["Games"]["ODG"] -= val["Games"]["Weekdays"]["Thu"]
            val["Games"]["ODG"] -= val["Games"]["Weekdays"]["Sat"]
        season_off_day_dict = dict(sorted(analysis_sorted_dict.items(),
            key=lambda item: (item[1]["Games"]["ODG"]), reverse=True))
        print(season_off_day_dict.keys())
        with open("ESPNData/master_odg_teams_ranked.json", "w", encoding='utf-8') as f:
            json.dump(season_off_day_dict, f, indent=4)

    def matchup_team_ranks(self, matchup_file):
        analysis_sorted_dict = self.matchup_analysis(matchup_file)
        with open(f"{matchup_file[:-5]}_ranked.json", "w", encoding='utf-8') as f:
            json.dump(analysis_sorted_dict, f, indent=4)

    def rest_days_analysis(self, games_dict: dict):
        for i in range(32):
            name = list(self.constant_obj.pro_team_abbrev.keys())[i]
            team_dict = games_dict[name]['Games']
            prev_val = team_dict['PrevSun']
            for val in team_dict['Weekdays'].values():      
                if val == 0:
                    team_dict['Rest'] += 1
                    prev_val = val
                    continue
                if prev_val == 1:
                    team_dict['BB'] += 1
                prev_val = val
        return games_dict
            

ESPN_data = ESPN()
