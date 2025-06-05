import random
import numpy as np

def choose_action(down, y_to_fd, y_to_td):
    if down == 4:
        if y_to_td > 55:
            return 'punt'
        elif 5 < y_to_td < 45:
            return 'field_goal' if random.random() < 0.75 else random.choice(['run', 'pass'])
        elif 45 <= y_to_td <= 55:
            rnd = random.random()
            if rnd < 0.35:
                return random.choice(['run', 'pass'])
            elif rnd < 0.85:
                return 'field_goal'
            else:
                return 'punt'
    return random.choice(['run', 'pass'])

def choose_outcome(action, qb_skill_level=0.03):
    if action == 'pass':
        outcomes = ['complete', 'incomplete', 'sack', 'interception']
        probabilities = [0.6, 0.3, 0.07, qb_skill_level]
        probabilities[0] += (0.03 - qb_skill_level)
        return random.choices(outcomes, probabilities)[0]
    elif action == 'run':
        return 'run'
    elif action == 'punt':
        return 'punt_attempt'
    elif action == 'field_goal':
        return 'field_goal_attempt'

def simulate_play(action, qb_skill_level=0.03):
    if action == 'run':
        y_gained = int(np.random.normal(4, 2))
        return y_gained, 'run'
    elif action == 'pass':
        outcome = choose_outcome(action, qb_skill_level)
        if outcome == 'complete':
            y_gained = int(np.random.normal(10, 5))
            return y_gained, 'complete'
        elif outcome == 'incomplete':
            return 0, 'incomplete'
        elif outcome == 'sack':
            y_lost = int(np.random.normal(5, 2))
            return -y_lost, 'sack'
        elif outcome == 'interception':
            return 0, 'interception'
    elif action == 'punt':
        return 0, 'punt_attempt'
    elif action == 'field_goal':
        return 0, 'field_goal_attempt'

def update_game_clock(clock, seconds, quarter):
    total_seconds = clock - seconds
    if total_seconds < 0:
        quarter += 1
        total_seconds += 15 * 60
    return max(0, total_seconds), quarter

def attempt_field_goal(y_to_td):
    distance = 100 - y_to_td
    success_chance = max(0.3, 1 - (distance / 100))
    return random.random() < success_chance

def initialize_stats():
    return {
        'pass_attempts': 0,
        'y_passing': 0,
        'passes_complete': 0,
        'passing_tds': 0,
        'interceptions': 0,
        'sacks_taken': 0,
        'run_attempts': 0,
        'y_running': 0,
        'running_tds': 0,
        'sacks_given': 0,
        'field_goals_attempted': 0,
        'field_goals_made': 0,
        'punts': 0,
        'punt_yards': 0
    }

