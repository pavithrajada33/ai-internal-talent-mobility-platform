"""NexaMove — Internal Talent Mobility & Workforce Intelligence Platform.

"""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import altair as alt
import joblib
import numpy as np
import pandas as pd
import streamlit as st

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="NexaMove | Internal Talent Mobility",
    page_icon="↗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "nexamove_v2.db"
CV_DIR = APP_DIR / "uploaded_cvs"
CV_DIR.mkdir(exist_ok=True)
ADMIN_PIN = "2026"
APP_VERSION = "NexaMove 2.0"

# Prototype annual gross salary ranges by role level (UK).
# These are editable assumptions because the uploaded dataset has no salary-range field.
SALARY_BY_LEVEL: dict[int, tuple[int, int]] = {
    1: (24000, 30000),
    2: (30000, 38000),
    3: (38000, 50000),
    4: (50000, 65000),
    5: (65000, 85000),
    6: (85000, 110000),
}

# -----------------------------------------------------------------------------
# Styling — light, clear, dashboard-focused
# -----------------------------------------------------------------------------
CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root{
 --bg:#05070b;--surface:#0c1118;--surface2:#111823;--line:#202b39;
 --text:#f5f7fb;--muted:#8f9aaa;--accent:#d7b55b;--accent2:#f4dc94;
 --blue:#5b8ff9;--green:#43c59e;--amber:#f0b44d;--red:#ef6b73;
}
html,body,[class*="css"]{font-family:"Inter",sans-serif}
.stApp{background:linear-gradient(145deg,#090a0d 0%,#05070b 55%,#080a0e 100%);color:var(--text)}
#MainMenu,footer,header{visibility:hidden}.block-container{max-width:1360px;padding:1.2rem 2rem 3rem}
h1,h2,h3,h4{color:var(--text)!important;letter-spacing:-.035em}p,label,.stCaption{color:var(--muted)!important}
.brand{display:flex;align-items:center;gap:.72rem;margin:.1rem 0 1.25rem}.brand-mark{width:40px;height:40px;border-radius:12px;display:grid;place-items:center;background:linear-gradient(145deg,var(--accent2),#a27b25);color:#08090b;font-weight:900;font-size:21px}.brand-name{font-size:1.1rem;font-weight:800;color:var(--text)}.brand-tag{font-size:.72rem;color:var(--muted);margin-top:.2rem}
.page-hero{padding:1.3rem 1.45rem;border:1px solid #342c1b;border-radius:18px;background:linear-gradient(135deg,rgba(215,181,91,.11),rgba(12,17,24,.95));margin-bottom:1rem}.page-kicker{font-size:.68rem;text-transform:uppercase;letter-spacing:.15em;color:var(--accent2);font-weight:800}.page-title{font-size:2.1rem;font-weight:800;margin:.28rem 0 .3rem;color:var(--text)}.page-copy{font-size:.88rem;color:var(--muted);margin:0}
.metric-card{background:linear-gradient(145deg,var(--surface2),var(--surface));border:1px solid var(--line);border-radius:15px;padding:.95rem 1rem;min-height:108px;box-shadow:0 12px 32px rgba(0,0,0,.2)}.metric-label{font-size:.68rem;text-transform:uppercase;letter-spacing:.08em;color:var(--accent2);font-weight:800}.metric-value{font-size:1.65rem;font-weight:800;color:var(--text);margin-top:.35rem}.metric-note{font-size:.72rem;color:var(--muted);margin-top:.25rem}
.profile-card,.panel,.result-hero{background:linear-gradient(145deg,var(--surface2),var(--surface));border:1px solid var(--line);border-radius:17px;padding:1.1rem 1.2rem;margin:.75rem 0 1rem}.result-hero{border-color:#42361d;background:linear-gradient(135deg,rgba(215,181,91,.13),rgba(12,17,24,.98))}.profile-label{font-size:.67rem;text-transform:uppercase;letter-spacing:.07em;color:var(--muted)}.profile-value{font-size:.94rem;font-weight:700;color:var(--text);margin-top:.18rem;overflow-wrap:anywhere}.score{font-size:2.8rem;font-weight:800;color:var(--accent2)}.score-label{font-size:.75rem;color:var(--muted)}
.requirement-row{display:flex;justify-content:space-between;align-items:center;gap:1rem;padding:.72rem 0;border-bottom:1px solid var(--line)}.requirement-row:last-child{border-bottom:0}.req-title{font-weight:700;color:var(--text)}.req-note{font-size:.76rem;color:var(--muted);margin-top:.18rem}.badge{display:inline-flex;border-radius:999px;padding:.3rem .6rem;font-size:.7rem;font-weight:800}.badge-green{background:rgba(67,197,158,.12);color:#7ee0c0;border:1px solid rgba(67,197,158,.25)}.badge-red{background:rgba(239,107,115,.12);color:#ff9ba2;border:1px solid rgba(239,107,115,.25)}.badge-amber{background:rgba(240,180,77,.12);color:#ffd17c;border:1px solid rgba(240,180,77,.25)}.badge-grey{background:#171e28;color:#c7ced8;border:1px solid #2a3544}.badge-purple{background:rgba(91,143,249,.12);color:#9bbcff;border:1px solid rgba(91,143,249,.25)}
.stButton>button{width:100%;min-height:44px;border-radius:10px;font-weight:800;background:linear-gradient(135deg,var(--accent2),var(--accent))!important;color:#090a0c!important;border:0!important}.stButton>button:hover{filter:brightness(1.06)}button[kind="secondary"]{background:#111823!important;color:#f5f7fb!important;border:1px solid var(--line)!important}
[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:13px;overflow:hidden;background:var(--surface)}[data-testid="stFileUploader"]{background:var(--surface);border:1px dashed #39475a;border-radius:12px;padding:.25rem .6rem}div[data-baseweb="input"]>div,div[data-baseweb="select"]>div,.stTextArea textarea{background:#0b1017!important;border-color:#2a3544!important;color:var(--text)!important;border-radius:10px!important}.stTextInput input,.stNumberInput input{color:var(--text)!important}[data-baseweb="popover"],[role="listbox"]{background:#111823!important;color:#fff!important}[data-testid="stProgress"]>div>div>div{background:linear-gradient(90deg,#a27b25,var(--accent2))}hr{border-color:var(--line)!important}
.home-shell{max-width:980px;margin:4.5rem auto 1.8rem;text-align:center}.home-logo{width:66px;height:66px;margin:0 auto 1rem;border-radius:19px;display:grid;place-items:center;background:linear-gradient(145deg,var(--accent2),#a27b25);color:#07080a;font-size:32px;font-weight:900;box-shadow:0 18px 50px rgba(215,181,91,.18)}.home-title{font-size:2.75rem;font-weight:800;color:var(--text);letter-spacing:-.055em}.home-subtitle{font-size:.78rem;text-transform:uppercase;letter-spacing:.17em;color:var(--accent2);font-weight:800;margin-top:.5rem}.home-card{min-height:195px;padding:1.5rem;border:1px solid var(--line);border-radius:19px;background:linear-gradient(145deg,var(--surface2),var(--surface));text-align:left;box-shadow:0 20px 55px rgba(0,0,0,.25)}.home-card-icon{width:48px;height:48px;border-radius:14px;display:grid;place-items:center;background:rgba(215,181,91,.1);border:1px solid rgba(215,181,91,.2);color:var(--accent2);font-size:22px}.home-card-title{font-size:1.25rem;font-weight:800;color:var(--text);margin-top:1rem}.home-card-copy{font-size:.84rem;line-height:1.55;color:var(--muted);margin-top:.45rem}
.dashboard-head{display:flex;justify-content:space-between;gap:1rem;align-items:flex-end;margin:.35rem 0 1rem}.dashboard-title{font-size:2rem;font-weight:800;color:var(--text)}.dashboard-copy{font-size:.84rem;color:var(--muted);margin-top:.25rem}.section-head{font-size:1.12rem;font-weight:800;color:var(--text);margin:1.25rem 0 .65rem}.chart-wrap{background:linear-gradient(145deg,var(--surface2),var(--surface));border:1px solid var(--line);border-radius:16px;padding:.8rem .9rem .35rem}.candidate-banner{background:linear-gradient(135deg,rgba(91,143,249,.08),rgba(12,17,24,.98));border:1px solid #263a59;border-radius:16px;padding:1.05rem 1.15rem;margin:.8rem 0}.candidate-name{font-size:1.25rem;font-weight:800;color:var(--text)}.candidate-sub{font-size:.78rem;color:var(--muted);margin-top:.2rem}
.chart-section-note{font-size:.74rem;color:var(--muted);margin-top:-.35rem;margin-bottom:.8rem}
[data-testid="stAltairChart"]{background:linear-gradient(145deg,var(--surface2),var(--surface));border:1px solid var(--line);border-radius:16px;padding:.45rem}
@media(max-width:768px){.block-container{padding:1rem}.home-shell{margin-top:1.5rem}.home-title{font-size:2.15rem}.metric-card{min-height:95px}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

st.markdown(
    """
    <style>
    /* Streamlit Cloud input visibility — employee and HR portals */

    /* White text and number fields */
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-baseweb="input"] input {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
        caret-color: #111827 !important;
        opacity: 1 !important;
    }

    div[data-testid="stTextInput"] input:disabled,
    div[data-testid="stNumberInput"] input:disabled,
    div[data-baseweb="input"] input:disabled {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
        opacity: 1 !important;
    }

    div[data-testid="stTextInput"] input::placeholder,
    div[data-testid="stNumberInput"] input::placeholder,
    div[data-baseweb="input"] input::placeholder {
        color: #6b7280 !important;
        -webkit-text-fill-color: #6b7280 !important;
        opacity: 1 !important;
    }

    /* Dark skills and certification text areas */
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stTextArea"] textarea:focus,
    div[data-testid="stTextArea"] textarea:active,
    div[data-testid="stTextArea"] textarea:disabled {
        color: #f8fafc !important;
        -webkit-text-fill-color: #f8fafc !important;
        caret-color: #f8fafc !important;
        opacity: 1 !important;
    }

    div[data-testid="stTextArea"] textarea::placeholder {
        color: #6b7280 !important;
        -webkit-text-fill-color: #6b7280 !important;
        opacity: 1 !important;
    }

    /* Selected value in white select boxes */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] span {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
        opacity: 1 !important;
    }

    /* Dropdown list */
    div[data-baseweb="popover"] div[role="listbox"],
    div[role="listbox"] {
        background-color: #111827 !important;
    }

    div[data-baseweb="popover"] div[role="option"],
    div[data-baseweb="popover"] div[role="option"] *,
    div[role="listbox"] div[role="option"],
    div[role="listbox"] div[role="option"] * {
        color: #f8fafc !important;
        -webkit-text-fill-color: #f8fafc !important;
        opacity: 1 !important;
    }

    div[role="option"][aria-selected="true"],
    div[role="option"]:hover {
        background-color: #263244 !important;
    }

    input:-webkit-autofill,
    input:-webkit-autofill:hover,
    input:-webkit-autofill:focus {
        -webkit-text-fill-color: #111827 !important;
        transition: background-color 9999s ease-in-out 0s;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------------------------------
# Data loading
# -----------------------------------------------------------------------------
def find_file(patterns: Iterable[str]) -> Path | None:
    candidates: list[Path] = []
    for pattern in patterns:
        candidates.extend(APP_DIR.glob(pattern))
    candidates = [p for p in candidates if p.is_file() and not p.name.startswith("~$")]
    return sorted(candidates, key=lambda p: (len(p.name), p.name.lower()))[0] if candidates else None


@st.cache_resource(show_spinner=False)
def load_assets() -> dict[str, Any]:
    dataset_path = find_file([
        "AI_Internal_Talent_Mobility_Dataset_1200*.xlsx",
        "AI_Internal_Talent_Mobility_ML_Dataset_1200*.xlsx",
        "*Talent*Mobility*Dataset*.xlsx",
        "*.xlsx",
    ])
    model_path = find_file(["tuned_logistic_model*.pkl", "*logistic*model*.pkl", "*.pkl"])
    if dataset_path is None:
        raise FileNotFoundError("The Excel dataset was not found in the same folder as app.py.")

    sheets = pd.read_excel(dataset_path, sheet_name=None)
    required = {"Employees", "Role_Requirements", "Course_Mapping", "Quiz_Questions"}
    missing = required.difference(sheets)
    if missing:
        raise ValueError(f"Dataset is missing worksheet(s): {', '.join(sorted(missing))}")

    model = None
    if model_path is not None:
        try:
            model = joblib.load(model_path)
        except Exception:
            model = None

    return {
        "employees": sheets["Employees"].copy(),
        "roles": sheets["Role_Requirements"].copy(),
        "courses": sheets["Course_Mapping"].copy(),
        "quiz": sheets["Quiz_Questions"].copy(),
        "model": model,
    }


try:
    ASSETS = load_assets()
except Exception as exc:
    st.error("NexaMove could not start because the required dataset is unavailable or invalid.")
    st.code(str(exc))
    st.stop()

EMPLOYEES = ASSETS["employees"]
ROLES = ASSETS["roles"]
COURSES = ASSETS["courses"]
QUIZ = ASSETS["quiz"]
MODEL = ASSETS["model"]

# -----------------------------------------------------------------------------
# Database — one consolidated record per employee and target role
# -----------------------------------------------------------------------------
def init_db() -> None:
    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS mobility_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT NOT NULL,
                employee_name TEXT,
                current_role TEXT,
                target_role TEXT NOT NULL,
                target_department TEXT,
                role_level INTEGER,
                salary_min REAL,
                salary_max REAL,
                expected_salary REAL,
                salary_match INTEGER DEFAULT 0,
                interested INTEGER DEFAULT 0,
                applied INTEGER DEFAULT 0,
                all_requirements_met INTEGER DEFAULT 0,
                readiness REAL,
                skill_match REAL,
                quiz_score REAL,
                experience_met INTEGER,
                matched_skills TEXT,
                missing_skills TEXT,
                certifications TEXT,
                cv_filename TEXT,
                updated_at TEXT NOT NULL,
                UNIQUE(employee_id, target_role)
            )
            """
        )
        con.commit()


def upsert_record(result: dict[str, Any], *, interested: int | None = None, applied: int | None = None) -> None:
    existing = None
    with sqlite3.connect(DB_PATH) as con:
        existing = con.execute(
            "SELECT interested, applied FROM mobility_records WHERE employee_id=? AND target_role=?",
            (result["employee_id"], result["target_role"]),
        ).fetchone()

        existing_interested = int(existing[0]) if existing else 0
        existing_applied = int(existing[1]) if existing else 0
        final_interested = existing_interested if interested is None else max(existing_interested, interested)
        final_applied = existing_applied if applied is None else max(existing_applied, applied)

        con.execute(
            """
            INSERT INTO mobility_records (
                employee_id, employee_name, current_role, target_role, target_department,
                role_level, salary_min, salary_max, expected_salary, salary_match,
                interested, applied, all_requirements_met, readiness, skill_match,
                quiz_score, experience_met, matched_skills, missing_skills,
                certifications, cv_filename, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(employee_id, target_role) DO UPDATE SET
                employee_name=excluded.employee_name,
                current_role=excluded.current_role,
                target_department=excluded.target_department,
                role_level=excluded.role_level,
                salary_min=excluded.salary_min,
                salary_max=excluded.salary_max,
                expected_salary=excluded.expected_salary,
                salary_match=excluded.salary_match,
                interested=excluded.interested,
                applied=excluded.applied,
                all_requirements_met=excluded.all_requirements_met,
                readiness=excluded.readiness,
                skill_match=excluded.skill_match,
                quiz_score=excluded.quiz_score,
                experience_met=excluded.experience_met,
                matched_skills=excluded.matched_skills,
                missing_skills=excluded.missing_skills,
                certifications=excluded.certifications,
                cv_filename=excluded.cv_filename,
                updated_at=excluded.updated_at
            """,
            (
                result["employee_id"], result["employee_name"], result["current_role"],
                result["target_role"], result["target_department"], result["role_level"],
                result["salary_min"], result["salary_max"], result["expected_salary"],
                int(result["salary_match"]), final_interested, final_applied,
                int(result["all_requirements_met"]), result["readiness"], result["skill_match"],
                result["quiz_score"], int(result["experience_met"]),
                json.dumps(result["matched_skills"]), json.dumps(result["missing_skills"]),
                result["certifications"], result.get("cv_filename", ""),
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        con.commit()


def load_records() -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as con:
        return pd.read_sql_query("SELECT * FROM mobility_records ORDER BY updated_at DESC", con)


init_db()

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def normalise_text(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def parse_items(value: Any) -> list[str]:
    text = str(value or "").replace(";", ",").replace("\n", ",")
    output: list[str] = []
    seen: set[str] = set()
    for raw in text.split(","):
        item = " ".join(raw.strip().split())
        key = normalise_text(item)
        if item and key not in seen and key not in {"na", "n/a", "none"}:
            seen.add(key)
            output.append(item)
    return output


def canonical_intersection(current: list[str], required: list[str]) -> tuple[list[str], list[str]]:
    current_keys = {normalise_text(x) for x in current}
    matched = [x for x in required if normalise_text(x) in current_keys]
    missing = [x for x in required if normalise_text(x) not in current_keys]
    return matched, missing


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def employee_display_name(row: pd.Series) -> str:
    for col in ("employee_name", "full_name", "name"):
        if col in row.index and pd.notna(row[col]) and str(row[col]).strip():
            return str(row[col]).strip()
    return f"Employee {row['employee_id']}"


def employee_email(row: pd.Series) -> str:
    """Return an employee email from the dataset or a clearly synthetic prototype address."""
    for col in ("employee_email", "email", "work_email", "official_email"):
        if col in row.index and pd.notna(row[col]) and str(row[col]).strip():
            return str(row[col]).strip()
    employee_id = str(row.get("employee_id", "employee")).strip().lower()
    return f"{employee_id}@nexamove.demo"


def salary_range_for_role(role: pd.Series) -> tuple[int, int]:
    level = int(round(safe_float(role.get("role_level"), 3)))
    return SALARY_BY_LEVEL.get(level, SALARY_BY_LEVEL[3])


def money(value: float) -> str:
    return f"£{value:,.0f}"


def badge(text: str, kind: str = "grey") -> str:
    return f'<span class="badge badge-{kind}">{text}</span>'


def brand(back_button: bool = False) -> None:
    left, right = st.columns([5, 1])
    with left:
        st.markdown(
            f"""
            <div class="brand">
              <div class="brand-mark">↗</div>
              <div><div class="brand-name">NexaMove</div>
              <div class="brand-tag">Internal Talent Mobility • {APP_VERSION}</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    if back_button:
        with right:
            if st.button("← Home", type="secondary", use_container_width=True):
                st.session_state.page = "home"
                st.session_state.pop("analysis_result", None)
                st.rerun()


def metric_card(label: str, value: str, note: str = "") -> None:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',
        unsafe_allow_html=True,
    )


def build_prediction(
    employee: pd.Series,
    role: pd.Series,
    skills: list[str],
    certification_text: str,
    quiz_score: float,
) -> tuple[float, dict[str, Any]]:
    required = parse_items(role.get("required_skills", ""))
    matched, missing = canonical_intersection(skills, required)
    required_count = len(required)
    match_pct = len(matched) / required_count * 100 if required_count else 0.0
    employee_exp = safe_float(employee.get("years_experience"))
    minimum_exp = safe_float(role.get("minimum_experience"))
    current_level = safe_float(employee.get("current_role_level"))
    target_level = safe_float(role.get("role_level"))

    row = {
        "age": safe_float(employee.get("age")),
        "education_level": str(employee.get("education_level", "Unknown")),
        "current_department": str(employee.get("current_department", "Unknown")),
        "current_role": str(employee.get("current_role", "Unknown")),
        "current_role_level": current_level,
        "years_experience": employee_exp,
        "years_in_current_role": safe_float(employee.get("years_in_current_role")),
        "performance_rating": safe_float(employee.get("performance_rating")),
        "engagement_score": safe_float(employee.get("engagement_score")),
        "manager_feedback_score": safe_float(employee.get("manager_feedback_score")),
        "training_hours_last_year": safe_float(employee.get("training_hours_last_year")),
        "certification_count": len(parse_items(certification_text)),
        "prior_internal_moves": safe_float(employee.get("prior_internal_moves")),
        "salary_band": str(employee.get("salary_band", "Unknown")),
        "target_department": str(role.get("department", "Unknown")),
        "target_role": str(role.get("role_name", "Unknown")),
        "target_role_level": target_level,
        "skill_overlap_count": len(matched),
        "required_skill_count": required_count,
        "skill_match_percentage": match_pct,
        "minimum_experience": minimum_exp,
        "experience_gap": minimum_exp - employee_exp,
        "role_level_gap": target_level - current_level,
        "quiz_score": quiz_score,
    }

    probability: float
    if MODEL is not None:
        try:
            expected = list(getattr(MODEL, "feature_names_in_", row.keys()))
            model_input = pd.DataFrame([{f: row.get(f) for f in expected}])
            probability = float(MODEL.predict_proba(model_input)[0, 1])
        except Exception:
            probability = -1.0
    else:
        probability = -1.0

    experience_component = 1.0 if minimum_exp <= employee_exp else max(0.0, 1 - (minimum_exp - employee_exp) / 5)
    if probability < 0:
        probability = float(np.clip(.50 * (match_pct / 100) + .30 * (quiz_score / 100) + .20 * experience_component, 0, 1))

    readiness = float(np.clip(probability * 40 + match_pct * .30 + quiz_score * .20 + experience_component * 10, 0, 100))
    details = {
        "required_skills": required,
        "matched_skills": matched,
        "missing_skills": missing,
        "skill_match": match_pct,
        "employee_experience": employee_exp,
        "minimum_experience": minimum_exp,
        "experience_met": employee_exp >= minimum_exp,
        "preferred_certifications": str(role.get("preferred_certifications", "Not specified")),
        "readiness": readiness,
    }
    return probability, details


def get_courses(missing_skills: list[str]) -> pd.DataFrame:
    if not missing_skills:
        return COURSES.iloc[0:0].copy()
    wanted = {normalise_text(x) for x in missing_skills}
    result = COURSES[COURSES["skill"].map(normalise_text).isin(wanted)].copy()
    cols = ["skill", "recommended_course", "course_level", "estimated_hours", "provider", "certificate_available"]
    return result[[c for c in cols if c in result.columns]]


def save_cv(uploaded_file: Any, employee_id: str, target_role: str) -> str:
    safe_role = "".join(ch if ch.isalnum() else "_" for ch in target_role).strip("_")
    suffix = Path(uploaded_file.name).suffix.lower()
    filename = f"{employee_id}_{safe_role}_{datetime.now():%Y%m%d_%H%M%S}{suffix}"
    path = CV_DIR / filename
    with path.open("wb") as output:
        shutil.copyfileobj(uploaded_file, output)
    return filename


def chart(data: pd.DataFrame, x: str, y: str, *, title: str, color: str = "#3530b8", horizontal: bool = False) -> None:
    if data.empty:
        st.info("More data is required for this chart.")
        return
    if horizontal:
        base = alt.Chart(data).mark_bar(cornerRadiusEnd=4, color=color).encode(
            x=alt.X(f"{y}:Q", title=None),
            y=alt.Y(f"{x}:N", sort="-x", title=None),
            tooltip=[alt.Tooltip(f"{x}:N"), alt.Tooltip(f"{y}:Q", format=".1f")],
        )
    else:
        base = alt.Chart(data).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, color=color).encode(
            x=alt.X(f"{x}:N", sort="-y", title=None, axis=alt.Axis(labelAngle=-25)),
            y=alt.Y(f"{y}:Q", title=None),
            tooltip=[alt.Tooltip(f"{x}:N"), alt.Tooltip(f"{y}:Q", format=".1f")],
        )
    st.altair_chart(base.properties(title=title, height=285), use_container_width=True)



def dark_chart(chart: alt.Chart) -> alt.Chart:
    """Apply a consistent dark enterprise chart theme."""
    return (chart.configure_view(strokeOpacity=0)
            .configure(background="#0c1118")
            .configure_title(color="#f5f7fb",fontSize=15,fontWeight=700,anchor="start",offset=14)
            .configure_axis(labelColor="#95a1b2",titleColor="#95a1b2",gridColor="#202b39",domainColor="#2a3544",tickColor="#2a3544")
            .configure_legend(labelColor="#c8d0db",titleColor="#c8d0db"))

# -----------------------------------------------------------------------------
# Session state
# -----------------------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

# -----------------------------------------------------------------------------
# Home
# -----------------------------------------------------------------------------
def home_page() -> None:
    """Display the final compact landing page."""
    st.markdown(
        '<div class="home-shell">'
        '<div class="home-logo">↗</div>'
        '<div class="home-title">NexaMove</div>'
        '<div class="home-subtitle">Internal Talent Mobility Platform</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    spacer_l, employee_col, hr_col, spacer_r = st.columns([0.35, 1.6, 1.6, 0.35], gap="large")
    with employee_col:
        st.markdown(
            '<div class="home-card">'
            '<div class="home-card-icon">◎</div>'
            '<div class="home-card-title">Employee Portal</div>'
            '<div class="home-card-copy">Discover internal roles, complete a role assessment and manage your application.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("Open Employee Portal", key="home_employee", use_container_width=True):
            st.session_state.page = "employee"
            st.rerun()

    with hr_col:
        st.markdown(
            '<div class="home-card">'
            '<div class="home-card-icon">▦</div>'
            '<div class="home-card-title">HR Dashboard</div>'
            '<div class="home-card-copy">Review applicants, compare readiness and identify the strongest internal candidates.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("Open HR Dashboard", key="home_admin", use_container_width=True):
            st.session_state.page = "admin"
            st.rerun()


# -----------------------------------------------------------------------------
# Employee portal
# -----------------------------------------------------------------------------
def employee_page() -> None:
    """Stable employee workflow using a submitted form.

    Radio selections, salary, skills, certifications and CV remain intact while
    the employee completes the assessment. A separate result is retained for
    every employee-role combination, preventing one employee's responses from
    resetting another employee's application.
    """
    brand(back_button=True)
    st.title("Employee Career Portal")
    st.caption("Update your profile, upload your latest CV and assess your fit for an internal role.")

    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = {}

    employee_ids = EMPLOYEES["employee_id"].astype(str).str.upper().tolist()
    entered_id = st.text_input(
        "Employee ID",
        placeholder="For example: E0001",
        key="employee_id_input",
    ).strip().upper()

    if not entered_id:
        st.info("Enter an employee ID to begin.")
        return
    if entered_id not in employee_ids:
        st.error("Employee ID not found. Check the ID and try again.")
        return

    employee = EMPLOYEES.loc[
        EMPLOYEES["employee_id"].astype(str).str.upper() == entered_id
    ].iloc[0]
    employee_name = employee_display_name(employee)

    st.markdown('<div class="profile-card">', unsafe_allow_html=True)
    st.subheader(employee_name)
    p1, p2, p3, p4 = st.columns([1, 2, 1.4, 1])
    values = [
        (p1, "Employee ID", entered_id),
        (p2, "Current role", str(employee.get("current_role", "—"))),
        (p3, "Department", str(employee.get("current_department", "—"))),
        (p4, "Experience", f"{safe_float(employee.get('years_experience')):.0f} years"),
    ]
    for col, label, value in values:
        with col:
            st.markdown(
                f'<div class="profile-label">{label}</div>'
                f'<div class="profile-value">{value}</div>',
                unsafe_allow_html=True,
            )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### Select an internal role")
    role_options = ["Select a role"] + sorted(
        ROLES["role_name"].dropna().astype(str).unique().tolist()
    )
    selected_role = st.selectbox(
        "Target role",
        role_options,
        key=f"target_role_{entered_id}",
        label_visibility="collapsed",
    )
    if selected_role == "Select a role":
        return

    role = ROLES.loc[ROLES["role_name"].astype(str) == selected_role].iloc[0]
    required_skills = parse_items(role.get("required_skills", ""))
    salary_min, salary_max = salary_range_for_role(role)
    min_exp = safe_float(role.get("minimum_experience"))

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("#### Role expectations")
    st.markdown(
        badge(str(role.get("department", "")), "purple")
        + badge(f"Level {int(safe_float(role.get('role_level')))}", "grey")
        + badge(f"Experience: {min_exp:.0f}+ years", "grey")
        + badge(f"Salary: {money(salary_min)}–{money(salary_max)} per annum", "purple"),
        unsafe_allow_html=True,
    )
    st.markdown("**Required skills**")
    st.markdown(
        "".join(badge(x, "grey") for x in required_skills),
        unsafe_allow_html=True,
    )
    st.markdown(
        f"**Preferred certification:** {role.get('preferred_certifications', 'Not specified')}"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    role_quiz = QUIZ.loc[
        QUIZ["target_role"].astype(str) == selected_role
    ].reset_index(drop=True)
    if role_quiz.empty:
        st.warning("No assessment questions are available for this role.")
        return

    safe_role_key = "".join(ch if ch.isalnum() else "_" for ch in selected_role)
    form_key = f"career_fit_{entered_id}_{safe_role_key}"

    st.markdown("### Complete your profile and role assessment")
    with st.form(form_key, clear_on_submit=False):
        c1, c2 = st.columns(2, gap="large")
        with c1:
            skills_text = st.text_area(
                "Current skills",
                value=str(employee.get("current_skills", "")),
                height=115,
                help="Separate skills with commas.",
                key=f"skills_{entered_id}_{safe_role_key}",
            )
            certifications = st.text_area(
                "Certifications",
                placeholder="Example: Microsoft Power BI Data Analyst",
                height=90,
                key=f"certifications_{entered_id}_{safe_role_key}",
            )
        with c2:
            uploaded_cv = st.file_uploader(
                "Upload updated CV",
                type=["pdf", "docx"],
                help="PDF or DOCX only.",
                key=f"cv_{entered_id}_{safe_role_key}",
            )
            expected_salary = st.number_input(
                "Expected annual salary (£ per annum)",
                min_value=0,
                value=40000,
                step=1000,
                key=f"salary_{entered_id}_{safe_role_key}",
                help="Any expectation is accepted and retained for HR review.",
            )

        st.markdown("#### Role assessment")
        answer_letters: list[str] = []
        for idx, q in role_quiz.iterrows():
            option_map = {
                "A": str(q["option_a"]),
                "B": str(q["option_b"]),
                "C": str(q["option_c"]),
            }
            selected_text = st.radio(
                f"{idx + 1}. {q['question']}",
                list(option_map.values()),
                index=None,
                key=f"quiz_{entered_id}_{safe_role_key}_{idx}",
            )
            answer_letters.append(
                next((letter for letter, option in option_map.items() if option == selected_text), "")
            )

        submitted = st.form_submit_button(
            "Check My Career Fit",
            type="primary",
            use_container_width=True,
        )

    result_key = f"{entered_id}|||{selected_role}"

    if submitted:
        skills = parse_items(skills_text)
        if not skills:
            st.error("Enter at least one current skill.")
        elif any(answer == "" for answer in answer_letters):
            answered = sum(answer != "" for answer in answer_letters)
            st.error(
                f"Please answer every assessment question. "
                f"You completed {answered} of {len(answer_letters)} questions."
            )
        elif uploaded_cv is None:
            st.error("Upload an updated PDF or DOCX CV before checking your career fit.")
        else:
            correct = sum(
                answer.upper()
                == str(role_quiz.iloc[i]["correct_option"]).strip().upper()
                for i, answer in enumerate(answer_letters)
            )
            quiz_score = correct / len(role_quiz) * 100
            probability, details = build_prediction(
                employee, role, skills, certifications, quiz_score
            )

            cv_filename = save_cv(uploaded_cv, entered_id, selected_role)
            salary_match = salary_min <= expected_salary <= salary_max
            all_skills_met = len(details["missing_skills"]) == 0
            assessment_met = quiz_score >= 60
            experience_met = bool(details["experience_met"])
            cv_met = bool(cv_filename)
            all_requirements_met = (
                all_skills_met and assessment_met and experience_met and cv_met
            )

            result = {
                "employee_id": entered_id,
                "employee_name": employee_name,
                "current_role": str(employee.get("current_role", "")),
                "target_role": selected_role,
                "target_department": str(role.get("department", "")),
                "role_level": int(safe_float(role.get("role_level"))),
                "salary_min": salary_min,
                "salary_max": salary_max,
                "expected_salary": expected_salary,
                "salary_match": salary_match,
                "readiness": details["readiness"],
                "skill_match": details["skill_match"],
                "quiz_score": quiz_score,
                "experience_met": experience_met,
                "all_requirements_met": all_requirements_met,
                "matched_skills": details["matched_skills"],
                "missing_skills": details["missing_skills"],
                "required_skills": details["required_skills"],
                "employee_experience": details["employee_experience"],
                "minimum_experience": details["minimum_experience"],
                "preferred_certifications": details["preferred_certifications"],
                "certifications": certifications.strip(),
                "cv_filename": cv_filename,
                "cv_met": cv_met,
                "assessment_met": assessment_met,
                "all_skills_met": all_skills_met,
            }
            st.session_state.analysis_results[result_key] = result
            st.session_state.analysis_result = result
            upsert_record(result)
            st.success("Career fit assessment completed successfully.")

    result = st.session_state.analysis_results.get(result_key)
    if not result:
        return

    st.markdown("---")
    ready_to_apply = bool(
        result["all_skills_met"]
        and result["assessment_met"]
        and result["experience_met"]
        and result["cv_met"]
    )
    status = "Ready to apply" if ready_to_apply else "Development required before applying"
    st.markdown(
        f'<div class="result-hero"><div style="display:flex;justify-content:space-between;gap:1rem;align-items:center;flex-wrap:wrap;">'
        f'<div><div class="eyebrow">{selected_role}</div><h2 style="margin:.4rem 0;">Career Readiness Assessment</h2>'
        f'<p style="margin:0;">{status}</p></div>'
        f'<div><div class="score">{result["readiness"]:.0f}%</div><div class="score-label">Overall readiness</div></div></div></div>',
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        metric_card(
            "Skill match",
            f"{result['skill_match']:.0f}%",
            f"{len(result['matched_skills'])}/{len(result['required_skills'])} skills",
        )
    with m2:
        metric_card("Assessment", f"{result['quiz_score']:.0f}%", "Pass mark: 60%")
    with m3:
        metric_card(
            "Experience",
            f"{result['employee_experience']:.0f} yrs",
            f"Required: {result['minimum_experience']:.0f} yrs",
        )
    with m4:
        metric_card("CV status", "Uploaded", result["cv_filename"])

    st.markdown("### Requirement checklist")
    checks = [
        (
            "Required skills",
            result["all_skills_met"],
            "All mandatory skills matched"
            if result["all_skills_met"]
            else f"Missing: {', '.join(result['missing_skills'])}",
        ),
        (
            "Minimum experience",
            result["experience_met"],
            f"{result['employee_experience']:.0f} years held; "
            f"{result['minimum_experience']:.0f} required",
        ),
        (
            "Role assessment",
            result["assessment_met"],
            f"{result['quiz_score']:.0f}% achieved; 60% required",
        ),
        ("Updated CV", result["cv_met"], result["cv_filename"]),
    ]
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    for title, passed, note in checks:
        st.markdown(
            f'<div class="requirement-row"><div><div class="req-title">{title}</div>'
            f'<div class="req-note">{note}</div></div>'
            f'{badge("Met" if passed else "Not met", "green" if passed else "red")}</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    if result["missing_skills"]:
        st.markdown("### Recommended learning")
        courses = get_courses(result["missing_skills"])
        if courses.empty:
            st.info("No mapped course is available. HR should create a tailored development plan.")
        else:
            st.dataframe(
                courses.rename(
                    columns={
                        "skill": "Skill",
                        "recommended_course": "Recommended course",
                        "course_level": "Level",
                        "estimated_hours": "Hours",
                        "provider": "Provider",
                        "certificate_available": "Certificate",
                    }
                ),
                hide_index=True,
                use_container_width=True,
            )
    else:
        st.success("No additional skills development is required for this role.")

    st.markdown("### Next step")
    if ready_to_apply:
        c1, c2 = st.columns(2)
        with c1:
            if st.button(
                "Show Interest",
                key=f"interest_ready_{entered_id}_{safe_role_key}",
                use_container_width=True,
            ):
                upsert_record(result, interested=1)
                st.success("Your interest has been recorded for HR review.")
        with c2:
            if st.button(
                "Apply Now",
                key=f"apply_ready_{entered_id}_{safe_role_key}",
                type="primary",
                use_container_width=True,
            ):
                upsert_record(result, interested=1, applied=1)
                st.success("Your application has been submitted to HR.")
    else:
        if st.button(
            "Show Interest",
            key=f"interest_only_{entered_id}_{safe_role_key}",
            use_container_width=True,
        ):
            upsert_record(result, interested=1)
            st.success("Your interest has been recorded for HR review.")
        st.info(
            "Apply Now becomes available after the mandatory skills, experience, "
            "assessment and CV requirements are met."
        )

# -----------------------------------------------------------------------------
# Admin dashboard
# -----------------------------------------------------------------------------
def admin_page() -> None:
    """Detailed HR analytics dashboard with candidate navigation and shortlisting."""
    brand(back_button=True)

    if not st.session_state.get("admin_authenticated", False):
        st.markdown(
            '<div class="page-hero"><div class="page-kicker">Secure access</div>'
            '<div class="page-title">HR Dashboard</div>'
            '<p class="page-copy">Enter the administrator PIN to review internal mobility activity.</p></div>',
            unsafe_allow_html=True,
        )
        c1, c2, c3 = st.columns([1.3, 1, 1.3])
        with c2:
            pin = st.text_input("Admin PIN", type="password")
            if st.button("Open Dashboard", use_container_width=True):
                if pin == ADMIN_PIN:
                    st.session_state.admin_authenticated = True
                    st.rerun()
                st.error("Incorrect PIN.")
        return

    # Persistent shortlist decisions are kept separately from the ML/application data.
    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS shortlist_decisions (
                employee_id TEXT NOT NULL,
                target_role TEXT NOT NULL,
                shortlisted INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (employee_id, target_role)
            )
            """
        )
        con.commit()

    def shortlist_map() -> dict[tuple[str, str], int]:
        with sqlite3.connect(DB_PATH) as con:
            rows = con.execute(
                "SELECT employee_id, target_role, shortlisted FROM shortlist_decisions"
            ).fetchall()
        return {(str(emp), str(role)): int(flag) for emp, role, flag in rows}

    def save_shortlist(employee_id: str, target_role: str, shortlisted: int) -> None:
        with sqlite3.connect(DB_PATH) as con:
            con.execute(
                """
                INSERT INTO shortlist_decisions(employee_id, target_role, shortlisted, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(employee_id, target_role) DO UPDATE SET
                    shortlisted=excluded.shortlisted,
                    updated_at=excluded.updated_at
                """,
                (employee_id, target_role, int(shortlisted), datetime.now().isoformat(timespec="seconds")),
            )
            con.commit()

    top_l, top_r = st.columns([7, 1])
    with top_l:
        st.markdown(
            '<div class="dashboard-title">Internal Mobility Intelligence</div>'
            '<div class="dashboard-copy">Application volume, department demand, salary expectations, candidate readiness and shortlist decisions.</div>',
            unsafe_allow_html=True,
        )
    with top_r:
        if st.button("Sign out", type="secondary", use_container_width=True):
            st.session_state.admin_authenticated = False
            st.rerun()

    records = load_records()
    if records.empty:
        st.info("No employee assessments are available yet.")
        return

    records["updated_at"] = pd.to_datetime(records["updated_at"], errors="coerce")
    records["status"] = np.select(
        [records["applied"].eq(1), records["interested"].eq(1)],
        ["Applied", "Interested"],
        default="Assessed",
    )
    records["salary_status"] = np.where(records["salary_match"].eq(1), "Within range", "Outside range")
    records["role_midpoint"] = (records["salary_min"].fillna(0) + records["salary_max"].fillna(0)) / 2
    records["salary_gap"] = records["expected_salary"].fillna(0) - records["role_midpoint"]
    records["criteria_status"] = np.where(records["all_requirements_met"].eq(1), "All criteria met", "Development required")
    records["candidate_label"] = records["employee_id"].astype(str) + " · " + records["employee_name"].astype(str)

    email_map = {
        str(row["employee_id"]).upper(): employee_email(row)
        for _, row in EMPLOYEES.iterrows()
    }
    records["employee_email"] = (
        records["employee_id"].astype(str).str.upper().map(email_map)
        .fillna(records["employee_id"].astype(str).str.lower() + "@nexamove.demo")
    )
    smap = shortlist_map()
    records["shortlisted"] = [
        smap.get((str(emp), str(role)), 0)
        for emp, role in zip(records["employee_id"], records["target_role"])
    ]

    # Filters stay high-level; individual candidate review uses arrow navigation below.
    st.markdown('<div class="section-head">Dashboard filters</div>', unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns([1.2, 1.1, 1.0, 1.0])
    role_choices = ["All roles"] + sorted(records["target_role"].dropna().astype(str).unique().tolist())
    dept_choices = ["All departments"] + sorted(records["target_department"].dropna().astype(str).unique().tolist())
    with f1:
        selected_role = st.selectbox("Target role", role_choices)
    with f2:
        selected_department = st.selectbox("Target department", dept_choices)
    with f3:
        selected_stage = st.selectbox("Application stage", ["All stages", "Applied", "Interested", "Assessed"])
    with f4:
        shortlist_filter = st.selectbox("Shortlist", ["All candidates", "Shortlisted", "Not shortlisted"])

    filtered = records.copy()
    if selected_role != "All roles":
        filtered = filtered[filtered["target_role"].eq(selected_role)]
    if selected_department != "All departments":
        filtered = filtered[filtered["target_department"].eq(selected_department)]
    if selected_stage != "All stages":
        filtered = filtered[filtered["status"].eq(selected_stage)]
    if shortlist_filter == "Shortlisted":
        filtered = filtered[filtered["shortlisted"].eq(1)]
    elif shortlist_filter == "Not shortlisted":
        filtered = filtered[filtered["shortlisted"].eq(0)]

    if filtered.empty:
        st.warning("No candidates match the selected filters.")
        return

    application_rows = filtered[filtered["status"].isin(["Applied", "Interested"])].copy()
    analytics_rows = application_rows if not application_rows.empty else filtered.copy()

    # Keep all chart fields in predictable numeric form. SQLite can sometimes
    # return mixed/object dtypes after older records have been migrated.
    numeric_fields = [
        "readiness", "skill_match", "quiz_score", "expected_salary",
        "salary_min", "salary_max", "all_requirements_met", "applied",
        "interested", "experience_met", "salary_match", "shortlisted",
    ]
    for field in numeric_fields:
        if field in analytics_rows.columns:
            analytics_rows[field] = pd.to_numeric(
                analytics_rows[field], errors="coerce"
            ).fillna(0)

    total_people = int(analytics_rows["employee_id"].nunique())
    applications = int(analytics_rows["applied"].eq(1).sum())
    interests = int(analytics_rows["interested"].eq(1).sum())
    ready = int(analytics_rows["all_requirements_met"].eq(1).sum())
    shortlisted = int(analytics_rows["shortlisted"].eq(1).sum())
    avg_ready = float(analytics_rows["readiness"].mean())

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    cards = [
        (k1, "Candidates", total_people, "Unique internal candidates"),
        (k2, "Applications", applications, "Applications submitted"),
        (k3, "Interest", interests, "Employees showing interest"),
        (k4, "Criteria met", ready, "Ready for review"),
        (k5, "Shortlisted", shortlisted, "HR shortlist"),
        (k6, "Avg readiness", f"{avg_ready:.0f}%", "Across selected candidates"),
    ]
    for col, label, value, note in cards:
        with col:
            metric_card(label, str(value), note)

    # ------------------------------------------------------------------
    # Detailed analytics
    # ------------------------------------------------------------------
    st.markdown('<div class="section-head">Application analytics</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="large")
    with c1:
        date_data = analytics_rows.dropna(subset=["updated_at"]).copy()
        date_data["Date"] = date_data["updated_at"].dt.floor("D")
        date_data = date_data.groupby("Date", as_index=False).agg(
            Applications=("applied", "sum"),
            Interest=("interested", "sum"),
        )
        date_long = date_data.melt("Date", var_name="Activity type", value_name="Count")
        date_chart = (
            alt.Chart(date_long)
            .mark_line(point=alt.OverlayMarkDef(filled=True, size=65), strokeWidth=3)
            .encode(
                x=alt.X("Date:T", title=None, axis=alt.Axis(format="%d %b")),
                y=alt.Y("Count:Q", title="Number received", axis=alt.Axis(tickMinStep=1)),
                color=alt.Color(
                    "Activity type:N",
                    scale=alt.Scale(domain=["Applications", "Interest"], range=["#d7b55b", "#5b8ff9"]),
                    legend=alt.Legend(orient="top"),
                ),
                tooltip=[alt.Tooltip("Date:T", format="%d %b %Y"), "Activity type:N", "Count:Q"],
            )
            .properties(title="Internal applications received by date", height=300)
        )
        st.altair_chart(dark_chart(date_chart), use_container_width=True, theme=None)

    with c2:
        dept_data = (
            analytics_rows.groupby("target_department", as_index=False)
            .agg(Candidates=("employee_id", "nunique"), Applications=("applied", "sum"))
            .sort_values("Candidates", ascending=True)
        )
        dept_chart = (
            alt.Chart(dept_data)
            .mark_bar(cornerRadiusEnd=6, color="#d7b55b")
            .encode(
                y=alt.Y("target_department:N", sort=None, title=None, axis=alt.Axis(labelLimit=180)),
                x=alt.X("Candidates:Q", title="Candidates", axis=alt.Axis(tickMinStep=1)),
                tooltip=[alt.Tooltip("target_department:N", title="Department"), "Candidates:Q", "Applications:Q"],
            )
            .properties(title="Applications by target department", height=300)
        )
        st.altair_chart(dark_chart(dept_chart), use_container_width=True, theme=None)

    c3, c4 = st.columns(2, gap="large")
    with c3:
        role_data = (
            analytics_rows.groupby("target_role", as_index=False)
            .agg(Candidates=("employee_id", "nunique"), Ready=("all_requirements_met", "sum"))
            .sort_values("Candidates", ascending=True)
        )
        role_long = role_data.melt("target_role", var_name="Measure", value_name="Count")
        role_chart = (
            alt.Chart(role_long)
            .mark_bar(cornerRadiusEnd=5)
            .encode(
                y=alt.Y("target_role:N", sort=None, title=None, axis=alt.Axis(labelLimit=185)),
                x=alt.X("Count:Q", title="Candidates", axis=alt.Axis(tickMinStep=1)),
                color=alt.Color(
                    "Measure:N",
                    scale=alt.Scale(domain=["Candidates", "Ready"], range=["#5b8ff9", "#43c59e"]),
                    legend=alt.Legend(orient="top"),
                ),
                xOffset="Measure:N",
                tooltip=[alt.Tooltip("target_role:N", title="Role"), "Measure:N", "Count:Q"],
            )
            .properties(title="Candidate demand and readiness by role", height=310)
        )
        st.altair_chart(dark_chart(role_chart), use_container_width=True, theme=None)

    with c4:
        stage_data = analytics_rows.groupby("status", as_index=False).size().rename(columns={"size": "Candidates"})
        stage_chart = (
            alt.Chart(stage_data)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X("status:N", title=None, sort=["Interested", "Applied", "Assessed"]),
                y=alt.Y("Candidates:Q", title="Candidates", axis=alt.Axis(tickMinStep=1)),
                color=alt.Color(
                    "status:N",
                    scale=alt.Scale(domain=["Interested", "Applied", "Assessed"], range=["#5b8ff9", "#d7b55b", "#8f9aaa"]),
                    legend=None,
                ),
                tooltip=[alt.Tooltip("status:N", title="Stage"), "Candidates:Q"],
            )
            .properties(title="Candidate pipeline by stage", height=310)
        )
        st.altair_chart(dark_chart(stage_chart), use_container_width=True, theme=None)

    st.markdown('<div class="section-head">Candidate and salary analysis</div>', unsafe_allow_html=True)
    c5, c6 = st.columns(2, gap="large")

    # Use one current row per employee-role combination so repeated assessments
    # do not overlap and hide marks in the charts.
    candidate_plot = (
        analytics_rows.sort_values("updated_at")
        .groupby(["employee_id", "target_role"], as_index=False)
        .tail(1)
        .copy()
    )
    candidate_plot["candidate_label"] = (
        candidate_plot["employee_id"].astype(str)
        + " · "
        + candidate_plot["employee_name"].astype(str)
    )

    with c5:
        readiness_data = candidate_plot.sort_values("readiness", ascending=True).copy()
        readiness_data["Recommendation"] = np.select(
            [
                readiness_data["all_requirements_met"].eq(1),
                readiness_data["readiness"].ge(70),
            ],
            ["Criteria met", "Near ready"],
            default="Development required",
        )

        readiness_bars = (
            alt.Chart(readiness_data)
            .mark_bar(cornerRadiusEnd=6, height=22)
            .encode(
                y=alt.Y(
                    "candidate_label:N",
                    sort=alt.SortField(field="readiness", order="ascending"),
                    title=None,
                    axis=alt.Axis(labelLimit=190),
                ),
                x=alt.X(
                    "readiness:Q",
                    title="Readiness score (%)",
                    scale=alt.Scale(domain=[0, 100], nice=False),
                    axis=alt.Axis(values=[0, 20, 40, 60, 80, 100]),
                ),
                color=alt.Color(
                    "Recommendation:N",
                    scale=alt.Scale(
                        domain=["Criteria met", "Near ready", "Development required"],
                        range=["#43c59e", "#f0b44d", "#ef6b73"],
                    ),
                    legend=alt.Legend(orient="top"),
                ),
                tooltip=[
                    alt.Tooltip("employee_name:N", title="Employee"),
                    alt.Tooltip("target_role:N", title="Applied role"),
                    alt.Tooltip("readiness:Q", title="Readiness", format=".0f"),
                    alt.Tooltip("skill_match:Q", title="Skill match", format=".0f"),
                    alt.Tooltip("quiz_score:Q", title="Assessment", format=".0f"),
                ],
            )
        )
        readiness_labels = readiness_bars.mark_text(
            align="left", baseline="middle", dx=5, color="#f5f7fb", fontWeight=700
        ).encode(text=alt.Text("readiness:Q", format=".0f"))
        readiness_chart = (readiness_bars + readiness_labels).properties(
            title="Applicant readiness and criteria status",
            height=max(300, min(520, len(readiness_data) * 44)),
        )
        st.altair_chart(dark_chart(readiness_chart), use_container_width=True, theme=None)

    with c6:
        salary_data = candidate_plot[
            candidate_plot["expected_salary"].gt(0)
            & candidate_plot["salary_min"].gt(0)
            & candidate_plot["salary_max"].gt(0)
        ].sort_values("expected_salary", ascending=True).copy()

        if salary_data.empty:
            st.info("Salary analysis will appear after candidates provide an expected annual salary.")
        else:
            salary_data["salary_status"] = np.where(
                salary_data["expected_salary"].between(
                    salary_data["salary_min"], salary_data["salary_max"], inclusive="both"
                ),
                "Within range",
                "Outside range",
            )
            base = alt.Chart(salary_data).encode(
                y=alt.Y(
                    "candidate_label:N",
                    sort=alt.SortField(field="expected_salary", order="ascending"),
                    title=None,
                    axis=alt.Axis(labelLimit=190),
                )
            )
            salary_range = base.mark_rule(strokeWidth=8, color="#516078").encode(
                x=alt.X(
                    "salary_min:Q",
                    title="Expected annual salary (£)",
                    scale=alt.Scale(zero=False),
                ),
                x2=alt.X2("salary_max:Q"),
                tooltip=[
                    alt.Tooltip("employee_name:N", title="Employee"),
                    alt.Tooltip("target_role:N", title="Role"),
                    alt.Tooltip("salary_min:Q", title="Role minimum", format=",.0f"),
                    alt.Tooltip("salary_max:Q", title="Role maximum", format=",.0f"),
                ],
            )
            salary_point = base.mark_point(filled=True, size=145, stroke="#f5f7fb", strokeWidth=1).encode(
                x=alt.X("expected_salary:Q", title="Expected annual salary (£)", scale=alt.Scale(zero=False)),
                color=alt.Color(
                    "salary_status:N",
                    scale=alt.Scale(
                        domain=["Within range", "Outside range"],
                        range=["#43c59e", "#ef6b73"],
                    ),
                    legend=alt.Legend(orient="top"),
                ),
                tooltip=[
                    alt.Tooltip("employee_name:N", title="Employee"),
                    alt.Tooltip("expected_salary:Q", title="Expected salary", format=",.0f"),
                    alt.Tooltip("salary_status:N", title="Alignment"),
                ],
            )
            salary_chart = alt.layer(salary_range, salary_point).properties(
                title="Salary expectation against role range",
                height=max(300, min(520, len(salary_data) * 44)),
            )
            st.altair_chart(dark_chart(salary_chart), use_container_width=True, theme=None)

    # ------------------------------------------------------------------
    # Transparent candidate suggestion
    # ------------------------------------------------------------------
    st.markdown('<div class="section-head">Candidate suggestion</div>', unsafe_allow_html=True)
    ranked = analytics_rows.copy()
    ranked["ranking_score"] = (
        ranked["all_requirements_met"].astype(float) * 1000
        + ranked["readiness"].fillna(0) * 4
        + ranked["skill_match"].fillna(0) * 2
        + ranked["quiz_score"].fillna(0)
        + ranked["experience_met"].fillna(0).astype(float) * 50
    )
    ranked = ranked.sort_values(
        ["ranking_score", "readiness", "skill_match", "quiz_score"],
        ascending=False,
    )
    top = ranked.iloc[0]
    top_reason = (
        "All mandatory criteria are met"
        if int(top["all_requirements_met"]) == 1
        else "Highest combined readiness among the currently filtered candidates"
    )
    st.markdown(
        f'''<div class="candidate-banner">
        <div class="page-kicker">Suggested candidate for HR review</div>
        <div class="candidate-name">{top["employee_name"]} · {top["target_role"]}</div>
        <div class="candidate-sub">{top_reason}. Readiness {top["readiness"]:.0f}% · Skill match {top["skill_match"]:.0f}% · Assessment {top["quiz_score"]:.0f}%.</div>
        </div>''',
        unsafe_allow_html=True,
    )
    st.caption("This suggestion uses transparent prototype rules. HR should verify experience, evidence, interview results and organisational requirements before making a decision.")

    # ------------------------------------------------------------------
    # Arrow-based candidate review
    # ------------------------------------------------------------------
    st.markdown('<div class="section-head">Applicant review</div>', unsafe_allow_html=True)
    review_pool = analytics_rows.sort_values(["applied", "all_requirements_met", "readiness"], ascending=[False, False, False]).reset_index(drop=True)
    filter_signature = "|".join([selected_role, selected_department, selected_stage, shortlist_filter, str(len(review_pool))])
    if st.session_state.get("admin_filter_signature") != filter_signature:
        st.session_state.admin_filter_signature = filter_signature
        st.session_state.admin_candidate_index = 0

    if "admin_candidate_index" not in st.session_state:
        st.session_state.admin_candidate_index = 0
    st.session_state.admin_candidate_index = max(0, min(st.session_state.admin_candidate_index, len(review_pool) - 1))

    nav_left, nav_count, nav_right = st.columns([1, 4, 1])
    with nav_left:
        if st.button("← Previous", use_container_width=True, disabled=len(review_pool) <= 1):
            st.session_state.admin_candidate_index = (st.session_state.admin_candidate_index - 1) % len(review_pool)
            st.rerun()
    with nav_count:
        st.markdown(
            f'<div style="text-align:center;color:#8f9aaa;padding:.7rem 0;font-weight:700">Candidate {st.session_state.admin_candidate_index + 1} of {len(review_pool)}</div>',
            unsafe_allow_html=True,
        )
    with nav_right:
        if st.button("Next →", use_container_width=True, disabled=len(review_pool) <= 1):
            st.session_state.admin_candidate_index = (st.session_state.admin_candidate_index + 1) % len(review_pool)
            st.rerun()

    row = review_pool.iloc[st.session_state.admin_candidate_index]
    candidate_shortlisted = int(row["shortlisted"]) == 1
    status_badge = badge("Shortlisted", "green") if candidate_shortlisted else badge(row["status"], "purple")
    st.markdown(
        f'''<div class="candidate-banner">
        <div style="display:flex;justify-content:space-between;gap:1rem;align-items:flex-start">
          <div><div class="candidate-name">{row["employee_name"]}</div>
          <div class="candidate-sub">{row["employee_id"]} · {row["employee_email"]}<br>{row["current_role"]} → {row["target_role"]} · {row["target_department"]}</div></div>
          <div>{status_badge}</div>
        </div></div>''',
        unsafe_allow_html=True,
    )

    p1, p2, p3, p4, p5, p6 = st.columns(6)
    candidate_cards = [
        (p1, "Readiness", f'{row["readiness"]:.0f}%', "Overall score"),
        (p2, "Skill match", f'{row["skill_match"]:.0f}%', "Required skills"),
        (p3, "Assessment", f'{row["quiz_score"]:.0f}%', "Pass mark 60%"),
        (p4, "Experience", "Met" if int(row["experience_met"]) else "Gap", "Minimum requirement"),
        (p5, "Expected salary", money(row["expected_salary"]), row["salary_status"]),
        (p6, "Role range", f'{money(row["salary_min"])}–{money(row["salary_max"])}', "Per annum"),
    ]
    for col, label, value, note in candidate_cards:
        with col:
            metric_card(label, str(value), str(note))

    try:
        matched = json.loads(row.get("matched_skills") or "[]")
    except Exception:
        matched = []
    try:
        missing = json.loads(row.get("missing_skills") or "[]")
    except Exception:
        missing = []

    d1, d2, d3, d4 = st.columns(4)
    detail_cards = [
        (d1, "Criteria", "All met" if int(row["all_requirements_met"]) else "Development required"),
        (d2, "Matched skills", ", ".join(matched) if matched else "None recorded"),
        (d3, "Skill gaps", ", ".join(missing) if missing else "No gaps"),
        (d4, "CV", row["cv_filename"] or "Not uploaded"),
    ]
    for col, label, value in detail_cards:
        with col:
            st.markdown(
                f'<div class="profile-card"><div class="profile-label">{label}</div><div class="profile-value">{value}</div></div>',
                unsafe_allow_html=True,
            )

    decision_left, decision_right = st.columns([1, 1])
    with decision_left:
        if candidate_shortlisted:
            if st.button("Remove from Shortlist", key="remove_shortlist", type="secondary", use_container_width=True):
                save_shortlist(str(row["employee_id"]), str(row["target_role"]), 0)
                st.success("Candidate removed from the shortlist.")
                st.rerun()
        else:
            if st.button("Shortlist Candidate", key="shortlist_candidate", use_container_width=True):
                save_shortlist(str(row["employee_id"]), str(row["target_role"]), 1)
                st.success("Candidate added to the shortlist.")
                st.rerun()
    with decision_right:
        if st.button("Move to Next Candidate", key="next_candidate_action", type="secondary", use_container_width=True):
            st.session_state.admin_candidate_index = (st.session_state.admin_candidate_index + 1) % len(review_pool)
            st.rerun()

    # Compact audit table remains available below the visual review.
    with st.expander("View detailed applicant records"):
        directory = analytics_rows[[
            "employee_id", "employee_name", "employee_email", "current_role", "target_role",
            "target_department", "status", "readiness", "skill_match", "quiz_score",
            "expected_salary", "salary_status", "criteria_status", "shortlisted", "updated_at",
        ]].copy()
        directory["Updated"] = directory["updated_at"].dt.strftime("%d %b %Y")
        directory["Expected salary"] = directory["expected_salary"].apply(money)
        directory["Shortlisted"] = np.where(directory["shortlisted"].eq(1), "Yes", "No")
        directory = directory.rename(columns={
            "employee_id": "Employee ID", "employee_name": "Employee", "employee_email": "Email",
            "current_role": "Current role", "target_role": "Applied role",
            "target_department": "Department", "status": "Stage", "readiness": "Readiness",
            "skill_match": "Skill match", "quiz_score": "Assessment",
            "salary_status": "Salary alignment", "criteria_status": "Criteria",
        })
        display_columns = [
            "Employee ID", "Employee", "Email", "Current role", "Applied role", "Department",
            "Stage", "Readiness", "Skill match", "Assessment", "Expected salary",
            "Salary alignment", "Criteria", "Shortlisted", "Updated",
        ]
        st.dataframe(
            directory[display_columns],
            hide_index=True,
            use_container_width=True,
            height=320,
            column_config={
                "Readiness": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.0f%%"),
                "Skill match": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.0f%%"),
                "Assessment": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.0f%%"),
            },
        )
        csv = directory[display_columns].to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download applicant report",
            csv,
            file_name=f"nexamove_applicants_{datetime.now():%Y%m%d_%H%M}.csv",
            mime="text/csv",
        )

    st.caption("Salary ranges are annual prototype assumptions mapped to role level. Demo emails are generated only when the source dataset has no email field.")

# -----------------------------------------------------------------------------
# Router
# -----------------------------------------------------------------------------
if st.session_state.page == "employee":
    employee_page()
elif st.session_state.page == "admin":
    admin_page()
else:
    home_page()
