"""Small, privacy-conscious FastAPI demo with invented sample students."""
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from .matching import Student, form_study_group, recommend

app = FastAPI(title="Study Group Matcher — Portfolio Prototype", version="0.1.0")
STATIC = Path(__file__).resolve().parent.parent / "static"
COURSES = ["ECE 406", "ECE 402", "M 408C", "PHY 303K", "CS 312", "M 427L"]
SLOTS = ["Mon 5pm", "Tue 6pm", "Wed 5pm", "Thu 7pm", "Fri 4pm", "Sat 1pm"]
GOALS = ["exam review", "homework", "concepts", "practice problems"]

# All names and profiles are invented demo data.
DEMO_PEOPLE = [
    Student("Alex", frozenset(["ECE 406", "M 408C"]), frozenset(["Mon 5pm", "Wed 5pm", "Fri 4pm"]), "in-person", frozenset(["practice problems", "exam review"])),
    Student("Casey", frozenset(["ECE 406", "ECE 402"]), frozenset(["Mon 5pm", "Tue 6pm"]), "flexible", frozenset(["homework", "concepts"])),
    Student("Morgan", frozenset(["M 408C", "PHY 303K"]), frozenset(["Thu 7pm", "Sat 1pm"]), "online", frozenset(["practice problems", "concepts"])),
    Student("Riley", frozenset(["ECE 406", "M 408C"]), frozenset(["Mon 5pm", "Fri 4pm"]), "in-person", frozenset(["exam review", "homework"])),
    Student("Taylor", frozenset(["CS 312", "ECE 406"]), frozenset(["Tue 6pm", "Wed 5pm"]), "flexible", frozenset(["concepts", "practice problems"])),
    Student("Quinn", frozenset(["ECE 402", "PHY 303K"]), frozenset(["Thu 7pm", "Sat 1pm"]), "online", frozenset(["homework", "exam review"])),
    Student("Sky", frozenset(["ECE 406", "M 408C"]), frozenset(["Wed 5pm", "Fri 4pm"]), "in-person", frozenset(["practice problems", "exam review"])),
]

class ProfileInput(BaseModel):
    alias: str = Field(min_length=1, max_length=32, pattern=r"^[a-zA-Z][a-zA-Z0-9 _-]*$")
    courses: list[str] = Field(min_length=1, max_length=4)
    slots: list[str] = Field(min_length=1, max_length=6)
    mode: str
    goals: list[str] = Field(min_length=1, max_length=4)

    def as_student(self) -> Student:
        if not set(self.courses).issubset(COURSES):
            raise ValueError("Unsupported course")
        if not set(self.slots).issubset(SLOTS):
            raise ValueError("Unsupported availability")
        if not set(self.goals).issubset(GOALS):
            raise ValueError("Unsupported goal")
        if self.mode not in {"in-person", "online", "flexible"}:
            raise ValueError("Unsupported meeting mode")
        return Student(self.alias.strip(), frozenset(self.courses), frozenset(self.slots), self.mode, frozenset(self.goals))

def parse_profile(payload: ProfileInput) -> Student:
    try:
        return payload.as_student()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.get("/")
def homepage():
    return FileResponse(STATIC / "index.html")

@app.get("/styles.css")
def styles():
    return FileResponse(STATIC / "styles.css", media_type="text/css")

@app.get("/app.js")
def javascript():
    return FileResponse(STATIC / "app.js", media_type="application/javascript")

@app.get("/api/options")
def options():
    return {"courses": COURSES, "slots": SLOTS, "goals": GOALS, "mode": ["in-person", "online", "flexible"], "demo_peers": len(DEMO_PEOPLE)}

@app.post("/api/matches")
def matches(payload: ProfileInput):
    seeker = parse_profile(payload)
    return {"recommendations": recommend(seeker, DEMO_PEOPLE), "count": len(DEMO_PEOPLE), "demo_only": True}

@app.post("/api/group")
def group(payload: ProfileInput):
    seeker = parse_profile(payload)
    return form_study_group(seeker, DEMO_PEOPLE)
