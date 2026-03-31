"""
Cricket Strategy AI — Data Cleaning Pipeline
Industry Level | Version 2.0
Author: Vishal

Dataset columns confirmed:
match_id, season, start_date, venue, innings, ball,
batting_team, bowling_team, striker, non_striker, bowler,
runs_off_bat, extras, wides, noballs, byes, legbyes, penalty,
wicket_type, player_dismissed, other_wicket_type, other_player_dismissed

Each CSV = one IPL match (named by match_id e.g. 1082591.csv)
Folder: C:\\Users\\vishal\\Desktop\\cricket_statergy_ai\\ipldata
"""

import os
import glob
import logging
import pandas as pd
import numpy as np
from datetime import datetime

# ─────────────────────────────────────────────────────────────
#  LOGGING — saves to file AND prints to terminal
# ─────────────────────────────────────────────────────────────
LOG_DIR = r"C:\Users\vishal\Desktop\cricket_statergy_ai\logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "datacleaning.log")),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
#  CONFIG — your exact paths and settings
# ─────────────────────────────────────────────────────────────
CONFIG = {
    "raw_data_dir":  r"C:\Users\vishal\Desktop\cricket_statergy_ai\ipldata",
    "processed_dir": r"C:\Users\vishal\Desktop\cricket_statergy_ai\processed",
    "output_file":   r"C:\Users\vishal\Desktop\cricket_statergy_ai\processed\batsman_features.csv",
    "min_balls":     30,    # skip batsmen with fewer than 30 balls
    "min_matches":   3,     # skip batsmen with fewer than 3 matches
}

# ─────────────────────────────────────────────────────────────
#  STEP 1 — LOAD ALL MATCH CSV FILES
# ─────────────────────────────────────────────────────────────
def load_raw_data(data_dir: str) -> pd.DataFrame:
    log.info("=" * 60)
    log.info("STEP 1 — Loading raw data")
    log.info(f"Folder: {data_dir}")

    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))

    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in: {data_dir}")

    log.info(f"Found {len(csv_files)} match CSV files")

    df_list = []
    for i, f in enumerate(csv_files, 1):
        try:
            temp = pd.read_csv(f, dtype=str)
            df_list.append(temp)
            if i % 50 == 0:
                log.info(f"  Loaded {i}/{len(csv_files)} files...")
        except Exception as e:
            log.warning(f"  Skipped {os.path.basename(f)}: {e}")

    if not df_list:
        raise ValueError("No valid CSV files loaded.")

    df = pd.concat(df_list, ignore_index=True)

    log.info(f"  OK Total rows loaded  : {len(df):,}")
    log.info(f"  OK Total matches      : {df['match_id'].nunique()}")
    log.info(f"  OK Columns            : {list(df.columns)}")
    return df

# ─────────────────────────────────────────────────────────────
#  STEP 2 — RENAME COLUMNS TO STANDARD NAMES
#  Your dataset uses: striker, runs_off_bat, wicket_type
#  We rename to:      batsman, runs_batsman, dismissal_kind
# ─────────────────────────────────────────────────────────────
def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    log.info("STEP 2 — Renaming columns to standard names")

    df = df.rename(columns={
        "striker":           "batsman",
        "runs_off_bat":      "runs_batsman",
        "wicket_type":       "dismissal_kind",
    })

    log.info("  OK striker        -> batsman")
    log.info("  OK runs_off_bat   -> runs_batsman")
    log.info("  OK wicket_type    -> dismissal_kind")
    return df

