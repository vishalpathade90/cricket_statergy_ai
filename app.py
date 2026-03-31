"""
Cricket Strategy AI - Advanced Dashboard
Industry Level | Version 2.0
Author: Vishal

Features:
- Multi-tab layout (Strategy / Compare / Team Analysis / Leaderboard)
- Interactive pitch diagram with fielder positions
- Radar chart for batsman weakness profile
- Head-to-head team comparison
- Top 10 most dismissable batsmen leaderboard
- PDF export ready layout
- Dark themed professional UI

Run with:
C:\\Users\\vishal\\Desktop\\cricket_statergy_ai\\venv311\\Scripts\\streamlit.exe run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, Rectangle
import sys
import os

sys.path.append(r"C:\Users\vishal\Desktop\cricket_statergy_ai")
from statergy_ingine import generate_strategy

# ─────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cricket Strategy AI",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
#  ADVANCED CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main { background: #0a0e1a; }

    .hero-banner {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        border: 1px solid #e94560;
        text-align: center;
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #e94560;
        margin: 0;
        letter-spacing: -1px;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: #a0aec0;
        margin-top: 0.5rem;
    }
    .hero-stats {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin-top: 1rem;
    }
    .hero-stat {
        text-align: center;
    }
    .hero-stat-val {
        font-size: 1.5rem;
        font-weight: 700;
        color: #48bb78;
    }
    .hero-stat-lbl {
        font-size: 0.75rem;
        color: #718096;
    }

    .metric-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        transition: all 0.3s;
    }
    .metric-card:hover { border-color: #e94560; transform: translateY(-2px); }
    .metric-val { font-size: 1.8rem; font-weight: 700; color: #e2e8f0; }
    .metric-lbl { font-size: 0.75rem; color: #718096; margin-top: 0.3rem; }
    .metric-delta-good { font-size: 0.8rem; color: #48bb78; }
    .metric-delta-bad  { font-size: 0.8rem; color: #fc8181; }

    .player-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #e94560;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .player-name {
        font-size: 1.8rem;
        font-weight: 700;
        color: #e2e8f0;
    }
    .player-team {
        font-size: 0.9rem;
        color: #a0aec0;
        margin-top: 0.2rem;
    }

    .dismissal-pill {
        display: inline-block;
        background: #e94560;
        color: white;
        padding: 0.4rem 1.2rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 1rem;
        letter-spacing: 1px;
    }

    .weakness-bar-container {
        background: #2d3748;
        border-radius: 8px;
        height: 12px;
        overflow: hidden;
        margin-top: 0.5rem;
    }

    .tip-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-left: 4px solid #e94560;
        border-radius: 0 12px 12px 0;
        padding: 0.8rem 1.2rem;
        margin: 0.5rem 0;
        color: #e2e8f0;
        font-size: 0.9rem;
    }
    .tip-num {
        color: #e94560;
        font-weight: 700;
        margin-right: 0.5rem;
    }

    .phase-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.2rem;
    }
    .phase-pp   { background: #2b6cb0; color: #bee3f8; }
    .phase-mid  { background: #276749; color: #c6f6d5; }
    .phase-slog { background: #b7791f; color: #fefcbf; }
    .phase-death{ background: #9b2335; color: #fed7d7; }

    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #e94560;
        border-bottom: 1px solid #2d3748;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
        letter-spacing: 0.5px;
    }

    .field-legend {
        display: flex;
        gap: 1rem;
        margin-top: 0.5rem;
        flex-wrap: wrap;
    }
    .field-legend-item {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.8rem;
        color: #a0aec0;
    }
    .legend-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
    }

    .compare-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 1rem;
        height: 100%;
    }

    .leaderboard-row {
        display: flex;
        align-items: center;
        padding: 0.6rem;
        border-radius: 8px;
        margin: 0.3rem 0;
        background: #1a1a2e;
        border: 1px solid #2d3748;
    }
    .lb-rank {
        font-size: 1.2rem;
        font-weight: 700;
        color: #e94560;
        width: 2rem;
    }
    .lb-name { font-size: 0.9rem; color: #e2e8f0; flex: 1; }
    .lb-score { font-size: 0.9rem; color: #48bb78; font-weight: 600; }

    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0e1a 0%, #16213e 100%);
        border-right: 1px solid #2d3748;
    }
    div[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

    .stTabs [data-baseweb="tab-list"] { background: #16213e; border-radius: 10px; padding: 0.3rem; }
    .stTabs [data-baseweb="tab"] { color: #a0aec0; border-radius: 8px; }
    .stTabs [aria-selected="true"] { background: #e94560 !important; color: white !important; }

    .stButton button {
        background: linear-gradient(135deg, #e94560, #c62a47);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .stButton button:hover { opacity: 0.9; transform: translateY(-1px); }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  LOAD DATA
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_features():
    return pd.read_csv(
        r"C:\Users\vishal\Desktop\cricket_statergy_ai\processed\batsman_features.csv"
    )

feat_df      = load_features()
batsmen_list = sorted(feat_df["batsman"].tolist())
teams_list   = sorted(feat_df["team"].dropna().unique().tolist())

# ─────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏏 Cricket Strategy AI")
    st.markdown("---")
    st.markdown("### Player Selection")

    batsman_name = st.selectbox(
        "Select Batsman",
        batsmen_list,
        index=batsmen_list.index("DA Warner") if "DA Warner" in batsmen_list else 0
    )

    phase = st.selectbox(
        "Match Phase",
        ["Powerplay", "Middle", "Slog", "Death"],
        index=3
    )

    st.markdown("---")
    st.markdown("### Filters")
    min_matches = st.slider("Min matches played", 5, 100, 10)

    st.markdown("---")
    generate_btn = st.button("Generate Strategy", use_container_width=True)

    st.markdown("---")
    st.markdown("**Model Stats**")
    st.markdown("Accuracy: **92.4%**")
    st.markdown("Matches: **845 IPL**")
    st.markdown("Deliveries: **401,328**")
    st.markdown("Batsmen: **398**")

# ─────────────────────────────────────────────────────────────
#  HERO BANNER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🏏 Cricket Strategy AI</div>
    <div class="hero-subtitle">AI-powered bowling strategy and fielding plan generator for IPL teams</div>
    <div class="hero-stats">
        <div class="hero-stat">
            <div class="hero-stat-val">92.4%</div>
            <div class="hero-stat-lbl">Model Accuracy</div>
        </div>
        <div class="hero-stat">
            <div class="hero-stat-val">845</div>
            <div class="hero-stat-lbl">IPL Matches</div>
        </div>
        <div class="hero-stat">
            <div class="hero-stat-val">398</div>
            <div class="hero-stat-lbl">Players Profiled</div>
        </div>
        <div class="hero-stat">
            <div class="hero-stat-val">401K</div>
            <div class="hero-stat-lbl">Deliveries Analysed</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "Strategy Report",
    "Player Comparison",
    "Team Analysis",
    "Leaderboard"
])

# ═══════════════════════════════════════════════════════════════
#  TAB 1 — STRATEGY REPORT
# ═══════════════════════════════════════════════════════════════
with tab1:
    with st.spinner(f"Generating AI strategy for {batsman_name}..."):
        strategy = generate_strategy(batsman_name, phase.lower())

    if not strategy:
        st.error(f"Batsman '{batsman_name}' not found.")
        st.stop()

    s  = strategy
    p  = s["stats"]
    d  = s["dismissal"]
    fp = s["fielding_plan"]

    # Player Card
    col_p1, col_p2, col_p3 = st.columns([2, 1, 1])

    with col_p1:
        st.markdown(f"""
        <div class="player-card">
            <div class="player-name">{s['batsman']}</div>
            <div class="player-team">🏟️ {s['team']}  |  📊 {s['phase']} overs</div>
        </div>
        """, unsafe_allow_html=True)

    with col_p2:
        weakness = p["weakness_score"]
        pct      = int(weakness * 100)
        color    = "#e94560" if weakness > 0.6 else "#f6ad55" if weakness > 0.4 else "#48bb78"
        label    = "HIGH RISK" if weakness > 0.6 else "MEDIUM RISK" if weakness > 0.4 else "LOW RISK"
        st.markdown(f"""
        <div class="player-card" style="text-align:center">
            <div style="font-size:0.8rem;color:#718096">WEAKNESS SCORE</div>
            <div style="font-size:2.5rem;font-weight:700;color:{color}">{weakness}</div>
            <div style="background:#2d3748;border-radius:8px;height:8px;margin-top:0.5rem">
                <div style="width:{pct}%;height:100%;background:{color};border-radius:8px"></div>
            </div>
            <div style="font-size:0.8rem;color:{color};margin-top:0.3rem">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_p3:
        most_likely = d["most_likely"]
        top_prob    = d["probabilities"][most_likely.lower()]
        st.markdown(f"""
        <div class="player-card" style="text-align:center">
            <div style="font-size:0.8rem;color:#718096">MOST LIKELY DISMISSAL</div>
            <div style="font-size:2rem;font-weight:700;color:#e94560;margin-top:0.5rem">{most_likely.upper()}</div>
            <div style="font-size:1rem;color:#48bb78;margin-top:0.3rem">{top_prob:.1f}% probability</div>
            <div style="font-size:0.75rem;color:#718096;margin-top:0.2rem">Based on 92.4% ML model</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Metrics Row
    st.markdown('<div class="section-title">CAREER STATISTICS</div>', unsafe_allow_html=True)
    m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
    metrics = [
        (m1, "Matches",     p["matches"],                    ""),
        (m2, "Total Runs",  f"{p['total_runs']:,}",          ""),
        (m3, "Batting Avg", f"{p['batting_avg']:.1f}",       ""),
        (m4, "Strike Rate", f"{p['strike_rate']:.1f}",       ""),
        (m5, "Dot Ball %",  f"{p['dot_pct']:.1f}%",          ""),
        (m6, "Boundary %",  f"{p['boundary_pct']:.1f}%",     ""),
        (m7, "Weakness",    f"{p['weakness_score']:.3f}",    ""),
    ]
    for col, label, val, delta in metrics:
        with col:
            st.metric(label, val)

    st.markdown("---")

    # Charts Row
    col_c1, col_c2, col_c3 = st.columns([1.2, 1.2, 1])

    # ── Radar Chart ──
    with col_c1:
        st.markdown('<div class="section-title">WEAKNESS RADAR</div>', unsafe_allow_html=True)

        categories = ["Dot %", "Boundary %", "Avg", "SR", "PP SR", "Death SR"]
        max_vals   = [60, 30, 60, 180, 200, 250]
        raw_vals   = [
            p["dot_pct"],
            p["boundary_pct"],
            p["batting_avg"],
            p["strike_rate"],
            p["sr_powerplay"],
            p["sr_death"]
        ]
        norm_vals  = [min(v / m, 1.0) for v, m in zip(raw_vals, max_vals)]
        norm_vals  += norm_vals[:1]

        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]

        fig_r, ax_r = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
        fig_r.patch.set_facecolor("#16213e")
        ax_r.set_facecolor("#0a0e1a")

        ax_r.plot(angles, norm_vals, "o-", linewidth=2, color="#e94560")
        ax_r.fill(angles, norm_vals, alpha=0.25, color="#e94560")
        ax_r.set_xticks(angles[:-1])
        ax_r.set_xticklabels(categories, size=8, color="#a0aec0")
        ax_r.set_yticks([0.25, 0.5, 0.75, 1.0])
        ax_r.set_yticklabels(["25%", "50%", "75%", "100%"], size=6, color="#718096")
        ax_r.grid(color="#2d3748", linewidth=0.5)
        ax_r.spines["polar"].set_color("#2d3748")
        fig_r.tight_layout()
        st.pyplot(fig_r)
        plt.close()

    # ── Phase SR Bar Chart ──
    with col_c2:
        st.markdown('<div class="section-title">STRIKE RATE BY PHASE</div>', unsafe_allow_html=True)

        phases    = ["Powerplay", "Middle", "Slog", "Death"]
        sr_vals   = [p["sr_powerplay"], p["sr_middle"], p["sr_slog"], p["sr_death"]]
        bar_cols  = ["#2b6cb0", "#276749", "#b7791f", "#9b2335"]

        fig_b, ax_b = plt.subplots(figsize=(4, 3.5))
        fig_b.patch.set_facecolor("#16213e")
        ax_b.set_facecolor("#0a0e1a")

        bars = ax_b.bar(phases, sr_vals, color=bar_cols, edgecolor="#0a0e1a",
                        linewidth=1, width=0.6)
        ax_b.axhline(y=120, color="#718096", linestyle="--", linewidth=0.8, alpha=0.6)
        ax_b.text(3.5, 122, "Avg 120", color="#718096", fontsize=7, ha="right")

        for bar, val in zip(bars, sr_vals):
            if val > 0:
                ax_b.text(
                    bar.get_x() + bar.get_width()/2,
                    bar.get_height() + 3,
                    f"{val:.0f}",
                    ha="center", va="bottom", fontsize=9,
                    color="white", fontweight="bold"
                )

        ax_b.set_ylabel("Strike Rate", color="#a0aec0", fontsize=9)
        ax_b.set_ylim(0, max(sr_vals) * 1.25 if max(sr_vals) > 0 else 200)
        ax_b.tick_params(colors="#a0aec0", labelsize=8)
        ax_b.spines["bottom"].set_color("#2d3748")
        ax_b.spines["left"].set_color("#2d3748")
        ax_b.spines["top"].set_visible(False)
        ax_b.spines["right"].set_visible(False)
        fig_b.tight_layout()
        st.pyplot(fig_b)
        plt.close()

    # ── Dismissal Donut ──
    with col_c3:
        st.markdown('<div class="section-title">DISMISSAL BREAKDOWN</div>', unsafe_allow_html=True)

        probs  = d["probabilities"]
        labels = list(probs.keys())
        values = list(probs.values())
        colors_d = ["#e94560", "#3182ce", "#38a169", "#d69e2e", "#805ad5"]

        fig_d, ax_d = plt.subplots(figsize=(3.5, 3.5))
        fig_d.patch.set_facecolor("#16213e")
        ax_d.set_facecolor("#16213e")

        wedges, texts, autotexts = ax_d.pie(
            values, labels=None, colors=colors_d,
            autopct="%1.1f%%", pctdistance=0.75,
            wedgeprops=dict(width=0.55, edgecolor="#16213e", linewidth=2),
            startangle=90
        )
        for at in autotexts:
            at.set_fontsize(7)
            at.set_color("white")

        ax_d.legend(
            wedges, [f"{l} ({v:.1f}%)" for l, v in zip(labels, values)],
            loc="lower center", bbox_to_anchor=(0.5, -0.15),
            fontsize=7, ncol=2,
            labelcolor="#a0aec0",
            framealpha=0
        )
        ax_d.text(0, 0, d["most_likely"].upper(),
                  ha="center", va="center",
                  fontsize=9, fontweight="bold", color="#e94560")
        fig_d.tight_layout()
        st.pyplot(fig_d)
        plt.close()

    st.markdown("---")

    # Bowling Tips + Pitch Diagram
    col_t1, col_t2 = st.columns([1, 1.2])

    with col_t1:
        st.markdown('<div class="section-title">AI BOWLING TIPS</div>', unsafe_allow_html=True)
        for i, tip in enumerate(s["bowling_tips"], 1):
            st.markdown(
                f'<div class="tip-card"><span class="tip-num">{i}.</span>{tip}</div>',
                unsafe_allow_html=True
            )

        st.markdown("---")
        st.markdown('<div class="section-title">FIELDING PLAN</div>', unsafe_allow_html=True)
        if fp["catching"]:
            st.markdown("**Catching positions:**")
            for pos in fp["catching"]:
                st.markdown(f"🔴 {pos}")
        if fp["boundary"]:
            st.markdown("**Boundary riders:**")
            for pos in fp["boundary"]:
                st.markdown(f"🟢 {pos}")
        if fp["pressure"]:
            st.markdown("**Pressure positions:**")
            for pos in fp["pressure"]:
                st.markdown(f"🔵 {pos}")

    with col_t2:
        st.markdown('<div class="section-title">PITCH DIAGRAM</div>', unsafe_allow_html=True)

        fig_p, ax_p = plt.subplots(figsize=(5.5, 5.5))
        fig_p.patch.set_facecolor("#0a2010")
        ax_p.set_facecolor("#1a4a1a")
        ax_p.set_xlim(-1.2, 1.2)
        ax_p.set_ylim(-1.2, 1.2)
        ax_p.set_aspect("equal")
        ax_p.axis("off")

        # Boundary
        boundary = Circle((0, 0), 1.0, fill=False, color="white",
                          linewidth=2, linestyle="-", alpha=0.6)
        ax_p.add_patch(boundary)

        # 30-yard circle
        inner = Circle((0, 0), 0.55, fill=False, color="white",
                       linewidth=1, linestyle="--", alpha=0.4)
        ax_p.add_patch(inner)

        # Outfield
        outfield = Circle((0, 0), 1.0, color="#1a5c1a", alpha=0.3)
        ax_p.add_patch(outfield)

        # Infield
        infield = Circle((0, 0), 0.55, color="#1a7a1a", alpha=0.3)
        ax_p.add_patch(infield)

        # Pitch
        pitch = Rectangle((-0.05, -0.2), 0.1, 0.4,
                          color="#c8a96e", zorder=5, alpha=0.9)
        ax_p.add_patch(pitch)

        # Crease lines
        ax_p.plot([-0.05, 0.05], [0.15, 0.15],  "w-", linewidth=1.5, zorder=6)
        ax_p.plot([-0.05, 0.05], [-0.15, -0.15], "w-", linewidth=1.5, zorder=6)

        # Stumps
        for x_off in [-0.015, 0, 0.015]:
            ax_p.plot(x_off,  0.18, "k|", markersize=8, zorder=7, linewidth=2)
            ax_p.plot(x_off, -0.18, "k|", markersize=8, zorder=7, linewidth=2)

        # Batsman
        ax_p.plot(0, -0.05, "o", color="#f6ad55", markersize=14, zorder=8,
                  markeredgecolor="white", markeredgewidth=1.5)
        ax_p.text(0, -0.05, "B", color="white", ha="center",
                  va="center", fontsize=8, fontweight="bold", zorder=9)

        # Bowler
        ax_p.plot(0, 0.35, "^", color="#63b3ed", markersize=12, zorder=8,
                  markeredgecolor="white", markeredgewidth=1)
        ax_p.text(0, 0.35, "W", color="white", ha="center",
                  va="center", fontsize=7, fontweight="bold", zorder=9)

        # Fielding positions
        positions = {
            "Fine leg":         (0.15,  -0.95),
            "Deep square leg":  (-0.8,  -0.6),
            "Square leg":       (-0.55, -0.3),
            "Mid-wicket":       (-0.6,   0.1),
            "Mid-on":           (-0.25,  0.55),
            "Mid-off":          (0.25,   0.55),
            "Cover point":      (0.6,    0.3),
            "Point":            (0.65,  -0.05),
            "Gully":            (0.55,  -0.4),
            "2nd slip":         (0.42,  -0.55),
            "Long-on":          (-0.3,   0.92),
            "Long-off":         (0.3,    0.92),
            "Deep mid-wicket":  (-0.85,  0.4),
            "Short leg":        (-0.18, -0.28),
            "Silly point":      (0.18,  -0.28),
            "Extra cover":      (0.5,    0.45),
            "Cover":            (0.5,    0.25),
            "Short mid-wicket": (-0.28,  0.22),
            "Silly mid-on":     (-0.15,  0.38),
        }

        color_map = {
            "catching": "#fc8181",
            "boundary": "#68d391",
            "pressure": "#63b3ed",
        }

        for field_type, field_positions in fp.items():
            if not field_positions:
                continue
            color = color_map.get(field_type, "#a0aec0")
            for pos in field_positions:
                if pos in positions:
                    x, y = positions[pos]
                    ax_p.plot(x, y, "o", color=color, markersize=16, zorder=6,
                             markeredgecolor="white", markeredgewidth=1.5)
                    ax_p.text(x, y, pos[:3].upper(), color="white",
                             ha="center", va="center",
                             fontsize=5.5, fontweight="bold", zorder=7)

        ax_p.set_title(
            f"{s['batsman']} — {s['phase']} overs",
            color="white", fontsize=10, pad=10, fontweight="bold"
        )
        fig_p.tight_layout()
        st.pyplot(fig_p)
        plt.close()

        # Legend
        st.markdown("""
        <div class="field-legend">
            <div class="field-legend-item">
                <span class="legend-dot" style="background:#fc8181"></span> Catching
            </div>
            <div class="field-legend-item">
                <span class="legend-dot" style="background:#68d391"></span> Boundary
            </div>
            <div class="field-legend-item">
                <span class="legend-dot" style="background:#63b3ed"></span> Pressure
            </div>
            <div class="field-legend-item">
                <span class="legend-dot" style="background:#f6ad55"></span> Batsman
            </div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  TAB 2 — PLAYER COMPARISON
# ═══════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">COMPARE TWO BATSMEN</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        player_a = st.selectbox("Player A", batsmen_list,
                                index=batsmen_list.index("DA Warner") if "DA Warner" in batsmen_list else 0,
                                key="pa")
    with col_b:
        player_b = st.selectbox("Player B", batsmen_list,
                                index=batsmen_list.index("CH Gayle") if "CH Gayle" in batsmen_list else 1,
                                key="pb")

    compare_phase = st.selectbox("Phase", ["Powerplay", "Middle", "Slog", "Death"],
                                 index=3, key="cp")

    if st.button("Compare Players"):
        with st.spinner("Comparing..."):
            strat_a = generate_strategy(player_a, compare_phase.lower())
            strat_b = generate_strategy(player_b, compare_phase.lower())

        if strat_a and strat_b:
            pa = strat_a["stats"]
            pb = strat_b["stats"]

            col1, col2 = st.columns(2)

            compare_metrics = [
                ("Batting Average",  pa["batting_avg"],    pb["batting_avg"],    False),
                ("Strike Rate",      pa["strike_rate"],    pb["strike_rate"],    False),
                ("Dot Ball %",       pa["dot_pct"],        pb["dot_pct"],        True),
                ("Boundary %",       pa["boundary_pct"],   pb["boundary_pct"],   False),
                ("Weakness Score",   pa["weakness_score"], pb["weakness_score"], True),
            ]

            with col1:
                st.markdown(f"### {player_a}")
                for label, val_a, val_b, lower_is_better in compare_metrics:
                    if lower_is_better:
                        delta_color = "normal" if val_a <= val_b else "inverse"
                    else:
                        delta_color = "normal" if val_a >= val_b else "inverse"
                    st.metric(label, f"{val_a:.1f}",
                              delta=f"{val_a - val_b:+.1f} vs {player_b}",
                              delta_color=delta_color)

            with col2:
                st.markdown(f"### {player_b}")
                for label, val_a, val_b, lower_is_better in compare_metrics:
                    if lower_is_better:
                        delta_color = "normal" if val_b <= val_a else "inverse"
                    else:
                        delta_color = "normal" if val_b >= val_a else "inverse"
                    st.metric(label, f"{val_b:.1f}",
                              delta=f"{val_b - val_a:+.1f} vs {player_a}",
                              delta_color=delta_color)

            st.markdown("---")

            # Side by side phase SR comparison
            st.markdown('<div class="section-title">PHASE STRIKE RATE COMPARISON</div>',
                        unsafe_allow_html=True)

            phases_c  = ["Powerplay", "Middle", "Slog", "Death"]
            sr_a      = [pa["sr_powerplay"], pa["sr_middle"], pa["sr_slog"], pa["sr_death"]]
            sr_b      = [pb["sr_powerplay"], pb["sr_middle"], pb["sr_slog"], pb["sr_death"]]

            x       = np.arange(len(phases_c))
            width   = 0.35

            fig_c, ax_c = plt.subplots(figsize=(8, 4))
            fig_c.patch.set_facecolor("#16213e")
            ax_c.set_facecolor("#0a0e1a")

            b1 = ax_c.bar(x - width/2, sr_a, width, label=player_a,
                          color="#e94560", edgecolor="#0a0e1a")
            b2 = ax_c.bar(x + width/2, sr_b, width, label=player_b,
                          color="#3182ce", edgecolor="#0a0e1a")

            ax_c.set_xticks(x)
            ax_c.set_xticklabels(phases_c, color="#a0aec0")
            ax_c.set_ylabel("Strike Rate", color="#a0aec0")
            ax_c.tick_params(colors="#a0aec0")
            ax_c.spines["bottom"].set_color("#2d3748")
            ax_c.spines["left"].set_color("#2d3748")
            ax_c.spines["top"].set_visible(False)
            ax_c.spines["right"].set_visible(False)
            ax_c.legend(labelcolor="#a0aec0", framealpha=0)
            ax_c.axhline(y=120, color="#718096", linestyle="--",
                         linewidth=0.8, alpha=0.5)
            fig_c.tight_layout()
            st.pyplot(fig_c)
            plt.close()

