"""SQLite persistence for the lifestyle coach prototype.

Single-user prototype: one profile row, many check-in rows.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "coach.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS profile (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    name TEXT NOT NULL,
    sleep_target_hours REAL NOT NULL DEFAULT 7.5,
    bad_habit TEXT NOT NULL,
    replacement_hobby TEXT NOT NULL,
    long_term_goal TEXT NOT NULL,          -- 'lose_weight' | 'learn_skill' | 'none'
    goal_detail TEXT NOT NULL DEFAULT '',  -- e.g. 'guitar', 'lose 8 kg'
    created_at TEXT NOT NULL DEFAULT (date('now'))
);

CREATE TABLE IF NOT EXISTS checkins (
    day TEXT PRIMARY KEY,                  -- ISO date, one check-in per day
    sleep_hours REAL NOT NULL,
    habit_replaced INTEGER,                -- NULL before phase 2, else 0/1
    goal_action_done INTEGER,              -- NULL before phase 3, else 0/1
    note TEXT NOT NULL DEFAULT '',
    coach_message TEXT NOT NULL DEFAULT '',
    daily_action TEXT NOT NULL DEFAULT ''
);
"""


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def get_profile(conn: sqlite3.Connection) -> dict | None:
    row = conn.execute("SELECT * FROM profile WHERE id = 1").fetchone()
    return dict(row) if row else None


def save_profile(conn: sqlite3.Connection, p: dict) -> None:
    conn.execute(
        """INSERT INTO profile (id, name, sleep_target_hours, bad_habit,
                                replacement_hobby, long_term_goal, goal_detail)
           VALUES (1, :name, :sleep_target_hours, :bad_habit,
                   :replacement_hobby, :long_term_goal, :goal_detail)
           ON CONFLICT(id) DO UPDATE SET
               name = :name,
               sleep_target_hours = :sleep_target_hours,
               bad_habit = :bad_habit,
               replacement_hobby = :replacement_hobby,
               long_term_goal = :long_term_goal,
               goal_detail = :goal_detail""",
        p,
    )
    conn.commit()


def get_checkins(conn: sqlite3.Connection, limit: int = 30) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM checkins ORDER BY day DESC LIMIT ?", (limit,)
    ).fetchall()
    return [dict(r) for r in rows]


def save_checkin(conn: sqlite3.Connection, c: dict) -> None:
    conn.execute(
        """INSERT INTO checkins (day, sleep_hours, habit_replaced,
                                 goal_action_done, note, coach_message, daily_action)
           VALUES (:day, :sleep_hours, :habit_replaced,
                   :goal_action_done, :note, :coach_message, :daily_action)
           ON CONFLICT(day) DO UPDATE SET
               sleep_hours = :sleep_hours,
               habit_replaced = :habit_replaced,
               goal_action_done = :goal_action_done,
               note = :note,
               coach_message = :coach_message,
               daily_action = :daily_action""",
        c,
    )
    conn.commit()