# ─────────────────────────────────────────────────────────────
#  STEP 3 — CLEAN DATA
# ─────────────────────────────────────────────────────────────
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    log.info("STEP 3 — Cleaning data")
    original = len(df)

    # Derive over number from ball column
    # ball format: 0.1, 0.2 ... 19.6 -> over = integer part
    df["over"] = df["ball"].astype(float).astype(int)

    # Remove wides (not faced by batsman)
    df = df[df["wides"].isna() | (df["wides"] == 0)]

    # Remove no-balls only when batsman didn't score off it
    df = df[df["noballs"].isna() | (df["noballs"] == 0)]

    # Fix data types
    df["runs_batsman"]   = pd.to_numeric(df["runs_batsman"], errors="coerce").fillna(0).astype(int)
    df["over"]           = pd.to_numeric(df["over"], errors="coerce").fillna(0).astype(int)
    df["dismissal_kind"] = df["dismissal_kind"].fillna("")
    df["player_dismissed"] = df["player_dismissed"].fillna("")

    # Remove rows with missing batsman or bowler
    df = df[df["batsman"].notna() & (df["batsman"] != "")]
    df = df[df["bowler"].notna()  & (df["bowler"]  != "")]

    # Remove invalid overs
    df = df[(df["over"] >= 0) & (df["over"] <= 19)]

    removed = original - len(df)
    log.info(f"  OK Removed {removed:,} wide/noball/invalid rows")
    log.info(f"  OK Legal deliveries   : {len(df):,}")
    log.info(f"  OK Unique batsmen     : {df['batsman'].nunique()}")
    log.info(f"  OK Unique bowlers     : {df['bowler'].nunique()}")
    log.info(f"  OK Unique matches     : {df['match_id'].nunique()}")
    if "season" in df.columns:
        seasons = sorted(df["season"].dropna().unique().tolist(), key=lambda x: str(x))
        log.info(f"  OK Seasons            : {seasons}")
    log.info(f"  OK Venues             : {df['venue'].nunique()} unique venues")
    return df

# ─────────────────────────────────────────────────────────────
#  STEP 4 — PHASE CLASSIFICATION
# ─────────────────────────────────────────────────────────────
def classify_phase(over: int) -> str:
    if over <= 5:    return "Powerplay"
    elif over <= 14: return "Middle"
    elif over <= 16: return "Slog"
    else:            return "Death"

