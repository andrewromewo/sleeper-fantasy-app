import os
import random
from dotenv import load_dotenv
from sleeper_wrapper import League, Players, User

load_dotenv()

def get_player_name(player_id, players_data):
    """Get player name from player ID"""
    if player_id in players_data:
        player = players_data[player_id]
        return f"{player.get('first_name', '')} {player.get('last_name', '')}".strip()
    return "Unknown Player"

def generate_trash_talk(winner_name, loser_name, winner_score, loser_score, context):
    """Generate trash talk based on the matchup context"""
    margin = winner_score - loser_score
    
    # Close game (within 5 points)
    if margin < 5:
        return random.choice([
            f"{loser_name}, you were THIS close 🤏 Maybe next week you'll actually win one.",
            f"{winner_name} squeaked by with a {margin:.2f} point win. {loser_name} basically gave them the W.",
            f"That was close, but close only counts in horseshoes. {loser_name} takes the L!",
            f"{loser_name} lost by {margin:.2f} points. That's gotta sting.",
        ])
    
    # Blowout (30+ points)
    elif margin >= 30:
        return random.choice([
            f"{loser_name} got absolutely DEMOLISHED by {winner_name}. Final score: {winner_score:.2f} - {loser_score:.2f}. Yikes. 💀",
            f"Did {loser_name} even show up this week? Lost by {margin:.2f} points. Embarrassing.",
            f"{winner_name} put up {winner_score:.2f} points. {loser_name}? A measly {loser_score:.2f}. Not even close.",
            f"Breaking news: {loser_name} found missing after {margin:.2f} point beatdown.",
            f"{loser_name}, you might want to check if your players are still in the NFL after that performance.",
        ])
    
    # Bench points scenario
    elif context.get("bench_would_have_won"):
        best_bench = context["best_bench_player"]
        worst_starter = context["worst_starter"]
        return f"{loser_name} left {best_bench} on the bench while starting {worst_starter}. You played yourself. 🤡"
    
    # Lowest score of the week
    elif context.get("lowest_score"):
        return random.choice([
            f"{loser_name} had the LOWEST score in the entire league this week. Congrats on the achievement! 🏆",
            f"Everyone scored more than {loser_name} this week. Everyone.",
            f"{loser_name} putting up {loser_score:.2f} points like it's a bye week. It's not.",
        ])
    
    # Default trash talk
    else:
        return random.choice([
            f"{winner_name} takes down {loser_name}, {winner_score:.2f} to {loser_score:.2f}. Better luck next week!",
            f"{loser_name} thought they had a chance. They didn't. {winner_name} wins by {margin:.2f}.",
            f"Another week, another L for {loser_name}. Tale as old as time.",
            f"{winner_name} cooking 👨‍🍳 {loser_name} getting cooked 🔥",
        ])

def analyze_matchup(matchup_data, roster_data, players_data):
    """Analyze a matchup for trash talk context"""
    context = {}
    
    starters = matchup_data.get("starters", [])
    starters_points = matchup_data.get("starters_points", [])
    
    # Find worst starter
    if starters_points:
        worst_idx = starters_points.index(min(starters_points))
        context["worst_starter"] = get_player_name(starters[worst_idx], players_data)
        context["worst_starter_points"] = starters_points[worst_idx]
    
    # Check bench (players not in starters)
    roster_players = roster_data.get("players", [])
    bench_players = [p for p in roster_players if p not in starters]
    
    # Get bench points from players_points
    players_points = matchup_data.get("players_points", {})
    bench_points = [(p, players_points.get(p, 0)) for p in bench_players]
    
    if bench_points:
        best_bench = max(bench_points, key=lambda x: x[1])
        context["best_bench_player"] = get_player_name(best_bench[0], players_data)
        context["best_bench_points"] = best_bench[1]
        
        # Check if best bench player would have helped them win
        if starters_points:
            context["bench_would_have_won"] = best_bench[1] > min(starters_points)
    
    return context

def main():
    username = os.getenv("SLEEPER_USER")
    print("🗑️  WELCOME TO TRASH TALK TIME! 🗑️")
    print("Username from env:", username)
    if not username:
        print("Error: SLEEPER_USER not found in .env file")
        return
    
    # Get user and leagues
    user = User(username)
    user_id = user.get_user_id()
    leagues = user.get_all_leagues("nfl", "2025")
    
    if not leagues:
        print("No leagues found")
        return
    
    # Load player data
    print("Loading player data...\n")
    players = Players()
    players_data = players.get_all_players()
    
    # Pick the first league (or let user choose)
    league_data = leagues[0]
    league_id = league_data["league_id"]
    league_name = league_data["name"]
    
    print(f"{'='*60}")
    print(f"🗑️  TRASH TALK TIME - {league_name}  🗑️")
    print(f"{'='*60}\n")
    
    # Get league details
    league = League(league_id)
    rosters = league.get_rosters()
    league_users = league.get_users()
    
    # Create mappings
    user_map = {u["user_id"]: u.get("display_name", u.get("username", "Unknown")) 
                for u in league_users}
    roster_owner_map = {r["roster_id"]: user_map.get(r.get("owner_id"), "Unknown") 
                       for r in rosters}
    roster_data_map = {r["roster_id"]: r for r in rosters}
    
    # Get latest week's matchups (try week 7, adjust as needed)
    week = 6
    try:
        matchups = league.get_matchups(week)
    except:
        print("Could not fetch matchups")
        return
    
    if not matchups:
        print("No matchups found")
        return
    
    # Group matchups by matchup_id
    matchup_groups = {}
    for m in matchups:
        mid = m.get("matchup_id")
        if mid not in matchup_groups:
            matchup_groups[mid] = []
        matchup_groups[mid].append(m)
    
    # Find all scores for context
    all_scores = [m.get("points", 0) for m in matchups]
    lowest_score = min(all_scores) if all_scores else 0
    
    # Generate trash talk for each matchup
    for matchup_id, teams in matchup_groups.items():
        if len(teams) != 2:
            continue
        
        team1, team2 = teams
        score1 = team1.get("points", 0)
        score2 = team2.get("points", 0)
        
        # Determine winner/loser
        if score1 > score2:
            winner, loser = team1, team2
            winner_score, loser_score = score1, score2
        else:
            winner, loser = team2, team1
            winner_score, loser_score = score2, score1
        
        winner_name = roster_owner_map.get(winner["roster_id"], "Unknown")
        loser_name = roster_owner_map.get(loser["roster_id"], "Unknown")
        
        # Analyze loser's team for extra context
        roster_data = roster_data_map.get(loser["roster_id"], {})
        context = analyze_matchup(loser, roster_data, players_data)
        context["lowest_score"] = (loser_score == lowest_score)
        
        # Generate and print trash talk
        trash_talk = generate_trash_talk(winner_name, loser_name, 
                                         winner_score, loser_score, context)
        print(f"📢 {trash_talk}\n")
    
    print(f"{'='*60}")
    print("Week over. See you next Sunday! 🏈")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()