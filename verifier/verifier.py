"""Deterministic verifier: a claim reaches the therapist only if the cited
evidence supports it. No LLM is involved in this file.

Evidence levels (occupational therapy):
  1 movement observed        2 prescribed exercise performed
  3 activity done independently (needs report or therapist observation)
  4 functional progress (therapist only, never generated)
"""
SOURCE_MAX_LEVEL = {"camera": 2, "phone": 2, "watch": 2, "report": 3, "therapist": 4}
SYSTEM_MAX_LEVEL = 3  # level 4 is never written by the system


def _by_id(events):
    return {e["id"]: e for e in events}


def check_claim(claim, events, plan):
    """Return (ok, reasons). claim fields:
    kind: 'reps' | 'sessions_done' | 'not_done' | 'not_observed' | 'independent' | 'progress' | 'conflict'
    level: int, value: optional number, session: optional id, evidence: list of event ids
    """
    ev = _by_id(events)
    reasons = []
    cited = [ev[i] for i in claim.get("evidence", []) if i in ev]
    missing = [i for i in claim.get("evidence", []) if i not in ev]
    kind, level = claim["kind"], claim["level"]

    if missing:
        reasons.append("cites events that do not exist: %s" % missing)
    if level > SYSTEM_MAX_LEVEL:
        reasons.append("level %d is reserved for the therapist" % level)

    if kind in ("reps", "sessions_done", "independent", "conflict") and not cited:
        reasons.append("no evidence cited")
    if cited:
        top = max(SOURCE_MAX_LEVEL[e["source"]] for e in cited)
        if level > top:
            reasons.append("level %d above what the cited sources support (max %d)" % (level, top))

    if kind == "reps":
        sensor = [e for e in cited if e["source"] in ("camera", "phone", "watch")]
        total = sum(e.get("reps", 0) for e in sensor)
        if not sensor:
            reasons.append("repetition count needs sensor evidence")
        elif claim.get("value") != total:
            reasons.append("claims %s repetitions, cited sensor events sum to %d" % (claim.get("value"), total))

    if kind == "sessions_done":
        sessions = {e["session"] for e in cited if e["source"] in ("camera", "phone", "watch")}
        if claim.get("value") != len(sessions):
            reasons.append("claims %s sessions, cited sensor evidence covers %d" % (claim.get("value"), len(sessions)))

    if kind == "not_done":
        reasons.append("absence of data cannot support 'did not do'; use 'not observed'")

    if kind == "not_observed":
        s = claim.get("session")
        if any(e["session"] == s for e in events):
            reasons.append("session %s has events, so it was observed" % s)

    if kind == "independent":
        if not any(e["source"] in ("report", "therapist") for e in cited):
            reasons.append("independence needs a patient report or therapist observation, sensors only show movement")

    if kind == "progress":
        reasons.append("functional progress is the therapist's judgement")

    # A claim that a session was completed must not hide a conflict with the patient's report.
    if kind in ("reps", "sessions_done"):
        for s in {e["session"] for e in cited}:
            if conflicted(s, events, plan) and not claim.get("flags_conflict"):
                reasons.append("session %s: sensor and patient report disagree, claim must flag it" % s)

    if kind == "conflict":
        s = claim.get("session")
        if not conflicted(s, events, plan):
            reasons.append("session %s has no conflict" % s)

    return (not reasons, reasons)


def conflicted(session, events, plan):
    sens = [e for e in events if e["session"] == session and e["source"] in ("camera", "phone", "watch")]
    rep = [e for e in events if e["session"] == session and e["source"] == "report"]
    if not sens or not rep:
        return False
    target = plan["reps_per_session"]
    sensor_done = sum(e.get("reps", 0) for e in sens) >= target
    report_done = rep[-1]["answer"] == "done"
    return sensor_done != report_done


def verify(draft, events, plan):
    out = []
    for c in draft:
        ok, why = check_claim(c, events, plan)
        out.append({"claim": c, "ok": ok, "reasons": why})
    return out


def render(results):
    lines = []
    for r in results:
        if r["ok"]:
            c = r["claim"]
            lines.append("- %s  [nível %d; evidência: %s]" % (c["text"], c["level"], ", ".join(c.get("evidence", [])) or "nenhuma"))
    return "\n".join(lines)