# ─────────────────────────────────────────────────────────────
#  STEP 5 — FEATURE ENGINEERING PER BATSMAN
# ─────────────────────────────────────────────────────────────
def engineer_features(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    log.info("STEP 4 — Engineering features per batsman")

    df["phase"] = df["over"].apply(classify_phase)

    features = []
    skipped  = 0
    batsmen  = df["batsman"].dropna().unique()
    total    = len(batsmen)

    log.info(f"  Processing {total} unique batsmen...")

    for i, batsman in enumerate(batsmen, 1):
        if i % 100 == 0:
            log.info(f"  {i}/{total} batsmen processed...")

        bat         = df[df["batsman"] == batsman]
        total_balls = len(bat)
        matches     = bat["match_id"].nunique()

        # Skip low sample batsmen
        if total_balls < config["min_balls"] or matches < config["min_matches"]:
            skipped += 1
            continue

        # ── Basic stats ──
        total_runs       = int(bat["runs_batsman"].sum())
        dismissed        = bat[bat["dismissal_kind"] != ""]
        total_dismissals = len(dismissed)
        batting_avg      = round(total_runs / total_dismissals, 2) if total_dismissals > 0 else float(total_runs)
        strike_rate      = round((total_runs / total_balls) * 100, 2)

        # ── Ball type breakdown ──
        dot_pct      = round(len(bat[bat["runs_batsman"] == 0]) / total_balls * 100, 1)
        single_pct   = round(len(bat[bat["runs_batsman"] == 1]) / total_balls * 100, 1)
        two_pct      = round(len(bat[bat["runs_batsman"] == 2]) / total_balls * 100, 1)
        three_pct    = round(len(bat[bat["runs_batsman"] == 3]) / total_balls * 100, 1)
        four_pct     = round(len(bat[bat["runs_batsman"] == 4]) / total_balls * 100, 1)
        six_pct      = round(len(bat[bat["runs_batsman"] == 6]) / total_balls * 100, 1)
        boundary_pct = round(four_pct + six_pct, 1)

        # ── Phase-wise strike rate ──
        def phase_sr(phase_name):
            p = bat[bat["phase"] == phase_name]
            return round((p["runs_batsman"].sum() / len(p)) * 100, 1) if len(p) > 0 else 0.0

        # ── Phase-wise balls faced ──
        pp_balls    = len(bat[bat["phase"] == "Powerplay"])
        mid_balls   = len(bat[bat["phase"] == "Middle"])
        slog_balls  = len(bat[bat["phase"] == "Slog"])
        death_balls = len(bat[bat["phase"] == "Death"])

        # ── Dismissal type breakdown ──
        def dis_pct(kind):
            if total_dismissals == 0: return 0.0
            return round(
                len(dismissed[dismissed["dismissal_kind"] == kind]) / total_dismissals * 100, 1
            )

        # ── Most likely dismissal ──
        if total_dismissals > 0:
            most_likely = dismissed["dismissal_kind"].value_counts().index[0].upper()
        else:
            most_likely = "UNKNOWN"

        # ── Team and venue info ──
        batting_team  = bat["batting_team"].mode()[0] if "batting_team" in bat.columns else "Unknown"
        top_venue     = bat["venue"].mode()[0] if "venue" in bat.columns else "Unknown"
        seasons_played = sorted(bat["season"].dropna().unique().tolist()) if "season" in bat.columns else []

        # ── Innings split ──
        inn1_balls = len(bat[bat["innings"] == 1]) if "innings" in bat.columns else 0
        inn2_balls = len(bat[bat["innings"] == 2]) if "innings" in bat.columns else 0
        inn1_sr    = round((bat[bat["innings"] == 1]["runs_batsman"].sum() / inn1_balls) * 100, 1) if inn1_balls > 0 else 0.0
        inn2_sr    = round((bat[bat["innings"] == 2]["runs_batsman"].sum() / inn2_balls) * 100, 1) if inn2_balls > 0 else 0.0

        # ── Weakness score (0–1, higher = easier to dismiss) ──
        norm_dot      = min(dot_pct / 60, 1.0)
        norm_boundary = 1 - min(boundary_pct / 30, 1.0)
        norm_avg      = 1 - min(batting_avg / 60, 1.0)
        norm_sr       = 1 - min(strike_rate / 180, 1.0)

        weakness_score = round(
            0.30 * norm_dot      +
            0.25 * norm_boundary +
            0.25 * norm_avg      +
            0.20 * norm_sr,
            3
        )

        features.append({
            # Identity
            "batsman":               batsman,
            "team":                  batting_team,
            "top_venue":             top_venue,
            "seasons":               str(seasons_played),

            # Volume
            "matches":               matches,
            "total_balls":           total_balls,
            "total_runs":            total_runs,
            "total_dismissals":      total_dismissals,

            # Core stats
            "batting_avg":           batting_avg,
            "strike_rate":           strike_rate,

            # Ball breakdown
            "dot_pct":               dot_pct,
            "single_pct":            single_pct,
            "two_pct":               two_pct,
            "three_pct":             three_pct,
            "four_pct":              four_pct,
            "six_pct":               six_pct,
            "boundary_pct":          boundary_pct,

            # Phase strike rates
            "sr_powerplay":          phase_sr("Powerplay"),
            "sr_middle":             phase_sr("Middle"),
            "sr_slog":               phase_sr("Slog"),
            "sr_death":              phase_sr("Death"),

            # Phase ball counts
            "pp_balls":              pp_balls,
            "mid_balls":             mid_balls,
            "slog_balls":            slog_balls,
            "death_balls":           death_balls,

            # Innings split
            "inn1_balls":            inn1_balls,
            "inn2_balls":            inn2_balls,
            "inn1_sr":               inn1_sr,
            "inn2_sr":               inn2_sr,

            # Dismissal breakdown
            "caught_pct":            dis_pct("caught"),
            "bowled_pct":            dis_pct("bowled"),
            "lbw_pct":               dis_pct("lbw"),
            "runout_pct":            dis_pct("run out"),
            "stumped_pct":           dis_pct("stumped"),
            "most_likely_dismissal": most_likely,

            # AI score
            "weakness_score":        weakness_score,
        })

    feat_df = pd.DataFrame(features)
    feat_df.sort_values("weakness_score", ascending=False, inplace=True)
    feat_df.reset_index(drop=True, inplace=True)

    log.info(f"  OK Features built for : {len(feat_df)} batsmen")
    log.info(f"  WARNING  Skipped            : {skipped} batsmen (low sample)")
    log.info(f"  OK Feature columns    : {len(feat_df.columns)}")
    return feat_df

# ─────────────────────────────────────────────────────────────
#  STEP 6 — SAVE OUTPUT
# ─────────────────────────────────────────────────────────────
def save_output(feat_df: pd.DataFrame, config: dict):
    log.info("STEP 5 — Saving output")
    os.makedirs(config["processed_dir"], exist_ok=True)
    feat_df.to_csv(config["output_file"], index=False)
    log.info(f"  OK Saved to : {config['output_file']}")
    log.info(f"  OK Shape    : {feat_df.shape[0]} rows x {feat_df.shape[1]} columns")

# ─────────────────────────────────────────────────────────────
#  STEP 7 — PRINT SUMMARY
# ─────────────────────────────────────────────────────────────
def print_summary(feat_df: pd.DataFrame):
    log.info("=" * 60)
    log.info("PIPELINE SUMMARY")
    log.info("=" * 60)
    log.info(f"Total batsmen processed : {len(feat_df)}")
    log.info(f"Avg batting average     : {feat_df['batting_avg'].mean():.1f}")
    log.info(f"Avg strike rate         : {feat_df['strike_rate'].mean():.1f}")
    log.info(f"Avg weakness score      : {feat_df['weakness_score'].mean():.3f}")

    cols = ["batsman", "team", "matches", "batting_avg", "strike_rate", "weakness_score"]

    log.info("\n── Top 15 most dismissable batsmen ──")
    log.info("\n" + feat_df[cols].head(15).to_string(index=False))

    log.info("\n── Top 15 strongest batsmen ──")
    log.info("\n" + feat_df[cols].tail(15).to_string(index=False))

# ─────────────────────────────────────────────────────────────
#  MAIN — runs all steps in order
# ─────────────────────────────────────────────────────────────
def run_pipeline():
    start = datetime.now()
    log.info("=" * 60)
    log.info("CRICKET STRATEGY AI — DATA CLEANING PIPELINE v2.0")
    log.info(f"Started : {start.strftime('%Y-%m-%d %H:%M:%S')}")
    log.info("=" * 60)

    try:
        df      = load_raw_data(CONFIG["raw_data_dir"])
        df      = rename_columns(df)
        df      = clean_data(df)
        feat_df = engineer_features(df, CONFIG)
        save_output(feat_df, CONFIG)
        print_summary(feat_df)

        elapsed = (datetime.now() - start).seconds
        log.info("=" * 60)
        log.info(f"OK PIPELINE COMPLETE in {elapsed} seconds")
        log.info(f"OK Output : {CONFIG['output_file']}")
        log.info("=" * 60)
        return feat_df

    except FileNotFoundError as e:
        log.error(f"FILE ERROR: {e}")
        log.error(f"Make sure CSV files are in: {CONFIG['raw_data_dir']}")
    except ValueError as e:
        log.error(f"DATA ERROR: {e}")
    except Exception as e:
        log.error(f"UNEXPECTED ERROR: {e}", exc_info=True)

if __name__ == "__main__":
    run_pipeline()
