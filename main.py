import os
from dotenv import load_dotenv
from sleeper_wrapper import League, Players, User

# Load environment variables
load_dotenv()

def get_player_name(player_id, players_data):
    """Get player name from player ID"""
    if player_id in players_data:
        player = players_data[player_id]
        return f"{player.get('first_name', '')} {player.get('last_name', '')}".strip()
    return player_id

def main():
    # Get username from environment
    username = os.getenv("SLEEPER_USER")
    if not username:
        print("Error: SLEEPER_USER not found in .env file")
        print("run: echo 'SLEEPER_USER=your_sleeper_username' > .env")
        return
    
    print(f"Fetching leagues for user: {username}\n")
    
    # Get user
    user = User(username)
    user_id = user.get_user_id()
    
    if not user_id:
        print(f"Error: Could not find user '{username}'")
        return
    
    # Get all NFL leagues for 2025 season
    leagues = user.get_all_leagues("nfl", "2025")
    
    if not leagues:
        print("No leagues found for 2025 season")
        return
    
    # Load all players data once
    print("Loading player data...\n")
    players = Players()
    players_data = players.get_all_players()
    
    # Process each league
    for league_data in leagues:
        league_name = league_data["name"]
        if league_name == "Jerry Jones' Holdout Club":
            league_id = league_data["league_id"]
            
            
            print(f"{'='*60}")
            print(f"League: {league_name}")
            print(f"{'='*60}\n")
            
            # Get league object
            league = League(league_id)
            
            # Get rosters and users
            rosters = league.get_rosters()
            league_users = league.get_users()
            
            # Create a mapping of user_id to display name
            user_map = {u["user_id"]: u.get("display_name", u.get("username", "Unknown")) 
                        for u in league_users}
            
            # Create a mapping of roster_id to owner
            roster_owner_map = {r["roster_id"]: user_map.get(r.get("owner_id"), "Unknown") 
                            for r in rosters}
            
            # Get week 7 matchups
            try:
                matchups = league.get_matchups(7)
            except Exception as e:
                print(f"Could not fetch week 7 matchups: {e}\n")
                continue
            
            if not matchups:
                print("No matchups found for week 7\n")
                continue
            
            # Process each matchup/lineup
            for matchup in matchups:
                roster_id = matchup["roster_id"]
                owner = roster_owner_map.get(roster_id, "Unknown")
                starters = matchup.get("starters", [])
                
                print(f"\n{owner}'s Week 7 Lineup:")
                print(f"{'-'*40}")
                
                if not starters:
                    print("  No starters set")
                else:
                    for i, player_id in enumerate(starters, 1):
                        player_name = get_player_name(player_id, players_data)
                        print(f"  {i}. {player_name}")
                
                print()
        
        print()

if __name__ == "__main__":
    main()