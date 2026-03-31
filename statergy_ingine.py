"""
Cricket Strategy AI - Strategy Engine
Industry Level | Version 1.0
Author: Vishal

Loads trained ML model + batsman features.
Generates complete bowling strategy, fielding plan,
dismissal probability for any IPL batsman.
"""

import os
import logging
import pandas as pd
import numpy as np
import joblib

# ─────────────────────────────────────────────────────────────
#  LOGGING
# ─────────────────────────────────────────────────────────────
LOG_DIR = r"C:\Users\vishal\Desktop\cricket_statergy_ai\logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "strategy_engine.log")),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────────────────────
CONFIG = {
    "features_file": r"C:\Users\vishal\Desktop\cricket_statergy_ai\processed\batsman_features.csv",
    "model_file":    r"C:\Users\vishal\Desktop\cricket_statergy_ai\models\dismissal_model.pkl",
    "encoder_file":  r"C:\Users\vishal\Desktop\cricket_statergy_ai\models\label_encoder.pkl",
    "features_meta": r"C:\Users\vishal\Desktop\cricket_statergy_ai\models\feature_names.pkl",
}

PHASE_MAP  = {"powerplay": 0, "middle": 1, "slog": 2, "death": 3}
OVER_MAP   = {"powerplay": 3, "middle": 10, "slog": 15, "death": 18}

# ─────────────────────────────────────────────────────────────
#  LOAD MODEL AND DATA
# ─────────────────────────────────────────────────────────────
def load_resources():
    log.info("Loading model and features...")
    model        = joblib.load(CONFIG["model_file"])
    le           = joblib.load(CONFIG["encoder_file"])
    feature_cols = joblib.load(CONFIG["features_meta"])
    feat_df      = pd.read_csv(CONFIG["features_file"])
    log.info(f"  Model loaded    : OK")
    log.info(f"  Batsmen loaded  : {len(feat_df)}")
    return model, le, feature_cols, feat_df

# ─────────────────────────────────────────────────────────────
#  GET BATSMAN STATS
# ─────────────────────────────────────────────────────────────
def get_batsman_stats(name: str, feat_df: pd.DataFrame):
    # Exact match first
    row = feat_df[feat_df["batsman"].str.lower() == name.lower()]
    # Partial match if not found
    if row.empty:
        row = feat_df[feat_df["batsman"].str.lower().str.contains(
            name.lower(), na=False)]
    if row.empty:
        return None
    return row.iloc[0].to_dict()

# ─────────────────────────────────────────────────────────────
#  PREDICT DISMISSAL PROBABILITY
# ─────────────────────────────────────────────────────────────
def predict_dismissal(stats: dict, phase: str,
                      model, le, feature_cols: list) -> dict:
    phase_num = PHASE_MAP.get(phase.lower(), 3)
    over_num  = OVER_MAP.get(phase.lower(), 18)

    sample = pd.DataFrame([{
        "over":           over_num,
        "phase":          phase_num,
        "innings":        1,
        "runs_this_ball": 0,
        "batting_avg":    float(stats.get("batting_avg",    20.0)),
        "strike_rate":    float(stats.get("strike_rate",    110.0)),
        "dot_pct":        float(stats.get("dot_pct",        40.0)),
        "boundary_pct":   float(stats.get("boundary_pct",   15.0)),
        "six_pct":        float(stats.get("six_pct",         5.0)),
        "sr_powerplay":   float(stats.get("sr_powerplay",   120.0)),
        "sr_middle":      float(stats.get("sr_middle",      110.0)),
        "sr_slog":        float(stats.get("sr_slog",        130.0)),
        "sr_death":       float(stats.get("sr_death",       130.0)),
        "caught_pct":     float(stats.get("caught_pct",     40.0)),
        "bowled_pct":     float(stats.get("bowled_pct",     20.0)),
        "lbw_pct":        float(stats.get("lbw_pct",        15.0)),
        "stumped_pct":    float(stats.get("stumped_pct",     5.0)),
        "weakness_score": float(stats.get("weakness_score",  0.5)),
        "matches":        float(stats.get("matches",         10.0)),
        "h2h_sr":         float(stats.get("strike_rate",    110.0)),
        "h2h_dis_rate":   5.0,
        "h2h_balls":      10,
        "bowler_economy": 8.0,
        "bowler_wsr":     20.0,
    }])

    # Keep only columns the model was trained on
    sample = sample[feature_cols]

    proba       = model.predict_proba(sample)[0]
    classes     = le.classes_
    results     = dict(zip(classes, [round(p * 100, 1) for p in proba]))
    most_likely = max(results, key=results.get)

    return {"probabilities": results, "most_likely": most_likely}

