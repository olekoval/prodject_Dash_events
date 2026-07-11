import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import pandas as pd

load_dotenv()

# Одразу створюємо об'єкт engine (він не створює реального з'єднання в цей момент)
engine = create_engine(os.getenv("DB_URL"))

query = text("""
SELECT 
       edrpou,
       patient_id,
	   service_number,
	   (details ->> 'К-сть послуг')::integer AS count_service
  FROM analytics.rds_smd_patient_treatments_2025
 WHERE packet_number = '9'
   AND report_month = :month
   AND comment_text = 'Пацієнт включений до звіту'
   AND service_number LIKE :service_pattern
""")
# ------------------------------ВИЗНАЧИТИ МІСЯЦЬ та СЕРВІС------------------⚡⚡⚡
# 'C%'  --'Консультування та лікування'
# 'E%'  -- 'Ургентні стани'
# 'I%'  -- 'Інструментальна діагностика'
# 'L%'  -- 'Лабораторна діагностика'
# 'P%'  -- 'Процедури'
params = {"month" : 6, "service_pattern" : "C%"} # використовується у запиті SQL та у скрипті дальше

# Створюємо зручні змінні, щоб не писати довгі конструкції params[...] всередині f-рядків
month = params["month"]
service_letter = params["service_pattern"][:-1]  # Виріже знак '%', залишиться тільки 'C', 'E' тощо

BASE_DIR = Path(__file__).resolve().parent
output_dir = f"{BASE_DIR}/data/treatments/year=2025/service={service_letter}/month={month:02d}"

os.makedirs(output_dir, exist_ok=True)
chunk_size = 100_000

try:
    # 1. Спершу перевіряємо з'єднання
    with engine.connect() as connection:
        print("✅ З'єднання з базою даних успішно встановлено!")
        
    # 2. Якщо все ок, запускаємо вивантаження
    print(f"Завантаження даних...")
    month_chunks = []
    df_iterator = pd.read_sql(query, con=engine, chunksize=chunk_size, params=params)
    
    for chunk in df_iterator:
        print(f"Сервіс {service_letter} Місяць {month:02d}: Завантажено чанк розміром {len(chunk)} рядків...")
        month_chunks.append(chunk)
        
    if month_chunks:
        df_month = pd.concat(month_chunks, ignore_index=True)
        print(f"Повний об'єм за місяць {month:02d}: {len(df_month)} рядків.")
        
        df_month['patient_id'] = df_month['patient_id'].astype(str)
        
        # Рядок став чистим і без синтаксичних конфліктів лапок
        file_name = f"{output_dir}/data_2025_{service_letter}_{month:02d}.parquet"
        
        df_month.to_parquet(file_name, compression='zstd')
        print(f"💾 Файл успішно збережено: {file_name}")
    else:
        print(f"⚠️ За {month:02d}-й місяць база даних не повернула жодного рядка.")

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
