# Databricks notebook source
# Run this in Databricks Free Edition: upload fares_clean.csv to a Volume, then paste/import this file.
# NOTE: written for Databricks - NOT tested in the sandbox where these files were created.

# COMMAND ----------
# Change the path to wherever you uploaded fares_clean.csv
path = "/Volumes/workspace/default/pricing/fares_clean.csv"
df = spark.read.csv(path, header=True, inferSchema=True)
display(df.limit(10))

# COMMAND ----------
from pyspark.sql import functions as F
summary = (df.groupBy("route", "cabin")
             .agg(F.count("*").alias("bookings"),
                  F.round(F.avg("fare_usd"), 2).alias("avg_fare"),
                  F.round(F.sum("fare_usd"), 0).alias("revenue")))
display(summary.orderBy("route", "cabin"))

# COMMAND ----------
summary.write.mode("overwrite").saveAsTable("pricing_route_summary")

# COMMAND ----------
# MAGIC %sql
# MAGIC SELECT route, ROUND(SUM(revenue),0) AS revenue,
# MAGIC        RANK() OVER (ORDER BY SUM(revenue) DESC) AS revenue_rank
# MAGIC FROM pricing_route_summary GROUP BY route
