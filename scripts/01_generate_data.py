import os
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

OUTPUT_DIR = os.path.join("data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

YEARS = [2021, 2022, 2023, 2024, 2025]  # 5 academic years
TARGET_STUDENTS = 10000

# ---------------------------
# 1) Programmes (12) — all NFQ Level 8
# ---------------------------
PROGRAMMES = [
    # Engineering & Built Environment
    ("P01", "BEng Mechanical Engineering", "Engineering & Built Environment", "Engineering", "FT", 0.78, 0.90),
    ("P02", "BEng Civil Engineering", "Engineering & Built Environment", "Engineering", "FT", 0.80, 0.85),
    ("P03", "BEng Electrical & Electronic Engineering", "Engineering & Built Environment", "Engineering", "FT", 0.76, 0.80),
    ("P04", "BSc Construction Management", "Engineering & Built Environment", "Built Environment", "FT", 0.81, 0.75),

    # Business & Computing
    ("P05", "BSc Business Management", "Business & Computing", "Business", "FT", 0.86, 1.30),
    ("P06", "BA Accounting & Finance", "Business & Computing", "Business", "FT", 0.84, 1.05),
    ("P07", "BSc Data Analytics", "Business & Computing", "Computing", "FT", 0.83, 0.95),
    ("P08", "BSc Computing (Software Development)", "Business & Computing", "Computing", "FT", 0.82, 1.10),

    # Applied Science & Health
    ("P09", "BSc Applied Biology", "Applied Science & Health", "Science", "FT", 0.79, 0.70),
    ("P10", "BSc Pharmaceutical Science", "Applied Science & Health", "Science", "FT", 0.82, 0.65),
    ("P11", "BSc Sports & Exercise Science", "Applied Science & Health", "Health", "FT", 0.85, 0.85),
    ("P12", "BSc Social Care Practice", "Applied Science & Health", "Health", "FT", 0.87, 0.90),
]

programmes_df = pd.DataFrame(
    PROGRAMMES,
    columns=[
        "programme_id",
        "programme_name",
        "faculty",
        "field_of_study",
        "mode_of_study",
        "retention_baseline",
        "popularity_weight",
    ],
)
programmes_df["nfq_level"] = 8

# ---------------------------
# 2) Students (dimension attributes)
# ---------------------------
def choice_with_probs(options: List[str], probs: List[float], n: int) -> List[str]:
    return list(np.random.choice(options, size=n, p=probs))

gender_opts = ["Female", "Male", "Non-binary", "Prefer not to say"]
gender_probs = [0.49, 0.48, 0.02, 0.01]

age_opts = ["<=20", "21-25", "26-34", "35+"]
age_probs = [0.55, 0.30, 0.10, 0.05]

ses_opts = ["Low", "Medium", "High"]
ses_probs = [0.30, 0.50, 0.20]

region_opts = ["Local", "Regional", "International"]
region_probs = [0.65, 0.25, 0.10]

entry_opts = ["Low", "Medium", "High"]
entry_probs = [0.25, 0.55, 0.20]

students_df = pd.DataFrame({
    "student_id": [f"S{str(i).zfill(5)}" for i in range(1, TARGET_STUDENTS + 1)],
    "gender": choice_with_probs(gender_opts, gender_probs, TARGET_STUDENTS),
    "age_band": choice_with_probs(age_opts, age_probs, TARGET_STUDENTS),
    "ses_band": choice_with_probs(ses_opts, ses_probs, TARGET_STUDENTS),
    "region_band": choice_with_probs(region_opts, region_probs, TARGET_STUDENTS),
    "entry_score_band": choice_with_probs(entry_opts, entry_probs, TARGET_STUDENTS),
})
students_df["international_flag"] = (students_df["region_band"] == "International")

# ---------------------------
# 3) Cohort year + initial programme assignment
# ---------------------------
# Slightly increasing intake each year (optional realism)
cohort_year_probs = np.array([0.18, 0.19, 0.20, 0.21, 0.22])  # sums to 1
students_df["cohort_year"] = np.random.choice(YEARS, size=TARGET_STUDENTS, p=cohort_year_probs)

# Programme assignment using popularity weights
programme_ids = programmes_df["programme_id"].tolist()
weights = programmes_df["popularity_weight"].to_numpy()
weights = weights / weights.sum()
students_df["entry_programme_id"] = np.random.choice(programme_ids, size=TARGET_STUDENTS, p=weights)

# ---------------------------
# 4) Retention & progression simulation
# ---------------------------
ENTRY_EFFECT = {"Low": -0.10, "Medium": 0.00, "High": 0.05}
SES_EFFECT = {"Low": -0.06, "Medium": 0.00, "High": 0.04}
AGE_EFFECT = {"<=20": 0.00, "21-25": -0.01, "26-34": -0.02, "35+": -0.05}

# Annual small improvement trend (institution improves over time)
YEAR_TREND = {2021: 0.00, 2022: 0.01, 2023: 0.02, 2024: 0.03, 2025: 0.04}

# Transfer rate among retained students
TRANSFER_RATE = 0.12  # 12% of retained switch programme (institutional retention still true)

# Dropout rate after Year 2 tends to reduce (optional realism)
YEAR2_PLUS_ADJ = -0.03  # slightly higher persistence after first year (i.e., less dropout risk)

programme_baseline: Dict[str, float] = dict(zip(programmes_df["programme_id"], programmes_df["retention_baseline"]))

def clamp(p: float, lo: float = 0.40, hi: float = 0.95) -> float:
    return max(lo, min(hi, p))

enrol_rows: List[Dict] = []

for _, s in students_df.iterrows():
    sid = s["student_id"]
    cohort_year = int(s["cohort_year"])
    prog = s["entry_programme_id"]

    # Build student journey year-by-year from cohort_year to 2025 (max)
    year_level = 1
    current_prog = prog

    for ay in YEARS:
        if ay < cohort_year:
            continue
        if ay == cohort_year:
            # First-year entrant row
            enrol_rows.append({
                "student_id": sid,
                "programme_id": current_prog,
                "academic_year": ay,
                "year_level": year_level,
                "is_first_year_entrant": True,
                "enrol_status": "Enrolled",
                "credits_attempted": int(np.random.choice([50, 60], p=[0.3, 0.7])),
            })
        else:
            # Decide if enrolled this year based on previous year retention decision
            # If they were not retained in the immediately previous year, break.
            # We simulate retention one step at a time (Markov-like).
            prev_year = ay - 1
            # only continue if previous year exists in enrol_rows for this student
            # (simple check: if last added row is prev_year)
            # If not, the student has already left.
            if not any(r["student_id"] == sid and r["academic_year"] == prev_year for r in enrol_rows):
                break

            base = programme_baseline.get(current_prog, 0.80)
            p = base + ENTRY_EFFECT[s["entry_score_band"]] + SES_EFFECT[s["ses_band"]] + AGE_EFFECT[s["age_band"]] + YEAR_TREND.get(prev_year, 0.0)

            # After first year, a tiny bump in persistence (optional)
            if year_level >= 2:
                p = p + (-YEAR2_PLUS_ADJ)  # reducing dropout risk (increase p)

            p = clamp(float(p))

            retained = (np.random.rand() < p)
            if not retained:
                break

            # If retained, maybe transfer programme (institutional retention remains true)
            if np.random.rand() < TRANSFER_RATE:
                # transfer to a different programme, weighted by popularity
                other_programmes = [pid for pid in programme_ids if pid != current_prog]
                other_weights = programmes_df.set_index("programme_id").loc[other_programmes, "popularity_weight"].to_numpy()
                other_weights = other_weights / other_weights.sum()
                current_prog = str(np.random.choice(other_programmes, p=other_weights))

                # When transfer occurs, year_level still increments (they progressed in institution),
                # but they will not count as "progressed within programme" later (dbt logic).
                year_level = min(year_level + 1, 4)
            else:
                year_level = min(year_level + 1, 4)

            enrol_rows.append({
                "student_id": sid,
                "programme_id": current_prog,
                "academic_year": ay,
                "year_level": year_level,
                "is_first_year_entrant": False,
                "enrol_status": "Enrolled",
                "credits_attempted": int(np.random.choice([50, 60], p=[0.3, 0.7])),
            })

enrolments_df = pd.DataFrame(enrol_rows)

# Add credits_earned with a light relationship to entry_score_band
entry_map = students_df.set_index("student_id")["entry_score_band"].to_dict()
def earned_credits(row):
    band = entry_map.get(row["student_id"], "Medium")
    base = 0.78 if band == "Low" else (0.85 if band == "Medium" else 0.90)
    earned = int(round(row["credits_attempted"] * np.random.normal(base, 0.07)))
    return max(0, min(row["credits_attempted"], earned))

enrolments_df["credits_earned"] = enrolments_df.apply(earned_credits, axis=1)

# ---------------------------
# Write CSVs
# ---------------------------
programmes_path = os.path.join(OUTPUT_DIR, "programmes.csv")
students_path = os.path.join(OUTPUT_DIR, "students.csv")
enrolments_path = os.path.join(OUTPUT_DIR, "enrolments.csv")

programmes_df.to_csv(programmes_path, index=False)
students_df.drop(columns=["cohort_year", "entry_programme_id"]).to_csv(students_path, index=False)  # cohort/programme derive from enrolments
enrolments_df.to_csv(enrolments_path, index=False)

print("✅ Wrote:")
print(" -", programmes_path, f"({len(programmes_df)} rows)")
print(" -", students_path, f"({len(students_df)} rows)")
print(" -", enrolments_path, f"({len(enrolments_df)} rows)")