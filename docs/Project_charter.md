Project Charter — Mini Institutional BI Environment (Student Retention)
1) Objective

Build a prototype institutional BI environment that enables leadership to monitor first-year entrant retention and identify drivers of student success, using a warehouse-style model and governed KPI definitions.

2) Problem Statement

The university lacks a unified, decision-ready analytical environment for tracking student retention and progression. Definitions are inconsistent across teams, and reporting is slow to update, limiting the ability to target early interventions and monitor strategic KPIs.

3) Primary Stakeholders

Executive Leadership (President / VPs): strategic KPIs and trend monitoring

Deans / Academic Leadership: programme-level retention and progression performance

Student Support Services: identification of higher-risk segments for intervention

Institutional Research / Planning: standard definitions, governance, and repeatable reporting

4) Scope (In)

Time horizon: 5 academic years

Primary cohort: first-year entrants (new entrants)

Grain: student–programme–academic year

Primary retention definition (Institutional): enrolled in Year N and enrolled anywhere in the institution in Year N+1

Secondary metric: programme-level progression within the same programme (Year N → Year N+1)

Deliverables: DuckDB warehouse prototype + dbt transformations/tests/docs + Tableau dashboards + governance documentation

5) Out of Scope (Explicit)

Real-time data ingestion / streaming

Full ERP/SIS integration

Complex machine learning pipelines

Full regulatory (HEA) submission formats

More than 4 dashboards or more than 8 KPIs

6) KPIs (Locked — max 8)

New Entrants (First-Year Headcount)

First-Year Entrant Retention Rate (Institutional, Y1→Y2)

Retained vs Not Retained Count

Programme Progression Rate (within programme, Y1→Y2)

Retention Gap by Demographic Group

Top/Bottom Programmes by Retention

Risk Segment Distribution (Low/Med/High)

Retention Trend over 5 Years

7) Success Criteria

A working star schema (facts + dimensions) supporting the KPIs

KPI definitions documented (numerator/denominator/grain/cohort)

dbt tests passing and dbt docs generated

3–4 Tableau dashboards built from marts (not raw tables)

Governance pack: glossary + lineage + data quality rules + user guide

GitHub repo with reproducible steps and screenshots

8) Timeline (10-day sprint)

Days 1–2: charter, KPI definitions, architecture + schema design

Days 3–6: DuckDB + dbt (staging → intermediate → marts) + tests/docs

Days 7–8: Tableau dashboards

Day 9: governance & enablement documentation

Day 10: final packaging (README, screenshots, executive summary)

9) Tools

Storage/Warehouse: DuckDB

Transformations & testing: dbt

Light modelling (optional): Python

BI: Tableau

Version control: Git/GitHub

Documentation: Markdown + diagrams.net