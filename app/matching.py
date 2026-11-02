"""Deterministic, explainable study-partner recommendations using fictional profiles."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Student:
    alias: str
    courses: frozenset[str]
    slots: frozenset[str]
    mode: str
    goals: frozenset[str]

def match_score(seeker: Student, candidate: Student) -> dict | None:
    """Require a shared class and meeting time; rank on legible signals."""
    common_courses = seeker.courses & candidate.courses
    common_slots = seeker.slots & candidate.slots
    if not common_courses or not common_slots:
        return None
    if seeker.mode != candidate.mode and "flexible" not in (seeker.mode, candidate.mode):
        return None

    course_points = min(2, len(common_courses)) * 25
    time_points = min(3, len(common_slots)) * 10
    mode_points = 10 if seeker.mode == candidate.mode else 5
    goals_points = min(2, len(seeker.goals & candidate.goals)) * 5
    score = course_points + time_points + mode_points + goals_points
    return {
        "alias": candidate.alias,
        "score": score,
        "shared_courses": sorted(common_courses),
        "shared_slots": sorted(common_slots),
        "shared_goals": sorted(seeker.goals & candidate.goals),
        "mode": candidate.mode,
        "why": f"{len(common_courses)} shared course(s), {len(common_slots)} overlapping time slot(s)",
    }

def recommend(seeker: Student, people: list[Student], limit: int = 5) -> list[dict]:
    scored = []
    for person in people:
        if person.alias.lower() == seeker.alias.lower():
            continue
        match = match_score(seeker, person)
        if match:
            scored.append(match)
    return sorted(scored, key=lambda r: (-r["score"], r["alias"].casefold()))[:limit]

def form_study_group(seeker: Student, people: list[Student], max_members: int = 4) -> dict:
    """Greedy group creation that preserves at least one mutual time slot."""
    if not (2 <= max_members <= 6):
        raise ValueError("Group size must be between 2 and 6")
    slots = set(seeker.slots)
    members = [seeker.alias]
    for result in recommend(seeker, people, limit=len(people)):
        if len(members) >= max_members:
            break
        intersection = slots & set(result["shared_slots"])
        if intersection:
            members.append(result["alias"])
            slots = intersection
    return {"members": members, "common_slots": sorted(slots), "size": len(members)}
