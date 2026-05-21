from fastapi import FastAPI
from db import cursor

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Retail Intelligence Platform API Running"}


@app.get("/orders")
def get_orders():
    cursor.execute("SELECT * FROM online_retail LIMIT 10")
    results = cursor.fetchall()
    return results

@app.get("/top-countries")
def top_countries():

    query = """
     SELECT 
     country,
     ROUND(SUM(Quantity * UnitPrice),2) AS revenue

     FROM online_retail
     WHERE Quantity > 0
     GROUP BY country
     ORDER BY revenue DESC
     LIMIT 10

     """
    cursor.execute(query)
    results = cursor.fetchall() 
    return results

# top product ....