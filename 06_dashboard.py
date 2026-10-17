"""Builds a one-page pricing dashboard image (Python/matplotlib) from fares_clean.csv.
This is a Python dashboard, not Power BI."""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("fares_clean.csv", parse_dates=["travel_date"])
eco = df[df.cabin == "Economy"]
NAVY = "#1F3A5F"

fig, ax = plt.subplots(2, 2, figsize=(13, 8))
fig.suptitle("Airline Fare Pricing Dashboard (simulated data)", fontsize=16, fontweight="bold", color=NAVY)

rev = df.groupby("route")["fare_usd"].sum().sort_values() / 1e6
ax[0, 0].barh(rev.index, rev.values, color=NAVY)
ax[0, 0].set(title="Revenue by route (USD millions)")

win = pd.cut(eco["days_before_departure"], [0, 7, 30, 90, 180], labels=["0-7", "8-30", "31-90", "91+"])
w = eco.groupby(win, observed=True)["fare_usd"].mean()
ax[0, 1].bar(w.index.astype(str), w.values, color="#3E7CB1")
ax[0, 1].set(title="Economy avg fare by days before departure", ylabel="USD")

m = eco.assign(month=eco.travel_date.dt.month).groupby(["month", "route"])["fare_usd"].mean().unstack()
m.plot(ax=ax[1, 0]); ax[1, 0].set(title="Economy avg fare by month", xlabel="Month", ylabel="USD")
ax[1, 0].legend(fontsize=7, ncol=2)

mix = df.groupby(["route", "cabin"])["fare_usd"].mean().unstack()
mix.plot.bar(ax=ax[1, 1], color=["#C0392B", NAVY]); ax[1, 1].set(title="Avg fare: Business vs Economy", xlabel="", ylabel="USD")
ax[1, 1].tick_params(axis="x", rotation=30)

for a in ax.flat: a.spines[["top", "right"]].set_visible(False)
fig.tight_layout(rect=[0, 0, 1, 0.95]); fig.savefig("dashboard.png", dpi=130)
print("dashboard.png saved")
