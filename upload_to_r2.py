import os
import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv

# Завантажуємо змінні з файлу .env
load_dotenv()

# --- НАЛАШТУВАННЯ ---
ACCESS_KEY_ID = os.getenv("CF_ACCESS_KEY_ID")
SECRET_ACCESS_KEY = os.getenv("CF_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("CF_BUCKET_NAME")
ENDPOINT_URL = os.getenv("CF_ENDPOINT_URL")

# Локальний корінь, де лежать папки month=01, month=02 тощо.
# "." означає поточну директорію, де запущено скрипт.
LOCAL_ROOT_DIR = "." 

# Якщо хочеш завантажити все всередину якоїсь папки в бакеті, вкажи її тут (наприклад, "raw-data/")
# Якщо потрібно завантажити прямо в корінь бакета — залиш порожнім рядок ""
REMOTE_PREFIX = "" 

# --- ІНІЦІАЛІЗАЦІЯ S3-КЛІЄНТА ДЛЯ CLOUDFLARE R2 ---
s3_client = boto3.client(
    "s3",
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id=ACCESS_KEY_ID,
    aws_secret_access_key=SECRET_ACCESS_KEY,
    config=Config(signature_version="s3v4"), # R2 вимагає підпису версії 4
)


def upload_partitioned_data(local_dir, bucket, remote_prefix):
    """
    Рекурсивно обходить локальну директорію та завантажує parquet-файли
    на Cloudflare R2 із збереженням структури папок.
    """
    print(f"Початок сканування директорії: {os.path.abspath(local_dir)}")
    print(f"Цільовий бакет: {bucket}\n" + "-" * 50)
    
    success_count = 0
    failure_count = 0

    # Обходимо дерево каталогів
    for root, dirs, files in os.walk(local_dir):
        for file in files:
            # Фільтруємо лише файли даних parquet
            if file.endswith(".parquet"):
                # Повний локальний шлях до файлу (наприклад, ./month=01\data_2026_01.parquet)
                local_path = os.path.join(root, file)
                
                # Отримуємо чистий відносний шлях (наприклад, month=01\data_2026_01.parquet)
                relative_path = os.path.relpath(local_path, local_dir)
                
                # Формуємо фінальний ключ для R2. 
                # Обов'язково замінюємо "\\" на "/", оскільки у сховищах R2/S3 роздільник завжди прямий слеш.
                s3_key = os.path.join(remote_prefix, relative_path).replace("\\", "/")
                
                print(f"[ЗАВАНТАЖЕННЯ] {relative_path} -> {s3_key}...")
                
                try:
                    s3_client.upload_file(local_path, bucket, s3_key)
                    print(f"[УСПІШНО] {relative_path} завантажено.")
                    success_count += 1
                except (BotoCoreError, ClientError) as e:
                    print(f"[ПОМИЛКА] Не вдалося завантажити {relative_path}. Деталі: {e}")
                    failure_count += 1

    print("-" * 50)
    print(f"Завантаження завершено! Успішно: {success_count}, Помилок: {failure_count}")


if __name__ == "__main__":
    upload_partitioned_data(LOCAL_ROOT_DIR, BUCKET_NAME, REMOTE_PREFIX)
