import os
import polars as pl
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

load_dotenv()

db_url = os.getenv("DB_URL")
if not db_url:
    raise ValueError("DB_URL не задано в .env")

engine = create_engine(db_url)

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
SELECT * FROM t_26;
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
SELECT * FROM s_26;
"""
# Абсолютний шлях до папки, де лежить цей скрипт (scripts/)
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
    }
}

# Вкажіть сюди лише ті ключі, які хочете запустити. 
# Наприклад, щоб запустити все: RUN_TASKS = ["service", "all"]
# Щоб запустити тільки один: RUN_TASKS = ["service"]
RUN_TASKS = [
    "service", 
    "all"
] 

try:
    with engine.connect() as connection:
        print("✅ З'єднання з базою даних успішно встановлено!")
        
        for task_name in RUN_TASKS:
            task = tasks[task_name]
            query = task["query"]
            file_name = task["file"]
            
            try:
                print(f"🚀  Запуск запита '{task_name}' -> {file_name.name}...")
                
                df = pl.read_database(query=text(query), connection=connection)
                df.write_parquet(file_name)
                print(f"✅  Дані збережено у {file_name} ({df.height} рядків)")
                
            except Exception as e:
                print(f"❌  Помилка у запиті '{task_name}': {e}")

except OperationalError as e:
    print(f"❌  Помилка з'єднання з базою даних! {e}")
finally:
    if 'engine' in locals():
        engine.dispose()
        print("🔌 Пул з'єднань з базою даних очищено.")

print("\n🏁  Робота скрипта завершена!")