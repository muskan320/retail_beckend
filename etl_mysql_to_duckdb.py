#etl system constantly connect api ,database ,warehouse,cloud system
import os
from pathlib import Path
from urllib.parse import quote_plus
import pandas as pd 
from sqlalchemy import create_engine

try:
    from dotenv import load_dotenv
except ImportError as exc:
    raise ImportError(
        "python-dotenv is required to load .env files. Install it with `pip install python-dotenv`."
    ) from exc

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)


def env_or_default(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return value.strip()

mysql_user = env_or_default("MYSQL_USER", "root")
mysql_password = env_or_default("MYSQL_PASSWORD", "2006")
mysql_host = env_or_default("MYSQL_HOST", "localhost")
mysql_database = env_or_default("MYSQL_DATABASE", "retail_oltp")

mysql_engine = create_engine(
    f"mysql+pymysql://{quote_plus(mysql_user)}:{quote_plus(mysql_password)}@{mysql_host}/{quote_plus(mysql_database)}"
)

query = "SELECT * FROM online_retail"

df = pd.read_sql(query, mysql_engine)
print(df.head())


import duckdb
#duck_conn =  duckdb.connect("retail_analytics.duckdb")
duck_conn =  duckdb.connect("md:")


# load data into duckdb 

duck_conn.register("df", df)
duck_conn.execute( """

     CREATE TABLE IF NOT EXISTS olap_retail AS
     SELECT * FROM df 

""")

# verify data inside duckdb 

result = duck_conn.execute( """
      SELECT *
      FROM olap_retail
      LIMIT 5

""").fetchdf()

print(result)

## create cloud database 
duck_conn.execute("CREATE DATABASE IF NOT EXISTS retail_warehouse")

duck_conn.execute("USE retail_warehouse")

## LOAD DATA INTO MOTHERDUCK
duck_conn.execute("""
    CREATE OR REPLACE TABLE olap_retail AS
    SELECT * FROM df
""")

##VERIFY CLOUD DATA
result = duck_conn.execute("""
    SELECT COUNT(*)
    FROM online_retail
""").fetchall()

print(result)
