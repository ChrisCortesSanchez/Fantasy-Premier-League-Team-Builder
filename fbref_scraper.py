import requests
from bs4 import BeautifulSoup


def get_fantasy_data():
    url = "https://fantasy.premierleague.com/player-list/"

    # Create a session to handle authentication
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

    # Send a request to get necessary cookies
    response = session.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code != 200:
        raise requests.exceptions.RequestException(f"Failed to fetch data. Status code: {response.status_code}")

    soup = BeautifulSoup(response.content, 'html.parser')

    player_data = []

    player_rows = soup.select('table.ism-table tbody tr')

    for row in player_rows:
        columns = row.select('td')

        # Extract player name, team, position, total points, and other statistics
        player_name = columns[2].text.strip()
        team = columns[0].text.strip()
        position = columns[1].text.strip()
        total_points = columns[3].text.strip()
        goals_scored = columns[4].text.strip()
        assists = columns[5].text.strip()
        clean_sheets = columns[6].text.strip()
        minutes_played = columns[7].text.strip()

        player_info = {
            'name': player_name,
            'team': team,
            'position': position,
            'total_points': total_points,
            'goals_scored': goals_scored,
            'assists': assists,
            'clean_sheets': clean_sheets,
            'minutes_played': minutes_played
        }

        player_data.append(player_info)

    return player_data


def create_ideal_team(player_data, budget):
    # Sort the player data by position and points
    sorted_data = sorted(player_data, key=lambda x: (x['position'], -int(x['total_points'])))

    goalkeepers = [p for p in sorted_data if p['position'] == 'GKP']
    defenders = [p for p in sorted_data if p['position'] == 'DEF']
    midfielders = [p for p in sorted_data if p['position'] == 'MID']
    forwards = [p for p in sorted_data if p['position'] == 'FWD']

    # Select the top 2 goalkeepers with the highest clean sheet count
    ideal_goalkeepers = sorted(goalkeepers, key=lambda x: -int(x['clean_sheets']))[:2]

    # Select the top 5 defenders with the highest clean sheet count and points
    ideal_defenders = sorted(defenders, key=lambda x: (-int(x['clean_sheets']), -int(x['total_points'])))[:5]

    # Select the top 5 midfielders with the highest points
    ideal_midfielders = sorted(midfielders, key=lambda x: -int(x['total_points']))[:5]

    # Select the top 3 forwards with the highest points
    ideal_forwards = sorted(forwards, key=lambda x: -int(x['total_points']))[:3]

    # Calculate the total cost of the selected players
    total_cost = sum(
        int(player['cost']) for player in ideal_goalkeepers + ideal_defenders + ideal_midfielders + ideal_forwards)

    # Check if the total cost is within the budget
    if total_cost <= budget:
        return ideal_goalkeepers + ideal_defenders + ideal_midfielders + ideal_forwards
    else:
        return None


def main():
    fantasy_data = get_fantasy_data()

    # Assuming a budget of 100 million
    budget = 100

    ideal_team = create_ideal_team(fantasy_data, budget)

    if ideal_team:
        print("Ideal Fantasy Team:")
        for player_info in ideal_team:
            print("Name:", player_info['name'])
            print("Position:", player_info['position'])
            print("Total Points:", player_info['total_points'])
            print("Clean Sheets:", player_info['clean_sheets'])
            print("Cost:", player_info['cost'])
            print("=" * 50)
    else:
        print("Unable to create an ideal team within the given budget.")


main()