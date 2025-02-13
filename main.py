import json
import pandas as pd
import plotly.express as px
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Carica e prepara i dati
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
            
            # Calcola il risultato e i punti
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

@app.get("/")
async def home(request: Request):
    # Statistiche generali
    total_matches = len(df_milan)
    wins = len(df_milan[df_milan['result'] == 'W'])
    draws = len(df_milan[df_milan['result'] == 'D'])
    losses = len(df_milan[df_milan['result'] == 'L'])
    total_points = df_milan['points'].sum()
    goals_scored = df_milan['goals_scored'].sum()
    goals_conceded = df_milan['goals_conceded'].sum()
    
    # Crea il grafico dell'andamento punti
    fig = px.line(df_milan, 
                  x='matchday', 
                  y='cumulative_points',
                  title='Andamento Punti AC Milan 2023/24',
                  labels={'matchday': 'Giornata', 
                         'cumulative_points': 'Punti Totali'},
                  markers=True)
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=14)
    )
    
    plot_json = fig.to_json()
    
    # Ultime 5 partite
    recent_matches = df_milan.tail(5).to_dict('records')
    
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
            "recent_matches": recent_matches
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)