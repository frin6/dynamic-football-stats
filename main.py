import json
import pandas as pd
import plotly.express as px
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import random  # Add this at the top with other imports
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load and prepare data
with open("src/data/it.1.json") as f:
    data = json.load(f)

def prepare_milan_data():
    matches = []
    points = 0
    
    for match in data['matches']:
        if "AC Milan" in [match['team1'], match['team2']]:
            is_home = match['team1'] == "AC Milan"
            milan_goals = match['score']['ft'][0] if is_home else match['score']['ft'][1]
            opponent_goals = match['score']['ft'][1] if is_home else match['score']['ft'][0]
            
            # Calculate result and points
            if milan_goals > opponent_goals:
                result = 'W'
                match_points = 3
            elif milan_goals < opponent_goals:
                result = 'L'
                match_points = 0
            else:
                result = 'D'
                match_points = 1
                
            points += match_points
            
            matches.append({
                'date': match['date'],
                'matchday': match['round'],
                'opponent': match['team2'] if is_home else match['team1'],
                'home_away': 'Home' if is_home else 'Away',
                'goals_scored': milan_goals,
                'goals_conceded': opponent_goals,
                'result': result,
                'points': match_points,
                'cumulative_points': points
            })
    
    return pd.DataFrame(matches)

df_milan = prepare_milan_data()

def prepare_quiz_question(df):
    # Choose a random question type (now with more options)
    question_type = random.randint(1, 7)  # Increased to 7 types
    
    if question_type == 1:
        # Random matchday opponent
        random_matchday = random.randint(1, len(df))
        matchday_str = f'Matchday {random_matchday}'
        correct_opponent = df[df['matchday'] == matchday_str]['opponent'].iloc[0]
        all_opponents = df['opponent'].unique()
        wrong_opponents = [opp for opp in all_opponents if opp != correct_opponent]
        wrong_answers = random.sample(list(wrong_opponents), 3)
        
        return {
            'question': f'Who did Milan face on {matchday_str}?',
            'correct_answer': correct_opponent,
            'wrong_answers': wrong_answers
        }
        
    elif question_type == 2:
        # Points after random matchday
        random_matchday = random.randint(5, len(df))  # Start from 5 to make it interesting
        points = df.iloc[random_matchday-1]['cumulative_points']
        wrong_points = []
        while len(wrong_points) < 3:
            wrong = points + random.randint(-6, 6)  # Smaller range for more realistic options
            if wrong > 0 and wrong != points and wrong not in wrong_points:
                wrong_points.append(wrong)
                
        return {
            'question': f'How many points did Milan have after {random_matchday} matches?',
            'correct_answer': str(points),
            'wrong_answers': [str(p) for p in wrong_points]
        }
        
    elif question_type == 3:
        # Largest victory
        df['goal_difference'] = df['goals_scored'] - df['goals_conceded']
        max_diff_idx = df['goal_difference'].idxmax()
        correct_score = f"{df.iloc[max_diff_idx]['goals_scored']}-{df.iloc[max_diff_idx]['goals_conceded']}"
        
        wrong_scores = []
        while len(wrong_scores) < 3:
            goals_scored = random.randint(1, 5)
            goals_conceded = random.randint(0, goals_scored-1)
            score = f"{goals_scored}-{goals_conceded}"
            if score != correct_score and score not in wrong_scores:
                wrong_scores.append(score)
                
        return {
            'question': 'What was the score in Milan\'s largest victory this season?',
            'correct_answer': correct_score,
            'wrong_answers': wrong_scores
        }
        
    elif question_type == 4:
        # Consecutive wins
        max_consecutive_wins = 0
        current_streak = 0
        for _, row in df.iterrows():
            if row['result'] == 'W':
                current_streak += 1
                max_consecutive_wins = max(max_consecutive_wins, current_streak)
            else:
                current_streak = 0
                
        wrong_answers = []
        while len(wrong_answers) < 3:
            wrong = random.randint(1, max_consecutive_wins + 2)
            if wrong != max_consecutive_wins and wrong not in wrong_answers:
                wrong_answers.append(str(wrong))
                
        return {
            'question': 'What was Milan\'s longest winning streak this season?',
            'correct_answer': str(max_consecutive_wins),
            'wrong_answers': wrong_answers
        }
        
    elif question_type == 5:
        # Clean sheets
        clean_sheets = len(df[df['goals_conceded'] == 0])
        wrong_answers = []
        while len(wrong_answers) < 3:
            wrong = random.randint(max(0, clean_sheets-3), clean_sheets+3)
            if wrong != clean_sheets and wrong not in wrong_answers:
                wrong_answers.append(str(wrong))
                
        return {
            'question': 'How many clean sheets did Milan keep this season?',
            'correct_answer': str(clean_sheets),
            'wrong_answers': wrong_answers
        }
        
    elif question_type == 6:
        # Goals in a specific match
        random_match = df.iloc[random.randint(0, len(df)-1)]
        total_goals = random_match['goals_scored'] + random_match['goals_conceded']
        wrong_answers = []
        while len(wrong_answers) < 3:
            wrong = random.randint(1, 6)
            if wrong != total_goals and wrong not in wrong_answers:
                wrong_answers.append(str(wrong))
                
        return {
            'question': f'How many total goals were scored in the match against {random_match["opponent"]}?',
            'correct_answer': str(total_goals),
            'wrong_answers': wrong_answers
        }
        
    else:
        # Average points per match up to a random matchday
        random_matchday = random.randint(10, len(df))
        points = df.iloc[random_matchday-1]['cumulative_points']
        avg_points = round(points / random_matchday, 2)
        wrong_answers = []
        while len(wrong_answers) < 3:
            wrong = round(random.uniform(max(0.5, avg_points-1), avg_points+1), 2)
            if abs(wrong - avg_points) > 0.2 and str(wrong) not in wrong_answers:
                wrong_answers.append(str(wrong))
                
        return {
            'question': f'What was Milan\'s average points per match after {random_matchday} games?',
            'correct_answer': str(avg_points),
            'wrong_answers': wrong_answers
        }

