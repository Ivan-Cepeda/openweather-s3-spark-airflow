import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

def main():
    spark = SparkSession.builder \
        .appName("ETL_Weather_Normalization") \
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "com.amazonaws.auth.InstanceProfileCredentialsProvider") \
        .config("spark.sql.parquet.compression.codec", "snappy") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    try:
        print(">>> Extrayendo S3...")
        df_hist = spark.read.option("multiline", "true").json("s3a://raw-data-engineer/historicos/Patagonia_-41.json")
        df_stream = spark.read.json("s3a://raw-data-engineer/raw-data-engineer/stream/onecall/2026_02_13_1770945429650_0.jsonl.gz")

        df_hist_norm = df_hist.select(col("dt").cast("long"), col("lat").cast("double"), col("lon").cast("double"), col("main.temp").cast("double").alias("temp"), col("main.humidity").cast("integer").alias("humidity"))
        df_stream_norm = df_stream.select(col("_airbyte_data.current.dt").cast("long").alias("dt"), col("_airbyte_data.lat").cast("double").alias("lat"), col("_airbyte_data.lon").cast("double").alias("lon"), col("_airbyte_data.current.temp").cast("double").alias("temp"), col("_airbyte_data.current.humidity").cast("integer").alias("humidity"))

        df_final = df_hist_norm.union(df_stream_norm)
        
        output_path = "s3a://silver-data-engineer/weather_unified_parquet/"
        df_final.write.mode("overwrite").parquet(output_path)
        print(">>> ETL Finalizado exitosamente.")
    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
