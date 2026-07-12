import polars as pl
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parents[1]
file_name = BASE_PATH / "data" / "gr_services_first_letter_25_26.parquet"


df = pl.read_parquet(file_name)

c_25 = df.filter(
    (pl.col('year') == '2025') & (pl.col('first_letter_code') == 'C')
).select('count_un_patient').item()

print(df)
print(c_25)  # 10911028
