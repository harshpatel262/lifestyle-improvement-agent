"""FastAPI app for the AI lifestyle coach prototype.

Run with:  uvicorn app.main:app --reload
Then open  http://127.0.0.1:8000
"""

from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import coach, database

app = FastAPI(title="Steady — AI Lifestyle Coach")

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class ProfileIn(BaseModel):
    name: str = Field(min_length=1)
    sleep_target_hours: float = Field(default=7.5, ge=4, le=12)
    bad_habit: str = Field(min_length=1)
    replacement_hobby: str = Field(min_length=1)
    long_term_goal: str = Field(pattern="^(lose_weight|learn_skill|none)$")
    goal_detail: str = ""


class CheckinIn(BaseModel):
    sleep_hours: float = Field(ge=0, le=24)
    habit_replaced: bool | None = None
    goal_action_done: bool | None = None
    note: str = ""


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/state")
def state():
    conn = database.get_conn()
    try:
        profile = database.get_profile(conn)
        if profile is None:
            return {"onboarded": False}
        checkins = database.get_checkins(conn)
        phase = coach.determine_phase(checkins, profile["sleep_target_hours"])
        return {
            "onboarded": True,
            "profile": profile,
            "phase": phase,
            "phase_label": coach.PHASE_LABELS[phase],
            "streaks": coach.streaks(checkins, profile["sleep_target_hours"]),
            "checkins": checkins,
            "today": date.today().isoformat(),
        }
    finally:
        conn.close()


@app.post("/api/profile")
def create_profile(p: ProfileIn):
    conn = database.get_conn()
    try:
        database.save_profile(conn, p.model_dump())
        return {"ok": True}
    finally:
        conn.close()


@app.post("/api/checkin")
def checkin(c: CheckinIn):
    conn = database.get_conn()
    try:
        profile = database.get_profile(conn)
        if profile is None:
            raise HTTPException(400, "Complete onboarding first")

        record = {
            "day": date.today().isoformat(),
            "sleep_hours": c.sleep_hours,
            "habit_replaced": None if c.habit_replaced is None else int(c.habit_replaced),
            "goal_action_done": None if c.goal_action_done is None else int(c.goal_action_done),
            "note": c.note.strip(),
            "coach_message": "",
            "daily_action": "",
        }
        database.save_checkin(conn, record)

        history = database.get_checkins(conn)  # newest-first, includes today
        reply = coach.coach_response(profile, record, history)

        record["coach_message"] = reply["coach_message"]
        record["daily_action"] = reply["daily_action"]
        database.save_checkin(conn, record)
        return reply
    finally:
        conn.close()