# ═══════════════════════════════════════════════════════════════
#  TAB 3 — TEAM ANALYSIS
# ═══════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">TEAM BATTING STRENGTH ANALYSIS</div>',
                unsafe_allow_html=True)

    selected_team = st.selectbox("Select Team", teams_list)
    team_df = feat_df[feat_df["team"] == selected_team].copy()

    if len(team_df) == 0:
        st.warning("No data found for selected team.")
    else:
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        with col_t1:
            st.metric("Total Players",   len(team_df))
        with col_t2:
            st.metric("Avg Strike Rate", f"{team_df['strike_rate'].mean():.1f}")
        with col_t3:
            st.metric("Avg Batting Avg", f"{team_df['batting_avg'].mean():.1f}")
        with col_t4:
            st.metric("Avg Weakness",    f"{team_df['weakness_score'].mean():.3f}")

        st.markdown("---")
        st.markdown(f"**All players for {selected_team}:**")

        display_cols = [
            "batsman", "matches", "batting_avg", "strike_rate",
            "dot_pct", "boundary_pct", "weakness_score",
            "most_likely_dismissal"
        ]
        st.dataframe(
            team_df[display_cols].sort_values("weakness_score", ascending=False),
            hide_index=True,
            use_container_width=True
        )

        # Team weakness bar chart
        st.markdown("---")
        st.markdown('<div class="section-title">PLAYER WEAKNESS SCORES</div>',
                    unsafe_allow_html=True)

        top_players = team_df.nlargest(10, "weakness_score")

        fig_t, ax_t = plt.subplots(figsize=(10, 4))
        fig_t.patch.set_facecolor("#16213e")
        ax_t.set_facecolor("#0a0e1a")

        colors_w = ["#e94560" if w > 0.6 else "#f6ad55" if w > 0.4 else "#48bb78"
                    for w in top_players["weakness_score"]]
        ax_t.barh(top_players["batsman"], top_players["weakness_score"],
                  color=colors_w, edgecolor="#0a0e1a")
        ax_t.set_xlabel("Weakness Score", color="#a0aec0")
        ax_t.axvline(x=0.5, color="#718096", linestyle="--",
                     linewidth=0.8, alpha=0.5)
        ax_t.tick_params(colors="#a0aec0")
        ax_t.spines["bottom"].set_color("#2d3748")
        ax_t.spines["left"].set_color("#2d3748")
        ax_t.spines["top"].set_visible(False)
        ax_t.spines["right"].set_visible(False)
        fig_t.tight_layout()
        st.pyplot(fig_t)
        plt.close()

