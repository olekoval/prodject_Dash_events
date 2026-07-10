from dotenv import load_dotenv
import duckdb
import os


load_dotenv()

ACCESS_KEY_ID = os.getenv("CF_ACCESS_KEY_ID")
SECRET_ACCESS_KEY = os.getenv("CF_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("CF_BUCKET_NAME")
ENDPOINT_URL = os.getenv("CF_ENDPOINT_URL")


# Створюємо підключення
con = duckdb.connect()


# Встановлюємо розширення для роботи з S3/R2
con.execute("INSTALL httpfs; LOAD httpfs;")


# Налаштовуємо доступ 
con.execute(f"""
    SET s3_endpoint='{ENDPOINT_URL.replace("https://", "")}';
    SET s3_access_key_id='{ACCESS_KEY_ID}';
    SET s3_secret_access_key='{SECRET_ACCESS_KEY}';
    SET s3_url_style='path';
""")


query = f"""
   SELECT *
     FROM read_parquet('s3://{BUCKET_NAME}/events/**/*.parquet')
   WHERE month = '01'
   LIMIT 10
"""

df = con.execute(query).df()
print(df.loc[0, 'actions'])

con.close()
