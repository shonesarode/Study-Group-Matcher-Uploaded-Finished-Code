from app.main import app
from app.matching import Student, match_score, recommend, form_study_group
from fastapi.testclient import TestClient

client = TestClient(app)

def student(alias="Me", courses=("ECE 406",), slots=("Mon 5pm",), mode="in-person", goals=("exam review",)):
    return Student(alias, frozenset(courses), frozenset(slots), mode, frozenset(goals))

def test_shared_class_and_slot_required():
    assert match_score(student(), student("Other", ("M 408C",))) is None
    assert match_score(student(), student("Other", slots=("Sat 1pm",))) is None

def test_mode_incompatibility():
    assert match_score(student(), student("Other", mode="online")) is None
    assert match_score(student(), student("Other", mode="flexible")) is not None

def test_explanations_and_rankings():
    strong = student("Strong", ("ECE 406", "M 408C"), ("Mon 5pm", "Wed 5pm"), goals=("exam review", "homework"))
    weak = student("Weak", goals=("concepts",))
    seeker = student(courses=("ECE 406", "M 408C"), slots=("Mon 5pm", "Wed 5pm"), goals=("exam review", "homework"))
    ranked = recommend(seeker, [weak, strong])
    assert ranked[0]["alias"] == "Strong"
    assert "shared course" in ranked[0]["why"]

def test_group_preserves_mutual_slot():
    seeker = student()
    participants = [student("A"), student("B", slots=("Mon 5pm", "Sat 1pm")), student("C", slots=("Sat 1pm",))]
    group = form_study_group(seeker, participants)
    assert set(group["members"]) == {"Me", "A", "B"}
    assert group["common_slots"] == ["Mon 5pm"]

def test_invalid_group_size():
    try:
        form_study_group(student(), [], max_members=1)
    except ValueError:
        pass
    else:
        assert False

PROFILE = {"alias":"You","courses":["ECE 406"],"slots":["Mon 5pm"],"mode":"in-person","goals":["exam review"]}

def test_api_matches():
    r = client.post("/api/matches", json=PROFILE)
    assert r.status_code == 200
    assert r.json()["recommendations"]

def test_api_group():
    r = client.post("/api/group", json=PROFILE)
    assert r.status_code == 200
    assert r.json()["members"][0] == "You"

def test_api_rejects_unknown_slot():
    r = client.post("/api/matches", json={**PROFILE, "slots":["Sun 3am"]})
    assert r.status_code == 422

def test_front_page_serves():
    r = client.get("/")
    assert r.status_code == 200
    assert "Study Circle" in r.text
