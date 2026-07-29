import os
import polars as pl
from pathlib import Path
from dotenv import load_dotenv
import time

from rich.console import Console
console = Console()

load_dotenv()

db_url = os.getenv("DB_URL")
if not db_url:
    raise ValueError("DB_URL не задано в .env")

# Для сторінки home (унікальні пацієнти за сервісами)
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
# Для сторінки home (унікальні пацієнти за пакетом)
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
# Для сторінки home (унікальні пацієнти за сервісами поквартально)
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
query_class = """
WITH class_name AS (
	SELECT service_number, name AS name_class
	  FROM (
			SELECT *,
			       ROW_NUMBER() OVER (PARTITION BY service_number ORDER BY date_from DESC) AS rn
			  FROM analytics.ref_pmg_coefficients_services
			 WHERE is_current = 'Y'
			   AND packet_number = '9'
			   ) AS t
	  WHERE rn = 1	
	),
Y25_Y26 AS (
SELECT '2025' AS year,
       service_number,
	   report_month::integer AS report_month,
	   COUNT(DISTINCT patient_id) AS count_un_patient,
	   COALESCE(SUM((details ->> 'К-сть послуг')::integer), 0) AS count_posluha
  FROM analytics.rds_smd_patient_treatments_2025
 WHERE packet_number = '9'
   AND is_correct
   AND comment_text = 'Пацієнт включений до звіту'
 GROUP BY service_number, report_month  

UNION ALL

SELECT '2026' AS year,
       service_number,
	   report_month::integer AS report_month,
	   COUNT(DISTINCT patient_id) AS count_un_patient,
	   COALESCE(SUM((details ->> 'К-сть послуг')::integer), 0) AS count_posluha
  FROM analytics.rds_smd_patient_treatments_2026
 WHERE packet_number = '9'
   AND is_correct
   AND comment_text = 'Пацієнт включений до звіту'
 GROUP BY service_number, report_month  
)

SELECT y.year,
       y.service_number,
	   cn.name_class,
	   y.report_month,
	   y.count_un_patient,
	   y.count_posluha
  FROM Y25_Y26 y
       LEFT JOIN class_name cn ON y.service_number = cn.service_number
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
     },
    "class": {
        "query" : query_class,
        "file": data_dir / "gr_class_month_25_26.parquet" 
    }
}

RUN_TASKS = [
    "service", 
    "all",
    "quarter",
    "class"
] 

console.print("🚀 ... Запуск процесу зчитування даних через Polars ADBC...", style="bright_blue")

for task_name in RUN_TASKS:
    task = tasks[task_name]
    query = task["query"]
    file_name = task["file"]
    
    start_time = time.perf_counter()
    
    try:
        console.print(f"📡 . Виконання запиту '{task_name}'", style="bold green")
        
        # Використовуємо рядок підключення та швидкий adbc двигун
        df = pl.read_database_uri(
            query=query,
            uri=db_url,
            engine="adbc"
        )
        
        elapsed = time.perf_counter() - start_time
        console.print(f"⏱️ ... {task_name} виконано за {elapsed:.2f} секунд", style="bold green")
        
        # Збереження результату
        df.write_parquet(file_name)
        console.print(f"✅ ... Дані збережено у {file_name.name} ({df.height} рядків)", style="bold green")
        
        file_size = file_name.stat().st_size / (1024 * 1024)  # у МБ
        console.print(f"📦 ... Розмір файлу: {file_size:.2f} МБ", style="bold green")
        
    except Exception as e:
        console.print(f"❌ ... Помилка у запиті '{task_name}': {e}", style="bold bright_red")

console.print("\n🏁 ... Робота скрипта завершена!", style="bright_blue")