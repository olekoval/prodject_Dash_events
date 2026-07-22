import os
import polars as pl
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DB_URL")
if not db_url:
    raise ValueError("DB_URL не задано в .env")

query_service = """
WITH t_25 AS (
    SELECT 
          '2025' AS year,
          LEFT(service_number, 1) AS first_letter_code,
          COUNT(DISTINCT patient_id) AS count_un_patient,
          COALESCE(SUM((details ->> 'К-сть послуг')::integer), 0) AS count_posluha
    FROM analytics.rds_smd_patient_treatments_2025
   WHERE packet_number = '9'
     AND is_correct
     AND comment_text = 'Пацієнт включений до звіту'
    GROUP BY LEFT(service_number, 1)
),
t_26 AS (
    SELECT 
          '2026' AS year,
          LEFT(service_number, 1) AS first_letter_code,
          COUNT(DISTINCT patient_id) AS count_un_patient,
          COALESCE(SUM((details ->> 'К-сть послуг')::integer), 0) AS count_posluha
     FROM analytics.rds_smd_patient_treatments_2026
    WHERE packet_number = '9'
      AND is_correct
      AND comment_text = 'Пацієнт включений до звіту'
    GROUP BY LEFT(service_number, 1)
)
SELECT * FROM t_25
UNION ALL
SELECT * FROM t_26
"""

query_all = """
WITH s_25 AS (
SELECT '2025' AS year,
       'ALL' AS first_letter_code, 
       COUNT(DISTINCT patient_id) AS count_un_patient,
       COALESCE(SUM((details ->> 'К-сть послуг')::integer), 0) AS count_posluha
  FROM analytics.rds_smd_patient_treatments_2025
 WHERE packet_number = '9'
   AND is_correct
   AND comment_text = 'Пацієнт включений до звіту'
),
s_26 AS (
SELECT '2026' AS year,
       'ALL' AS first_letter_code,  
       COUNT(DISTINCT patient_id) AS count_un_patient,
       COALESCE(SUM((details ->> 'К-сть послуг')::integer), 0) AS count_posluha
  FROM analytics.rds_smd_patient_treatments_2026
 WHERE packet_number = '9'
   AND is_correct
   AND comment_text = 'Пацієнт включений до звіту'
)
SELECT * FROM s_25
UNION ALL
SELECT * FROM s_26
"""

query_Q = """
WITH q_25 AS (
SELECT '2025' AS year,
       LEFT(service_number, 1) AS first_letter_code,
       CASE 
            WHEN report_month IN (1, 2, 3) THEN 'Q1'
            WHEN report_month IN (4, 5, 6) THEN 'Q2'
            WHEN report_month IN (7, 8, 9) THEN 'Q3'
            ELSE 'Q4'
        END AS quarter,
       COUNT(DISTINCT patient_id) AS count_un_patient,
       COALESCE(SUM((details ->> 'К-сть послуг')::integer), 0) AS count_posluha
  FROM analytics.rds_smd_patient_treatments_2025
 WHERE packet_number = '9'
   AND is_correct
   AND comment_text = 'Пацієнт включений до звіту'
 GROUP BY quarter, LEFT(service_number, 1)  
),
q_26 AS (
SELECT '2026' AS year,
       LEFT(service_number, 1) AS first_letter_code,
       CASE 
            WHEN report_month IN (1, 2, 3) THEN 'Q1'
            WHEN report_month IN (4, 5, 6) THEN 'Q2'
            WHEN report_month IN (7, 8, 9) THEN 'Q3'
            ELSE 'Q4'
        END AS quarter,
       COUNT(DISTINCT patient_id) AS count_un_patient,
       COALESCE(SUM((details ->> 'К-сть послуг')::integer), 0) AS count_posluha
  FROM analytics.rds_smd_patient_treatments_2026
 WHERE packet_number = '9'
   AND is_correct
   AND comment_text = 'Пацієнт включений до звіту'
 GROUP BY quarter, LEFT(service_number, 1) 
 )

SELECT * FROM q_25
UNION ALL
SELECT * FROM q_26
"""
# Визначення шляхів до папок
script_dir = Path(__file__).resolve().parent
data_dir = script_dir.parent / "data"

tasks = {
    "service": {
        "query": query_service,
        "file": data_dir / "gr_services_first_letter_25_26.parquet"
    },
    "all": {
        "query": query_all,
        "file": data_dir / "gr_services_all_25_26.parquet"
    },
    "quarter": {
        "query": query_Q,
        "file": data_dir / "gr_services_Q_25_26.parquet"
     }
}

RUN_TASKS = [
 #   "service", 
 #   "all",
    "quarter"
] 

print("🚀 --- Запуск процесу зчитування даних через Polars ADBC...")

for task_name in RUN_TASKS:
    task = tasks[task_name]
    query = task["query"]
    file_name = task["file"]
    
    try:
        print(f"📡 ... Виконання запиту '{task_name}' напряму в Arrow-потік...")
        
        # Використовуємо рядок підключення та швидкий adbc двигун
        df = pl.read_database_uri(
            query=query,
            uri=db_url,
            engine="adbc"
        )
        
        # Збереження результату
        df.write_parquet(file_name)
        print(f"✅ ... Дані збережено у {file_name.name} ({df.height} рядків)")
        
    except Exception as e:
        print(f"❌ ... Помилка у запиті '{task_name}': {e}")

print("\n🏁 ... Робота скрипта завершена!")