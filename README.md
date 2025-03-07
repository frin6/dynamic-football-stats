# Dynamic Football Stats

## Intro

This repository was created to generate valuable insights from football data. While the current dataset is static, taken from the 2023/24 Serie A League, the project is designed to be dynamic and could easily integrate data from the current season through an API. Also other leagues in other seasons could be analysed.

The data were taken from an open-source repository (https://github.com/openfootball/football.json/tree/master).

The real objective of the repository was to test actual capabilities of FastAPI and Render.

## Summary
This web application shows football seasons statistics (AC Milan stats in the example), including:
- Points progression
- Match results
- Interactive quiz
- Season statistics

## Features
- Interactive points progression chart
- Last 5 matches display
- Random quiz questions about the season
- General statistics overview

## Tech Stack
- FastAPI
- Plotly
- Pandas
- Jinja2
- Bootstrap

## Local Development
1. Clone the repository
2. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   uvicorn src.main:app --reload
   ```
5. Visit http://127.0.0.1:8000

## Deployment
The application is configured for deployment on Render.com using the provided `render.yaml` configuration.
The application is deployed on Render.com at https://dynamic-football-stats-2.onrender.com/. If it doesn't load immediately, please allow up to 20 seconds due to the free tier service limitations. (Note: Availability may be limited as it's hosted on a free plan.)