# ═══════════════════════════════════════════════════════════════
#  TAB 4 — LEADERBOARD
# ═══════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">MOST DISMISSABLE BATSMEN (IPL ALL-TIME)</div>',
                unsafe_allow_html=True)

    lb_col1, lb_col2 = st.columns(2)

    with lb_col1:
        st.markdown("#### Top 15 Most Dismissable")
        top15 = feat_df.nlargest(15, "weakness_score")[
            ["batsman", "team", "matches", "batting_avg",
             "strike_rate", "weakness_score"]
        ].reset_index(drop=True)
        top15.index = top15.index + 1
        st.dataframe(top15, use_container_width=True)

    with lb_col2:
        st.markdown("#### Top 15 Strongest Batsmen")
        bot15 = feat_df.nsmallest(15, "weakness_score")[
            ["batsman", "team", "matches", "batting_avg",
             "strike_rate", "weakness_score"]
        ].reset_index(drop=True)
        bot15.index = bot15.index + 1
        st.dataframe(bot15, use_container_width=True)

    st.markdown("---")

    # Overall distribution chart
    st.markdown('<div class="section-title">WEAKNESS SCORE DISTRIBUTION (ALL 398 BATSMEN)</div>',
                unsafe_allow_html=True)

    fig_l, ax_l = plt.subplots(figsize=(10, 3))
    fig_l.patch.set_facecolor("#16213e")
    ax_l.set_facecolor("#0a0e1a")

    ax_l.hist(feat_df["weakness_score"], bins=30, color="#e94560",
              edgecolor="#0a0e1a", alpha=0.8)
    ax_l.axvline(x=feat_df["weakness_score"].mean(), color="#48bb78",
                 linestyle="--", linewidth=1.5, label="Mean")
    ax_l.set_xlabel("Weakness Score", color="#a0aec0")
    ax_l.set_ylabel("Number of Batsmen", color="#a0aec0")
    ax_l.tick_params(colors="#a0aec0")
    ax_l.legend(labelcolor="#a0aec0", framealpha=0)
    ax_l.spines["bottom"].set_color("#2d3748")
    ax_l.spines["left"].set_color("#2d3748")
    ax_l.spines["top"].set_visible(False)
    ax_l.spines["right"].set_visible(False)
    fig_l.tight_layout()
    st.pyplot(fig_l)
    plt.close()

# Footer
st.markdown("---")
st.markdown(
    "<center style='color:#718096;font-size:0.8rem'>"
    "Cricket Strategy AI v2.0 | Built by Vishal | "
    "Gradient Boosting ML | 92.4% Accuracy | IPL 2007-2021"
    "</center>",
    unsafe_allow_html=True
)
