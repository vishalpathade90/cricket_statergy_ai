"""
Cricket Strategy AI - FastAPI Backend
Industry Level | Version 1.0
Author: Vishal
"""

import sys
import os
sys.path.append(r"C:\Users\vishal\Desktop\cricket_statergy_ai")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import pandas as pd
from datetime import datetime

from statergy_ingine import generate_strategy

# ─────────────────────────────────────────────────────────────
#  APP SETUP
# ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="Cricket Strategy AI API",
    description="AI-powered cricket strategy using IPL data and 92.4% ML model",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FEATURES_PATH = r"C:\Users\vishal\Desktop\cricket_statergy_ai\processed\batsman_features.csv"
feat_df = pd.read_csv(FEATURES_PATH)

# ─────────────────────────────────────────────────────────────
#  REQUEST MODELS
# ─────────────────────────────────────────────────────────────
class StrategyRequest(BaseModel):
    batsman: str
    phase: str = "death"

class CompareRequest(BaseModel):
    player_a: str
    player_b: str
    phase: str = "death"

class ChatRequest(BaseModel):
    batsman: str
    question: str
    phase: Optional[str] = "death"

# ─────────────────────────────────────────────────────────────
#  ENDPOINTS
# ─────────────────────────────────────────────────────────────
@app.get("/")
def health_check():
    return {
        "status":    "online",
        "app":       "Cricket Strategy AI",
        "version":   "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "players":   len(feat_df),
        "model":     "Gradient Boosting 92.4% accuracy",
    }


@app.get("/players")
def get_all_players(team: Optional[str] = None):
    df = feat_df.copy()
    if team:
        df = df[df["team"].str.lower().str.contains(team.lower(), na=False)]
    players = df[["batsman", "team", "matches", "batting_avg",
                  "strike_rate", "weakness_score"]].to_dict(orient="records")
    return {"total": len(players), "players": players}


@app.get("/player/{name}")
def get_player(name: str):
    row = feat_df[feat_df["batsman"].str.lower() == name.lower()]
    if row.empty:
        row = feat_df[feat_df["batsman"].str.lower().str.contains(name.lower(), na=False)]
    if row.empty:
        raise HTTPException(status_code=404, detail=f"Player '{name}' not found")
    return row.iloc[0].to_dict()


@app.post("/strategy")
def get_strategy(req: StrategyRequest):
    strategy = generate_strategy(req.batsman, req.phase)
    if not strategy:
        raise HTTPException(status_code=404, detail=f"Batsman '{req.batsman}' not found")
    return strategy


@app.post("/compare")
def compare_players(req: CompareRequest):
    strat_a = generate_strategy(req.player_a, req.phase)
    strat_b = generate_strategy(req.player_b, req.phase)
    if not strat_a:
        raise HTTPException(status_code=404, detail=f"Player '{req.player_a}' not found")
    if not strat_b:
        raise HTTPException(status_code=404, detail=f"Player '{req.player_b}' not found")

    weaker = req.player_a if (
        strat_a["stats"]["weakness_score"] > strat_b["stats"]["weakness_score"]
    ) else req.player_b

    return {
        "player_a":       strat_a,
        "player_b":       strat_b,
        "phase":          req.phase,
        "weaker_batsman": weaker,
        "recommendation": f"Target {weaker} first in {req.phase} overs",
    }


@app.post("/llm-strategy")
async def get_llm_strategy(req: StrategyRequest):
    strategy = generate_strategy(req.batsman, req.phase)
    if not strategy:
        raise HTTPException(status_code=404, detail=f"Batsman '{req.batsman}' not found")

    try:
        from llm_engine import generate_llm_strategy
        narrative = await generate_llm_strategy(strategy)
    except Exception as e:
        narrative = f"LLM not configured yet. Add ANTHROPIC_API_KEY to .env file. Error: {str(e)}"

    return {
        "batsman":      req.batsman,
        "phase":        req.phase,
        "ml_strategy":  strategy,
        "ai_narrative": narrative,
    }


@app.post("/chat")
async def chat(req: ChatRequest):
    strategy = generate_strategy(req.batsman, req.phase)
    if not strategy:
        raise HTTPException(status_code=404, detail=f"Batsman '{req.batsman}' not found")

    try:
        from llm_engine import chat_with_ai
        answer = await chat_with_ai(req.question, strategy)
    except Exception as e:
        answer = f"LLM not configured yet. Add ANTHROPIC_API_KEY to .env file."

    return {
        "batsman":  req.batsman,
        "question": req.question,
        "answer":   answer,
    }


@app.get("/leaderboard")
def get_leaderboard(limit: int = 15, order: str = "weakest"):
    df = feat_df.copy()
    if order == "weakest":
        df = df.nlargest(limit, "weakness_score")
    else:
        df = df.nsmallest(limit, "weakness_score")
    cols = ["batsman", "team", "matches", "batting_avg",
            "strike_rate", "weakness_score", "most_likely_dismissal"]
    return {"order": order, "limit": limit, "players": df[cols].to_dict(orient="records")}


@app.get("/teams")
def get_teams():
    teams = feat_df["team"].dropna().unique().tolist()
    team_stats = []
    for team in sorted(teams):
        team_df = feat_df[feat_df["team"] == team]
        team_stats.append({
            "team":            team,
            "players":         len(team_df),
            "avg_strike_rate": round(team_df["strike_rate"].mean(), 1),
            "avg_weakness":    round(team_df["weakness_score"].mean(), 3),
        })
    return {"teams": team_stats}