def simulate_possession(possession, score_A, score_B, clock, quarter, stats_A, stats_B, y_to_td):
    down = 1
    y_to_fd = 10

    while down <= 4 and y_to_td > 0 and clock > 0 and quarter <= 4:
        action = choose_action(down, y_to_fd, y_to_td)
        y_gained, outcome = simulate_play(action)

        print(f"Quarter: {quarter} - Time: {clock // 60}:{clock % 60:02d} - Down: {down}, "
              f"Yards to First Down: {y_to_fd}, Yards to Touchdown: {y_to_td}")
        print(f"Action chosen: {action}, Outcome: {outcome}, Yards gained: {y_gained}")

        if possession == 1:
            stats = stats_A
            stats_inv = stats_B
        else:
            stats = stats_B
            stats_inv = stats_A

        # Update stats based on action
        if action == 'run':
            stats['run_attempts'] += 1
            stats['y_running'] += y_gained
        elif action == 'pass':
            stats['pass_attempts'] += 1
            if outcome == 'complete':
                stats['passes_complete'] += 1
                stats['y_passing'] += y_gained
            elif outcome == 'sack':
                stats['sacks_taken'] += 1
                stats_inv['sacks_given'] += 1
            elif outcome == 'interception':
                stats['interceptions'] += 1
                print("Interception! Changing possession.")
                possession *= -1
                clock, quarter = update_game_clock(clock, random.randint(5, 15), quarter)
                return score_A, score_B, possession, clock, quarter, stats_A, stats_B, 100 - y_to_td
        elif action == 'field_goal':
            stats['field_goals_attempted'] += 1
            if attempt_field_goal(y_to_td):
                print("Field goal successful!")
                if possession == 1:
                    score_A += 3
                else:
                    score_B += 3
                stats['field_goals_made'] += 1
            else:
                print("Field goal missed!")
            possession *= -1
            clock, quarter = update_game_clock(clock, random.randint(5, 15), quarter)
            return score_A, score_B, possession, clock, quarter, stats_A, stats_B, 80

        elif action == 'punt':
            punt_distance = random.randint(30, 65)
            print(f"Punt! Ball moved {punt_distance} yards.")
            stats['punts'] += 1
            stats['punt_yards'] += punt_distance
            possession *= -1
            new_y_to_td = max(100 - punt_distance, 20)
            clock, quarter = update_game_clock(clock, random.randint(5, 15), quarter)
            return score_A, score_B, possession, clock, quarter, stats_A, stats_B, new_y_to_td

        # Adjust yards
        y_to_fd -= y_gained
        y_to_td -= y_gained

        # Determine time taken by the play
        if action == 'pass' and outcome == 'incomplete':
            # Incomplete pass, stops clock quickly
            t_play = random.randint(3, 12)
        else:
            # Determine if play ends out of bounds or in bounds
            if quarter == 4:
                # 4th quarter logic: if winning team has ball, try to stay in bounds with low out_of_bounds chance
                # If not winning (i.e., losing team), more likely to go out_of_bounds (0.7) to stop clock (hurry-up)
                if (possession == 1 and score_A > score_B) or (possession == -1 and score_B > score_A):
                    out_of_bounds = (random.random() < 0.1)
                else:
                    out_of_bounds = (random.random() < 0.7)
            else:
                out_of_bounds = (random.random() < 0.5)

            if out_of_bounds or action in ['field_goal', 'punt'] or outcome == 'interception':
                # Clock stops
                t_play = random.randint(3, 7)
            else:
                # Inbounds play
                if quarter == 4:
                    # In the 4th quarter, if the team with the ball is losing, hurry-up (20-30 seconds)
                    if (possession == 1 and score_A < score_B) or (possession == -1 and score_B < score_A):
                        t_play = random.randint(20, 30)
                    else:
                        # Normal 4th quarter inbounds play: 20-40 seconds
                        t_play = random.randint(20, 40)
                else:
                    # Non-4th quarter inbounds: 35-50 seconds
                    t_play = random.randint(35, 50)

        # Update clock
        clock, quarter = update_game_clock(clock, t_play, quarter)
        if clock == 0 and quarter <= 4:
            quarter += 1
            clock = 15 * 60

        # Check for touchdown
        if y_to_td <= 0:
            print("Touchdown!")
            if possession == 1:
                score_A += 6
                stats['passing_tds' if action == 'pass' else 'running_tds'] += 1
                if random.random() < 0.95:
                    score_A += 1
            else:
                score_B += 6
                stats['passing_tds' if action == 'pass' else 'running_tds'] += 1
                if random.random() < 0.95:
                    score_B += 1
            possession *= -1
            clock, quarter = update_game_clock(clock, random.randint(5, 15), quarter)
            return score_A, score_B, possession, clock, quarter, stats_A, stats_B, 100

        # Check downs
        if y_to_fd <= 0:
            down = 1
            y_to_fd = min(10, y_to_td)
        else:
            down += 1

    print("Failed to advance. Changing possession.")
    possession *= -1
    new_y_to_td = 100 - y_to_td
    clock, quarter = update_game_clock(clock, random.randint(5, 15), quarter)
    return score_A, score_B, possession, clock, quarter, stats_A, stats_B, new_y_to_td

def simulate_game():
    possession = 1
    score_A = 0
    score_B = 0
    clock = 15 * 60
    quarter = 1

    stats_A = initialize_stats()
    stats_B = initialize_stats()

    y_to_td = 100

    while clock > 0 and quarter <= 4:
        print(f"\nQuarter: {quarter} - Time remaining: {clock // 60}:{clock % 60:02d}")
        print(f"Team {'A' if possession == 1 else 'B'}'s possession")
        score_A, score_B, possession, clock, quarter, stats_A, stats_B, y_to_td = simulate_possession(possession, score_A, score_B, clock, quarter, stats_A, stats_B, y_to_td)
        if clock == 0 and quarter <= 4:
            quarter += 1
            clock = 15 * 60

    print(f"\nFinal Score - Team A: {score_A}, Team B: {score_B}")
    print("\nTeam A Stats:")
    for stat, value in stats_A.items():
        print(f"{stat}: {value}")

    print("\nTeam B Stats:")
    for stat, value in stats_B.items():
        print(f"{stat}: {value}")

simulate_game()