# ─────────────────────────────────────────────────────────────
#  GENERATE BOWLING TIPS
# ─────────────────────────────────────────────────────────────
def generate_bowling_tips(stats: dict, phase: str,
                          dismissal: dict) -> list:
    tips        = []
    most_likely = dismissal["most_likely"]
    phase_lower = phase.lower()

    # Phase-specific tips
    if phase_lower == "powerplay":
        sr = stats.get("sr_powerplay", 120)
        if sr > 140:
            tips.append("Bowl full with swing early - attacks hard in powerplay")
        elif sr < 100:
            tips.append("Bowl short of length - struggles to score in powerplay")
        else:
            tips.append("Use seam movement - keep it full and straight")

    elif phase_lower == "middle":
        dot = stats.get("dot_pct", 40)
        sr  = stats.get("sr_middle", 110)
        if dot > 40:
            tips.append("Bowl tight lines - high dot ball rate in middle overs")
        if sr > 140:
            tips.append("Use spin with variation - attacks aggressively in middle")
        else:
            tips.append("Bowl slow yorkers to restrict scoring in middle overs")

    elif phase_lower == "slog":
        sr = stats.get("sr_slog", 130)
        if sr < 120:
            tips.append("Bowl wide yorkers - weak in slog overs")
        else:
            tips.append("Use slower balls - hard to time when expecting pace")

    elif phase_lower == "death":
        sr = stats.get("sr_death", 130)
        if sr == 0 or sr < 100:
            tips.append("Very weak in death overs - bowl any good length")
        elif sr < 130:
            tips.append("Bowl toe-crushing yorkers - below average death SR")
        else:
            tips.append("Mix yorkers and bouncers - strong death overs batsman")

    # Dismissal-based tips
    if most_likely == "caught":
        pct = stats.get("caught_pct", 40)
        tips.append(f"Bowl corridor of uncertainty - {pct}% caught dismissal rate")
        tips.append("Set 2nd slip and gully - strong catching positions")
    elif most_likely == "bowled":
        pct = stats.get("bowled_pct", 20)
        tips.append(f"Bowl full and straight - {pct}% bowled dismissal rate")
        tips.append("Aim at off stump to induce inside edge onto stumps")
    elif most_likely == "lbw":
        pct = stats.get("lbw_pct", 15)
        tips.append(f"Bowl into pads with inswing - {pct}% LBW dismissal rate")
        tips.append("Use off-spin or left-arm pace angled into batsman")
    elif most_likely == "stumped":
        tips.append("Use wrist spin - stumping opportunity outside off stump")
        tips.append("Flight the ball to invite drive and miss")
    elif most_likely == "run out":
        tips.append("Quick returns to stumps - high run out dismissal rate")
        tips.append("Place fielders at sharp angles to cut off quick singles")

    # Weakness score tip
    weakness = stats.get("weakness_score", 0.5)
    if weakness > 0.7:
        tips.append(f"High weakness score {weakness} - use aggressive attacking field")
    elif weakness < 0.35:
        tips.append(f"Low weakness score {weakness} - bowl defensively and build pressure")

    return tips[:5]

# ─────────────────────────────────────────────────────────────
#  GENERATE FIELDING PLAN
# ─────────────────────────────────────────────────────────────
def generate_fielding_plan(stats: dict, dismissal: dict) -> dict:
    most_likely = dismissal["most_likely"]

    catching  = []
    boundary  = []
    pressure  = []

    if most_likely == "caught":
        catching = ["2nd slip", "Gully", "Point", "Cover point"]
    elif most_likely == "bowled":
        catching = ["Mid-on", "Mid-off"]
        pressure = ["Short mid-wicket", "Silly mid-on"]
    elif most_likely == "lbw":
        catching = ["Square leg", "Fine leg"]
        pressure = ["Short leg", "Silly point"]
    elif most_likely == "stumped":
        catching = ["Cover", "Extra cover"]
        pressure = ["Mid-off", "Long-off"]
    elif most_likely == "run out":
        pressure = ["Cover point", "Mid-wicket", "Square leg"]

    six_pct = stats.get("six_pct", 5)
    if six_pct > 8:
        boundary = ["Long-on", "Long-off", "Deep mid-wicket"]
    else:
        boundary = ["Fine leg", "Deep square leg"]

    return {"catching": catching, "boundary": boundary, "pressure": pressure}

