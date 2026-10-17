"""Cleans fares.csv and produces an Excel pricing report + charts automatically.
Run it any time:  python 03_automated_report.py"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

raw = pd.read_csv("fares.csv", parse_dates=["booking_date", "travel_date"])
clean = raw.drop_duplicates("booking_id")
clean = clean[clean["fare_usd"] > 0].dropna(subset=["fare_usd"])
print(f"Rows: raw={len(raw)}  clean={len(clean)}  removed={len(raw)-len(clean)}")

clean = clean.assign(
    month=clean["travel_date"].dt.to_period("M").astype(str),
    booking_window=pd.cut(clean["days_before_departure"], [0, 7, 30, 90, 180],
                          labels=["0-7 days", "8-30 days", "31-90 days", "91+ days"]),
)
by_route = clean.groupby(["route", "cabin"]).agg(bookings=("fare_usd", "size"),
        avg_fare=("fare_usd", "mean"), revenue=("fare_usd", "sum")).round(2).reset_index()
by_window = (clean[clean.cabin == "Economy"].groupby("booking_window", observed=True)
             .agg(bookings=("fare_usd", "size"), avg_fare=("fare_usd", "mean")).round(2).reset_index())
monthly = clean[clean.cabin == "Economy"].pivot_table(index="month", columns="route",
                values="fare_usd", aggfunc="mean").round(2)

with pd.ExcelWriter("pricing_report.xlsx") as xl:
    by_route.to_excel(xl, sheet_name="By route", index=False)
    by_window.to_excel(xl, sheet_name="By booking window", index=False)
    monthly.to_excel(xl, sheet_name="Monthly trend")
clean.to_csv("fares_clean.csv", index=False)  # use this file in Power BI

fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(by_window["booking_window"].astype(str), by_window["avg_fare"], color="#1F3A5F")
ax.set(title="Economy: average fare by booking window", ylabel="USD")
fig.tight_layout(); fig.savefig("fare_by_booking_window.png", dpi=120)

fig, ax = plt.subplots(figsize=(9, 4))
monthly.plot(ax=ax); ax.set(title="Economy: monthly average fare by route", ylabel="USD")
fig.tight_layout(); fig.savefig("monthly_fare_trend.png", dpi=120)
print("Saved: pricing_report.xlsx, fares_clean.csv, 2 charts")
