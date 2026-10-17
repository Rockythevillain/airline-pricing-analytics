"""Loads fares.csv into SQLite and runs analysis queries (CTEs + window functions)."""
import sqlite3
import pandas as pd

df = pd.read_csv("fares.csv").drop_duplicates("booking_id")
df = df[df["fare_usd"] > 0].dropna(subset=["fare_usd"])
con = sqlite3.connect("fares.db")
df.to_sql("fares", con, if_exists="replace", index=False)

queries = {
"1. Average fare and bookings by route and cabin": """
    SELECT route, cabin, COUNT(*) AS bookings, ROUND(AVG(fare_usd),2) AS avg_fare
    FROM fares GROUP BY route, cabin ORDER BY route, cabin;""",

"2. Route revenue rank (CTE + RANK window function)": """
    WITH rev AS (SELECT route, SUM(fare_usd) AS revenue FROM fares GROUP BY route)
    SELECT route, ROUND(revenue,0) AS revenue,
           RANK() OVER (ORDER BY revenue DESC) AS revenue_rank
    FROM rev;""",

"3. Fare by booking window bucket (Economy)": """
    SELECT CASE WHEN days_before_departure <= 7  THEN '0-7 days'
                WHEN days_before_departure <= 30 THEN '8-30 days'
                WHEN days_before_departure <= 90 THEN '31-90 days'
                ELSE '91+ days' END AS booking_window,
           COUNT(*) AS bookings, ROUND(AVG(fare_usd),2) AS avg_fare
    FROM fares WHERE cabin = 'Economy'
    GROUP BY booking_window ORDER BY MIN(days_before_departure);""",

"4. Monthly avg fare with 3-month moving average (window function)": """
    WITH m AS (
        SELECT route, SUBSTR(travel_date,1,7) AS month, AVG(fare_usd) AS avg_fare
        FROM fares WHERE cabin = 'Economy' GROUP BY route, month)
    SELECT route, month, ROUND(avg_fare,2) AS avg_fare,
           ROUND(AVG(avg_fare) OVER (PARTITION BY route ORDER BY month
                 ROWS BETWEEN 2 PRECEDING AND CURRENT ROW),2) AS moving_avg_3m
    FROM m WHERE route = 'AUH-LHR' ORDER BY month;""",
}
for title, q in queries.items():
    print("\n" + title)
    print(pd.read_sql(q, con).to_string(index=False))
