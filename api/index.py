"""
Cricket Strategy AI - Vercel Serverless Entry Point
Handles all API requests
"""

import sys
import os
from pathlib import Path

# Set up path to import from parent directory
PROJECT_ROOT = str(Path(__file__).parent.parent)
sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import joblib
from datetime import datetime

# Import strategy engine (OS-agnostic)
try:
    from statergy_ingine import generate_strategy
except ImportError:
    from strategy_engine import generate_strategy

# ─────────────────────────────────────────────────────────────
#  INITIALIZE APP
# ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="Cricket Strategy AI API",
    description="AI-powered cricket strategy using IPL data",
    version="2.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────
#  LOAD DATA (OS-AGNOSTIC)
# ─────────────────────────────────────────────────────────────
def get_data_path(filename: str) -> str:
    """Get OS-agnostic path to data files"""
    return os.path.join(PROJECT_ROOT, "data", filename)

try:
    FEATURES_PATH = get_data_path("batsman_features.csv")
    feat_df = pd.read_csv(FEATURES_PATH)
    print(f"Loaded batsman features: {FEATURES_PATH}")
except Exception as e:
    print(f"Warning: Could not load batsman features: {e}")
    feat_df = pd.DataFrame()

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

class LeaderboardRequest(BaseModel):
    phase: str = "death"
    limit: int = 10

# ─────────────────────────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Cricket Strategy AI",
        "version": "2.0.0",
        "data_loaded": len(feat_df) > 0
    }

@app.get("/api/health")
async def health_check():
    """Health check for Vercel"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.post("/api/strategy")
async def get_strategy(request: StrategyRequest):
    """Generate bowling strategy for a batsman"""
    try:
        if feat_df.empty:
            raise HTTPException(status_code=503, detail="Data not loaded")
        
        strategy = generate_strategy(
            batsman_name=request.batsman,
            phase=request.phase,
            features_df=feat_df
        )
        return {
            "success": True,
            "batsman": request.batsman,
            "phase": request.phase,
            "strategy": strategy
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/compare")
async def compare_batsmen(request: CompareRequest):
    """Compare two batsmen"""
    try:
        if feat_df.empty:
            raise HTTPException(status_code=503, detail="Data not loaded")
        
        player_a_data = feat_df[feat_df["batsman"] == request.player_a]
        player_b_data = feat_df[feat_df["batsman"] == request.player_b]
        
        if player_a_data.empty or player_b_data.empty:
            raise HTTPException(status_code=404, detail="Player not found")
        
        return {
            "success": True,
            "player_a": request.player_a,
            "player_b": request.player_b,
            "comparison": {
                "player_a": player_a_data.iloc[0].to_dict(),
                "player_b": player_b_data.iloc[0].to_dict()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/leaderboard")
async def get_leaderboard(phase: str = "death", limit: int = 10):
    """Get top dismissable batsmen"""
    try:
        if feat_df.empty:
            raise HTTPException(status_code=503, detail="Data not loaded")
        
        # Sort by dismissal probability (adjust based on your data)
        top_batsmen = feat_df.nlargest(min(limit, len(feat_df)), "dismissal_probability")
        
        return {
            "success": True,
            "phase": phase,
            "count": len(top_batsmen),
            "leaderboard": top_batsmen.to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/batsman/{batsman_name}")
async def get_batsman_profile(batsman_name: str):
    """Get detailed profile for a batsman"""
    try:
        if feat_df.empty:
            raise HTTPException(status_code=503, detail="Data not loaded")
        
        batsman = feat_df[feat_df["batsman"] == batsman_name]
        if batsman.empty:
            raise HTTPException(status_code=404, detail="Batsman not found")
        
        return {
            "success": True,
            "batsman": batsman_name,
            "profile": batsman.iloc[0].to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ─────────────────────────────────────────────────────────────
#  ASGI Handler for Vercel
# ─────────────────────────────────────────────────────────────
# Vercel looks for this
handler = app
