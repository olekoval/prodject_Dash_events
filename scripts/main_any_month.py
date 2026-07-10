import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import pandas as pd

load_dotenv()

engine = create_engine(os.getenv("DB_URL"))

main_query = text("""
WITH unnested_treatments AS (
    SELECT 
        unnest(emz_list) AS event_id,
        service_number
     FROM analytics.rds_smd_patient_treatments_2026
    WHERE emz_list IS NOT NULL
	  AND is_correct
	  AND report_month = :month
	  AND packet_number = '9'
),
aggregated_services AS (
    SELECT 
        event_id,
        array_agg(DISTINCT service_number) AS service_numbers
     FROM unnested_treatments
    WHERE event_id IS NOT NULL
    GROUP BY event_id
)
SELECT 
    a.edrpou,
    a.event_id,
    a.patient_id,
    s.service_numbers,
    a.principal_diagnosis,
    a.actions
  FROM analytics.rds_pmg_events_analytics AS a
       LEFT JOIN aggregated_services AS s ON a.event_id = s.event_id
 WHERE a.is_correct
   AND a.report_year = 2026
   AND a.report_month = :month
   AND a.packet_number = '9'
""")

chunk_size = 50_000
output_dir = './data'
os.makedirs(output_dir, exist_ok=True)

# ------------------------------ВИЗНАЧИТИ МІСЯЦЬ ----------------------⚡⚡⚡
month = 6

print(f"\n--- Початок процесу для {month}-го місяця ---")

try:
    # 1. Спершу перевіряємо з'єднання
    with engine.connect() as connection:
        print("✅ З'єднання з базою даних НСЗУ успішно встановлено! Все ОК.")
    
    # 2. Якщо все ок, запускаємо вивантаження
    print(f"Завантаження даних...")
    month_chunks = []
    
    df_iterator = pd.read_sql(
        main_query, 
        con=engine, 
        chunksize=chunk_size, 
        params={"month": month}
    )
    
    for chunk in df_iterator:
        print(f"Місяць {month}: Завантажено чанк розміром {len(chunk)} рядків...")
        month_chunks.append(chunk)
        
    if month_chunks:
        df_month = pd.concat(month_chunks, ignore_index=True)
        print(f"Повний об'єм за місяць {month}: {len(df_month)} рядків.")

        df_month['event_id'] = df_month['event_id'].astype(str)
        df_month['patient_id'] = df_month['patient_id'].astype(str)
        
        file_name = f"{output_dir}/data_2026_{month:02d}.parquet"
        df_month.to_parquet(file_name, compression='zstd')
        print(f"💾 Файлк успішно збережено: {file_name}")
    else:
        print(f"⚠️ За {month}-й місяць база даних не повернула жодного рядка.")

except OperationalError as e:
    print("❌ Помилка з'єднання з базою даних!")
    print("Перевірте статус VPN та дані у файлі .env")
except Exception as e:
    print(f"❌ Критична помилка під час виконання скрипта: {e}")

# Блок finally гарантовано закриє пул сесій, якщо вони взагалі створювалися
finally:
    if 'engine' in locals():
        engine.dispose()
        print("🔌 Пул з'єднань з базою даних очищено.")

print("\n🚀 Робота скрипта завершена!")
