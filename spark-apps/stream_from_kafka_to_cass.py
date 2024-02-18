from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, struct
from pyspark.sql.types import StructType, StructField, StringType


if __name__ == "__main__":
    spark:SparkSession = SparkSession.builder \
        .appName("TrackEventLoader") \
        .config("spark.cassandra.connection.host", "cassandra") \
        .getOrCreate()
    
    schema = StructType([
        StructField("id", StringType(), True),
        StructField("user_id", StringType(), True),
        StructField("track_id", StringType(), True),
        StructField("track_name", StringType(), True),
        StructField("artist_name", StringType(), True),
    ])

    jdbcUrl = "jdbc:postgresql://postgres:5432/postgres"
    properties = {
        "user": "postgres",
        "password": "postgres",
        "driver": "org.postgresql.Driver"
    }

    userInfoDF = spark.read.jdbc(
        url=jdbcUrl, 
        table="user_info", 
        properties=properties
    )

    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "track-events") \
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
                               .option('checkpointLocation', '/tmp/checkpoint/track_events')
                               .option('keyspace', 'track_streams')
                               .option('table', 'track_events')
                               .start())
    
    casted_df = df.withColumn("user_id", df.user_id.cast("int"))
    enrichedDF = casted_df.join(userInfoDF, casted_df.user_id == userInfoDF.id)
    enrichedDF = enrichedDF.drop(userInfoDF.id)

    query = (enrichedDF.writeStream.format("org.apache.spark.sql.cassandra")
                               .option('checkpointLocation', '/tmp/checkpoint/enriched_track_events')
                               .option('keyspace', 'track_streams')
                               .option('table', 'enriched_track_events')
                               .start())
    
    aggDF = df.groupBy("user_id").count().withColumnRenamed("count", "track_events_count")

    # query = (aggDF.writeStream.format("org.apache.spark.sql.cassandra")
    #                            .option('checkpointLocation', '/tmp/checkpoint/user_metrics')
    #                            .option('keyspace', 'track_streams')
    #                            .option('table', 'user_metrics')
    #                            #.outputMode("append")
    #                            .start())
    
    ###

    def writeToCassandra(batchDF, batchId):
    # Write the batch DataFrame to Cassandra
        batchDF.write \
            .format("org.apache.spark.sql.cassandra") \
            .mode("append") \
            .option("keyspace", "track_streams") \
            .option("table", "user_metrics") \
            .save()

    query = (aggDF.writeStream 
        .outputMode("complete") 
        .foreachBatch(writeToCassandra) 
        .trigger(processingTime='5 seconds')  # Adjust based on your event rate
        .start())


    spark.streams.awaitAnyTermination()