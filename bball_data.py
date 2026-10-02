import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

def cell_text(table_row, *stat_names):
    for stat_name in stat_names:
        cell = table_row.find(["td", "th"], {"data-stat": stat_name})
        if cell is not None:
            return cell.get_text(strip=True)
    return None


def parse_season(html, season):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"id": "per_game_stats"})
    if table is None:
        raise ValueError(f"Player stats table not found for {season}")

    rows = []
    for table_row in table.select("tbody tr"):
        player_cell = table_row.find(["td", "th"], attrs={"data-append-csv": True})
        if player_cell is None:
            continue

        row = {
            "season": season,
            "player": player_cell.get_text(strip=True),
            "team": cell_text(table_row, "team_id", "team_name_abbr"),
            "games_played": cell_text(table_row, "g", "games"),
            "points_per_game": cell_text(table_row, "pts_per_g"),
            "assists_per_game": cell_text(table_row, "ast_per_g"),
            "rebounds_per_game": cell_text(table_row, "trb_per_g"),
        }
        missing = [name for name, value in row.items() if value is None]
        if missing:
            raise ValueError(
                f"Missing columns for {row['player']} in {season}: {', '.join(missing)}"
            )
        rows.append(row)

    if not rows:
        raise ValueError(f"No player rows found for {season}")
    return rows


def main():
    rows = []
    seasons = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
    for index, season in enumerate(seasons):
        if index:
            time.sleep(5)
        url = f"https://www.basketball-reference.com/leagues/NBA_{season}_per_game.html"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        rows.extend(parse_season(response.content, season))

    data = pd.DataFrame(rows)
    data.to_csv("nba_player_stats.csv", index=False)
    print(len(data), "rows of data saved to nba_player_stats.csv")
    print(data.head())

if __name__ == "__main__":
    main()
