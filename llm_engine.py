"""
Cricket Strategy AI - LLM Engine (Groq - Free)
Industry Level | Version 2.0
Author: Vishal

Uses Groq (free) with LLaMA3 to generate:
- Natural language strategy reports
- Match commentary
- Pre-match briefings
- Q&A chatbot for player analysis
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv(r"C:\Users\vishal\Desktop\cricket_statergy_ai\.env")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are an elite cricket strategy analyst with 20 years of IPL coaching experience.
You analyze ball-by-ball data and provide precise, actionable bowling strategies.
Speak like a professional cricket coach. Use cricket terminology naturally.
Be specific with field placements. Keep responses concise and tactical.
Always back recommendations with the stats provided."""

# ─────────────────────────────────────────────────────────────
#  GENERATE LLM STRATEGY NARRATIVE
# ─────────────────────────────────────────────────────────────
async def generate_llm_strategy(strategy: dict) -> str:
    s = strategy
    p = s["stats"]
    d = s["dismissal"]

    prompt = f"""
Analyze this IPL batsman and provide a bowling strategy brief:

BATSMAN: {s['batsman']} ({s['team']})
PHASE: {s['phase']} overs
Batting avg: {p['batting_avg']}, Strike rate: {p['strike_rate']}
Dot ball %: {p['dot_pct']}%, Boundary %: {p['boundary_pct']}%
Weakness score: {p['weakness_score']} / 1.0
Phase SR - PP:{p['sr_powerplay']} Mid:{p['sr_middle']} Slog:{p['sr_slog']} Death:{p['sr_death']}
Most likely dismissal: {d['most_likely']} ({d['probabilities'].get(d['most_likely'], 0):.1f}%)
Bowling tips: {', '.join(s['bowling_tips'])}

Write a 150-word professional pre-match bowling brief for {s['batsman']} in {s['phase']} overs.
Include: key weakness, exact bowling plan, field setting, what to avoid.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt}
        ],
        max_tokens=400,
        temperature=0.7,
    )
    return response.choices[0].message.content


# ─────────────────────────────────────────────────────────────
#  CHAT WITH AI
# ─────────────────────────────────────────────────────────────
async def chat_with_ai(question: str, strategy: dict) -> str:
    s = strategy
    p = s["stats"]
    d = s["dismissal"]

    context = f"""
Player: {s['batsman']} ({s['team']})
Batting avg: {p['batting_avg']}, SR: {p['strike_rate']}
Weakness: {p['weakness_score']}/1.0
Most likely dismissal: {d['most_likely']}
Bowling tips: {', '.join(s['bowling_tips'])}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": f"{context}\n\nQuestion: {question}"}
        ],
        max_tokens=300,
        temperature=0.7,
    )
    return response.choices[0].message.content


# ─────────────────────────────────────────────────────────────
#  GENERATE MATCH BRIEFING
# ─────────────────────────────────────────────────────────────
async def generate_match_briefing(batting_team: str,
                                   bowling_team: str,
                                   strategies: list) -> str:
    players_summary = ""
    for s in strategies:
        p = s["stats"]
        d = s["dismissal"]
        players_summary += f"- {s['batsman']}: Avg {p['batting_avg']}, SR {p['strike_rate']}, Most likely out: {d['most_likely']}\n"

    prompt = f"""
Bowling team: {bowling_team} vs Batting team: {batting_team}
Top batting threats:
{players_summary}
Write a 200-word pre-match bowling strategy briefing.
Include: overall assessment, priority targets, phase-by-phase plan.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7,
    )
    return response.choices[0].message.content


# ─────────────────────────────────────────────────────────────
#  TEST
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import asyncio
    import sys
    sys.path.append(r"C:\Users\vishal\Desktop\cricket_statergy_ai")
    from statergy_ingine import generate_strategy

    async def test():
        print("Testing Groq LLM Engine...")
        print("=" * 60)
        strategy = generate_strategy("DA Warner", "death")
        if strategy:
            print("Generating strategy for DA Warner - Death overs...")
            result = await generate_llm_strategy(strategy)
            print(result)
            print("=" * 60)
            print("Chat test:")
            answer = await chat_with_ai(
                "What yorker variations should I use against Warner?",
                strategy
            )
            print(answer)
        print("Groq LLM test complete!")

    asyncio.run(test())
