# Brainstorm — AI Lifestyle Coach

**Working name:** Steady (small steps, sustainable change)

**Target audience:** Middle-class professionals, recently out of college, with a good job.
They have income and ambition but poor routines: late nights, doomscrolling, no exercise,
"I'll start Monday" energy. They don't need information — they need sequencing,
accountability, and tiny daily wins.

## Core philosophy

1. **One thing at a time.** The agent never asks the user to fix everything at once.
   It works in phases, and each phase has exactly one focus.
2. **Sleep first, always.** Sleep is the keystone habit — willpower, mood, appetite, and
   focus all degrade without it. Until sleep is stable, nothing else is coached.
3. **Small daily actions.** Every day the agent gives one small, concrete action
   ("tonight, put your phone outside the bedroom at 11pm") — never a life overhaul.
4. **Slow and sustainable.** For weight loss and skill-building, the agent explicitly
   optimizes for consistency over speed (e.g., ~0.5 kg/week max, 20 minutes of practice,
   not 3 hours).
5. **Self-reported data only.** No wearables or health-API integration in v1. The user
   tells the agent how many hours they slept; the agent tracks what the user reports.
   This keeps the prototype simple and keeps the user actively engaged.

## The three phases

| Phase | Focus | Graduation criteria |
|---|---|---|
| 1. Sleep | Hit a target sleep duration (default 7.5h) at a consistent time | Hit target on 5 of the last 7 days |
| 2. Habit swap | Replace one bad habit (doomscrolling, late gaming) with a chosen hobby: gym, a sport, chess, a community/club | Did the replacement on 10 of the last 14 days |
| 3. Goal | The user's long-term goal: lose weight or learn a skill | Ongoing — coached indefinitely with weekly micro-milestones |

Earlier phases are never abandoned — after graduating from sleep, the user still logs
sleep, and the agent gently intervenes if it slips (regression drops them back a phase).

## Daily loop

1. User opens the app and checks in: hours slept, did the habit swap happen (phase 2+),
   did the goal action happen (phase 3), optional free-text note ("stressful day").
2. The agent responds with a short coaching message: acknowledge → one insight from the
   data ("your sleep is 40 min better than last week") → **today's one small action**.
3. Streaks and phase progress are visible but framed gently — a missed day is "data,
   not failure."

## Why an LLM at all?

The tracking is deterministic; the *coaching voice* is where Claude adds value:
- Reads the user's free-text notes and responds like a human coach would.
- Personalizes the daily action to context ("you said work is crazy this week, so
  tonight's action is just: lights out by 12, no other rules").
- Adjusts tone: celebratory on streaks, zero-guilt on lapses.

The prototype calls the Claude API (`claude-opus-4-8`) when `ANTHROPIC_API_KEY` is set,
and falls back to rule-based template messages otherwise, so the demo always works.

## Later ideas (not in prototype)

- Weekly review: agent writes a Sunday summary and sets the next week's micro-milestone.
- Push/notification nudges at the user's chosen wind-down time.
- Optional health-data import (Apple Health / Google Fit) to pre-fill sleep hours.
- Community layer: match users into small accountability pods.
- Monetization: free tracker, paid coach voice + weekly reviews (this audience can pay).