@app.get("/")
async def home(request: Request):
    # Debug prints
    print("\n=== Debug Information ===")
    print("1. Raw Data Check:")
    print(df_milan[['date', 'opponent', 'points', 'cumulative_points']].head())
    
    # Create points progression chart
    plot_df = df_milan.copy()
    plot_df = plot_df.sort_values('date')  # Sort by date
    print("\n2. After Sorting:")
    print(plot_df[['date', 'opponent', 'points', 'cumulative_points']].head())
    
    plot_df = plot_df.reset_index(drop=True)
    plot_df['game_number'] = plot_df.index + 1
    
    print("\n3. Final Plot Data:")
    print(plot_df[['game_number', 'date', 'opponent', 'points', 'cumulative_points']].head())
    print("\nTotal Points:", plot_df['cumulative_points'].max())
    print("Number of matches:", len(plot_df))
    
    # General statistics
    total_matches = len(df_milan)
    wins = len(df_milan[df_milan['result'] == 'W'])
    draws = len(df_milan[df_milan['result'] == 'D'])
    losses = len(df_milan[df_milan['result'] == 'L'])
    total_points = df_milan['points'].sum()
    goals_scored = df_milan['goals_scored'].sum()
    goals_conceded = df_milan['goals_conceded'].sum()
    
    # Create figure using go instead of px
    from plotly import graph_objects as go
    
    fig = go.Figure()
    
    # Print debug info about the data being plotted
    print("\n4. Plotting Data:")
    print("X values:", list(plot_df['game_number']))
    print("Y values:", list(plot_df['cumulative_points']))
    
    fig.add_trace(
        go.Scatter(
            x=list(plot_df['game_number']),  # Convert to list explicitly
            y=list(plot_df['cumulative_points']),  # Convert to list explicitly
            mode='lines+markers',
            name='Points',
            line=dict(color='#AC1620', width=2),
            marker=dict(size=8, color='#AC1620'),
            customdata=plot_df[['opponent', 'result', 'date']].values,  # Convert to values
            hovertemplate="<br>".join([
                "Match %{x}",
                "Total Points: %{y}",
                "Date: %{customdata[2]}",
                "Opponent: %{customdata[0]}",
                "Result: %{customdata[1]}",
                "<extra></extra>"
            ])
        )
    )
    
    fig.update_layout(
        title='AC Milan Points Progression 2023/24',
        xaxis_title='Match Number',
        yaxis_title='Total Points',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=14),
        showlegend=False,
        yaxis=dict(
            range=[0, max(plot_df['cumulative_points']) + 5],
            dtick=5,
            gridcolor='lightgrey'
        ),
        xaxis=dict(
            dtick=5,
            gridcolor='lightgrey',
            range=[0, len(plot_df) + 1]
        ),
        margin=dict(t=50, l=50, r=50, b=50)
    )
    
    plot_json = fig.to_json()
    
    # Last 5 matches
    recent_matches = df_milan.tail(5).to_dict('records')
    
    # Add quiz question
    quiz = prepare_quiz_question(plot_df)
    
    # Shuffle answers
    all_answers = [quiz['correct_answer']] + quiz['wrong_answers']
    random.shuffle(all_answers)
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "stats": {
                "matches": total_matches,
                "wins": wins,
                "draws": draws,
                "losses": losses,
                "points": total_points,
                "goals_scored": goals_scored,
                "goals_conceded": goals_conceded,
                "goal_difference": goals_scored - goals_conceded
            },
            "plot_json": plot_json,
            "recent_matches": recent_matches,
            "quiz": {
                "question": quiz['question'],
                "answers": all_answers,
                "correct_answer": quiz['correct_answer']
            }
        }
    )

# Dopo app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)