"""Predicts fares with scikit-learn and compares against a simple baseline."""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error

df = pd.read_csv("fares_clean.csv", parse_dates=["travel_date"])
df["month"] = df["travel_date"].dt.month
df["dow"] = df["travel_date"].dt.dayofweek
df = df.sort_values("travel_date")

# time-based split: train on the earlier 80%, test on the latest 20%
cut = int(len(df) * 0.8)
train, test = df.iloc[:cut], df.iloc[cut:]

# baseline: average fare for the same route + cabin
base = train.groupby(["route", "cabin"])["fare_usd"].mean().rename("baseline")
test = test.join(base, on=["route", "cabin"])
mae_base = mean_absolute_error(test["fare_usd"], test["baseline"])

feats = ["route", "cabin", "days_before_departure", "month", "dow"]
X = pd.get_dummies(df[feats], columns=["route", "cabin"])
Xtr, Xte = X.iloc[:cut], X.iloc[cut:]
model = GradientBoostingRegressor(random_state=0).fit(Xtr, train["fare_usd"])
mae_model = mean_absolute_error(test["fare_usd"], model.predict(Xte))

print(f"Baseline MAE (route+cabin average): ${mae_base:,.2f}")
print(f"Model MAE (gradient boosting):      ${mae_model:,.2f}")
print(f"Improvement: {100*(1-mae_model/mae_base):.1f}%")

imp = pd.Series(model.feature_importances_, index=X.columns).sort_values().tail(8)
fig, ax = plt.subplots(figsize=(7, 4)); imp.plot.barh(ax=ax, color="#1F3A5F")
ax.set(title="What drives the predicted fare?"); fig.tight_layout()
fig.savefig("feature_importance.png", dpi=120)
