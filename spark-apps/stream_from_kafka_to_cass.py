from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, struct, window, date_format, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, LongType


if __name__ == "__main__":
    spark:SparkSession = SparkSession.builder \
        .appName("TrackEventLoader") \
        .config("spark.cassandra.connection.host", "cassandra") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadminsecret") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .getOrCreate()
    
    schema = StructType([
        StructField("id", StringType(), True),
        StructField("user_id", StringType(), True),
        StructField("track_id", StringType(), True),
        StructField("track_name", StringType(), True),
        StructField("artist_name", StringType(), True),
        StructField("timestamp", LongType(), False)
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
        .option("startingOffsets", "latest") \
        .load()
    
    df = df.selectExpr("CAST(value AS STRING) as json_str") 
    df = df.select(from_json("json_str", schema).alias("data")).select("data.*")

    # Convert milliseconds to seconds for to_timestamp
    df = df.withColumn("timestamp", to_timestamp(col("timestamp") / 1000))


    # Write the streaming data to Cassandra

    query = (df.writeStream.format("org.apache.spark.sql.cassandra")
                               .option('checkpointLocation', '/tmp/checkpoint/track_events')
                               .option('keyspace', 'track_streams')
                               .option('table', 'track_events')
                               .start())
    
    # Delta table stream

    deltaQuery = (df.writeStream
        .format("delta")
        .option("checkpointLocation", "/tmp/checkpoint/minio/track_events") 
        .start("s3a://track-streams/track-events")
    )

    

    windowedCounts = df \
        .withWatermark("timestamp", "3 minute") \
        .groupBy(window("timestamp", "5 minutes", "1 minute"))  \
        .count()  # 5 minutes window, 1 minute slide, watermark 3 minutes to handle late events 
    

    def process_track_event_count(batch_df, batch_id):
        flattened_df = batch_df.select(
            date_format(col("window.start"), "yyyy-MM-dd HH:mm:ss").alias("start"),
            date_format(col("window.end"), "yyyy-MM-dd HH:mm:ss").alias("end"),
            col("count").alias("track_event_count")
        )
        flattened_df.write \
            .format("org.apache.spark.sql.cassandra") \
            .option("keyspace", "track_streams") \
            .option("table", "track_event_counts") \
            .mode("append") \
            .save()

    track_events_count_query = (
        windowedCounts.writeStream \
        .foreachBatch(process_track_event_count) \
        .option('checkpointLocation', '/tmp/checkpoint/track_events_count') \
        .outputMode("append") \
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
        # batchDF.persist() Cache data if writing to multiple data source to prevent multiple reads
        batchDF.write \
            .format("org.apache.spark.sql.cassandra") \
            .mode("append") \
            .option("keyspace", "track_streams") \
            .option("table", "user_metrics") \
            .save()
        # batchDF.unpersist() # Unpersist the data after write

    query = (aggDF.writeStream 
        .outputMode("complete") 
        .foreachBatch(writeToCassandra) 
        .trigger(processingTime='5 seconds')  # Adjust based on your event rate
        .start())


    spark.streams.awaitAnyTermination()