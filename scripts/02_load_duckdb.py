import os
import duckdb

DB_PATH = os.path.join("data", "duckdb", "institutional.duckdb")
RAW_DIR = os.path.join("data", "raw")

con = duckdb.connect(DB_PATH)

con.execute("DROP TABLE IF EXISTS raw_programmes;")
con.execute("DROP TABLE IF EXISTS raw_students;")
con.execute("DROP TABLE IF EXISTS raw_enrolments;")

con.execute(f"""
CREATE TABLE raw_programmes AS
SELECT * FROM read_csv_auto('{os.path.join(RAW_DIR, 'programmes.csv')}', header=True);
""")

con.execute(f"""
CREATE TABLE raw_students AS
SELECT * FROM read_csv_auto('{os.path.join(RAW_DIR, 'students.csv')}', header=True);
""")

con.execute(f"""
CREATE TABLE raw_enrolments AS
SELECT * FROM read_csv_auto('{os.path.join(RAW_DIR, 'enrolments.csv')}', header=True);
""")

print("✅ Loaded DuckDB:", DB_PATH)
print("raw_programmes:", con.execute("SELECT COUNT(*) FROM raw_programmes").fetchone()[0])
print("raw_students  :", con.execute("SELECT COUNT(*) FROM raw_students").fetchone()[0])
print("raw_enrolments:", con.execute("SELECT COUNT(*) FROM raw_enrolments").fetchone()[0])

# quick sanity: years present
print("years:", con.execute("SELECT DISTINCT academic_year FROM raw_enrolments ORDER BY 1").fetchall())

con.close()