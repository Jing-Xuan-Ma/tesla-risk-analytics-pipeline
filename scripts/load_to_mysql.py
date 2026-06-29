import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# 从 .env 读取密码(不写死在代码里)
load_dotenv()
password = os.getenv("DB_PASSWORD")

# 连接信息(你的标准配置)
USER = "root"
HOST = "127.0.0.1"
PORT = "3306"
DB   = "tesla_risk"

engine = create_engine(f"mysql+pymysql://{USER}:{password}@{HOST}:{PORT}/{DB}")

# 要入库的四张表:文件路径 -> 数据库表名
tables = {
    "data/processed/complaints_clean.csv":        "complaints_clean",
    "data/processed/complaints_by_component.csv":  "complaints_by_component",
    "data/processed/recalls_clean.csv":            "recalls_clean",
    "data/processed/recall_lag.csv":               "recall_lag",
}

for csv_path, table_name in tables.items():
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, con=engine, if_exists="replace", index=False)
    print(f"已写入 {table_name}: {len(df)} 行")

print("-" * 40)
print("全部入库完成!")