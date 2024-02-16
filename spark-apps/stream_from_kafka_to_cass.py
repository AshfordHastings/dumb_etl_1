from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, struct
from pyspark.sql.types import StructType, StructField, StringType


if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("KafkaToCassandra") \
        .config("spark.cassandra.connection.host", "cassandra") \
        .getOrCreate()
    
    schema = StructType([
        StructField("id", StringType(), True),
        StructField("first_name", StringType(), True),
        StructField("last_name", StringType(), True),
    ])

    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "users1") \
        .load()
    
    df = df.selectExpr("CAST(value AS STRING) as json_str") 
    df = df.select(from_json("json_str", schema).alias("data")).select("data.*")

    # Write the streaming data to Cassandra
    # query = df.writeStream \
    #     .foreachBatch(lambda batch_df, _: batch_df.write \
    #                   .format("org.apache.spark.sql.cassandra") \
    #                   .option("keyspace", "user_streams") \
    #                   .option("table", "users") \
    #                   .mode("append") \
    #                   .save()) \
    #     .outputMode("update") \
    #     .start()
    query = (df.writeStream.format("org.apache.spark.sql.cassandra")
                               .option('checkpointLocation', '/tmp/checkpoint')
                               .option('keyspace', 'user_streams')
                               .option('table', 'users')
                               .start())
    query.awaitTermination()