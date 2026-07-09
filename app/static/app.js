const $ = (id) => document.getElementById(id);

async function api(path, opts) {
  const res = await fetch(path, opts);
  if (!res.ok) throw new Error((await res.json()).detail || res.statusText);
  return res.json();
}

async function loadState() {
  const state = await api("/api/state");
  if (!state.onboarded) {
    $("onboarding").classList.remove("hidden");
    $("dashboard").classList.add("hidden");
    return;
  }
  $("onboarding").classList.add("hidden");
  $("dashboard").classList.remove("hidden");
  renderDashboard(state);
}

function renderDashboard(state) {
  const { profile, phase, phase_label, streaks, checkins, today } = state;

  $("phase-label").textContent = phase_label;
  $("streaks").textContent =
    `Streaks — sleep: ${streaks.sleep}d · habit: ${streaks.habit}d · goal: ${streaks.goal}d`;

  // Phase-appropriate check-in questions
  const habitRow = $("habit-row");
  const goalRow = $("goal-row");
  habitRow.classList.toggle("hidden", phase === "sleep");
  $("habit-question").textContent =
    `Did you swap ${profile.bad_habit} for ${profile.replacement_hobby} today?`;
  goalRow.classList.toggle("hidden", phase !== "goal" || profile.long_term_goal === "none");
  $("goal-question").textContent =
    profile.long_term_goal === "lose_weight"
      ? "Did you do today's small weight-loss action?"
      : `Did you practice ${profile.goal_detail || "your skill"} today?`;

  // History + today's coach message if already checked in
  const list = $("history");
  list.innerHTML = "";
  for (const c of checkins) {
    const li = document.createElement("li");
    const bits = [`${c.sleep_hours}h sleep`];
    if (c.habit_replaced !== null) bits.push(c.habit_replaced ? "habit ✓" : "habit ✗");
    if (c.goal_action_done !== null) bits.push(c.goal_action_done ? "goal ✓" : "goal ✗");
    li.innerHTML = `<span>${c.day}</span><span class="meta">${bits.join(" · ")}</span>`;
    list.appendChild(li);
  }
  const todays = checkins.find((c) => c.day === today);
  if (todays && todays.coach_message) {
    showCoach({ coach_message: todays.coach_message, daily_action: todays.daily_action });
  }
}

function showCoach(reply) {
  $("coach-card").classList.remove("hidden");
  $("coach-message").textContent = reply.coach_message;
  $("daily-action").textContent = reply.daily_action;
}

$("onboarding-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = new FormData(e.target);
  await api("/api/profile", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: f.get("name"),
      sleep_target_hours: parseFloat(f.get("sleep_target_hours")),
      bad_habit: f.get("bad_habit"),
      replacement_hobby: f.get("replacement_hobby"),
      long_term_goal: f.get("long_term_goal"),
      goal_detail: f.get("goal_detail") || "",
    }),
  });
  loadState();
});

$("checkin-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const btn = $("checkin-btn");
  btn.disabled = true;
  btn.textContent = "Coach is thinking…";
  try {
    const f = new FormData(e.target);
    const habitVisible = !$("habit-row").classList.contains("hidden");
    const goalVisible = !$("goal-row").classList.contains("hidden");
    const reply = await api("/api/checkin", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sleep_hours: parseFloat(f.get("sleep_hours")),
        habit_replaced: habitVisible ? f.get("habit_replaced") === "on" : null,
        goal_action_done: goalVisible ? f.get("goal_action_done") === "on" : null,
        note: f.get("note") || "",
      }),
    });
    showCoach(reply);
    loadState();
  } finally {
    btn.disabled = false;
    btn.textContent = "Check in";
  }
});

$("goal-select").addEventListener("change", (e) => {
  $("goal-detail-row").classList.toggle("hidden", e.target.value === "none");
});

loadState();
