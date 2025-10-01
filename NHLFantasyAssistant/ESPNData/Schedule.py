"""
This is for creating a master 2025-2026 season JSON schedule file
"""
import json

with open("ESPNData/nhl_teams.json", "r", encoding='utf-8') as f:
    saved_data = json.load(f)

teams = saved_data["sports"][0]["leagues"][0]["teams"]



