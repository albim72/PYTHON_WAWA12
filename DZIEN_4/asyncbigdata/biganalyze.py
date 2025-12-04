# spark_analysis.py
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

def main():
    spark = (
        SparkSession.builder
        .appName("Events5MAnalysis")
        .getOrCreate()
    )

    df = spark.read.parquet("events_5m.parquet")

    # 1) liczba zdarzeń per event_type
    cnt_by_type = (
        df.groupBy("event_type")
          .agg(F.count("*").alias("cnt"))
          .orderBy(F.desc("cnt"))
    )
    cnt_by_type.show(truncate=False)

    # 2) suma kwoty per user
    user_amounts = (
        df.groupBy("user_id")
          .agg(F.sum("amount").alias("total_amount"))
          .orderBy(F.desc("total_amount"))
    )
    user_amounts.show(10, truncate=False)

    # 3) window – cumulative sum per user
    purchase_df = df.filter(df.event_type == "purchase")

    w_user_time = Window.partitionBy("user_id").orderBy(F.col("timestamp").cast("long")) \
                        .rowsBetween(Window.unboundedPreceding, Window.currentRow)

    purchase_with_cum = purchase_df.withColumn(
        "cum_amount",
        F.sum("amount").over(w_user_time)
    )

    purchase_with_cum.select("user_id", "timestamp", "amount", "cum_amount") \
                     .orderBy("user_id", "timestamp") \
                     .show(20, truncate=False)

    # 4) okno czasowe 10 minut (agregacja)
    windowed = (
        df.withWatermark("timestamp", "30 minutes")  # przydatne przy strumieniach, tu symbolicznie
          .groupBy(
              F.window("timestamp", "10 minutes"),
              "event_type"
          )
          .agg(F.count("*").alias("cnt"))
          .orderBy("window")
    )

    windowed.show(20, truncate=False)

    spark.stop()

if __name__ == "__main__":
    main()