# ─────────────────────────────────────────────────────────────
#  GENERATE COMPLETE STRATEGY
# ─────────────────────────────────────────────────────────────
def generate_strategy(batsman_name: str, phase: str = "death") -> dict:
    model, le, feature_cols, feat_df = load_resources()

    stats = get_batsman_stats(batsman_name, feat_df)
    if not stats:
        log.error(f"Batsman '{batsman_name}' not found!")
        log.info("Available batsmen sample:")
        log.info(str(feat_df["batsman"].head(30).tolist()))
        return None

    dismissal = predict_dismissal(stats, phase, model, le, feature_cols)
    tips      = generate_bowling_tips(stats, phase, dismissal)
    fielding  = generate_fielding_plan(stats, dismissal)

    return {
        "batsman":      stats["batsman"],
        "team":         stats.get("team", "Unknown"),
        "phase":        phase.capitalize(),
        "stats": {
            "matches":        int(stats.get("matches", 0)),
            "total_runs":     int(stats.get("total_runs", 0)),
            "batting_avg":    float(stats.get("batting_avg", 0)),
            "strike_rate":    float(stats.get("strike_rate", 0)),
            "dot_pct":        float(stats.get("dot_pct", 0)),
            "boundary_pct":   float(stats.get("boundary_pct", 0)),
            "weakness_score": float(stats.get("weakness_score", 0)),
            "sr_powerplay":   float(stats.get("sr_powerplay", 0)),
            "sr_middle":      float(stats.get("sr_middle", 0)),
            "sr_slog":        float(stats.get("sr_slog", 0)),
            "sr_death":       float(stats.get("sr_death", 0)),
        },
        "dismissal":     dismissal,
        "bowling_tips":  tips,
        "fielding_plan": fielding,
    }

# ─────────────────────────────────────────────────────────────
#  PRINT STRATEGY REPORT
# ─────────────────────────────────────────────────────────────
def print_strategy_report(strategy: dict):
    if not strategy:
        return
    s = strategy
    p = s["stats"]
    d = s["dismissal"]

    print("\n" + "=" * 58)
    print(f"  STRATEGY REPORT")
    print("=" * 58)
    print(f"  Batsman      : {s['batsman']}")
    print(f"  Team         : {s['team']}")
    print(f"  Phase        : {s['phase']}")
    print("-" * 58)
    print(f"  Matches      : {p['matches']}")
    print(f"  Total runs   : {p['total_runs']}")
    print(f"  Batting avg  : {p['batting_avg']}")
    print(f"  Strike rate  : {p['strike_rate']}")
    print(f"  Dot ball %   : {p['dot_pct']}%")
    print(f"  Boundary %   : {p['boundary_pct']}%")
    print(f"  Weakness     : {p['weakness_score']} / 1.0")
    print("-" * 58)
    print(f"  Strike rate by phase:")
    print(f"    Powerplay  : {p['sr_powerplay']}")
    print(f"    Middle     : {p['sr_middle']}")
    print(f"    Slog       : {p['sr_slog']}")
    print(f"    Death      : {p['sr_death']}")
    print("-" * 58)
    print(f"  DISMISSAL PREDICTION:")
    print(f"  Most likely  : {d['most_likely'].upper()}")
    for kind, prob in sorted(
        d["probabilities"].items(), key=lambda x: x[1], reverse=True
    ):
        bar = "#" * int(prob / 3)
        print(f"    {kind:<12} {prob:5.1f}%  {bar}")
    print("-" * 58)
    print(f"  BOWLING TIPS:")
    for i, tip in enumerate(s["bowling_tips"], 1):
        print(f"    {i}. {tip}")
    print("-" * 58)
    print(f"  FIELDING PLAN:")
    if s["fielding_plan"]["catching"]:
        print(f"    Catching : {', '.join(s['fielding_plan']['catching'])}")
    if s["fielding_plan"]["boundary"]:
        print(f"    Boundary : {', '.join(s['fielding_plan']['boundary'])}")
    if s["fielding_plan"]["pressure"]:
        print(f"    Pressure : {', '.join(s['fielding_plan']['pressure'])}")
    print("=" * 58)

# ─────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log.info("=" * 58)
    log.info("CRICKET STRATEGY AI - STRATEGY ENGINE v1.0")
    log.info("=" * 58)

    test_cases = [
        ("DA Warner",  "powerplay"),
        ("DA Warner",  "death"),
        ("CH Gayle",   "powerplay"),
        ("RR Pant",    "death"),
        ("AD Russell", "death"),
    ]

    for batsman, phase in test_cases:
        strategy = generate_strategy(batsman, phase)
        if strategy:
            print_strategy_report(strategy)