import os
import polars as pl
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

load_dotenv()

db_url = os.getenv("DB_URL")
if not db_url:
    raise ValueError("DB_URL не задано в .env")

engine = create_engine(db_url)

query = """
WITH t_25 AS (
    SELECT 
          '2025' AS year,
          LEFT(service_number, 1) AS first_letter_code,
          COUNT(DISTINCT patient_id) AS count_un_patient,
          COALESCE(SUM((details ->> 'К-сть послуг')::integer), 0) AS count_posluha
    FROM analytics.rds_smd_patient_treatments_2025
   WHERE packet_number = '9'
     AND is_correct
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
    GROUP BY LEFT(service_number, 1)
)
SELECT * FROM t_25
UNION ALL
SELECT * FROM t_26;
"""
# 'C'  --'Консультування та лікування'
# 'E'  -- 'Ургентні стани'
# 'I'  -- 'Інструментальна діагностика'
# 'L'  -- 'Лабораторна діагностика'
# 'P'  -- 'Процедури'

try:
    with engine.connect() as connection:
        print("✅ З'єднання з базою даних успішно встановлено!")
        print("Завантаження даних...")

        file_name = "../data/gr_services_first_letter_25_26.parquet"
        Path(file_name).parent.mkdir(parents=True, exist_ok=True)

        df = pl.read_database(query=query, connection=connection)
        df.write_parquet(file_name)

        print(f"✅ Дані збережено у {file_name} ({df.height} рядків)")

except OperationalError as e:
    print(f"❌ Помилка з'єднання з базою даних! {e}")
except Exception as e:
    print(f"❌ Помилка під час виконання скрипта: {e}")

finally:
    if 'engine' in locals():
        engine.dispose()
        print("🔌 Пул з'єднань з базою даних очищено.")

print("\n🚀 Робота скрипта завершена!")
