from fastapi.testclient import TestClient
from src.main import app, prepare_milan_data, prepare_quiz_question

client = TestClient(app)

def test_home_status():
    """Test if home page loads correctly"""
    response = client.get("/")
    assert response.status_code == 200

def test_data_preparation():
    """Test if data is loaded and structured correctly"""
    df = prepare_milan_data()
    assert len(df) > 0  # Check if data exists
    assert 'cumulative_points' in df.columns  # Check required columns
    assert 'opponent' in df.columns
    assert 'result' in df.columns

def test_quiz_generation():
    """Test if quiz is generated with correct structure"""
    df = prepare_milan_data()
    quiz = prepare_quiz_question(df)
    
    # Check quiz structure
    assert 'question' in quiz
    assert 'correct_answer' in quiz
    assert 'wrong_answers' in quiz
    assert len(quiz['wrong_answers']) == 3

def test_stats_calculation():
    """Test if statistics are calculated correctly"""
    df = prepare_milan_data()
    
    # Check statistics calculations
    total_matches = len(df)
    wins = len(df[df['result'] == 'W'])
    draws = len(df[df['result'] == 'D'])
    losses = len(df[df['result'] == 'L'])
    
    assert total_matches == wins + draws + losses
    assert all(df['points'] <= 3)  # Points per match not exceeding 3
    assert all(df['cumulative_points'].diff().dropna() >= 0)  # Cumulative points always increasing

def test_html_content():
    """Test if HTML contains all required sections"""
    response = client.get("/")
    content = response.text
    
    # Check key HTML elements
    assert "AC Milan - Season Analysis" in content
    assert "General Statistics" in content
    assert "Quiz Time!" in content
    assert "Points Progression" in content

def test_quiz_answer_uniqueness():
    """Test if quiz answers are unique"""
    df = prepare_milan_data()
    quiz = prepare_quiz_question(df)
    all_answers = [quiz['correct_answer']] + quiz['wrong_answers']
    assert len(all_answers) == len(set(all_answers))  # No duplicates

def test_match_points_calculation():
    """Test if match points are calculated correctly"""
    df = prepare_milan_data()
    for _, match in df.iterrows():
        if match['result'] == 'W':
            assert match['points'] == 3
        elif match['result'] == 'D':
            assert match['points'] == 1
        else:
            assert match['points'] == 0

def test_recent_matches():
    """Test if recent matches section shows last 5 games"""
    response = client.get("/")
    assert response.status_code == 200
    assert len(response.context['recent_matches']) == 5

def test_plot_data():
    """Test if plot data is structured correctly"""
    response = client.get("/")
    plot_data = response.context['plot_json']
    assert 'data' in plot_data
    assert 'layout' in plot_data

def test_invalid_routes():
    """Test handling of invalid routes"""
    response = client.get("/invalid_route")
    assert response.status_code == 404

def test_data_consistency():
    """Test data consistency and ordering"""
    df = prepare_milan_data()
    assert df['date'].is_monotonic_increasing  # Dates in order
    assert not df.duplicated().any()  # No duplicates
    assert df['cumulative_points'].is_monotonic_increasing  # Cumulative points increasing

# ... resto del codice ... 