# KPI Definitions — Student Retention & Success Prototype

## Global conventions
- **Time horizon:** 5 academic years
- **Primary cohort:** first-year entrants (new entrants)
- **Grain:** student–programme–academic_year
- **Primary retention definition (institutional):** enrolled in AY N AND enrolled anywhere in the institution in AY N+1
- **Secondary metric:** programme progression within same programme (AY N → AY N+1)
- **Inclusion rule (cohort):** first-time entrants in AY N (no prior enrolment in earlier years)
- **Exclusions (unless stated otherwise):** test records, non-credit short courses

---

## KPI 1 — New Entrants (First-Year Headcount)
**Purpose:** Size of the incoming cohort; denominator for retention KPIs.

**Definition:** Count of distinct students who are classified as first-year entrants in the selected academic year.

- **Numerator:** N/A
- **Denominator:** N/A
- **Calculation:** `COUNT(DISTINCT student_id)`
- **Filters:** `is_first_year_entrant = TRUE` and `academic_year = selected_year`
- **Grain:** academic_year (aggregate), sliceable by programme/demographics
- **Primary table(s):** `fct_student_year_status`
- **Edge cases / notes:** Handle students with multiple programme records in same year (use primary programme flag).

---

## KPI 2 — First-Year Entrant Retention Rate (Institutional, Y1→Y2)
**Purpose:** Executive KPI indicating whether first-year entrants return the following year anywhere in the institution.

**Definition:** Of first-year entrants in AY N, the % who are enrolled in AY N+1 in any programme.

- **Numerator:** Count of first-year entrants in AY N with `retained_next_year_institution = TRUE`
- **Denominator:** Total first-year entrants in AY N
- **Calculation:** `numerator / denominator`
- **Filters:** cohort year = selected_year (AY N)
- **Grain:** cohort_year (AY N), sliceable by programme/demographics
- **Primary table(s):** `fct_student_year_status` (AY N rows)
- **Edge cases / notes:** Students who transfer programmes are still “retained” under this definition.

---

## KPI 3 — Retained vs Not Retained Count
**Purpose:** Clear count view behind the retention rate; useful for programme ranking and workload planning.

**Definition:** Count of retained and not retained first-year entrants from AY N.

- **Calculation:** `COUNT(DISTINCT student_id)` grouped by `retention_status`
- **Retention status mapping:**
  - Retained: `retained_next_year_institution = TRUE`
  - Not retained: `retained_next_year_institution = FALSE`
- **Filters:** cohort year = selected_year
- **Primary table(s):** `fct_student_year_status`

---

## KPI 4 — Programme Progression Rate (Within Programme, Y1→Y2)
**Purpose:** Academic KPI showing whether students progressed to the next level within the same programme.

**Definition:** Of first-year entrants in programme P in AY N, the % who are enrolled in the same programme in AY N+1 at the expected next level.

- **Numerator:** Count with `progressed_next_year_programme = TRUE`
- **Denominator:** Total first-year entrants in programme P in AY N
- **Calculation:** `numerator / denominator`
- **Filters:** cohort year = selected_year; programme = selected programme
- **Primary table(s):** `fct_student_year_status`
- **Edge cases / notes:** Students retained institutionally but transferred programmes count as not progressed (by design).

---

## KPI 5 — Retention Gap by Demographic Group
**Purpose:** Equity lens—identify gaps across demographic segments.

**Definition:** Retention rate (KPI 2) calculated by demographic group.

- **Calculation:** KPI 2 computed per demographic category (e.g., gender, SES band, region, age band)
- **Primary table(s):** `fct_student_year_status` + relevant dimensions (or flattened fields)
- **Edge cases / notes:** Small counts should be suppressed/flagged (privacy-safe reporting).

---

## KPI 6 — Top/Bottom Programmes by Retention
**Purpose:** Identify programmes performing unusually well/poorly for targeted interventions.

**Definition:** Programmes ranked by retention rate for the selected cohort year.

- **Calculation:** KPI 2 by programme, then sort desc/asc
- **Filters:** cohort year = selected_year; optionally min cohort size threshold (e.g., >= 30)
- **Primary table(s):** `fct_student_year_status`
- **Edge cases / notes:** Use a minimum cohort size threshold to avoid noisy rankings.

---

## KPI 7 — Risk Segment Distribution (Low/Med/High)
**Purpose:** Provide a practical segmentation for student support planning.

**Definition:** Distribution of first-year entrants across risk segments derived from a simple risk score.

- **Risk score (prototype):** weighted index using selected factors (e.g., entry_score_band, SES band, commute distance band, prior attainment proxy)
- **Segmentation rule:**
  - Low: score <= P33
  - Medium: P34–P66
  - High: score >= P67
- **Calculation:** `COUNT(DISTINCT student_id)` by `risk_segment`
- **Primary table(s):** `fct_student_year_status` (risk fields)
- **Edge cases / notes:** This is not a production model; include transparency notes and limitations.

---

## KPI 8 — Retention Trend Over 5 Years
**Purpose:** Strategic monitoring of retention over time.

**Definition:** Retention rate (KPI 2) plotted for each cohort year across the 5-year window.

- **Calculation:** KPI 2 for each cohort_year in window
- **Primary table(s):** `fct_student_year_status`
- **Edge cases / notes:** Ensure cohorts are comparable (first-year entrants only).
