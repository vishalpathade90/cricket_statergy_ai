"""
Cricket Strategy AI - LLM Engine (Claude AI)
Industry Level | Version 1.0
Author: Vishal

Uses Anthropic Claude to generate:
- Natural language strategy reports
- Match commentary
- Pre-match briefings
- Q&A chatbot for player analysis
"""

import os
import anthropic
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv(r"C:\Users\vishal\Desktop\cricket_statergy_ai\.env")

# Initialize Anthropic client
client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

SYSTEM_PROMPT = """You are an elite cricket strategy analyst with 20 years of experience
in IPL coaching. You analyze ball-by-ball data and provide precise, actionable bowling
strategies for professional cricket teams.

Your analysis style:
- Speak like a professional cricket coach, not an academic
- Use cricket terminology naturally (corridor of uncertainty, length ball, yorker etc.)
- Be specific with field placements and bowling variations
- Keep responses concise and tactical
- Focus on dismissal patterns and phase-specific weaknesses
- Always back recommendations with data from the stats provided"""

# ─────────────────────────────────────────────────────────────
#  GENERATE LLM STRATEGY NARRATIVE
# ─────────────────────────────────────────────────────────────
async def generate_llm_strategy(strategy: dict) -> str:
    """
    Takes ML strategy output and generates a natural language
    coaching brief using Claude AI.
    """
    s = strategy
    p = s["stats"]
    d = s["dismissal"]

    prompt = f"""
Analyze this IPL batsman and provide a detailed bowling strategy brief:

BATSMAN: {s['batsman']} ({s['team']})
PHASE: {s['phase']} overs

CAREER STATS:
- Matches: {p['matches']}
- Batting average: {p['batting_avg']}
- Strike rate: {p['strike_rate']}
- Dot ball %: {p['dot_pct']}%
- Boundary %: {p['boundary_pct']}%
- Weakness score: {p['weakness_score']} / 1.0

PHASE-WISE STRIKE RATE:
- Powerplay: {p['sr_powerplay']}
- Middle: {p['sr_middle']}
- Slog: {p['sr_slog']}
- Death: {p['sr_death']}

DISMISSAL ANALYSIS:
- Most likely: {d['most_likely']} ({d['probabilities'].get(d['most_likely'], 0):.1f}%)
- Caught: {d['probabilities'].get('caught', 0):.1f}%
- Bowled: {d['probabilities'].get('bowled', 0):.1f}%
- LBW: {d['probabilities'].get('lbw', 0):.1f}%
- Run out: {d['probabilities'].get('run out', 0):.1f}%
- Stumped: {d['probabilities'].get('stumped', 0):.1f}%

ML BOWLING TIPS: {', '.join(s['bowling_tips'])}
FIELD PLAN: Catching: {s['fielding_plan']['catching']}, Boundary: {s['fielding_plan']['boundary']}

Write a professional pre-match bowling strategy brief for {s['batsman']} in the {s['phase']} overs.
Include:
1. Key weakness to exploit
2. Exact bowling plan (line, length, pace, variation)
3. Field setting with reasoning
4. What to avoid bowling to this batsman
Keep it under 200 words. Write as if briefing the bowling attack before a match.
"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


# ─────────────────────────────────────────────────────────────
#  CHAT WITH AI ABOUT A PLAYER
# ─────────────────────────────────────────────────────────────
async def chat_with_ai(question: str, strategy: dict) -> str:
    """
    Answer any cricket strategy question about a specific batsman.
    """
    s = strategy
    p = s["stats"]
    d = s["dismissal"]

    context = f"""
Player context for {s['batsman']} ({s['team']}):
- Batting avg: {p['batting_avg']}, SR: {p['strike_rate']}
- Dot %: {p['dot_pct']}%, Boundary %: {p['boundary_pct']}%
- Weakness: {p['weakness_score']}/1.0
- Phase SR - PP:{p['sr_powerplay']} Mid:{p['sr_middle']} Slog:{p['sr_slog']} Death:{p['sr_death']}
- Most likely dismissal: {d['most_likely']} ({d['probabilities'].get(d['most_likely'], 0):.1f}%)
- Bowling tips: {', '.join(s['bowling_tips'])}
"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"{context}\n\nQuestion: {question}"
            }
        ]
    )
    return message.content[0].text


# ─────────────────────────────────────────────────────────────
#  GENERATE PRE-MATCH BRIEFING
# ─────────────────────────────────────────────────────────────
async def generate_match_briefing(
    batting_team: str,
    bowling_team: str,
    strategies: list
) -> str:
    """
    Generate a complete pre-match bowling strategy briefing
    for the entire batting lineup.
    """
    players_summary = ""
    for s in strategies:
        p = s["stats"]
        d = s["dismissal"]
        players_summary += f"""
- {s['batsman']}: Avg {p['batting_avg']}, SR {p['strike_rate']},
  Weakness {p['weakness_score']}/1.0, Most likely out: {d['most_likely']}
  Key tip: {s['bowling_tips'][0] if s['bowling_tips'] else 'Bowl tight'}
"""

    prompt = f"""
PRE-MATCH BRIEFING REQUEST:
Bowling team: {bowling_team}
Batting team: {batting_team}

TOP BATTING THREATS:
{players_summary}

Generate a concise pre-match bowling strategy briefing for {bowling_team}
facing {batting_team}. Include:
1. Overall batting team assessment
2. Priority targets (who to get out first)
3. Phase-by-phase bowling plan
4. Key warnings (dangerous batsmen to be careful with)
5. Overall field strategy

Keep under 300 words. Write like a head coach briefing the team.
"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


# ─────────────────────────────────────────────────────────────
#  GENERATE LIVE COMMENTARY
# ─────────────────────────────────────────────────────────────
async def generate_live_commentary(
    batsman: str,
    over: int,
    runs_scored: int,
    balls_faced: int,
    strategy: dict
) -> str:
    """
    Generate live match commentary for a batsman currently batting.
    """
    phase = "Powerplay" if over <= 5 else "Middle" if over <= 14 else "Death"
    run_rate = round(runs_scored / balls_faced * 6, 1) if balls_faced > 0 else 0

    prompt = f"""
LIVE MATCH SITUATION:
Batsman: {batsman}
Over: {over}, Phase: {phase}
Current: {runs_scored} runs off {balls_faced} balls (RR: {run_rate})
Weakness score: {strategy['stats']['weakness_score']}/1.0
Most likely dismissal: {strategy['dismissal']['most_likely']}

Give a 2-3 sentence live commentary update + immediate bowling recommendation
for the next 3 balls. Be dramatic but tactical.
"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=200,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


# ─────────────────────────────────────────────────────────────
#  TEST THE LLM ENGINE
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import asyncio
    import sys
    sys.path.append(r"C:\Users\vishal\Desktop\cricket_statergy_ai")
    from statergy_ingine import generate_strategy

    async def test():
        print("Testing LLM Engine...")
        print("=" * 60)

        # Test 1: Strategy narrative
        strategy = generate_strategy("DA Warner", "death")
        if strategy:
            print("Test 1: Generating strategy narrative for DA Warner...")
            result = await generate_llm_strategy(strategy)
            print(result)
            print("=" * 60)

        # Test 2: Chat
        if strategy:
            print("Test 2: Chat - How to bowl to Warner in death overs?")
            answer = await chat_with_ai(
                "What specific yorker variations should I use against Warner in death overs?",
                strategy
            )
            print(answer)
            print("=" * 60)

        print("LLM Engine test complete!")

    asyncio.run(test())
